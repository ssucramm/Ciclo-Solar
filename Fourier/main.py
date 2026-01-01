import numpy as np
import matplotlib.pyplot as plt

dados = np.loadtxt("sunspots.txt")

tempo = dados[:,2]
n_manchas = dados[:,3]

fig = plt.figure(figsize=(20,8))
plt.plot(tempo,n_manchas)
plt.xlabel("Ano",fontsize=18)
plt.ylabel("Número de Manchas",fontsize=18)
plt.yticks(fontsize=18)
plt.xticks(fontsize=18)
plt.show

def dft(y):
    N = len(y)
    c = np.zeros(N//2+1,complex)
    for k in range(N//2+1):
        for n in range(N):
            c[k] += y[n]*np.exp(-2j*np.pi*k*n/N)
    return c

coef = list(dft(n_manchas))

fig = plt.figure(figsize=(20,8))
plt.plot(abs(np.array(coef)**2),"r")
plt.xlim(1,50)
plt.ylim(0,5e9)
plt.axvline(24)
plt.xticks(list(plt.xticks()[0]) + [24],fontsize=18)
plt.yticks(fontsize=18)
plt.title("Espectro de Potência",fontsize=18)
plt.show()
