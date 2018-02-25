import pwd
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
    
def clean_string(text_list, list=True):
    f = lambda x: re.sub(u"{(.*)}", "", x)
    if not list:
        return f(text_list.replace("=","")).strip().lower()
    return [f(c.replace("=","")).strip().lower() for c in text_list]

def get_topics2(page_text):
    topics = clean_string(find_patten(u"==(.+)==", page_text, 'all'))
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
    site = pywikibot.Site('en', 'wikipedia')  # The site we want to run our bot on
    user_page = pywikibot.User(site, 'Nicozheng')
    if contributions:
        contributions = list(user_page.contributions())
        return (user_page, contributions)
    return user_page

def get_time_intervals(revisions):
    revisions['timestamp'] = pd.to_datetime(revisions['timestamp'])
    revisions = revisions.sort_values('timestamp', ascending=False)
    times = revisions['timestamp'].reset_index(drop=True)
    time_intervals = []
    for i in range(len(times)-1):
        time_intervals.append(times[i] - times[i+1])
    time_intervals = [c.total_seconds() for c in time_intervals]
    # time_intervals = [c.total_seconds()/(60*60*24) for c in time_intervals]
    return pd.Series(time_intervals)

def cal_burstiness(time_intervals):
    # hist, bins = np.histogram(time_intervals, bins=100, density=True)
    std = np.std(time_intervals)
    mean = np.mean(time_intervals)
    return (std-mean)/(std+mean)

def cal_burstiness_window(revisions, window='60D', username = False):
    g = revisions.groupby(pd.Grouper(key='timestamp', freq=window))
    burst = {}
    submission = {}
    for key,df in g:
        if not username:
            burst[key] = cal_burstiness(get_time_intervals(df))
            submission[key] = len(df)
        else:
            if isinstance(username, str):
                mask = df['user'] == username
                burst[key] = cal_burstiness(get_time_intervals(df[mask]))
                submission[key] = len(df[mask])
            elif isinstance(username, set):
                mask = df['user'].apply(lambda x: x in username)
                burst[key] = cal_burstiness(get_time_intervals(df[mask]))
                submission[key] = len(df[mask])        
    return (pd.Series(burst), pd.Series(submission))

def lag_x(con1, coordinators, x):
    tmp = pd.DataFrame([con1, coordinators]).T
    con = tmp[0].dropna().values
    lag = tmp.ix[[c - pd.to_timedelta(x) for c in tmp[0].dropna().index],1].values
    return pd.DataFrame([con,lag]).T.corr().ix[0,1]

def cal_pearson(username, coordinator_set, lagged=False):
    con1_bursts, con1_submissions = cal_burstiness_window(revisions, username=username)
    top_con_bursts, top_con_submissions = cal_burstiness_window(revisions, username=coordinator_set)
    if not lagged:
        pearson = pd.DataFrame([con1_bursts, top_con_bursts]).T.dropna().corr().ix[0,1]
    elif lagged:
        pearson = lag_x(con1_bursts, top_con_bursts, '60D')
    return pearson 

def plot_user(username):
    top_contributors = set(contributors.sort_values(ascending=False).index[:30])
    con1_bursts, con1_submissions = cal_burstiness_window(revisions, username=username)
    top_con_bursts, top_con_submissions = cal_burstiness_window(revisions, username=top_contributors-set(username))
    pd.DataFrame([con1_bursts, top_con_bursts]).T.plot()
    pd.DataFrame([con1_submissions, top_con_submissions]).T.plot()
    
# from diff_match_patch import diff

# changes = diff("Hello world.", "Hello moon.",
#         timelimit=0, checklines=False)

# print(changes)

# for op, length in changes:
#         if op == "-": print ("next", length, "characters are deleted")
#         if op == "=": print ("next", length, "characters are in common")
#         if op == "+": print ("next", length, "characters are inserted")
# c = pywikibot.diff.difflib.context_diff(a.splitlines(),b.splitlines())

# compare difference 
def get_topics(page_text):
    topics = find_patten(u"==(.+)==", page_text, 'all')
    return topics

def parse_element(wikidoc, top1, top2):
    reg = r"=={0}==+((.|\n)+)=={1}==".format(top1, top2)
    return find_patten(reg, wikidoc)[0]

def wikidoc_parser(title, wikidoc):
    # generate parse tags
    topics = get_topics(wikidoc)
    # inforbox and introduction 
    try:
        info = find_patten("Infobox((.|\n)+)'''{0}'''".format(title), wikidoc)
    except:
        info = 'NA'
    try:
        intro = find_patten("'''{0}'''((.|\n)+)=={1}==".format(title, topics[0]),wikidoc)
    except:
        intro = 'NA'
    tags = {'info_box': info, 
            'introduction': intro}
    # parse topics
    for i in range(len(topics)-1):
#         print(topics[i])
        try:
            tmp = parse_element(wikidoc, topics[i], topics[i+1])
        except:
            tmp = 'NA'
        tags[clean_string(topics[i], list=False)] = tmp
    
    # last element 
    try:
        tmp = find_patten("=={0}==((.|\n)+)\n\n".format(topics[-1]), wikidoc)
    except:
        tmp = 'NA'
    tags[clean_string(topics[-1], list=False)] = tmp
    return tags

def topic_diff(doc1, doc2, topic):
    '''
    return 0 for the same; 1 for not the same 
    '''
    # check existence
    a, b = topic in doc1.keys(), topic in doc2.keys()
    if a+b==0:
        return 0
    elif a+b==1:
        return 1
    else:
        if doc1[topic] == doc2[topic]:
            return 0
        else:
            return 1

def doc_diff(doc1, doc2, topics):
    diff = {}
    for i in topics:
        diff[i] = topic_diff(doc1, doc2, i)
    return diff

def gini(array):
    """Calculate the Gini coefficient of a numpy array."""
    # based on bottom eq:
    # http://www.statsdirect.com/help/generatedimages/equations/equation154.svg
    # from:
    # http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
    # All values are treated equally, arrays must be 1d:
    array = array.flatten()
    if np.amin(array) < 0:
        # Values cannot be negative:
        array -= np.amin(array)
    # Values cannot be 0:
    array += 0.0000001
    # Values must be sorted:
    array = np.sort(array)
    # Index per array element:
    index = np.arange(1,array.shape[0]+1)
    # Number of array elements:
    n = array.shape[0]
    # Gini coefficient:
    return ((np.sum((2 * index - n  - 1) * array)) / (n * np.sum(array)))
