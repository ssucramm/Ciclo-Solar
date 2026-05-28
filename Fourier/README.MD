Este projeto realiza uma análise temporal do número de manchas solares utilizando a Transformada Rápida de Fourier (FFT) para identificar ciclos periódicos na atividade solar.

O programa:

Carrega os dados do arquivo sunspots.txt;
Separa as colunas de tempo e quantidade de manchas solares;
Gera um gráfico da evolução do número de manchas ao longo dos anos;
Calcula o espectro de potência usando FFT;
Identifica o pico dominante do espectro para estimar o período do ciclo solar.

A análise espectral permite detectar padrões periódicos nos dados. O pico principal encontrado corresponde aproximadamente ao conhecido ciclo solar de cerca de 11 anos.

A frequência foi calculada considerando dados mensais (d=1/12), permitindo converter corretamente o pico da FFT em período temporal.