import pandas as pd

df = pd.read_csv("grosshandelpreise_2022_2025_15min.csv", sep=";")
df = df.dropna(how="all")

columns_to_keep = ["Datum von","Datum bis","Deutschland/Luxemburg [€/MWh] Originalauflösungen"]
df = df[columns_to_keep]

df.to_csv('filtered_output.csv', index=False)

print("Filtered file saved as 'filtered_output.csv'")