import pandas as pd
#from xml.dom import minidom
import pickle
import os
from lxml import html as etree_lxml

tagsnotconsidered = []

def getIfExists(article,tag):
    if article.find(tag) != None:
        return article.find(tag).text
    return ""

myDF = pd.DataFrame()
#with open('dblp-clean-noauthor.xml', 'rb') as xml:
with open('out.xml', 'rb') as xml:
    print('[etree lxml] Starting to parse XML')
    tree = etree_lxml.fromstring(xml.read())
    xml_etree_lxml = tree.findall('./proceedings', {})
    counter = 0
    total = len(xml_etree_lxml)
    lastArticleTitle = ""
    toCheck = False
    if os.path.exists('lastArticleTitle.txt'):
        fff = open('lastArticleTitle.txt','r')
        lastArticleTitle = fff.readline()
        toCheck = True
    for article in xml_etree_lxml:
        if toCheck:
            if article.find('title') != None:
                title = article.find('title').text
                if lastArticleTitle == title:
                    toCheck = False
                else:
                    continue
            else:
                continue

        if counter % 1000 == 0:
            print(counter/total)
        if counter % 10000 == 0:
            if os.path.exists('dblp.p'):
                myDFTmp = pickle.load(open('dblp.p','rb'))
                myDF = myDF.append(myDFTmp)
            pickle.dump(myDF,open('dblp.p','wb'))
            fw = open('lastArticleTitle.txt','w')
            fw.write(lastArticleTitle + '\n')
            fw.close()
            myDF = pd.DataFrame()
        counter += 1
        # Check non controlled tags
        for mytag in article.getchildren():
            if mytag.tag not in ['title','journal','author','publtype','ee','key','publisher','year','key']:
                if mytag.tag not in tagsnotconsidered:
                    tagsnotconsidered.append(mytag.tag)
                    print(mytag.tag)

        authors = ""
        publtype = ""
        ee = ""
        key = ""
        publisher = ""
        year = ""
        key = ""
        journal = ""
        if article.find('publtype') != None:
            publtype = article.find('publtype').text
        for ees in article.findall('ee'):
            ee += ees.text + ","
        ee = ee[:-1]
        if article.find('key') != None:
            key = article.find('key').text
        for auth in article.findall('author'):
            authors += auth.text + ","
        authors=authors[:-1]
        if article.find('title') != None:
            title = article.find('title').text
        if article.find('publisher') != None:
            publisher = article.find('publisher').text
        if article.find('year') != None:
            year = article.find('year').text
        if article.find('journal') != None:
            journal = article.find('journal').text

        editor = getIfExists(article,'editor')
        booktitle = getIfExists(article,'booktitle')
        pages = getIfExists(article,'pages')
        address = getIfExists(article,'address')
        volume = getIfExists(article,'volume')
        number = getIfExists(article,'number')
        month = getIfExists(article,'month')
        url = getIfExists(article,'url')
        cdrom = getIfExists(article,'cdrom')
        cite = getIfExists(article,'cite')
        note = getIfExists(article,'note')
        crossref = getIfExists(article,'crossref')
        isbn = getIfExists(article,'isbn')
        series = getIfExists(article,'series')
        school = getIfExists(article,'school')
        chapter = getIfExists(article,'chapter')
        publnr = getIfExists(article,'publnr')

        myDF = myDF.append({'title':title,'authors':authors,'publisher':publisher,'year':year,
            'journal':journal,'ee':ee,'type':publtype,'key':key, 'editor':editor, 'booktitle':booktitle, 'pages':pages,
            'address':address, 'volume':volume, 'number':number, 'month':month, 'url':url, 'cdrom':cdrom, 'cite':cite,
            'note':note, 'crossref':crossref, 'isbn':isbn, 'series':series, 'school':school, 'chapter':chapter, 'publnr':publnr, 'CIT':-1},
            ignore_index=True)
        lastArticleTitle = title
print(tagsnotconsidered)
print(myDF)
myDFTmp = pickle.load(open('dblp.p','rb'))
myDF = myDF.append(myDFTmp)
pickle.dump(myDF,open('dblp.p','wb'))
fw = open('lastArticleTitle.txt','w')
fw.write(lastArticleTitle + '\n')
fw.close()
