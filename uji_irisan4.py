# Uji irisan 4 — baterai kesalahan sintaks: setiap kelas
# kesalahan menaikkan TempliteSyntaxError dengan pesan persis
# babnya, plus regresi irisan 1-3 sebagai subproses.
import subprocess
import sys

from templite import Templite, TempliteSyntaxError

lulus = 0


def cek(nama, kondisi):
    global lulus
    assert kondisi, f"GAGAL: {nama}"
    lulus += 1
    print(f"  ok {lulus:2d}. {nama}")


def cek_salah(nama, teks, pesan):
    try:
        Templite(teks)
    except TempliteSyntaxError as e:
        cek(nama, str(e) == pesan)
        return
    cek(nama + " (tidak menaikkan kesalahan!)", False)


print("== kelas kesalahan & pesan persis bab ==")
cek("TempliteSyntaxError adalah subclass ValueError",
    issubclass(TempliteSyntaxError, ValueError))
cek_salah("if tanpa ekspresi", "{% if %}",
          "Don't understand if: '{% if %}'")
cek_salah("if kelebihan kata", "{% if x y %}",
          "Don't understand if: '{% if x y %}'")
cek_salah("for tanpa 'in'", "{% for x y %}",
          "Don't understand for: '{% for x y %}'")
cek_salah("for dengan kata tengah salah", "{% for x dari ys %}{% endfor %}",
          "Don't understand for: '{% for x dari ys %}'")
cek_salah("end kelebihan kata", "{% endif x %}",
          "Don't understand end: '{% endif x %}'")
cek_salah("end tanpa pembuka", "{% endif %}",
          "Too many ends: '{% endif %}'")
cek_salah("end tak cocok dengan pembuka", "{% if x %}{% endfor %}",
          "Mismatched end tag: 'for'")
cek_salah("end tak cocok (arah sebaliknya)", "{% for x in ys %}{% endif %}",
          "Mismatched end tag: 'if'")
cek_salah("tag tak dikenal", "{% apaini %}",
          "Don't understand tag: 'apaini'")
cek_salah("nama variabel tak sah", "{{ 9nama }}",
          "Not a valid name: '9nama'")
cek_salah("nama filter tak sah", "{{ x|filter-jelek }}",
          "Not a valid name: 'filter-jelek'")
cek_salah("nama variabel loop tak sah", "{% for 9x in ys %}{% endfor %}",
          "Not a valid name: '9x'")
cek_salah("if tak ditutup", "{% if x %}isi",
          "Unmatched action tag: 'if'")
cek_salah("for tak ditutup", "{% for x in ys %}isi",
          "Unmatched action tag: 'for'")

print("== template sah tetap sah di tengah baterai ==")
cek("template campuran lengkap tetap jalan",
    Templite("{% if ok %}{% for t in ts %}{{t|upper}} {% endfor %}{% endif %}",
             {'upper': str.upper}).render({'ok': True, 'ts': ['a', 'b']})
    == "A B ")

print("== regresi irisan 1-3 (subproses) ==")
for n in (1, 2, 3):
    r = subprocess.run([sys.executable, f"uji_irisan{n}.py"],
                       capture_output=True, text=True)
    cek(f"uji_irisan{n} hijau penuh", r.returncode == 0
        and "HIJAU" in r.stdout)

print(f"\nIRISAN 4 HIJAU: {lulus} pemeriksaan")
