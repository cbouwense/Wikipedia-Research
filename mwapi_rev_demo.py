"""
Program that gets the total number of revisions for a Wikipedia article
"""

import mwapi
import numpy as np
from matplotlib import axes
from matplotlib import pyplot as plt

article_title = 'The Elder Scrolls III: Morrowind'

first_revision_year = 0
revisions_by_year = {}

# Connect to Wikipedia
session = mwapi.Session('https://en.wikipedia.org', user_agent='cbouwense')

# Query Wikipedia for revisions on the supplied article
# The result is stored into the dictionary "rev_dict"
rev_dict = session.get(action='query', prop='revisions', rvprop='timestamp', titles=article_title, rvlimit='max')

for keys in rev_dict['query']['pages'].keys():
    page_id = keys

# Find most recent edit year
for timestamps in rev_dict['query']['pages'][str(page_id)]['revisions']:
    latest_revision_year = timestamps['timestamp'][:4]
    revisions_by_year[timestamps['timestamp'][:4]] = 0
    break

# Check if there is a section named "continue".
# If there is, that means the query did not get all the data
# because of the per-user query limits.
while 'continue' in rev_dict:

    # Go through the timestamps for each revision made.
    # If the timestamp is already a key in our dictionary, increment that key value by 1.
    # Else, create a new key for that year in our dictionary and set it to 1
    for timestamps in rev_dict['query']['pages'][str(page_id)]['revisions']:
        if (int(timestamps['timestamp'][:4]) < int(latest_revision_year)):
            latest_revision_year = timestamps['timestamp'][:4]
            revisions_by_year[timestamps['timestamp'][:4]] = 1
        else:
            revisions_by_year[timestamps['timestamp'][:4]] += 1

    for keys in rev_dict['query']['pages'].keys():
        page_id = keys
    continue_val = rev_dict['continue']['rvcontinue']
    rev_dict = session.get(action='query', prop='revisions', rvprop='timestamp', titles=article_title, rvlimit='max', rvcontinue=continue_val)

# Go through the timestamps for each revision made.
# If the timestamp is already a key in our dictionary, increment that key value by 1.
# Else, create a new key for that year in our dictionary and set it to 1
for timestamps in rev_dict['query']['pages'][str(page_id)]['revisions']:
    if (int(timestamps['timestamp'][:4]) < int(latest_revision_year)):
        latest_revision_year = timestamps['timestamp'][:4]
        revisions_by_year[timestamps['timestamp'][:4]] = 1
    else:
        revisions_by_year[timestamps['timestamp'][:4]] += 1

ind = np.arange(len(list(revisions_by_year.keys())))    # the x locations for the groups
width = 0.4       # the width of the bars: can also be len(x) sequence

plt.figure(figsize=(20, 3))
plt.bar(ind, list(revisions_by_year.values()), width, color='#d62728', linewidth=10)

plt.ylabel('Revisions')
plt.title('Revisions of %s Wikipedia Article' % article_title)
plt.xticks(ind, sorted(list(revisions_by_year.keys()), key=int))

plt.show()