"""
Carregamento dos dados brutos de manchas solares e fluxo X-ray,
já agregados em médias mensais.
"""
import numpy as np
import pandas as pd

COLUNAS_MANCHAS = [
    'Ano', 'Mes', 'Dia', 'Ano_Fracionado',
    'Num_Manchas', 'Desvio_Padrao', 'Num_Observacoes', 'Marcador'
]


def carregar_manchas_mensal(caminho='dados/daily_Sunspots(97-17).csv'):
    """
    Lê o CSV diário de manchas solares e retorna a média mensal
    (pd.Series, index = Period('M'), name='Num_Manchas').
    """
    df = pd.read_csv(caminho, sep=';', names=COLUNAS_MANCHAS)
    df = df[df['Num_Manchas'] >= 0]

    df_mensal = df.groupby(['Ano', 'Mes'])['Num_Manchas'].mean().reset_index()
    df_mensal['Data'] = pd.to_datetime(
        df_mensal[['Ano', 'Mes']].assign(day=1).rename(columns={'Ano': 'year', 'Mes': 'month'})
    ).dt.to_period('M')

    return df_mensal.set_index('Data')['Num_Manchas']


def carregar_xray_mensal(caminho='dados/daily_xray(97-17).csv', min_obs=10):
    """
    Lê o CSV diário de fluxo X-ray e retorna a média mensal (pd.Series,
    index DatetimeIndex mensal). Meses com menos de `min_obs` observações
    (ex.: o gap real de 1998) são marcados como NaN.
    """
    df = pd.read_csv(caminho, index_col=0, parse_dates=True)
    media = df['xrsb'].resample('ME').mean()
    contagem = df['xrsb'].resample('ME').count()
    media[contagem < min_obs] = np.nan
    return media
