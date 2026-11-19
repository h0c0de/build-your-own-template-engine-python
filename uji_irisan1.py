# Uji irisan 1 — CodeBuilder + kompilasi dasar Templite:
# literal, {{ nama }}, titik (atribut/kunci/callable), komentar,
# dan gabungan context.
from templite import CodeBuilder, Templite, TempliteSyntaxError

lulus = 0


def cek(nama, kondisi):
    global lulus
    assert kondisi, f"GAGAL: {nama}"
    lulus += 1
    print(f"  ok {lulus:2d}. {nama}")


print("== CodeBuilder ==")
cb = CodeBuilder()
cb.add_line("SEVENTEEN = 17")
cb.add_line("def three():")
cb.indent()
cb.add_line("return 3")
cb.dedent()
ns = cb.get_globals()
cek("contoh exec bab: SEVENTEEN = 17", ns['SEVENTEEN'] == 17)
cek("contoh exec bab: three() = 3", ns['three']() == 3)

cb = CodeBuilder()
cb.add_line("def f():")
cb.indent()
seksi = cb.add_section()
cb.add_line("return x")
cb.dedent()
seksi.add_line("x = 41")
cek("section diisi belakangan, tampil di tempatnya",
    str(cb) == "def f():\n    x = 41\n    return x\n")
cek("fungsi hasil section berjalan", cb.get_globals()['f']() == 41)

cb = CodeBuilder()
cb.add_line("x = 1")
cb.indent()
try:
    cb.get_globals()
    cek("get_globals menolak indent menggantung", False)
except AssertionError:
    cek("get_globals menolak indent menggantung", True)

print("== literal & ekspresi polos ==")
cek("template literal utuh", Templite("Halo dunia").render() == "Halo dunia")
cek("template kosong", Templite("").render() == "")
cek("satu variabel", Templite("Hello {{name}}!").render(
    {'name': "Ned"}) == "Hello Ned!")
cek("nilai bukan string diubah str()", Templite("n={{n}}").render(
    {'n': 17}) == "n=17")
cek("beberapa variabel & literal berselang",
    Templite("A{{x}}B{{y}}C").render({'x': 1, 'y': 2}) == "A1B2C")
cek("fungsi terkompilasi tersimpan & callable",
    callable(Templite("x")._render_function))

print("== titik: atribut, kunci, callable ==")
cek("titik pada dict", Templite("{{user.name}}").render(
    {'user': {'name': 'Charlie'}}) == "Charlie")
cek("titik berantai", Templite("{{a.b.c}}").render(
    {'a': {'b': {'c': 'dalam'}}}) == "dalam")


class Produk:
    def __init__(self):
        self.name = "Apple"

    def price(self):
        return 100


cek("titik pada atribut objek", Templite("{{p.name}}").render(
    {'p': Produk()}) == "Apple")
cek("metode callable dipanggil otomatis (tanpa kurung)",
    Templite("{{p.price}}").render({'p': Produk()}) == "100")
cek("callable di dalam dict dipanggil", Templite("{{d.f}}").render(
    {'d': {'f': lambda: 'panggil'}}) == "panggil")


class HanyaItem:
    def __getitem__(self, kunci):
        return "item:" + kunci


cek("cadangan ke akses item bila atribut tak ada",
    Templite("{{o.kunci}}").render({'o': HanyaItem()}) == "item:kunci")

print("== komentar ==")
cek("komentar hilang", Templite("A{# ini komentar #}B").render() == "AB")
cek("komentar multi-baris hilang",
    Templite("A{# satu\ndua #}B").render() == "AB")

print("== context: gabungan & pemakaian ulang ==")
t = Templite("{{a}}{{b}}", {'a': '1', 'b': '2'})
cek("context konstruktor dipakai", t.render() == "12")
cek("context render menimpa konstruktor", t.render({'b': '3'}) == "13")
cek("render berikutnya tidak tercemar render sebelumnya",
    t.render() == "12")
try:
    Templite("{{takada}}").render({})
    cek("variabel hilang -> KeyError", False)
except KeyError:
    cek("variabel hilang -> KeyError (dari prolog context[...])", True)

print("== tag {% %} tak dikenal tetap ditolak ==")
try:
    Templite("{% apaini x %}")
    cek("tag tak dikenal ditolak", False)
except TempliteSyntaxError:
    cek("tag tak dikenal ditolak (if/for sah tiba di irisan 3)", True)

print(f"\nIRISAN 1 HIJAU: {lulus} pemeriksaan")
