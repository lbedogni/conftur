from os import kill
import re
import time

import numpy as np
import pandas as pd
from helium import *
from selenium.webdriver import ChromeOptions
import chromedriver_autoinstaller
from selenium.webdriver.remote.webelement import WebElement

chromedriver_autoinstaller.install()

first_google_search = True
first_tripadvisor_search = True
first_attractions_search = True


def init_browser():
    options = ChromeOptions()
    options.add_argument('--start-maximized')
    start_chrome(headless=False, options=options)

def get_total_results_from_booking_attractions(q):
    global first_attractions_search
    iter = 1

    while iter <= 3:
        try:
            go_to('https://www.booking.com/attractions/index.it.html')
            if first_attractions_search:
                wait_until(Button("Accetta").exists)
                click('Accetta')
                first_attractions_search = False
            slow_type(S(selector="[name^='query']").web_element, q, 0.1)
            # write(q, into=S(selector="[name^='query']"))
            # wait_until(S(selector="//li/div[contains(text(), 'Destinazioni')"))

            wait_until(lambda: len(
                find_all(S(selector="//li/div[contains(text(), 'Destinazioni')]/parent::*/parent::*/li"))) > 1)
            # wait_until(S(selector="//li/div[contains(text(), 'Destinazioni')]/parent::*/parent::*"))
            press(ARROW_DOWN)
            press(ENTER)
            results = S(selector="//h1[contains(text(),'attività')]").web_element.text
            reg = re.search('(.*)attività', results)
            total_results = reg.group(1).strip().replace('.', '')
            return total_results
        except:
            print('Not found ' + q + ' at try: ' + str(iter))
            iter += 1

    return False

def apply_results_from_booking_attractions(row):
    print("Processing: " + row['location'])
    return get_total_results_from_booking_attractions(row['city'])


def process_booking_attractions_results():
    # init_browser()
    df = pd.read_csv('datasets/complete_dataframe.csv')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    cities_df = df[['city']].drop_duplicates().dropna().reset_index()

    # decommenta se si vuole testare
    # cities_df = cities_df.head(30)

    # print(cities_df)

    # cities_df['google_results'] = cities_df.apply (lambda row: apply_results_from_google(row), axis=1)

    chunks = np.array_split(cities_df, 100)

    # Se si blocca decommentare questa linea e farlo ripartire specificando da quale chunk sostituendo la X in chunks[X:]
    # chunks = chunks[1:]

    total_chunks = len(chunks)

    for i, chunk in enumerate(chunks):
        init_browser()
        print("Processing chunk: " + str(i + 1) + "/" + str(total_chunks))
        start = time.time()
        chunk['attractions_results'] = chunk.apply(lambda row: apply_results_from_booking_attractions(row), axis=1)
        chunk.to_csv('cities/attractions_' + str(i) + ".csv")
        end = time.time()
        print(str(end - start))
        kill_browser()

def slow_type(element: WebElement, text: str, delay: float=0.1):
    """Send a text to an element one character at a time with a delay."""
    for character in text:
        element.send_keys(character)
        time.sleep(delay)

    
process_booking_attractions_results()