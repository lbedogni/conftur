#!/usr/bin/env python
# coding: utf-8

# In[26]:


import pandas as pd
import pickle
import glob
import sys
from lxml import etree
import requests
from bs4 import BeautifulSoup


# In[27]:


path = 'dataset'
all_files = glob.glob(path + "/*.csv")

df_complete = None

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0, low_memory=False)
    df = df.drop(['oci', 'creation', 'timespan', 'journal_sc', 'author_sc', 'citing'], axis=1)
    df = df.rename(columns={'cited': 'Articolo'})
    df = df.groupby(['Articolo']).size().reset_index(name='Citazioni')
    
    if df_complete is None:
        df_complete = df.copy()
    else:
        df_complete = pd.concat([df, df_complete])
        df_complete = df_complete.groupby(['Articolo']).sum().reset_index()
        
df_open_citations = df_complete.sort_values(by='Citazioni', ascending=False).set_index('Articolo')



# In[29]:


if len(glob.glob('dblp_new.xml')) == 0:
    
    myfile = open(path + '/dblp.xml', 'r')
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


# In[30]:


db = []

for event, element in etree.iterparse("dblp_new.xml", 
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
df_dblp['doi'] = df_dblp['ee'].str.replace('https://doi.org/', '')


# In[31]:


df_dblp.rename(columns={'doi' : 'Articolo'}, inplace=True)



# In[33]:


df_merge_col = pd.merge(df_open_citations, df_dblp, on='Articolo')


# In[34]:


df_merge_col['url'] = df_merge_col['url'].str.replace(r'#.*', "") 
df_merge_col = df_merge_col.groupby(['year', 'url'], as_index=False).sum()



# In[36]:


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


# In[37]:


df_merge_col[['title','location']] = df_merge_col['url'].apply(fun)


# In[38]:


df_merge_col.to_csv('complete_dataframe')






