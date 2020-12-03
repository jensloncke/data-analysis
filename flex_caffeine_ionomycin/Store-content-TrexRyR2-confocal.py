from pathlib import Path
import os
import pandas as pd
import numpy as np
# from plotly import graph_objs as go
# from plotly import offline as po

path_analysis = Path("C:\\Users\\u0132307\\Box Sync\\PhD\\Data\\Ca2+_G-erCEPIA1_confocal\\20201113-TrexERCEPIA")

path_response = Path("C:\\Users\\u0132307\\Box Sync\\PhD\\Data\\CCa2+_G-erCEPIA1_confocal\\20201113-TrexERCEPIA\\response")
os.makedirs(path_response, exist_ok=True)

filename = "Results-WT1.csv"
data = pd.read_csv(path_analysis / filename, sep=",")
print(data)
