import duckdb
import pandas as pd

print("=== PREPROCESAMIENTO TURBO ===")
con = duckdb.connect()

# --------------------------------
# 1. Cargar transacciones RAW y enriquecer con año/mes/día
# --------------------------------
print("Cargando transacciones RAW (Parquet) con DuckDB...")

df_tx_raw = con.execute("""
    SELECT
        *,
        CAST(fechaf AS TIMESTAMP) AS fechaf_ts
    FROM read_parquet('data/transacciones_part1.parquet')
""").fetchdf()

print("Añadiendo columnas año/mes/día...")

# Mejor hacerlo en pandas porque ya tenemos fechaf_ts convertido
df_tx_raw["año"] = df_tx_raw["fechaf_ts"].dt.year
df_tx_raw["mes"] = df_tx_raw["fechaf_ts"].dt.month
df_tx_raw["dia"] = df_tx_raw["fechaf_ts"].dt.day

print("Guardando tx_raw_opt.parquet...")
df_tx_raw.to_parquet("data/tx_raw_opt.parquet", index=False)

# --------------------------------
# 2. Agregación por usuario/día (df_tx)
# --------------------------------
print("Agregando transacciones por usuario/día...")

con.register("df_tx_raw", df_tx_raw)

df_tx = con.execute("""
    SELECT
        año,
        mes,
        dia,
        id_user,
        SUM(amount) AS amount,
        COUNT(*) AS n_tx
    FROM df_tx_raw
    GROUP BY 1,2,3,4
""").fetchdf()

df_tx.to_parquet("data/tx_agregado.parquet", index=False)
print("-> tx_agregado.parquet listo")

# --------------------------------
# 3. Ingresos por semana (para gráfica global / ventana)
# --------------------------------
print("Agregando ingresos por semana...")

df_semana = con.execute("""
    SELECT 
        DATE_TRUNC('week', fechaf_ts) AS semana,
        SUM(amount) AS amount
    FROM df_tx_raw
    GROUP BY 1
    ORDER BY 1
""").fetchdf()

df_semana.to_parquet("data/tx_semana.parquet", index=False)
print("-> tx_semana.parquet listo")

# --------------------------------
# 4. Ingresos por mes (para vista Año / Mes)
# --------------------------------
print("Agregando ingresos por mes...")

df_mes = con.execute("""
    SELECT 
        año,
        mes,
        SUM(amount) AS amount
    FROM df_tx_raw
    GROUP BY 1,2
    ORDER BY 1,2
""").fetchdf()

df_mes.to_parquet("data/tx_mes.parquet", index=False)
print("-> tx_mes.parquet listo")

# --------------------------------
# 5. Casos + Master → merge + parquet
# --------------------------------
print("Cargando CasosContactCenter_limpio.csv...")
df_casos = pd.read_csv("data/CasosContactCenter_limpio.csv", engine="pyarrow")

df_casos["fecha"] = pd.to_datetime(df_casos["fecha"], errors="coerce")
df_casos["año"] = df_casos["fecha"].dt.year
df_casos["mes"] = df_casos["fecha"].dt.month

print("Cargando df_master_corregido.csv...")
df_master = pd.read_csv("data/df_master_corregido.csv", engine="pyarrow")

print("Haciendo merge de casos + master...")
df_casos_full = df_casos.merge(
    df_master[[
        "id_user",
        "churn",
        "occupation_category",
        "qualification",
        "tendencia_uso",
        "state"
    ]],
    on="id_user",
    how="left"
)

print("Guardando casos_full_opt.parquet y master_opt.parquet...")
df_casos_full.to_parquet("data/casos_full_opt.parquet", index=False)
df_master.to_parquet("data/master_opt.parquet", index=False)

print("=== PREPROCESAMIENTO COMPLETO (TURBO) ===")
