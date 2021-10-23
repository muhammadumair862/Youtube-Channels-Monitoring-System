
from selenium import webdriver
import pandas as pd
import bs4
import time
import csv
import os
import random

driver = webdriver.Chrome('chromedriver.exe')

# ## Read Excel file


def read_excelfile(path):
    df = pd.read_excel(path)
    return list(df['Links'])


# ## URL map playlist-to-upload-video


def cha(x):
    if '/playlists' in x:
        x = x.replace('/playlists', '/videos')
    elif '/videos' != x[-7]:
        x = x + '/videos'
    return x


# ## Store Data


def store_data(v_url, v_title, v_views, vtags, plist):
    plist = [plist for i in range(len(v_title))]
    data = pd.DataFrame(
        {'Channel playlist': plist, 'Video URL': v_url, 'Title': v_title, 'Views': v_views, 'Tags': vtags})
    if os.path.isfile('sample.csv'):
        data.to_csv('sample.csv', index=False, mode='a', header=False)
    else:
        data.to_csv('sample.csv', index=False, mode='a')


# ## Extract Page

def extract_data():
    page = bs4.BeautifulSoup(driver.page_source, 'lxml')
    items = page.find('div', attrs={'id': 'contents'})
    v_url, v_title, v_views, vtags = [], [], [], []
    for i in items.find_all('ytd-grid-video-renderer'):
        #         print('Video URL :','https://www.youtube.com'+i.a['href'])
        #         print('Video Title :',i.find('a',attrs={'id':'video-title'}).text)
        title = i.find('a', attrs={'id': 'video-title'}).text
        v_d = i.find('div', attrs={'id': 'metadata-line'}).text
        #         print('Views :',v_d.split('views')[0])
        #         print('Date :',v_d.split('views')[1])

        v_url.append('https://www.youtube.com' + i.a['href'])
        v_title.append(i.find('a', attrs={'id': 'video-title'}).text)
        v_views.append(v_d.split('views')[0])
        if '|' in title:
            vtags.append(', '.join(title.strip().split('|')))

        else:
            vtags.append('')

    return v_url, v_title, v_views, vtags


# ## For Second Time Search



def second_monitor(plist):
    while True:
        driver.execute_script('window.scrollTo(0,document.documentElement.scrollHeight)')
        time.sleep(2)

        v_url, v_title, v_views, vtags = extract_data()
        dd1 = pd.read_csv('sample.csv')
        if len(dd1[dd1['Title'].isin(v_title)]) == len(v_title):
            print('All Videos Present Already')
            break
        elif len(dd1[dd1['Title'].isin(v_title)]) == 0:
            print('Continue')
            continue
        else:
            print('other')
            l1 = list(set(v_title) - set(dd1['Title'][dd1['Title'].isin(v_title)]))
            n_index_list = [v_title.index(i) for i in l1]
            v_url1, v_title1, v_views1, vtags1 = [], [], [], []
            for i in n_index_list:
                v_url1.append(v_url[i])
                v_title1.append(v_title[i])
                v_views1.append(v_views[i])
                vtags1.append(vtags[i])
            #             print(v_url1,v_title1,v_views1,vtags1)
            store_data(v_url1, v_title1, v_views1, vtags1, plist)

            break


# ## For First Time Search


def first_monitor(plist):
    c = 1
    while True:
        start = driver.execute_script('return document.documentElement.scrollHeight')
        driver.execute_script('window.scrollTo(0,document.documentElement.scrollHeight)')
        #         time.sleep(1)
        time.sleep(2.5)
        end = driver.execute_script('return document.documentElement.scrollHeight')
        print(start, end)
        if (start == end) & (c < 4):
            time.sleep(c * 3)
            c += 1
            print("Same & Run")
            continue
        elif start != end:
            print("Loading")
            c = 1
        elif c == 4:
            print("No More Load")
            break
    v_url, v_title, v_views, vtags = extract_data()
    store_data(v_url, v_title, v_views, vtags, plist)


# ## Main Run

def start_run(links):
    for i in links:
        driver.get(i)
        try:
            if os.path.isfile('sample.csv'):
                d2 = pd.read_csv('sample.csv')
                if len(d2[d2['Channel playlist'].isin([i])]):
                    print('This Channel Present in Output file')
                    second_monitor(i)
                else:
                    print('This Channel Monitor First Time')
                    first_monitor(i)
            else:
                print('This Channel Monitor First Time')
                first_monitor(i)
        except:
            print("Invalied URL or some other issues with This channel")


while True:
    try:
        df = read_excelfile('Fan Videos.xlsx')
        for i in range(len(df)):
            df[i] = cha(df[i])
    except:
        print('Youtube Channels URL File Not Present')
        break
    start_run(df[:])
    time.sleep(random.randint(100, 200))





