import pandas as pd

df = pd.read_csv("../../data/grosshandelpreise_2022_2025_15min.csv", sep=";")
df = df.dropna(how="all")

columns_to_keep = ["Datum von","Datum bis","Deutschland/Luxemburg [€/MWh] Originalauflösungen"]
df = df[columns_to_keep]

df.to_csv('../../data/fact_liferantenpreis.csv', index=False)

print("Filtered file saved as 'fact_liferantenpreis.csv'")