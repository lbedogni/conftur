import pandas as pd
import requests
from bs4 import BeautifulSoup
import os.path

path = 'dataset'
df_merge_col = pd.read_csv(path + '/initial_dataframe.csv', index_col=0)
skiprows = 0

if os.path.isfile('complete_dataframe.csv'):
    df = pd.read_csv('complete_dataframe.csv', low_memory=False)
    skiprows = df.shape[0]

df_merge_col = df_merge_col.iloc[skiprows:]


def fun(address):
    try:
        url = "https://dblp.org/" + address
        get_url = requests.get(url)
        get_text = get_url.text
        soup = BeautifulSoup(get_text, "html.parser")
        dirtyTitle = soup.select('h1')[0].text.strip()
        dirtyTitle = dirtyTitle.split(':')
        title = dirtyTitle[0]
        location = dirtyTitle[1].replace('\n', '')

    except:
        title = None
        location = None

    return pd.Series([title, location])


n = 500000 
chunks = [df_merge_col[i:i + n] for i in range(0, df_merge_col.shape[0], n)]
header = True
for chunk in chunks:
    chunk[['title', 'location']] = chunk['url'].apply(fun)
    chunk.to_csv('complete_dataframe.csv', mode='a', header=header)
    header = False
