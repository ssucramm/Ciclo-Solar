import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from scipy.signal import savgol_filter
from scipy.stats import zscore
import os

os.makedirs("gráficos", exist_ok=True)

# ── Parâmetros ───────────────────────────────────────────────────────────────
SG_WINDOW    = 13
SG_POLYORDER = 3
MAX_LAG      = 12   # ±12 meses

# ── 1. Manchas solares ────────────────────────────────────────────────────────
colunas = ['Ano','Mes','Dia','Ano_Fracionado','Num_Manchas','Desvio_Padrao','Num_Observacoes','Marcador']
df_spots = pd.read_csv('dados/daily_Sunspots(97-17).csv', sep=';', names=colunas)
df_spots = df_spots[df_spots['Num_Manchas'] >= 0]

df_mensal = df_spots.groupby(['Ano','Mes'])['Num_Manchas'].mean().reset_index()
df_mensal['Data'] = pd.to_datetime(
    df_mensal[['Ano','Mes']].assign(day=1).rename(columns={'Ano':'year','Mes':'month'})
).dt.to_period('M')   # Period mensal para alinhar com X-ray

df_mensal['Z']       = zscore(df_mensal['Num_Manchas'], nan_policy='omit')
df_mensal['Z_Suave'] = savgol_filter(df_mensal['Z'], SG_WINDOW, SG_POLYORDER)
spots_s = df_mensal.set_index('Data')

# ── 2. X-ray ──────────────────────────────────────────────────────────────────
df_xray      = pd.read_csv('dados/daily_xray(97-17).csv', index_col=0, parse_dates=True)
xray_m_mean  = df_xray['xrsb'].resample('ME').mean()
xray_m_count = df_xray['xrsb'].resample('ME').count()
xray_m_mean[xray_m_count < 10] = np.nan          # gap real: 1998 inteiro

xray_log     = np.log10(xray_m_mean)
mask_ok      = xray_log.notna()
xray_log_z   = (xray_log - xray_log[mask_ok].mean()) / xray_log[mask_ok].std()

xray_interp  = xray_log_z.interpolate(method='time')
xray_suave   = pd.Series(
    savgol_filter(xray_interp.values, SG_WINDOW, SG_POLYORDER),
    index=xray_log_z.index
)
t0 = xray_log_z.first_valid_index()
t1 = xray_log_z.last_valid_index()
xray_log_z   = xray_log_z.loc[t0:t1]
xray_suave   = xray_suave.loc[t0:t1]

# Converte para Period mensal para alinhar com manchas
xray_log_z.index = xray_log_z.index.to_period('M')
xray_suave.index = xray_suave.index.to_period('M')

# ── 3. Alinhamento ───────────────────────────────────────────────────────────
common  = spots_s.index.intersection(xray_log_z.index)
s_raw   = spots_s.loc[common, 'Z']
x_raw   = xray_log_z.loc[common]
s_suave = spots_s.loc[common, 'Z_Suave']
x_suave = xray_suave.loc[common]
N       = len(common)

# ── 4. CCF robusta a NaN ─────────────────────────────────────────────────────
def ccf_nanrob(x, y, max_lag):
    """
    Correlação cruzada normalizada para lags -max_lag … +max_lag.
    Descarta pares NaN individualmente por lag.

    Convenção:
      lag > 0 → x adianta y  (x lidera)
      lag < 0 → y adianta x  (y lidera)
    """
    lags, corrs, ns = [], [], []
    for lag in range(-max_lag, max_lag + 1):
        if lag >= 0:
            xi = x.values[:N - lag] if lag < N else np.array([])
            yi = y.values[lag:]
        else:
            xi = x.values[-lag:]
            yi = y.values[:N + lag] if -lag < N else np.array([])

        if len(xi) == 0 or len(yi) == 0:
            lags.append(lag); corrs.append(np.nan); ns.append(0)
            continue

        mask = ~(np.isnan(xi) | np.isnan(yi))
        n    = mask.sum()
        r    = np.corrcoef(xi[mask], yi[mask])[0, 1] if n > 10 else np.nan
        lags.append(lag); corrs.append(r); ns.append(n)

    return np.array(lags), np.array(corrs), np.array(ns)

