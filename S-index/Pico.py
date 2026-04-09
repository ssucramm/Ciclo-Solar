from converter import jd_to_date
from astropy.io import fits

hdul = fits.open("sindex.fit")
data = hdul[1].data

sindex = []
for i in data:
    sindex.append(float(i[2]))
sindex = sorted(sindex, reverse=True)[0], sorted(sindex, reverse=True)[1]
print(sindex)

anos = []
for i in data:
    if i[2] in sindex:
        anos.append(float(i[0]))


for i in anos:
    print(jd_to_date(i + 2400000)[0])
    
print(anos)