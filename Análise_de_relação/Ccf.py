import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from Common.config import SG_WINDOW, SG_POLYORDER, CAMINHO_MANCHAS, CAMINHO_XRAY, DIR_GRAFICOS, garantir_dir_graficos
from Common.dados import carregar_manchas_mensal, carregar_xray_mensal
from Common.processamento import suavizar, zscore_serie, preparar_xray_zscore_suave, alinhar
from Common.estatisticas import ccf_nanrob

MAX_LAG = 12  # +-12 meses

garantir_dir_graficos()

# ── 1. Manchas solares ────────────────────────────────────────────────────────
manchas = carregar_manchas_mensal(CAMINHO_MANCHAS)
manchas_z = zscore_serie(manchas)
manchas_z_suave = suavizar(manchas_z, SG_WINDOW, SG_POLYORDER)

# ── 2. X-ray ──────────────────────────────────────────────────────────────────
xray_mensal = carregar_xray_mensal(CAMINHO_XRAY)
xray_log_z, xray_suave = preparar_xray_zscore_suave(xray_mensal, SG_WINDOW, SG_POLYORDER)

# ── 3. Alinhamento ───────────────────────────────────────────────────────────
common, (s_raw, x_raw) = alinhar(manchas_z, xray_log_z)
_, (s_suave, x_suave) = alinhar(manchas_z_suave, xray_suave)
N = len(common)

# ── 4. CCF robusta a NaN ─────────────────────────────────────────────────────
lags_r, corr_raw, ns_r = ccf_nanrob(s_raw, x_raw, MAX_LAG)
lags_s, corr_suave, ns_s = ccf_nanrob(s_suave, x_suave, MAX_LAG)

# Intervalo de confiança 95%: +-1.96 / sqrt(N_efetivo)
ci_r = 1.96 / np.sqrt(ns_r.mean())
ci_s = 1.96 / np.sqrt(ns_s.mean())

best_lag_raw = lags_r[np.nanargmax(np.abs(corr_raw))]
best_lag_suave = lags_s[np.nanargmax(np.abs(corr_suave))]
best_r_raw = corr_raw[np.nanargmax(np.abs(corr_raw))]
best_r_suave = corr_suave[np.nanargmax(np.abs(corr_suave))]

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

    ax.axhspan(-ci, ci, color='crimson', alpha=0.08, zorder=1)
    ax.axhline(ci, color='crimson', linewidth=1.3, linestyle='--',
               label=f'IC 95% (±{ci:.3f})', zorder=2)
    ax.axhline(-ci, color='crimson', linewidth=1.3, linestyle='--', zorder=2)
    ax.axhline(0, color='black', linewidth=0.7, alpha=0.4, zorder=2)
    ax.axvline(0, color='black', linewidth=0.9, linestyle=':', alpha=0.5, zorder=2)

    h_off = 1.5 if best_lag <= 0 else -3.5
    v_off = 0.07 if best_r >= 0 else -0.10
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


plota_ccf(ax1, lags_r, corr_raw, best_lag_raw, best_r_raw, ci_r,
          "Séries Brutas (Z-score mensal)", '#6BAED6', '#08306B')

plota_ccf(ax2, lags_s, corr_suave, best_lag_suave, best_r_suave, ci_s,
          f"Séries Suavizadas (Savitzky-Golay, w={SG_WINDOW})", '#FC8D59', '#7F0000')

ax2.set_xlabel("Lag (meses)", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(f'{DIR_GRAFICOS}/ccf_manchas_xray.png', dpi=150)
plt.close(fig)
print(f"Gráfico salvo em {DIR_GRAFICOS}/ccf_manchas_xray.png")
