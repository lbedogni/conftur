import re
import time

import numpy as np
import pandas as pd
from helium import *
from selenium.webdriver import ChromeOptions

first_google_search = True
first_tripadvisor_search = True
first_attractions_search = True


def init_browser():
    global first_google_search
    first_google_search = True
    options = ChromeOptions()
    options.add_argument('--start-maximized')
    start_chrome(headless=False, options=options)


def get_total_results_from_google(q):
    global first_google_search
    Config.implicit_wait_secs = 0

    go_to('https://google.com')
    if first_google_search:
        wait_until(Button("Accetto").exists)
        click('Accetto')
        first_google_search = False

    iter = 1

    while iter <= 3:
        try:
            write(q, into=S(selector="[name^='q']"))
            press(ENTER)
            results = S(selector="#result-stats").web_element.text
            reg = re.search('Circa(.*)risultati', results)
            total_results = reg.group(1).strip().replace('.', '')

            return total_results
        except:
            print('Not found ' + q + ' at try: ' + str(iter))
            iter += 1

    return False


def apply_results_from_google(row):
    print("Processing: " + row['location'])
    return get_total_results_from_google(row['location'])


def process_google_results():
    # init_browser()
    df = pd.read_csv('datasets/complete_dataframe.csv')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    cities_df = df[['location']].drop_duplicates().dropna().reset_index()

    # decommenta se si vuole testare

    # print(cities_df)

    # cities_df['google_results'] = cities_df.apply (lambda row: apply_results_from_google(row), axis=1)

    chunks = np.array_split(cities_df, 50)

    # Se si blocca decommentare questa linea e farlo ripartire specificando da quale chunk sostituendo la X in chunks[X:]
   # chunks = chunks[16:]

    total_chunks = len(chunks)

    for i, chunk in enumerate(chunks):
        try:
            init_browser()
            print("Processing chunk: " + str(i + 1) + "/" + str(total_chunks))
            start = time.time()
            chunk['google_results'] = chunk.apply(lambda row: apply_results_from_google(row), axis=1)
            chunk.to_csv('cities/google_' + str(i) + ".csv")
            end = time.time()
            print(str(end - start))
            kill_browser()
        except:
            print('Error')


process_google_results()
