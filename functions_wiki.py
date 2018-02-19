import pywikibot
import pandas as pd 
import numpy as np
import time 
import re
import seaborn as sns
import matplotlib.pyplot as plt 

# %matplotlib inline 

plt.rc('figure', figsize=(12, 6))


def find_patten(regx,page,how="one"):
    pattern = re.compile(regx)
    result = pattern.findall(page)
    if how == "one":
        return result[0]
    elif how == "all":
        return result
    
def clean_string(text_list):
    f = lambda x: re.sub(u"{(.*)}", "", x)
    return [f(c.replace("=","")) for c in text_list]

def get_topics(page_text):
    topics = clean_string(find_patten(u"==(.+)==", text, 'all'))
    return topics

def get_page(page_title, talk_page=False):
    site = pywikibot.Site('en', 'wikipedia')  # The site we want to run our bot on
    page = pywikibot.Page(site, page_title)
    print("current page url %s" % page.full_url())
    if talk_page == True:
        talk = page.toggleTalkPage()
        return (page,talk)
    return page

def identify_users(user_name):
    if 'bot' in user_name.lower():
        return "bot"
    elif re.findall(u"\d+\.\d+\.\d+\.\d+", user_name):
        return "anonymous"
    else:
        return "registered"

def get_page_sub(page, subtitle):
    '''
    subtitle can be: 
    "categories"
    "text"
    "contributors"
    "revisions"
    "revisions_full"
    '''
    if subtitle == "categories":
        return list(page.categories())
    elif subtitle == "text":
        return page.text
    elif subtitle == "contributors":
        return page.contributors()
    elif subtitle == "revisions":
        revisions = page.revisions()
        revisions = pd.DataFrame([c.__dict__ for c in revisions])
        revisions['timestamp'] = pd.to_datetime(revisions['timestamp'])
        revisions.sort_values("timestamp", ascending=False, inplace=True)
        revisions.reset_index(drop=True, inplace=True)
        return revisions
    elif subtitle == "revisions_full":
        revisions = page.revisions(content=True)
        revisions = pd.DataFrame([c.__dict__ for c in revisions])
        revisions['timestamp'] = pd.to_datetime(revisions['timestamp'])
        revisions.sort_values("timestamp", ascending=False, inplace=True)
        revisions.reset_index(drop=True, inplace=True)
        return revisions
    else:
        print("please add a subtitle: {'categories', 'text', 'contributors', 'revisions', 'revisions_full'}")

def date2string(date, reverse = False):
    if reverse:
        return pd.to_datetime(date)
    else:
        return "-".join([str(c) for c in [date.year, date.month, date.day]])

def get_len(x):
    try:
        return len(x)
    except:
        return None

def get_user_page(user_name, contributions=False):
    site = pywikibot.Site('euser_namedia')  # The site we want to run our bot on
    user_page = pywikibot.User(site, 'Nicozheng')
    if contributions:
        contributions = list(user_page.contributions())
        return (user_page, contributions)
    return user_page