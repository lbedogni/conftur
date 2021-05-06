import pandas as pd
import pickle
import glob
import sys
from lxml import etree
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


path = 'dataset'

df_complete = pd.read_csv(path + '/oci_raw_dataset.csv')
df_dblp = pd.read_csv('dblp_dataframe.csv')

df_merge_col = pd.merge(df_complete, df_dblp, on='Articolo')

df_merge_col['url'] = df_merge_col['url'].str.replace(r'#.*', "", regex=True) 
df_merge_col = df_merge_col.groupby(['year', 'url'], as_index=False).sum()

df_merge_col.to_csv('dataframe_conf_cit.csv')
