"""
Rotinas estatísticas específicas de cada análise:
- ccf_nanrob: correlação cruzada robusta a NaN (usada em ccf.py)
- ajustar_lei_potencia: regressão log-log (usada em lei_potencia.py)
"""
import numpy as np
from scipy.stats import linregress, spearmanr


def ccf_nanrob(x, y, max_lag):
    """
    Correlação cruzada normalizada para lags -max_lag ... +max_lag.
    Descarta pares NaN individualmente por lag.

    Convenção:
      lag > 0 -> x adianta y  (x lidera)
      lag < 0 -> y adianta x  (y lidera)

    Retorna (lags, corrs, ns) como arrays numpy.
    """
    N = len(x)
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
        n = mask.sum()
        r = np.corrcoef(xi[mask], yi[mask])[0, 1] if n > 10 else np.nan
        lags.append(lag); corrs.append(r); ns.append(n)

    return np.array(lags), np.array(corrs), np.array(ns)


def ajustar_lei_potencia(mx, xx):
    """
    Regressão linear em log-log:
        log10(xray) = beta * log10(manchas) + log10(a)
        ->  xray = a * manchas^beta

    Retorna: beta, log10(a), R², p-valor, Spearman rho, resíduos (em log10).
    """
    lm, lx = np.log10(mx), np.log10(xx)
    sl, ic, r, pv, _ = linregress(lm, lx)
    rho, _ = spearmanr(mx, xx)
    resid = lx - (ic + sl * lm)
    return sl, ic, r ** 2, pv, rho, resid
