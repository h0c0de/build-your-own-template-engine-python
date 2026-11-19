# templite.py — Mesin template mini yang MENGOMPILASI template
# menjadi fungsi Python, lalu mengeksekusi fungsi itu.
#
# Ditulis ulang dari nol mengikuti desain Ned Batchelder,
# "A Template Engine", 500 Lines or Less (AOSA). Mesin yang
# sama dipakai coverage.py untuk laporan HTML-nya.
# Irisan 1: CodeBuilder + ekspresi & titik.
# Irisan 2: filter pipa. Irisan 3: tag if/for.

import re


class TempliteSyntaxError(ValueError):
    """Dinaikkan bila template tidak bisa dipahami kompiler."""


class CodeBuilder:
    """Membangun sumber Python baris demi baris dengan
    pengelolaan indentasi, plus 'section' — sub-builder yang
    tempatnya dipesan sekarang, isinya ditulis belakangan."""

    INDENT_STEP = 4      # Kata PEP8!

    def __init__(self, indent=0):
        self.code = []
        self.indent_level = indent

    def add_line(self, line):
        """Tambah satu baris; indent & newline disediakan."""
        self.code.extend([" " * self.indent_level, line, "\n"])

    def indent(self):
        self.indent_level += self.INDENT_STEP

    def dedent(self):
        self.indent_level -= self.INDENT_STEP

    def add_section(self):
        """Pesan tempat untuk sub-CodeBuilder; kembalikan dia
        agar bisa diisi kapan pun sebelum __str__ dipanggil."""
        section = CodeBuilder(self.indent_level)
        self.code.append(section)
        return section

    def __str__(self):
        return "".join(str(c) for c in self.code)

    def get_globals(self):
        """Eksekusi kode yang terkumpul, kembalikan dict global
        yang didefinisikannya."""
        # Pemeriksaan bahwa pemanggil menutup semua bloknya.
        assert self.indent_level == 0
        python_source = str(self)
        global_namespace = {}
        exec(python_source, global_namespace)
        return global_namespace


class Templite:
    """Template yang dikompilasi sekali, dirender berkali-kali.

    Templite(teks, *contexts) — contexts konstruktor adalah
    nilai global (bagus untuk filter & konstanta); render(ctx)
    menggabungkannya dengan data per-render (yang menang).
    """

    def __init__(self, text, *contexts):
        self.context = {}
        for context in contexts:
            self.context.update(context)

        self.all_vars = set()
        self.loop_vars = set()

        code = CodeBuilder()
        code.add_line("def render_function(context, do_dots):")
        code.indent()
        vars_code = code.add_section()
        code.add_line("result = []")
        code.add_line("append_result = result.append")
        code.add_line("extend_result = result.extend")
        code.add_line("to_str = str")

        buffered = []

        def flush_output():
            """Paksa isi penyangga menjadi baris kode."""
            if len(buffered) == 1:
                code.add_line("append_result(%s)" % buffered[0])
            elif len(buffered) > 1:
                code.add_line("extend_result([%s])" % ", ".join(buffered))
            del buffered[:]

        tokens = re.split(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", text)

        # Tumpukan tag aksi yang sedang terbuka ('if'/'for'),
        # untuk memeriksa pasangan end-nya.
        ops_stack = []

        for token in tokens:
            if token.startswith('{#'):
                # Komentar: abaikan, lanjut token berikutnya.
                continue
            elif token.startswith('{{'):
                # Ekspresi untuk dievaluasi.
                expr = self._expr_code(token[2:-2].strip())
                buffered.append("to_str(%s)" % expr)
            elif token.startswith('{%'):
                # Tag aksi: pisah menjadi kata-kata, urai lebih
                # lanjut. Penyangga harus ditulis dulu karena
                # struktur kontrol memotong aliran keluaran.
                flush_output()
                words = token[2:-2].strip().split()

                if words[0] == 'if':
                    # {% if ekspresi %}
                    if len(words) != 2:
                        self._syntax_error("Don't understand if", token)
                    ops_stack.append('if')
                    code.add_line("if %s:" % self._expr_code(words[1]))
                    code.indent()
                elif words[0] == 'for':
                    # {% for nama in ekspresi %}
                    if len(words) != 4 or words[2] != 'in':
                        self._syntax_error("Don't understand for", token)
                    ops_stack.append('for')
                    self._variable(words[1], self.loop_vars)
                    code.add_line(
                        "for c_%s in %s:" % (
                            words[1],
                            self._expr_code(words[3]),
                        )
                    )
                    code.indent()
                elif words[0].startswith('end'):
                    # {% endif %} / {% endfor %}: cukup dedent,
                    # sisanya pemeriksaan pasangan.
                    if len(words) != 1:
                        self._syntax_error("Don't understand end", token)
                    end_what = words[0][3:]
                    if not ops_stack:
                        self._syntax_error("Too many ends", token)
                    start_what = ops_stack.pop()
                    if start_what != end_what:
                        self._syntax_error("Mismatched end tag", end_what)
                    code.dedent()
                else:
                    self._syntax_error("Don't understand tag", words[0])
            else:
                # Konten literal. Lewati yang kosong.
                if token:
                    buffered.append(repr(token))

        if ops_stack:
            self._syntax_error("Unmatched action tag", ops_stack[-1])

        flush_output()

        # Prolog: bongkar semua nama yang dipakai (dan bukan
        # variabel loop) dari context menjadi lokal c_*.
        for var_name in self.all_vars - self.loop_vars:
            vars_code.add_line("c_%s = context[%r]" % (var_name, var_name))

        code.add_line("return ''.join(result)")
        code.dedent()

        self._render_function = code.get_globals()['render_function']

    # -- kompilasi ekspresi -------------------------------------

    def _expr_code(self, expr):
        """Ubah ekspresi template menjadi ekspresi Python."""
        if "|" in expr:
            # Filter pipa: nilai mengalir kiri -> kanan melewati
            # tiap fungsi; nama filter juga variabel context.
            pipes = expr.split("|")
            code = self._expr_code(pipes[0])
            for func in pipes[1:]:
                self._variable(func, self.all_vars)
                code = "c_%s(%s)" % (func, code)
        elif "." in expr:
            dots = expr.split(".")
            code = self._expr_code(dots[0])
            args = ", ".join(repr(d) for d in dots[1:])
            code = "do_dots(%s, %s)" % (code, args)
        else:
            self._variable(expr, self.all_vars)
            code = "c_%s" % expr
        return code

    # -- pembantu ------------------------------------------------

    def _syntax_error(self, msg, thing):
        raise TempliteSyntaxError("%s: %r" % (msg, thing))

    def _variable(self, name, vars_set):
        """Catat `name` sebagai variabel; tolak nama tak sah."""
        if not re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", name):
            self._syntax_error("Not a valid name", name)
        vars_set.add(name)

    # -- rendering ------------------------------------------------

    def render(self, context=None):
        """Render template dengan `context` (dict) tertentu."""
        render_context = dict(self.context)
        if context:
            render_context.update(context)
        return self._render_function(render_context, self._do_dots)

    def _do_dots(self, value, *dots):
        """Makna titik saat runtime: coba atribut dulu, lalu
        kunci item; hasil yang callable langsung dipanggil."""
        for dot in dots:
            try:
                value = getattr(value, dot)
            except AttributeError:
                value = value[dot]
            if callable(value):
                value = value()
        return value
