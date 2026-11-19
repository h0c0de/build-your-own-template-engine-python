# Uji irisan 2 — filter pipa: satu filter, rantai filter,
# filter di atas ekspresi titik, dan urutan penerapan.
from templite import Templite, TempliteSyntaxError

lulus = 0


def cek(nama, kondisi):
    global lulus
    assert kondisi, f"GAGAL: {nama}"
    lulus += 1
    print(f"  ok {lulus:2d}. {nama}")


print("== satu filter: contoh bab ==")
t = Templite("<h1>Hello {{name|upper}}!</h1>", {'upper': str.upper})
cek("{{name|upper}} dengan upper dari context konstruktor",
    t.render({'name': "Ned"}) == "<h1>Hello NED!</h1>")

print("== rantai filter: contoh bab slugify|lower ==")


def slugify(s):
    return s.replace(' ', '-')


t = Templite("<p>Short name: {{story.subject|slugify|lower}}</p>",
             {'slugify': slugify, 'lower': str.lower})
cek("dua filter berantai pada ekspresi titik",
    t.render({'story': {'subject': 'Hello World Again'}})
    == "<p>Short name: hello-world-again</p>")

print("== urutan penerapan kiri -> kanan ==")
t = Templite("{{x|tambah1|kali10}}",
             {'tambah1': lambda v: v + 1, 'kali10': lambda v: v * 10})
cek("(5 + 1) * 10 = 60, bukan 5 + (1 * 10)",
    t.render({'x': 5}) == "60")

print("== filter di atas titik & dari context render ==")
t = Templite("{{product.price|format_price}}")
cek("format_price ala bab: 1.5 -> $1.50",
    t.render({'product': {'price': 1.5},
              'format_price': lambda p: "$%.2f" % p}) == "$1.50")
t = Templite("{{x|dobel}}")
cek("filter boleh datang dari context render saja",
    t.render({'x': 3, 'dobel': lambda v: v * 2}) == "6")

print("== bentuk kode yang dibangkitkan ==")
t = Templite("{{name|upper}}", {'upper': str.upper})
cek("_expr_code('name|upper') = c_upper(c_name)",
    t._expr_code("name|upper") == "c_upper(c_name)")
cek("_expr_code('a.b|f') = c_f(do_dots(c_a, 'b'))",
    t._expr_code("a.b|f") == "c_f(do_dots(c_a, 'b'))")

print("== kegagalan yang jujur ==")
try:
    Templite("{{x|tak-ada}}")
    cek("nama filter tak sah -> TempliteSyntaxError", False)
except TempliteSyntaxError:
    cek("nama filter tak sah -> TempliteSyntaxError", True)
try:
    Templite("{{x|hilang}}").render({'x': 1})
    cek("filter tak ada di context -> KeyError saat render", False)
except KeyError:
    cek("filter tak ada di context -> KeyError saat render", True)

print(f"\nIRISAN 2 HIJAU: {lulus} pemeriksaan")
