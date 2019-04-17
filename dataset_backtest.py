import calculus as c
import pandas as pd

data = pd.read_csv('bmf/DOL$NM5.csv')

# DMI (20, 26)
data = c.dmi(data, 20, 26)

# DMI (3, 9)
data = c.dmi(data, 3, 9)

# Stoch (9, 5, WMA)
data = c.stoch(data, 9, 5, 2)

# Stoch (9, 2, SMA)
data = c.stoch(data, 9, 2, 0)

# HiLo (3, SMA)
data = c.hilo(data, 'SMA', 3)

# Volume (2, SMA) (14, SMA)
data = c.averages(data, 'SMA', [2, 14], 'Volume')

# Didi 2/9/20 WMA
data = c.didi(data, 2, 9, 20, 'WMA')

data = data.dropna()

data.to_csv('final_datasets/DOL_BACKTEST.csv')
