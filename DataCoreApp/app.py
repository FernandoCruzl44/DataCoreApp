import pandas as pd 

def load_data():

    #df_master = pd.read_csv('data/dataset_master.csv')
    df_casos = pd.read_csv('data/CasosContactCenter_limpio.csv')
    df_tx = pd.read_csv('data/transacciones_cleaned.csv')

    df_casos['fecha'] = pd.to_datetime(df_casos['fecha'], errors='coerce')   
    df_casos['año'] = df_casos['fecha'].dt.year
    df_casos['mes'] = df_casos['fecha'].dt.month

    df_tx['fechaf'] = pd.to_datetime(df_tx['fechaf'], errors='coerce')
    df_tx['año'] = df_tx['fechaf'].dt.year
    df_tx['mes'] = df_tx['fechaf'].dt.month

    return df_casos, df_tx

