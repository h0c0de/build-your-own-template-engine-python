# Build Your Own Template Engine — Python

Mesin template mini **Templite** yang ditulis ulang dari nol di
Python murni (hanya `re`, tanpa dependensi), mengikuti desain
**Ned Batchelder, "A Template Engine"**, dari buku
*500 Lines or Less* (Architecture of Open Source Applications)
— http://aosabook.org/en/500L/a-template-engine.html.
Mesin inilah yang dipakai **coverage.py** untuk laporan HTML-nya.

Berbeda dari banyak mesin template, Templite **mengompilasi**
template menjadi fungsi Python sungguhan (sekali, saat
konstruksi), lalu mengeksekusi fungsi itu pada setiap render.

## Contoh

```python
from templite import Templite

templite = Templite('''
    <h1>Hello {{name|upper}}!</h1>
    {% for topic in topics %}
        <p>You are interested in {{topic}}.</p>
    {% endfor %}
    ''', {'upper': str.upper})

print(templite.render({
    'name': "Ned",
    'topics': ['Python', 'Geometry', 'Juggling'],
}))
```

Fitur bahasa templatenya:

- `{{ nama }}` — variabel; `{{ a.b.c }}` — titik berarti
  atribut, kunci dict, atau metode tanpa argumen (dicoba
  berurutan, yang callable dipanggil).
- `{{ x|f|g }}` — filter pipa, diterapkan kiri ke kanan;
  filter hanyalah callable di dalam context.
- `{% if x %} ... {% endif %}`, `{% for t in ts %} ...
  {% endfor %}` — termasuk bersarang.
- `{# komentar #}` — dibuang saat kompilasi.
- Kesalahan sintaks menaikkan `TempliteSyntaxError` dengan
  pesan yang jelas ("Mismatched end tag: 'for'", dst).

Yang sengaja **tidak** ada (sesuai babnya): pewarisan/include
template, tag kustom, autoescaping, argumen filter, else/elif,
loop multi-variabel, kontrol whitespace.

## Arsitektur

- `CodeBuilder` — merakit sumber Python baris demi baris
  dengan indentasi terkelola dan *section* (tempat yang dipesan
  sekarang, diisi belakangan — kunci prolog variabel).
- Kompilasi satu regex memecah template menjadi token literal,
  `{{ }}`, `{% %}`, `{# #}`; keluaran disangga menjadi
  `append_result`/`extend_result`; di akhir, semua variabel
  non-loop dibongkar dari context di prolog fungsi.
- `_expr_code` rekursif: pipa dulu, lalu titik, lalu nama.

## Uji

```bash
python3 uji_irisan1.py   # CodeBuilder + ekspresi & titik
python3 uji_irisan2.py   # filter pipa
python3 uji_irisan3.py   # if/for + dua contoh bab byte-exact
python3 uji_irisan4.py   # baterai kesalahan + regresi penuh
```

Total 74 pemeriksaan, termasuk dua render contoh bab yang
byte-exact, perbandingan struktur kode terbangkit terhadap
fungsi yang dicetak bab, dan 13 kelas kesalahan sintaks dengan
pesan persis babnya.

Bagian dari seri **build-your-own-x** (fork
`codecrafters-io/build-your-own-x`): implementasi ulang
Python dari panduan-panduan klasik, dikerjakan irisan demi
irisan dengan uji di setiap langkah. Rencana dan pagar
kelengkapan ada di `RENCANA.md`; konsep per irisan dan temuan
selama pengerjaan ada di `CATATAN.md`.

## Lisensi & atribusi

Kode di repo ini adalah penulisan ulang untuk belajar.
Desain dan algoritmanya berasal dari bab "A Template Engine"
karya Ned Batchelder dalam *500 Lines or Less* (AOSA),
dilisensikan CC BY 3.0.
