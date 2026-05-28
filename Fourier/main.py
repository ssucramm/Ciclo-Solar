import numpy as np
import matplotlib.pyplot as plt

dados = np.loadtxt("sunspots.txt")

tempo = dados[:, 2]
n_manchas = dados[:, 3]



fig = plt.figure(figsize=(20, 8))
plt.plot(tempo, n_manchas)
plt.xlabel("Ano", fontsize=18)
plt.ylabel("Número de Manchas", fontsize=18)
plt.yticks(fontsize=18)
plt.xticks(fontsize=18)
plt.savefig("gráficos/número_de_manchas.png")

coef = np.fft.rfft(n_manchas)
potencia = np.abs(coef) ** 2

fig = plt.figure(figsize=(20, 8))
plt.plot(potencia, "r")
plt.xlim(1, 50)
plt.ylim(0, 5e9)
plt.axvline(24)
plt.xticks(list(plt.xticks()[0]) + [24], fontsize=18)
plt.yticks(fontsize=18)
plt.title("Espectro de Potência", fontsize=18)
plt.savefig("gráficos/potência.png")

N = len(n_manchas)
freqs = np.fft.rfftfreq(N, d=1/12) 
k_pico = np.argmax(potencia[1:]) + 1
periodo_pico = 1 / freqs[k_pico]
print(f"Pico em k={k_pico}, período = {periodo_pico:.1f} anos")