lags_r, corr_raw,   ns_r = ccf_nanrob(s_raw,   x_raw,   MAX_LAG)
lags_s, corr_suave, ns_s = ccf_nanrob(s_suave, x_suave, MAX_LAG)

# Intervalo de confiança 95%: ±1.96 / sqrt(N_efetivo)
ci_r = 1.96 / np.sqrt(ns_r.mean())
ci_s = 1.96 / np.sqrt(ns_s.mean())

best_lag_raw   = lags_r[np.nanargmax(np.abs(corr_raw))]
best_lag_suave = lags_s[np.nanargmax(np.abs(corr_suave))]
best_r_raw     = corr_raw[np.nanargmax(np.abs(corr_raw))]
best_r_suave   = corr_suave[np.nanargmax(np.abs(corr_suave))]

print(f"Lag ótimo (bruto) : {best_lag_raw:+d} meses  r = {best_r_raw:.3f}")
print(f"Lag ótimo (suave) : {best_lag_suave:+d} meses  r = {best_r_suave:.3f}")

# ── 5. Gráfico ────────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig.suptitle(
    "Correlação Cruzada — Manchas Solares × Fluxo X-ray\n"
    "lag > 0: manchas lideram o X-ray  |  lag < 0: X-ray lidera as manchas",
    fontsize=11, fontweight='bold', y=0.99
)

def plota_ccf(ax, lags, corrs, best_lag, best_r, ci, titulo, cor_bar, cor_dest):
    cores = [cor_dest if l == best_lag else cor_bar for l in lags]
    ax.bar(lags, corrs, color=cores, width=0.72, alpha=0.88, zorder=3)

    # Faixa IC 95%
    ax.axhspan(-ci, ci, color='crimson', alpha=0.08, zorder=1)
    ax.axhline( ci, color='crimson', linewidth=1.3, linestyle='--',
                label=f'IC 95% (±{ci:.3f})', zorder=2)
    ax.axhline(-ci, color='crimson', linewidth=1.3, linestyle='--', zorder=2)
    ax.axhline(0,   color='black',   linewidth=0.7, alpha=0.4,  zorder=2)
    ax.axvline(0,   color='black',   linewidth=0.9, linestyle=':', alpha=0.5, zorder=2)

    # Anotação do lag ótimo
    h_off = 1.5  if best_lag <= 0 else -3.5
    v_off = 0.07 if best_r   >= 0 else -0.10
    ax.annotate(
        f'lag={best_lag:+d} meses\nr = {best_r:.3f}',
        xy=(best_lag, best_r),
        xytext=(best_lag + h_off, best_r + v_off),
        fontsize=8.5, color=cor_dest, fontweight='bold',
        arrowprops=dict(arrowstyle='->', color=cor_dest, lw=1.3)
    )

    ax.set_title(titulo, fontsize=10, fontweight='bold', pad=5)
    ax.set_ylabel("Correlação (r)", fontsize=9)
    ax.set_ylim(-1.05, 1.05)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.2))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax.grid(True, which='major', linestyle='--', alpha=0.35)
    ax.grid(True, which='minor', linestyle=':', alpha=0.15)
    ax.legend(fontsize=8.5, loc='lower right', framealpha=0.85)

plota_ccf(ax1, lags_r, corr_raw,
          best_lag_raw,   best_r_raw,   ci_r,
          "Séries Brutas (Z-score mensal)",
          '#6BAED6', '#08306B')

plota_ccf(ax2, lags_s, corr_suave,
          best_lag_suave, best_r_suave, ci_s,
          f"Séries Suavizadas (Savitzky-Golay, w={SG_WINDOW})",
          '#FC8D59', '#7F0000')

ax2.set_xlabel("Lag (meses)", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig('gráficos/ccf_manchas_xray.png', dpi=150)
plt.close(fig)
print("Gráfico salvo em gráficos/ccf_manchas_xray.png")