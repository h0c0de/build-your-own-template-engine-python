# Catatan — Template Engine (Templite, 500L)

Satu halaman per irisan: konsep inti dan temuan selama membangun.
Panduan: Ned Batchelder, "A Template Engine", 500 Lines or Less.

## Irisan 1 — CodeBuilder + kompilasi dasar

Konsep inti: **template dikompilasi menjadi fungsi Python.**
CodeBuilder merakit sumber baris demi baris (indent otomatis,
`add_section` memesan tempat yang diisi belakangan — dipakai
untuk prolog variabel yang baru diketahui di akhir kompilasi),
lalu `get_globals` meng-exec sumber itu dan mengembalikan
fungsi render-nya. Template dipecah satu regex menjadi token
literal / `{{ }}` / `{% %}` / `{# #}`; literal menjadi
`repr(token)`, ekspresi menjadi `to_str(...)`, dan keduanya
disangga lalu ditulis sebagai satu append/extend.

Titik adalah sihir runtime, bukan kompilasi: `{{a.b.c}}`
dikompilasi menjadi `do_dots(c_a, 'b', 'c')`, dan do_dots
mencoba getattr, cadangan ke akses item, dan memanggil hasil
yang callable — satu sintaks titik untuk tiga makna Python.

Temuan:
- Contoh exec bab (SEVENTEEN/three) dan mekanisme section
  bereproduksi persis; section yang diisi paling akhir tampil
  di posisi yang dipesan di awal — kunci seluruh desain prolog.
- Variabel yang hilang meledak sebagai KeyError dari baris
  prolog `context['nama']` pada saat render, bukan saat
  kompilasi — perilaku asli desain bab, dicatat apa adanya.
- Komentar sudah tuntas di irisan ini (token `{# #}` memang
  dibuang sejak tokenisasi pertama bab).

## Irisan 2 — Filter

Konsep inti: **pipa adalah komposisi fungsi yang dikompilasi
bersarang.** `_expr_code` memeriksa pipa *sebelum* titik:
`x|f|g` menjadi `c_g(c_f(<kode x>))`, dan `a.b|f` menjadi
`c_f(do_dots(c_a, 'b'))` — rekursi pada potongan pertama
menangani sisanya. Nama filter diperlakukan persis seperti
variabel: dicatat di all_vars, dibongkar di prolog, dan boleh
datang dari context konstruktor (global) atau context render.

Temuan:
- Urutan penerapan murni kiri → kanan: (5+1)×10 = 60 pada uji
  tambah1|kali10 — rantai pipa tidak berkelompok ke kanan.
- Karena filter hanyalah variabel context yang callable,
  "filter tak terdaftar" bukan kesalahan kompilasi melainkan
  KeyError saat render — konsisten dengan variabel hilang.
- Bentuk kode terbangkit bisa diuji langsung sebagai string
  (`c_upper(c_name)`) — kompiler yang bisa diintip hasil
  terjemahannya jauh lebih mudah diuji daripada yang kotak
  hitam.

## Irisan 3 — Pernyataan if & for

Konsep inti: **tag aksi adalah struktur kontrol Python yang
sedang ditulis.** Kompiler memelihara ops_stack untuk
memeriksa pasangan end (end tag sendiri tidak membangkitkan
apa pun selain dedent — keajaiban if/for murni indentasi
Python), dan memisahkan all_vars dari loop_vars supaya prolog
membongkar hanya nama dari context: variabel loop lahir dari
pernyataan for itu sendiri.

Bukti terkuat build ini sejauh ini: DUA contoh bab bereproduksi
byte-exact — halaman mainan Charlie + Apple/Fig/Pomegranate
dan contoh pemakaian Ned + tiga topik — dan potongan struktur
kode terbangkit cocok dengan fungsi yang dicetak bab,
termasuk fakta bahwa c_product TIDAK muncul di prolog.

Temuan:
- Uji irisan 1 harus disesuaikan: pemeriksaannya "tag ditolak"
  mencerminkan penahapan irisan, bukan perilaku akhir — diganti
  menjadi "tag tak dikenal ditolak", yang memang permanen.
- Menangkap sumber terkompilasi untuk pengujian bisa dilakukan
  dengan menambal CodeBuilder di modul — kompiler yang hasil
  terjemahannya bisa diintip adalah kompiler yang bisa diuji.

## Irisan 4 — Error & terbit

Konsep inti: **kompiler yang baik gagal dengan pesan yang
baik.** Seluruh permukaan kesalahan bab diperiksa satu-satu —
aritas if/for/end, end berlebih, end tak cocok dua arah, tag
tak dikenal, nama tak sah (variabel, filter, dan variabel
loop), dan tag tak tertutup — dan ke-13 kelasnya menaikkan
TempliteSyntaxError dengan pesan yang sama persis dengan
babnya, termasuk format "%s: %r"-nya.

Temuan:
- Pesan kesalahan bab cukup spesifik untuk dipakai sebagai
  jangkar byte-exact ("Mismatched end tag: 'for'") — dan
  semuanya cocok tanpa satu pun penyesuaian implementasi di
  irisan ini: kelas-kelas kesalahan itu sudah jatuh secara
  alami dari struktur kompiler irisan 1–3.
- Total seri uji build ini: 74 pemeriksaan (24 + 9 + 22 + 19).
