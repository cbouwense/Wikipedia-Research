import pywikibot as pwb
from subprocess import Popen, PIPE

# Given a shell command, runs it on machine's kernel 
# (could be Windows or UNIX, so use OS agnostic commands if possible!)
def runCommand(cmd, verbose=True):
    if verbose:
        print ("running:\n%s\n" % cmd)
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output = p.communicate()[0]
    if verbose:
        print ("output:\n%s\n" % output.decode("utf-8"))
    return output

# Returns a list of revids for a page sorted from oldest to newest
def getRevIds(page, fullTuples=False):
    revid_tuples = page.revisions(reverse=True)
    
    if not fullTuples:
        revid_list = []
        for i in revid_tuples:
            print (i)
            revid_list.append(i['revid'])
        return revid_list
    else:
        return revid_tuples

# # TODO: Do we even need this?
# def getDiffHistory(page):
    
#     # Get list of all the revision ids of the page
#     revid_list = getRevIds(page, True)
    
#     # Perform diff on all pairwise revids
#     diff_history = []
    
#     index1 = 0
#     index2 = 1
    
#     for i in range(0, len(revid_list)-2):
#         text1 = page.getOldVersion(oldid=revid_list[index1])
#         text2 = page.getOldVersion(oldid=revid_list[index2])
#         print ("REVID1: %s" % revid_list[index1])
#         print ("REVID2: %s" % revid_list[index2])
#         diff_history.append(wordDiff(text1, text2, 'all', False))
#         index1 += 1
#         index2 += 1
#     return diff_history

def wordDiff(text1, text2, attrib, verbose=False):
    
    # Write texts to files
    text_file = open("text1.txt", "w", encoding="utf-8")
    
    try:
        text_file.write(text1)
    except:
        print ("ERROR: writing text1 to file")
        print (text1)
        return None
    
    text_file.close()
    
    text_file = open("text2.txt", "w", encoding="utf-8")
    
    try:
        text_file.write(text2)
    except:
        print ("ERROR: writing text2 to file")
        print (text2)
        return None
    
    text_file.close()
    
    # Check man pages for options
    cmd = "wdiff -1 -2 -3 -s text1.txt text2.txt"
    output = runCommand(cmd, verbose)
    
    # Format of wdiff output
    # <filename1>.<ext>: <num_words> words  <num_common> <percent_common>% common  <num_deleted> <percent_deleted>% deleted  <num_changed> <percent_changed>% changed\r\n
    # <filename2>.<ext>: <num_words> words  <num_common> <percent_common>% common  <num_inserted> <percent_inserted>% inserted  <num_changed> <percent_changed>% changed\r\n
    
    """
    Index 6: Number of words deleted from previous revision
    Index 7: Percentage of words deleted from previous revision
    Index 9: Number of words changed from previous revision
    Index 10: Percentage of words changed from previous revision
    Index 18: Number of words inserted from previous revision
    Index 19: Percentage of words inserted from previous revision
    Index 21: Number of words changed from previous revision
    Index 22: Percentage of words changed from previous revision
    """
    tokens = output.decode("utf-8").split()
    
    num_words1 = tokens[1]
    num_words2 = tokens[13]
    
    try: 
        num_deleted = tokens[6]
        percent_deleted = tokens[7]

        num_changed1 = tokens[9]
        percent_changed1 = tokens[10]

        num_inserted = tokens[18]
        percent_inserted = tokens[19]

        num_changed2 = tokens[21]
        percent_changed2 = tokens[22]
    except:
        print ("nonstandard wdiff output!")
            
        num_deleted = None
        percent_deleted = None

        num_changed1 = None
        percent_changed1 = None

        num_inserted = None
        percent_inserted = None

        num_changed2 = None
        percent_changed2 = None

    if verbose:
        print ("Words in text1: %s " % num_words1)
        print ("Words in text2: %s " % num_words2)
        print ("Words deleted: %s" % num_deleted)
        print ("Percent deleted: %s" % percent_deleted)
        print ("Words changed 1: %s" % num_changed1)
        print ("Percent changed 1: %s" % percent_changed1)
        print ("Words inserted: %s" % num_inserted)
        print ("Percent inserted: %s" % percent_inserted)
        print ("Words changed 2: %s" % num_changed2)
        print ("Percent changed 2: %s" % percent_changed2)
    
    if attrib == "words":
        return {"text1_words": num_words1,
                "text2_words": num_words2}
    if attrib ==  "deleted":
        return {"num_deleted": num_deleted,
                "percent_deleted": percent_deleted}
    # For now I'm just returning the "first" changed, not sure how the second one could ever differ
    elif attrib == "changed":
        return {"num_changed": num_changed1,
                "percent_changed": percent_changed1}
    elif attrib == "inserted":
        return {"num_inserted": num_inserted,
                "percent_inserted": percent_inserted}
    elif attrib == "all":
        return {"text1_words": num_words1,
                "text2_words": num_words2,
                "num_deleted": num_deleted,
                "percent_deleted": percent_deleted,
                "num_changed1": num_changed1,
                "percent_changed1": percent_changed1,
                "num_changed2": num_changed2,
                "percent_changed2": percent_changed2,
                "num_inserted": num_inserted,
                "percent_inserted": percent_inserted}
    else:
        print ("ERROR: Unknown attribute in wordDiff.\nPlease use \"deleted\", \"changed\", \"inserted\", or \"all\"")
        return {}

