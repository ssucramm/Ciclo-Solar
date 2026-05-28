import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from scipy.signal import savgol_filter
from scipy.stats import zscore
import os

os.makedirs("gráficos", exist_ok=True)

# ── 1. Manchas solares ────────────────────────────────────────────────────────
colunas = ['Ano','Mes','Dia','Ano_Fracionado','Num_Manchas','Desvio_Padrao','Num_Observacoes','Marcador']
df_spots = pd.read_csv('dados/daily_Sunspots(97-17).csv', sep=';', names=colunas)
df_spots = df_spots[df_spots['Num_Manchas'] >= 0]

df_mensal = df_spots.groupby(['Ano','Mes'])['Num_Manchas'].mean().reset_index()
df_mensal['Data'] = pd.to_datetime(
    df_mensal[['Ano','Mes']].assign(day=1).rename(columns={'Ano':'year','Mes':'month'})
)

df_mensal['Z'] = zscore(df_mensal['Num_Manchas'], nan_policy='omit')
df_mensal['Z_Suave'] = savgol_filter(df_mensal['Z'], 13, 3)

# ── 2. X-ray ──────────────────────────────────────────────────────────────────
df_xray = pd.read_csv('dados/daily_xray(97-17).csv', index_col=0, parse_dates=True)

xray_m_mean  = df_xray['xrsb'].resample('ME').mean()
xray_m_count = df_xray['xrsb'].resample('ME').count()
xray_m_mean[xray_m_count < 10] = np.nan    

# Log-transform e Z-score
xray_log  = np.log10(xray_m_mean)
mask_ok   = xray_log.notna()
xray_log_z = (xray_log - xray_log[mask_ok].mean()) / xray_log[mask_ok].std()


xray_interp = xray_log_z.interpolate(method='time')

sg_vals    = savgol_filter(xray_interp.values, 13, 3)
xray_suave = pd.Series(sg_vals, index=xray_log_z.index)

# Recorta para período com dados válidos em ambas as extremidades
t0 = xray_log_z.first_valid_index()
t1 = xray_log_z.last_valid_index()
xray_log_z = xray_log_z.loc[t0:t1]
xray_suave = xray_suave.loc[t0:t1]
dates_spots = df_mensal['Data']

def formata_eixo(ax):
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_minor_locator(mdates.YearLocator(1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.tick_params(axis='x', labelsize=9)
    ax.tick_params(axis='y', labelsize=9)
    ax.set_ylabel("Z-score", fontsize=10)
    ax.set_xlabel("Ano", fontsize=10)
    ax.grid(True, which='major', linestyle='--', alpha=0.35)
    ax.grid(True, which='minor', linestyle=':', alpha=0.15)
    ax.axhline(0, color='#555555', linewidth=0.8, linestyle='--', alpha=0.5)
    # Sombreia o gap de 1998
    ax.axvspan(pd.Timestamp('1998-01-01'), pd.Timestamp('1999-01-01'),
               color='gray', alpha=0.10, label='Gap sensor (1998)')


# ── Gráfico 1 — Bruto ─────────────────────────────────────────────────────────
fig1, ax1 = plt.subplots(figsize=(14, 5))

ax1.plot(dates_spots, df_mensal['Z'],
         color='#E07B39', linewidth=0.9, alpha=0.85, label='Manchas solares')
ax1.plot(xray_log_z.index, xray_log_z,
         color='#4A90C4', linewidth=0.9, alpha=0.85, label='Fluxo X-ray (log₁₀)')
formata_eixo(ax1)
ax1.set_title("Ciclos Solares 23 e 24 — Médias Mensais", fontsize=12, fontweight='bold')
ax1.legend(loc='upper left', fontsize=9, framealpha=0.85)
fig1.tight_layout()
fig1.savefig('gráficos/ciclo_solar_bruto.png', dpi=150)
plt.close(fig1)

# ── Gráfico 2 — Suavizado SG ──────────────────────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(14, 5))

ax2.plot(dates_spots, df_mensal['Z_Suave'],
         color='#B22222', linewidth=2.2, label=f'Manchas solares (SG, w={13})')
ax2.plot(xray_suave.index, xray_suave,
         color='#1A5C8A', linewidth=2.2, label=f'Fluxo X-ray (SG, w={13})')
formata_eixo(ax2)
ax2.set_title("Ciclos Solares 23 e 24 — Savitzky-Golay", fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', fontsize=9, framealpha=0.85)
fig2.tight_layout()
fig2.savefig('gráficos/ciclo_solar_suavizado.png', dpi=150)
plt.close(fig2)

# ── Gráfico 3 — Comparação ─────────────────────────────────
fig3, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(14, 9), sharex=True)

ax_top.plot(dates_spots, df_mensal['Z'],
            color='#E07B39', linewidth=0.8, alpha=0.5, label='Bruto')
ax_top.plot(dates_spots, df_mensal['Z_Suave'],
            color='#B22222', linewidth=2.2, label=f'SG w={13}')
formata_eixo(ax_top)
ax_top.set_xlabel("")
ax_top.set_title("Ciclos Solares 23 e 24 — Comparação", fontsize=12, fontweight='bold')
ax_top.set_ylabel("Z-score — Manchas", fontsize=10)
ax_top.legend(loc='upper left', fontsize=9, framealpha=0.85)

ax_bot.plot(xray_log_z.index, xray_log_z,
            color='#4A90C4', linewidth=0.8, alpha=0.5, label='Bruto')
ax_bot.plot(xray_suave.index, xray_suave,
            color='#1A5C8A', linewidth=2.2, label=f'SG w={13}')
formata_eixo(ax_bot)
ax_bot.set_ylabel("Z-score — X-ray", fontsize=10)
ax_bot.legend(loc='upper left', fontsize=9, framealpha=0.85)

fig3.tight_layout()
fig3.savefig('gráficos/ciclo_solar_comparacao.png', dpi=150)
plt.close(fig3)