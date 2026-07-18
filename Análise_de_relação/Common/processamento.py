"""
Funções de pré-processamento reutilizadas pelos scripts de análise:
suavização Savitzky-Golay, z-score e alinhamento de séries mensais.
"""
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from scipy.stats import zscore


def suavizar(serie, window, polyorder):
    """Aplica Savitzky-Golay. A série não pode conter NaN (interpole antes)."""
    return pd.Series(savgol_filter(serie.values, window, polyorder), index=serie.index)


def zscore_serie(serie):
    """Z-score robusto a NaN (nan_policy='omit'), preservando o index."""
    return pd.Series(zscore(serie, nan_policy='omit'), index=serie.index)


def preparar_xray_zscore_suave(xray_mensal, window, polyorder):
    """
    Pipeline padrão do X-ray: log10 -> z-score -> corta bordas sem dado
    -> interpola (só para permitir o SG) -> Savitzky-Golay.

    Retorna (bruto_z, suave_z), duas pd.Series com index Period('M'),
    já recortadas ao intervalo com dado válido.
    """
    log = np.log10(xray_mensal)
    mask_ok = log.notna()
    log_z = (log - log[mask_ok].mean()) / log[mask_ok].std()

    interp = log_z.interpolate(method='time')
    suave = suavizar(interp, window, polyorder)

    t0, t1 = log_z.first_valid_index(), log_z.last_valid_index()
    log_z = log_z.loc[t0:t1]
    suave = suave.loc[t0:t1]

    log_z.index = log_z.index.to_period('M')
    suave.index = suave.index.to_period('M')
    return log_z, suave


def alinhar(*series):
    """
    Recorta uma lista de pd.Series ao índice comum (interseção).
    Retorna (index_comum, [series_recortadas...]) na mesma ordem recebida.
    """
    common = series[0].index
    for s in series[1:]:
        common = common.intersection(s.index)
    return common, [s.loc[common] for s in series]
