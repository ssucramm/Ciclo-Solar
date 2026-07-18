"""Parâmetros e caminhos compartilhados entre os scripts do projeto."""
import os

# Suavização Savitzky-Golay
SG_WINDOW = 13
SG_POLYORDER = 3

# Caminhos (seguem a convenção dados/ e gráficos/ do projeto)
CAMINHO_MANCHAS = 'dados/daily_Sunspots(97-17).csv'
CAMINHO_XRAY = 'dados/daily_xray(97-17).csv'
DIR_GRAFICOS = 'gráficos'


def garantir_dir_graficos():
    os.makedirs(DIR_GRAFICOS, exist_ok=True)
