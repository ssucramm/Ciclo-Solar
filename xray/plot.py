import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
from scipy.stats import zscore

# ── 1. Manchas solares ──────────────────────────────────────────────────────
colunas = ['Ano', 'Mes', 'Dia', 'Ano_Fracionado', 'Num_Manchas', 'Desvio_Padrao', 'Num_Observacoes', 'Marcador']
df_spots = pd.read_csv("dados/daily_Sunspots(97-17).csv", sep=';', names=colunas)
df_spots = df_spots[df_spots['Num_Manchas'] >= 0]

df_mensal = df_spots.groupby(['Ano', 'Mes'])['Num_Manchas'].mean().reset_index()
df_mensal['Data'] = pd.to_datetime(
    df_mensal[['Ano', 'Mes']].assign(day=1).rename(columns={'Ano': 'year', 'Mes': 'month'})
)
df_mensal['Z'] = zscore(df_mensal['Num_Manchas'], nan_policy='omit')
df_mensal['Z_Suave'] = savgol_filter(df_mensal['Z'], window_length=13, polyorder=3)

# ── 2. Fluxo X-ray GOES ─────────────────────────────────────────────────────
df_xray = pd.read_csv("dados/daily_xray(97-17).csv", index_col=0, parse_dates=True)
xray_monthly = df_xray["xrsb"].resample("ME").agg(mean="mean", count="count")
xray_monthly.loc[xray_monthly["count"] < 10, "mean"] = np.nan

xray_log = np.log10(xray_monthly["mean"])
mascara = xray_log.notna()
xray_log_z = (xray_log - xray_log[mascara].mean()) / xray_log[mascara].std()

xray_interp = xray_log_z.interpolate(method='time')
xray_z_suave = pd.Series(
    savgol_filter(xray_interp, window_length=23, polyorder=3),
    index=xray_log_z.index
)
xray_z_suave[xray_log_z.isna()] = np.nan

# ── 3. Gráfico 1 — Dados brutos (sem suavização) ────────────────────────────
fig1, ax1 = plt.subplots(figsize=(14, 5))

ax1.plot(df_mensal['Data'], df_mensal['Z'],
         color='darkorange', linewidth=0.8, alpha=0.8, label='Manchas — média mensal')
ax1.plot(xray_log_z.index, xray_log_z,
         color='steelblue', linewidth=0.8, alpha=0.8, label='X-ray — média mensal')
ax1.axhline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.4)
ax1.set_ylabel("Z-score")
ax1.set_xlabel("Data")
ax1.set_title("Ciclo Solar 23 e 24: Manchas Solares e Fluxo X-ray")
ax1.legend(loc="upper left", fontsize=8)
ax1.grid(True, linestyle='--', alpha=0.3)
fig1.tight_layout()
plt.savefig("gráficos/ciclo_solar_bruto.png", dpi=150)

# ── 4. Gráfico 2 — Dados suavizados ─────────────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(14, 5))

ax2.plot(df_mensal['Data'], df_mensal['Z_Suave'],
         color='darkred', linewidth=2, label='Manchas - média mensal')
ax2.plot(xray_z_suave.index, xray_z_suave,
         color='steelblue', linewidth=2, label='X-ray - média mensal')
ax2.axhline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.4)
ax2.set_ylabel("Z-score")
ax2.set_xlabel("Data")
ax2.set_title("Ciclo Solar 23 e 24: Manchas Solares e Fluxo X-ray")
ax2.legend(loc="upper left", fontsize=8)
ax2.grid(True, linestyle='--', alpha=0.3)
fig2.tight_layout()
plt.savefig("gráficos/ciclo_solar_suavizado.png", dpi=150)

plt.show()