from sunpy.net import Fido, attrs as a
from sunpy import timeseries as ts
import pandas as pd
import os
import concurrent.futures
import tempfile
import shutil

COLUNAS_POSSIVEIS = ["xrsb", "xrsb_flux", "XRSB", "b_flux", "xrs_b"]
ARQUIVO_FINAL = "goes_1997_2017.csv"


def processar_ano(ano):
    print(f"  [{ano}] baixando...")
    tmp_dir = tempfile.mkdtemp(prefix=f"goes_{ano}_")

    try:
        result = Fido.search(
            a.Time(f"{ano}-01-01", f"{ano}-12-31"),
            a.Instrument("XRS")
        )
        files = Fido.fetch(result, path=tmp_dir, max_conn=8)
        arquivos_validos = [f for f in files if f and os.path.exists(f)]

        if not arquivos_validos:
            print(f"  [{ano}] nenhum arquivo válido")
            return None

        goes = ts.TimeSeries(arquivos_validos, concatenate=True)
        df = goes.to_dataframe()

        col = next((c for c in COLUNAS_POSSIVEIS if c in df.columns), None)
        if col is None:
            print(f"  [{ano}] colunas disponíveis: {list(df.columns)} — pulando")
            return None

        df = df[[col]].rename(columns={col: "xrsb"})

        # Remove valores fisicamente impossíveis e agrega para diário
        df["xrsb"] = df["xrsb"].where(df["xrsb"] > 0)
        df = df.resample("1D").mean()

        print(f"  [{ano}] OK ({len(arquivos_validos)} arquivos, {len(df)} dias)")
        return df

    except Exception as e:
        print(f"  [{ano}] ERRO: {e}")
        return None

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


anos = list(range(1997, 2017 + 1))

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    resultados = list(executor.map(processar_ano, anos))

dfs_validos = [df for df in resultados if df is not None]

if dfs_validos:
    df_final = pd.concat(dfs_validos).sort_index()
    df_final.to_csv(ARQUIVO_FINAL, index=True)
    print(f"\nArquivo salvo: '{ARQUIVO_FINAL}' ({len(df_final)} dias no total)")
else:
    print("\nNenhum dado foi baixado.")