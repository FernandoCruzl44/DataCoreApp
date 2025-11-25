import pandas as pd

df = pd.read_csv("data/transacciones_cleaned.csv", low_memory=True)
df.to_parquet("data/transacciones_cleaned.parquet")