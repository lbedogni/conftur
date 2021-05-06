import modin.pandas as pd
import pickle
import glob
import sys
from lxml import etree
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


path = 'dataset'
all_files = glob.glob(path + "/*.csv")

df_complete = pd.DataFrame()

if len(glob.glob(path + '/oci_raw_dataset.csv')) == 0:
    for filename in tqdm(all_files):
        df = pd.read_csv(filename, index_col=None, header=0, low_memory=False)
        df = df.drop(['oci', 'creation', 'timespan', 'journal_sc', 'author_sc', 'citing'], axis=1)
        df = df.rename(columns={'cited': 'Articolo'})
    
        df.loc[:,'Citazioni'] = 1
        df_complete = df_complete.append(df)
        df_complete = df_complete.groupby(['Articolo'], as_index=False).sum()#.reset_index()
    df_complete.to_csv(path + '/oci_raw_dataset.csv')
else:
    df_complete = pd.read_csv(path + '/oci_raw_dataset.csv')
