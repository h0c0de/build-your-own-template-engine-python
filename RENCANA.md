# Rencana — Build Keempat Belas: Template Engine (Templite, 500L)

Mengikuti bab **Ned Batchelder**, *"A Template Engine"*, dari
buku *500 Lines or Less* (The Architecture of Open Source
Applications) — entri Python kategori Template Engine di repo
codecrafters-io/build-your-own-x. Mesin yang sama dipakai
coverage.py untuk laporan HTML-nya.

Panduan: http://aosabook.org/en/500L/a-template-engine.html

## Isi bab (terverifikasi 19 Nov 2026, dibaca utuh)

Pendekatan **kompilasi**, bukan interpretasi: template
dikompilasi sekali menjadi fungsi Python `render_function`,
lalu fungsi itu dieksekusi tiap render.

- `CodeBuilder` — pembangun sumber Python: add_line dengan
  indent otomatis, add_section (sub-builder yang diisi
  belakangan, untuk prolog variabel), get_globals mengeksekusi
  kode jadi namespace.
- Tokenisasi satu regex: `(?s)({{.*?}}|{%.*?%}|{#.*?#})`.
- Ekspresi `{{ }}`: nama polos → lokal `c_nama`; titik →
  `do_dots(v, 'a', 'b')` yang saat runtime mencoba getattr,
  lalu item, dan memanggil hasil yang callable; filter pipa
  → `c_filter(ekspresi)`.
- Tag `{% if %}` / `{% for x in xs %}` / `{% end... %}` dengan
  tumpukan ops untuk memeriksa pasangan; kesalahan menaikkan
  `TempliteSyntaxError`.
- Prolog fungsi: semua nama di all_vars dikurangi loop_vars
  dibongkar dari context menjadi lokal `c_*`.
- Keluaran disangga: 1 potong → append_result, banyak →
  extend_result (mikro-optimasi khas bab ini).

Jangkar dari bab: kode Python hasil kompilasi untuk template
mainan bab (Welcome Charlie + daftar produk) DICETAK di bab —
struktur hasil kompilasi kami dibandingkan dengannya; contoh
pemakaian Templite bab (Hello NED + topik) dirender byte-exact.

## Adaptasi yang dicatat terbuka

- Tidak ada adaptasi fungsional: bab ini murni Python stdlib
  (re saja) dan kodenya berjalan apa adanya di Python 3.12.
  Penulisan ulang mengikuti struktur bab baris demi baris
  konsep, dengan komentar bahasa Indonesia.

## Irisan

- [x] Irisan 1 — CodeBuilder + kompilasi dasar: CodeBuilder
      utuh (termasuk contoh exec SEVENTEEN bab), Templite
      dengan literal + `{{ nama }}` + titik (do_dots: atribut,
      kunci dict, callable dipanggil) + komentar `{# #}` +
      render dengan gabungan context konstruktor & render.
- [x] Irisan 2 — Filter: rantai pipa `{{ x|f|g }}` lewat
      _expr_code rekursif; filter dari context konstruktor.
      Bukti: contoh bab {{name|upper}} → NED; rantai dua
      filter persis contoh bab (slugify|lower).
- [x] Irisan 3 — Pernyataan: {% if %}, {% for %}, end tag +
      ops_stack + prolog all_vars − loop_vars. Bukti: halaman
      mainan bab (Charlie + 3 produk) byte-exact; contoh
      lengkap bab (Ned + 3 topik) byte-exact; struktur kode
      terkompilasi dibandingkan dengan cetakan bab.
- [x] Irisan 4 — Error & terbit: TempliteSyntaxError untuk
      if/for/end menyimpang, end berlebih, end tak cocok,
      tag tak dikenal, nama tak sah, tag tak tertutup;
      regresi 1–3; terbit ke
      `build-your-own-template-engine-python`.

## Pagar selesai

- [x] Halaman mainan bab dirender byte-exact dari template
      persis bab.
- [x] Struktur render_function terkompilasi cocok dengan
      cetakan bab (dinormalisasi spasi).
- [x] Semua kelas kesalahan sintaks menaikkan
      TempliteSyntaxError dengan pesan bab.
- [x] `CATATAN.md` satu halaman per irisan: konsep inti + temuan.
- [x] Repo GitHub publik `build-your-own-template-engine-python`
      terbit & terverifikasi.
