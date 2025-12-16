import pandas as pd
from datetime import date

# testni podaci
data = {
    "Tim 1": ["Partizan", "Crvena Zvezda"],
    "Tim 2": ["Vojvodina", "Radnicki"],
    "Golovi 1": [2, 1],
    "Golovi 2": [1, 3]
}

df = pd.DataFrame(data)

# sačuvaj Excel sa današnjim datumom
df.to_excel(f"rezultati_{date.today()}.xlsx", index=False)

print("Excel fajl je uspešno napravljen.")
