import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from scipy.signal import savgol_filter
from scipy.stats import linregress, spearmanr
import os

os.makedirs("gráficos", exist_ok=True)

# ── Parâmetros ────────────────────────────────────────────────────────────────
SG_WINDOW, SG_POLYORDER = 13, 3

# ── 1. Manchas solares ────────────────────────────────────────────────────────
colunas = ['Ano','Mes','Dia','Ano_Fracionado','Num_Manchas','Desvio_Padrao','Num_Observacoes','Marcador']
df_spots = pd.read_csv('dados/daily_Sunspots(97-17).csv', sep=';', names=colunas)
df_spots = df_spots[df_spots['Num_Manchas'] >= 0]

df_mensal = df_spots.groupby(['Ano','Mes'])['Num_Manchas'].mean().reset_index()
df_mensal['Data'] = pd.to_datetime(
    df_mensal[['Ano','Mes']].assign(day=1).rename(columns={'Ano':'year','Mes':'month'})
).dt.to_period('M')
df_mensal['Manchas_SG'] = savgol_filter(df_mensal['Num_Manchas'].values, SG_WINDOW, SG_POLYORDER)
spots_s = df_mensal.set_index('Data')

# ── 2. X-ray ──────────────────────────────────────────────────────────────────
df_xray     = pd.read_csv('dados/daily_xray(97-17).csv', index_col=0, parse_dates=True)
xm          = df_xray['xrsb'].resample('ME').mean()
xc          = df_xray['xrsb'].resample('ME').count()
xm[xc < 10] = np.nan                         # gap 1998
xm_interp   = xm.interpolate(method='time')  # interpola só para o SG
xm_sg       = pd.Series(savgol_filter(xm_interp.values, SG_WINDOW, SG_POLYORDER), index=xm.index)
xm.index    = xm.index.to_period('M')
xm_sg.index = xm_sg.index.to_period('M')

# ── 3. Alinhamento ────────────────────────────────────────────────────────────
common     = spots_s.index.intersection(xm.index)
manchas    = spots_s.loc[common, 'Num_Manchas'].values
manchas_sg = spots_s.loc[common, 'Manchas_SG'].values
xray       = xm.loc[common].values
xray_sg    = xm_sg.loc[common].values

# Mantém apenas pares positivos válidos (necessário para log-log)
mask_raw = (~np.isnan(manchas))    & (~np.isnan(xray))    & (manchas > 0)    & (xray > 0)
mask_sg  = (~np.isnan(manchas_sg)) & (~np.isnan(xray_sg)) & (manchas_sg > 0) & (xray_sg > 0)

m_r, x_r = manchas[mask_raw],   xray[mask_raw]
m_s, x_s = manchas_sg[mask_sg], xray_sg[mask_sg]

# ── 4. Ajuste log-log ─────────────────────────────────────────────────────────
def fit(mx, xx):
    """
    Regressão linear em log-log:
        log10(xray) = β·log10(manchas) + log10(a)
        →  xray = a · manchas^β
    Retorna: β, log10(a), R², p-valor, Spearman ρ
    """
    lm, lx = np.log10(mx), np.log10(xx)
    sl, ic, r, pv, _ = linregress(lm, lx)
    rho, _  = spearmanr(mx, xx)
    return sl, ic, r**2, pv, rho

β_r, a_r, r2_r, pv_r, ρ_r = fit(m_r, x_r)
β_s, a_s, r2_s, pv_s, ρ_s = fit(m_s, x_s)

print(f"[Bruto]  β={β_r:.3f}  log(a)={a_r:.3f}  R²={r2_r:.3f}  ρ={ρ_r:.3f}  p={pv_r:.1e}")
print(f"[SG]     β={β_s:.3f}  log(a)={a_s:.3f}  R²={r2_s:.3f}  ρ={ρ_s:.3f}  p={pv_s:.1e}")

# ── 5. Paleta ─────────────────────────────────────────────────────────────────
C_RAW = '#E07B39'   # laranja — bruto
C_SG  = '#08306B'   # azul escuro — suavizado
C_FIT = '#2CA02C'   # verde — linha de ajuste

# ── 6. Figura 1×2 ─────────────────────────────────────────────────────────────
# Apenas os scatters log-log com ajuste (sem gráfico de resíduos)
fig = plt.figure(figsize=(13, 5.5))
fig.suptitle(
    "Lei da Potência: Fluxo X-ray × Manchas Solares\n"
    r"Modelo: $X\text{-}ray = a \cdot N_{manchas}^{\,\beta}$",
    fontsize=12, fontweight='bold', y=1.04
)
gs = gridspec.GridSpec(1, 2, wspace=0.32)
ax_sc_r = fig.add_subplot(gs[0, 0])
ax_sc_s = fig.add_subplot(gs[0, 1])


# def plota_residuos(ax, mx, resid, cor, titulo):
#     ax.scatter(np.log10(mx), resid, s=14, alpha=0.55, color=cor, zorder=3)
#     ax.axhline(0, color='black', lw=1.0, linestyle='--', alpha=0.6)
#     sigma = resid.std()
#     ax.axhspan(-sigma, sigma, color=cor, alpha=0.08, label=f'±1σ = {sigma:.3f}')
#     ax.set_xlabel('log₁₀(Manchas)', fontsize=9)
#     ax.set_ylabel('Resíduo (log₁₀)', fontsize=9)
#     ax.set_title(titulo, fontsize=10, fontweight='bold')
#     ax.legend(fontsize=8, framealpha=0.88)
#     ax.grid(True, which='major', linestyle='--', alpha=0.3)
#     ax.tick_params(labelsize=8)

def plota_scatter(ax, mx, xx, beta, a_ic, r2, pv, rho, cor, titulo):
    ax.scatter(mx, xx, s=14, alpha=0.55, color=cor, zorder=3, label='Dados mensais')

    xl = np.linspace(mx.min(), mx.max(), 300)
    yl = 10 ** (a_ic + beta * np.log10(xl))
    label_fit = (f'$X = 10^{{{a_ic:.2f}}} \\cdot N^{{{beta:.3f}}}$\n'
                 f'$R^2={r2:.3f}$   $\\rho={rho:.3f}$\n'
                 f'$p={pv:.1e}$')
    ax.plot(xl, yl, color=C_FIT, lw=2.2, zorder=4, label=label_fit)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('Manchas solares (média mensal)', fontsize=9)
    ax.set_ylabel('Fluxo X-ray (W/m²)', fontsize=9)
    ax.set_title(titulo, fontsize=10, fontweight='bold')
    ax.legend(fontsize=8, framealpha=0.88, loc='upper left')
    ax.grid(True, which='both', linestyle='--', alpha=0.3)
    ax.tick_params(labelsize=8)


plota_scatter(ax_sc_r, m_r, x_r, β_r, a_r, r2_r, pv_r, ρ_r, C_RAW, "Scatter log-log — Dados Brutos")
plota_scatter(ax_sc_s, m_s, x_s, β_s, a_s, r2_s, pv_s, ρ_s, C_SG,  "Scatter log-log — Dados Suavizados (SG)")

fig.savefig('gráficos/lei_potencia_xray_manchas.png', dpi=150, bbox_inches='tight')
plt.close(fig)
print("Gráfico salvo em gráficos/lei_potencia_xray_manchas.png")