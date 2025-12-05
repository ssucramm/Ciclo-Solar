import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import numpy as np
from reader import years, cals, ciclos

x= np.array(years)
y= np.array(cals)

plt.scatter(x, y, s=4, color='gray')

def periodo(x, y):
    spline = UnivariateSpline(x, y, s=0.1)
    xs = np.linspace(min(x), max(x), 100)
    ys = spline(xs)
    plt.plot(xs, ys, color='blue', linewidth=2)

for inicio, fim in ciclos:
    mask = (x >= inicio) & (x <= fim)
    periodo(x[mask], y[mask])

plt.xlabel('Years in JD-2400000')
plt.ylabel('S-index')
plt.title('S-index during Solar Cycles')
plt.show()
