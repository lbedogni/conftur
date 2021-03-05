import requests
import json
import pickle
import os
import pandas as pd

BASE_URL = 'https://w3id.org/oc/index/coci/api/v1/citations/'

myDF = pickle.load(open('dblp-with-cite.p','rb'))
#lastDoi = ""
#if os.path.exists('lastDoi.txt'):
#    fff = open('lastDoi.txt','r')
#    lastDoi = fff.readline()
#allDoiDone = pickle.load(open('dblp-with-cite.p','rb'))['ee']
#print(allDoiDone)

ok = False
counter = 0
totWithCite = len(myDF[myDF['CIT']!=-1])
for line in myDF.iterrows():
    counter += 1
    if line[1]['CIT'] != -1:
        continue
    #if line[1]['ee'] == lastDoi and not ok:
    #    ok = True
    ll = line[1]['ee'].split(',')
    done = False
    for l in ll:
        tries = 0
        if not done and 'doi.org/' in l:
            while not done and tries < 10:
                try:
                    tries += 1
                    print(l)
                    url = BASE_URL + l.split('doi.org/')[1]
                    r = requests.get(url)
                    myDF.loc[myDF['ee'] == line[1]['ee'],'CIT'] = len(json.loads(r.text))
                    done = True
                    totWithCite += 1
                    print("Now done " + str(totWithCite) + " DOIs")
                except json.decoder.JSONDecodeError:
                    print('JSON Decode Error')
                    print(r.text)
                except Exception as e:
                    print('Generic Error')
                    print(e)
                    print(r.text)
            if tries >= 10:
                pickle.dump(myDF,open('dblp-with-cite.p','wb'))

    if counter % 1000 == 0:
        pickle.dump(myDF,open('dblp-with-cite.p','wb'))
