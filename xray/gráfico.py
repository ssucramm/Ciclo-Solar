import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import zscore

# ── 1. Manchas solares ──────────────────────────────────────────────────────

# O arquivo "Daily_Sunspots(97-17).csv" deve conter colunas: Ano;Mes;Dia;Ano_Fracionado;Num_Manchas;Desvio_Padrao;Num_Observacoes;Marcador
colunas = ['Ano', 'Mes', 'Dia', 'Ano_Fracionado', 'Num_Manchas', 'Desvio_Padrao', 'Num_Observacoes', 'Marcador']
df_spots = pd.read_csv("dados/daily_Sunspots(97-17).csv", sep=';', names=colunas)
df_spots = df_spots[df_spots['Num_Manchas'] >= 0]
df_mensal = df_spots.groupby(['Ano', 'Mes'])['Num_Manchas'].mean().reset_index()
df_mensal['Data'] = pd.to_datetime(df_mensal[['Ano', 'Mes']].assign(day=1).rename(columns={'Ano': 'year', 'Mes': 'month'}))
df_mensal['Z'] = zscore(df_mensal['Num_Manchas'], nan_policy='omit')

# ── 2. Fluxo X-ray GOES ─────────────────────────────────────────────────────
df_xray = pd.read_csv("dados/daily_xray(97-17).csv", index_col=0, parse_dates=True)
xray_monthly = df_xray["xrsb"].resample("ME").agg(mean="mean", count="count")
xray_monthly.loc[xray_monthly["count"] < 10, "mean"] = np.nan
xray_log = np.log10(xray_monthly["mean"])
mascara = xray_log.notna()
xray_log_z = (xray_log - xray_log[mascara].mean()) / xray_log[mascara].std()


def media_movel(y, janela=49):
    return pd.Series(y).rolling(window=janela, center=True, min_periods=1).mean().values

spots_media = media_movel(df_mensal['Z'].values)

xray_interp = xray_log_z.interpolate(method='time')
xray_media = media_movel(xray_interp.values)
xray_media = pd.Series(xray_media, index=xray_log_z.index)
xray_media[xray_log_z.isna()] = np.nan

# ── 3. Gráfico ───────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(df_mensal['Data'], df_mensal['Z'],
        color='darkorange', linewidth=0.8, alpha=0.4, label='Manchas — média mensal')
ax.plot(df_mensal['Data'], spots_media,
        color='darkred', linewidth=2.5, label='Manchas — média móvel (49 meses)')

ax.plot(xray_log_z.index, xray_log_z,
        color='steelblue', linewidth=0.8, alpha=0.4, label='X-ray — média mensal')
ax.plot(xray_media.index, xray_media,
        color='darkblue', linewidth=2.5, label='X-ray — média móvel (49 meses)')

ax.axhline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.4)
ax.set_ylabel("Z-score")
ax.set_xlabel("Data")
ax.set_title("Ciclo Solar 23 e 24: Manchas Solares e Fluxo X-ray")
ax.legend(loc="upper left", fontsize=8)
ax.grid(True, linestyle='--', alpha=0.3)

fig.tight_layout()
plt.savefig("gráficos/ciclo_solar.png", dpi=150)
plt.show()