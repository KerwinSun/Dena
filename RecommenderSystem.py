import pandas as pd
import numpy as np
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
df = pd.read_csv('user-id-sentiment-category_and_score.csv', error_bad_lines=False)
print(df.shape);