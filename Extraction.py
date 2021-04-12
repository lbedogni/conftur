#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import pickle
import glob
import sys
from lxml import etree
import requests
from bs4 import BeautifulSoup


# In[5]:


path = r'/Users/gianluigiiannantuoni/Desktop/Tirocinio/dataset'
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0, low_memory=False)
    li.append(df)

df_open_citations = pd.concat(li, axis=0, ignore_index=True)


# In[85]:


df_open_citations.sort_values(by='citing', ascending=True)


# In[86]:


df_open_citations.drop(['creation', 'timespan', 'journal_sc', 'author_sc'], axis=1, inplace=True)


# In[87]:


df_cited = df_open_citations.groupby(['cited']).count()
df_cited.sort_values(by='citing', ascending=False, inplace=True)
df_cited


# In[88]:


df_cited.index.names = ['Articoli']


# In[89]:


df_cited.drop('oci', axis=1, inplace=True)
df_cited


# In[ ]:


if len(glob.glob('dblp_new.xml')) == 0:
    
    myfile = open('/Users/gianluigiiannantuoni/Desktop/Tirocinio/dataset/dblp.xml', 'r')
    outfile = open('dblp_new.xml', 'w')
    ok = False

    for line in myfile.readlines():
       if "<inproceedings" in line or ok:
           ok = True
           if "</inproceedings" in line and ok:
               if "<inproceedings" in line:
                   ok = True
                   outfile.write(line)
               else:
                   outfile.write('</inproceedings>\n')
                   ok = False
           else:
               try:
                   if line[1] == "/":
                       outfile.write(line[line.find('>') + 1:])
                   else:
                       outfile.write(line)
               except:
                   print(line)
    myfile.close()
    outfile.close()


# In[90]:


db = []

for event, element in etree.iterparse('/Users/gianluigiiannantuoni/Desktop/Tirocinio/dataset/dblp_new.xml', 
                                      tag="inproceedings", load_dtd=True, html=True):
   title = ''
   year = ''
   ee = ''
   url = ''
   author = []

   for child in element:
       if child.tag == 'author' and child.text:
           author.append(child.text)
       if child.tag == 'title' and child.text:
           title = child.text
       if child.tag == 'year' and child.text:
           year = child.text
       if child.tag == 'ee' and child.text:
           ee = child.text
       if child.tag == 'url' and child.text:
           url = child.text
 
   db.append({
       'author': ','.join(author),
       'title': title,
       'year': year,
       'ee': ee,
       'url': url
   })

   element.clear()

pd.set_option('display.max_columns', None)

df_dblp = pd.DataFrame(db)
df_dblp['doi'] = df['ee'].str.replace('https://doi.org/', '')


# In[91]:


df_dblp.rename(columns={'doi' : 'Articoli'}, inplace=True)


# In[92]:


df_cited


# In[93]:


df_dblp


# In[94]:


df_merge_col = pd.merge(df_cited, df_dblp, on='Articoli')


# In[96]:


df_merge_col['url'] = df_merge_col['url'].str.replace(r'#.*', "") 
df_merge_col = df_merge_col.groupby(['year', 'url'], as_index=False).sum()


# In[97]:


def fun(address):
    
    url = "https://dblp.org/" + address
    get_url = requests.get(url)
    get_text = get_url.text
    soup = BeautifulSoup(get_text, "html.parser")

    dirtyTitle = soup.select('h1')[0].text.strip()
    dirtyTitle = dirtyTitle.split(':')
    
    title = dirtyTitle[0]
    location = dirtyTitle[1].replace('\n', '')

    return pd.Series([title, location])


# In[98]:


df_merge_col[['title','location']] = df_merge_col['url'].apply(fun)


# In[ ]:




