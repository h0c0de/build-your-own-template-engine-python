# Uji irisan 3 — tag {% if %} & {% for %}: dua contoh bab
# byte-exact (halaman mainan & contoh pemakaian), struktur kode
# terbangkit vs cetakan bab, dan sarang tag.
import templite as modul
from templite import Templite

lulus = 0


def cek(nama, kondisi):
    global lulus
    assert kondisi, f"GAGAL: {nama}"
    lulus += 1
    print(f"  ok {lulus:2d}. {nama}")


print("== if dasar ==")
t = Templite("{% if x %}YA{% endif %}")
cek("if benar -> isi tampil", t.render({'x': True}) == "YA")
cek("if salah -> kosong", t.render({'x': False}) == "")
t = Templite("{% if user.is_logged_in %}<p>Welcome, {{user.name}}!</p>{% endif %}")
cek("contoh bab: if dengan kondisi titik",
    t.render({'user': {'is_logged_in': True, 'name': 'Ned'}})
    == "<p>Welcome, Ned!</p>")
cek("kondisi titik salah -> kosong",
    t.render({'user': {'is_logged_in': False, 'name': 'Ned'}}) == "")

print("== for dasar: contoh tokenisasi bab ==")
t = Templite("<p>Topics for {{name}}: {% for t in topics %}{{t}}, {% endfor %}</p>")
cek("daftar topik bab byte-exact",
    t.render({'name': "Ned",
              'topics': ['Python', 'Geometry', 'Juggling']})
    == "<p>Topics for Ned: Python, Geometry, Juggling, </p>")
cek("loop kosong -> tak ada keluaran",
    Templite("{% for t in ts %}[{{t}}]{% endfor %}").render({'ts': []}) == "")

print("== contoh pemakaian bab, byte-exact ==")
teks = ("\n    <h1>Hello {{name|upper}}!</h1>\n"
        "    {% for topic in topics %}\n"
        "        <p>You are interested in {{topic}}.</p>\n"
        "    {% endfor %}\n    ")
t = Templite(teks, {'upper': str.upper})
harapan = ("\n    <h1>Hello NED!</h1>\n    "
           + "".join("\n        <p>You are interested in %s.</p>\n    " % topik
                     for topik in ['Python', 'Geometry', 'Juggling'])
           + "\n    ")
cek("halaman Ned + 3 topik persis seperti turunan bab",
    t.render({'name': "Ned",
              'topics': ['Python', 'Geometry', 'Juggling']}) == harapan)

print("== halaman mainan bab, byte-exact ==")
teks_mainan = ("<p>Welcome, {{user_name}}!</p>\n"
               "<p>Products:</p>\n"
               "<ul>\n"
               "{% for product in product_list %}\n"
               "    <li>{{ product.name }}:\n"
               "        {{ product.price|format_price }}</li>\n"
               "{% endfor %}\n"
               "</ul>\n")
produk = [{'name': 'Apple', 'price': 1.0},
          {'name': 'Fig', 'price': 1.5},
          {'name': 'Pomegranate', 'price': 3.25}]
t = Templite(teks_mainan, {'format_price': lambda p: "$%.2f" % p})
harapan = ("<p>Welcome, Charlie!</p>\n<p>Products:</p>\n<ul>\n"
           + "".join("\n    <li>%s:\n        $%.2f</li>\n" % (p['name'], p['price'])
                     for p in produk)
           + "\n</ul>\n")
cek("Charlie + Apple/Fig/Pomegranate persis target bab",
    t.render({'user_name': "Charlie", 'product_list': produk}) == harapan)

print("== struktur kode terbangkit vs cetakan bab ==")
tertangkap = {}


class Rekam(modul.CodeBuilder):
    def get_globals(self):
        tertangkap['sumber'] = str(self)
        return super().get_globals()


modul.CodeBuilder = Rekam
try:
    Templite(teks_mainan, {'format_price': lambda p: "$%.2f" % p})
finally:
    modul.CodeBuilder = modul.CodeBuilder.__mro__[1]
sumber = tertangkap['sumber']
for potongan in ["def render_function(context, do_dots):",
                 "c_user_name = context['user_name']",
                 "c_product_list = context['product_list']",
                 "c_format_price = context['format_price']",
                 "for c_product in c_product_list:",
                 "to_str(do_dots(c_product, 'name'))",
                 "to_str(c_format_price(do_dots(c_product, 'price')))",
                 "append_result('\\n</ul>\\n')",
                 "return ''.join(result)"]:
    cek(f"kode mengandung potongan bab: {potongan[:44]}", potongan in sumber)
cek("variabel loop TIDAK dibongkar dari context",
    "c_product = context['product']" not in sumber)

print("== sarang tag ==")
t = Templite("{% for r in baris %}{% for c in r %}{{c}}{% endfor %};{% endfor %}")
cek("for di dalam for", t.render({'baris': [[1, 2], [3]]}) == "12;3;")
t = Templite("{% if tampil %}{% for x in xs %}[{{x}}]{% endfor %}{% endif %}")
cek("for di dalam if (benar)",
    t.render({'tampil': True, 'xs': [1, 2]}) == "[1][2]")
cek("for di dalam if (salah)", t.render({'tampil': False, 'xs': [1, 2]}) == "")
t = Templite("{% for n in ns %}{% if n.genap %}{{n.v}} {% endif %}{% endfor %}")
cek("if di dalam for dengan titik",
    t.render({'ns': [{'genap': True, 'v': 'a'},
                     {'genap': False, 'v': 'b'},
                     {'genap': True, 'v': 'c'}]}) == "a c ")

print(f"\nIRISAN 3 HIJAU: {lulus} pemeriksaan")
