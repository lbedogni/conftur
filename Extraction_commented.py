#!/usr/bin/env python
# coding: utf-8

# In[21]:


import pandas as pd
import pickle
import glob
import sys
from lxml import etree
import pandas as pd
import requests
from bs4 import BeautifulSoup


# In[ ]:


path = r'/Users/gianluigiiannantuoni/Desktop/Tirocinio/dataset'
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0, low_memory=False)
    li.append(df)

df_open_citations = pd.concat(li, axis=0, ignore_index=True)


# In[64]:


# Import the file cvs (nrows = 10)
# df_original = pd.read_csv('/Users/gianluigiiannantuoni/Desktop/Tirocinio/dataset/2020-04-25T04_48_36_1.csv', low_memory=False)


# In[65]:


# show the first 5 elements of dataset
df_open_citations.head(30)


# In[68]:


df_original.sort_values(by='citing', ascending=True)


# In[24]:


# create a Series with grouping for citing --- >fare sul cited
df_cited = df.groupby(['cited']).count()


# In[25]:


df_cited


# In[26]:


# Sort a Series with grouping for citing 
df_cited.sort_values(by='oci', ascending=False, inplace=True)


# In[27]:


df_cited.head(150)


# In[28]:


df_cited.drop(['creation', 'timespan', 'journal_sc', 'author_sc'], axis=1, inplace=True)


# In[29]:


df_cited.head(150)


# In[30]:


df_cited.index.names = ['Articoli']


# In[31]:


df_cited.head(150)


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


# In[93]:




myfile = open('/Users/gianluigiiannantuoni/Desktop/Tirocinio/dataset/dblp.xml', 'r')
ok = False
count = 0

for line in myfile.readlines():
   if "<inproceedings" in line:
       count += 1
print(count)
myfile.close()


# In[122]:



#from crossref.restful import Works
#works = Works()

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

df = pd.DataFrame(db)
df['doi'] = df['ee'].str.replace('https://doi.org/', '')


# In[57]:


df.rename(columns={'doi' : 'Articoli'}, inplace=True)


# In[70]:


#df["Articoli"] = df["Articoli"].apply(pd.to_string)


# In[47]:


df_cited


# In[39]:


df_cited.drop('oci', axis=1, inplace=True)


# In[40]:


df_cited


# In[41]:


df_cited.reset_index()


# In[123]:


df


# In[76]:


df_cited.sort_values(by='Articoli', ascending=False)


# In[84]:


df_cited.index.name = 'doi'


# In[85]:


df_cited


# In[191]:


df_merge_col = pd.merge(df_cited, df, on='doi')


# In[193]:


df_merge_col['url'] = df_merge_col['url'].str.replace(r'#.*', "") 
df_merge_col = df_merge_col.groupby(['year', 'url'], as_index=False).sum()
# df_merge_col.sort_values(by='url', ascending=False, inplace=True)
df_merge_col
#cancellare url da '#' in poi per raggruppare e sommare cited 


# In[194]:


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


# In[170]:


df_merge_col_sample[['title','location']] = df_merge_col_sample['url'].apply(fun)


# In[171]:


df_merge_col_sample

