from astropy.io import fits
from converter import jd_to_date

input("Pressione Enter para continuar...")
print("Certifique-se de que a data esteja entre 1966 e 2016")

start_txt = input("Periodo de start (Enter = 1966): ").strip()
end_txt = input("Periodo de end (Enter = 2016): ").strip()

start = 1966
end = 2016

if start_txt.isdigit():
    start = int(start_txt)

if end_txt.isdigit():
    end = int(end_txt)


start = max(1966, min(start, 2016))
end = max(1966, min(end, 2016))


if start > end:
    start, end = end, start

print(f"Período definido de {start} a {end}")
input("Pressione Enter para continuar...")


hdul = fits.open("sindex.fit")

data = hdul[1].data

years = []
cals = []

ciclo20, ciclo21, ciclo22, ciclo23, ciclo24 = [], [], [], [], []

for row in data:
    jd = float(row[0])
    year = jd_to_date(jd + 2400000)[0] 

    if not (start <= year <= end):
        continue

    years.append(jd)
    cals.append(float(row[2]))

    if 1965 <= year <= 1977:
        ciclo20.append(jd)
    elif 1976 < year <= 1987:
        ciclo21.append(jd)
    elif 1986 < year <= 1997:
        ciclo22.append(jd)
    elif 1996 < year <= 2009:
        ciclo23.append(jd)
    

ciclos = []
for ciclo in [ciclo20, ciclo21, ciclo22, ciclo23, ciclo24]:
    if len(ciclo) > 1:
        ciclos.append((ciclo[0], ciclo[-1]))