# Sorts the revids of a given page into months and years
def divideByMonth(page):
    rev_dict = getRevIds(page, fullTuples=True)

    year = 0
    month = 0
    month_list = []

    rev_data= {}

    for i in rev_dict:
        if i['timestamp'].year > year:
            year = i['timestamp'].year
            month = 0
            rev_data[year] = {}
        if i['timestamp'].month > month:
            month = i['timestamp'].month
            rev_data[year][month] = []

        rev_data[year][month].append(i['revid'])

    return rev_data

# TODO: Do we even need this?
# # Gets the last revid in a given month
# def getMonthsLastRev(year, month, rev_data):
#     return rev_data[year][month][len(rev_data[year][month])-1] 

# Gets the next month in which an article was edited, if it exists at all
def getNextMonth(year, month, rev_data):
    months = list(rev_data[year].keys())
    
    # Are there any months left in current year?
    for month_idx in range(0, len(months)):
        # Yes, return the next month
        if months[month_idx] == month and month_idx < len(months)-1:
            #print ([year, months[month_idx+1]])
            return [year, months[month_idx+1]]
        # No, check if there are remaining years
        
    years = list(rev_data.keys())
    
    for year_idx in range(0, len(years)):
        # Are there any years left?
        if years[year_idx] == year and year_idx < len(years)-1:
            # Yes, return first month of next year
            #print ([years[year_idx+1], list(rev_data[years[year_idx+1]].keys())[0]])
            return [years[year_idx+1], list(rev_data[years[year_idx+1]].keys())[0]]
        # No, return error message
        else:
            #print ("Could not find a month in which an edit was made after %s/%s" % (month, year))
            return [None, None]
            
# Gets the distance between two versions of a given page.
# Takes the difference between the specified month and the next month edited if it exists.
def getMonthsPersistentContribs(page, year, month):
    rev_data = divideByMonth(page)
    
    next_period = getNextMonth(year, month, rev_data)

    next_year = next_period[0]
    next_month = next_period[1]
    
    # compare this month's last version with next month's last version
    try:
        month1_text = page.getOldVersion(oldid=rev_data[year][month][0])
        month2_text = page.getOldVersion(oldid=rev_data[next_year][next_month][0])
        diff = wordDiff(month1_text, month2_text, "all")
    except:
        pass
        #print ("There was probably some error trying to get the version from the months you wanted!")
    
    # Get distance between article versions
    try:
        distance = int(diff['num_deleted']) + int(diff['num_changed1']) + int(diff['num_changed2']) + int(diff['num_inserted'])
        return distance
    except:
        #print ("Issue getting distance between versions %s and %s! (Most likely from a 0 word entry)" % (month, next_month))
        #print ("Fear not, a team of highly skilled monkeys are currently working on a bug fix.")
        return 0

def getPersistentContribs(text1, text2):
    try:
        diff = wordDiff(text1, text2, "all")
    except:
        pass
    try:
        distance = int(diff['num_deleted']) + int(diff['num_changed1']) + int(diff['num_changed2']) + int(diff['num_inserted'])
        return distance
    except:
        #print ("Issue getting distance between versions %s and %s! (Most likely from a 0 word entry)" % (month, next_month))
        #print ("Fear not, a team of highly skilled monkeys are currently working on a bug fix.")
        return 0

# Gets the C^per, A^per, and M^per for a specified page
def getPersistentHistory(page):
    
    # Get all rev_id's indexed in a dictionary by year and month 
    rev_data = divideByMonth(page)
    diffs = []

    years = list(rev_data.keys())
    # Use that dictionary to iterate through the years of editing
    # and enumerate months of editing
    for year in years:
        #if year == years[len(years)-1]:
            #break
        # Get list of months in current year 
        months = list(rev_data[year].keys())

        # Iterate through months of editing and get that month's persistent contribs
        for month in months:
            diffs.append(getMonthsPersistentContribs(page, year, month))

    # Calculate the attributes associated with the article's persistent contributions
    try:
        # C^per
        persistent_sum = sum(diffs)
        # A^per
        persistent_avg = sum(diffs) / len(diffs)
        # M^per
        persistent_max = max(diffs)

        return {'sum': persistent_sum,
                'avg': persistent_avg,
                'max': persistent_max}
    except:
        print ("Error trying to get persistent stats!")
        return None

page = pwb.Page(pwb.Site(), 'High_Sierra_Trail')
