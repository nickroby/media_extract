#California Drought and Water Consumption (California)

#Import necessary modules
import csv
import math
import time
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import ast
import numpy as np
import time

# User inputs
#____________________________________________________________________________________________________________________________

output_filename = 'media_results.csv'
refdate = '01-01-2005'

#____________________________________________________________________________________________________________________________

media_sites = []
sites_key = []
keywords = []
keyword_list = [] #tags
commands = {}
#byday = [] an array named after the days ave been established
error = 0

xmonth = []
media_byphrase_month_in = {}
media_byphrase_month_ex = {}
miss = 0
itval = 1

#DK is an array with all developer keys
DK = ['AIzaSyAcuvJhmNsmSeuIgUF6c_LzIcmxRHW8nUA',
    'AIzaSyAbT0JKJeWw9kBFnJA0xLb9oRhAb3eFUIE',
    'AIzaSyBilrGb3kC2QWto52SKKOATPiLOZsbhNro',
    'f86142f91017335a828ca4c42554d1c448f395df',
    'AIzaSyA4jTMoTLQ84uXEPrNggzXv-S38gT2Lrvw',
    'AIzaSyC05WyhgmafGYoaSPzw3oA5TqhInYi75pI']#,
    #'AIzaSyCfOCEo0UAgn4xxi8ujzwpLQz3rdjIOMYA']
DKnum = 5

#First extract the websites to a list without other information
with open('mediasites2.csv', 'rb') as s:
    rdr = csv.reader(s)
    next(rdr)
    for x in rdr:
        media_sites.append(x[1])
        sites_key.append(x[0])

#This establishes the words being searched for in an article
with open('keywords2.csv', 'rb') as s:
    rdr = csv.reader(s)
    next(rdr)
    for x in rdr:
        keywords.append(x[1])

#load in api specific code
with open('codes_pb.csv','rb') as s:
    rdr = csv.reader(s)
    for x in rdr:
        keys = x
        break
    for x in rdr:
        try:
            commands[keys[1]].append(x[1]) #'type'
            commands[keys[2]].append(x[2]) #'date'
            commands[keys[3]].append(x[3]) #'keyword'
            commands[keys[4]].append(x[4]) #'title'
            commands[keys[5]].append(x[5]) #'website'
            commands[keys[6]].append(x[6]) #'type2'
        except KeyError:
            commands[keys[1]] = ([x[1]]) #'type'
            commands[keys[2]] = ([x[2]]) #'date'
            commands[keys[3]] = ([x[3]]) #'keyword'
            commands[keys[4]] = ([x[4]]) #'title'
            commands[keys[5]] = ([x[5]]) #'website'
            commands[keys[6]] = ([x[6]]) #'type2'

#list of topics to do further search (currently unused)
with open('topics2.csv', 'rb') as s:
    rdr = csv.reader(s)
    for x in rdr:
        topics = x

#set up variable dateres, used to restrict search results to after 1/1/2005
today = datetime.now().date()
daydelta = today - refdate
past = int(daydelta.days)
dateres = 'd%s' %(past)

#____________________________________________________________________________________________________________________________
# Get dump of all media results for the time period
#____________________________________________________________________________________________________________________________

with open(output_filename, 'wb') as f:

    wtr = csv.writer(f)

    for k in range(len(keywords)): #for each keyword there is another dictionary

        keyword = keywords[k]

        for n in range(len(media_sites)): #for each site, creating a new dictionary

            site = media_sites[n]  
            # Reset the results counter to 1 for the given keyphrase and mediasite 
            rn_tot = 1
            # Reset the start date to 01-01-2005 for the given keyphrase and mediasite

            rn = 1 # Reset the number of results from the keyword, media_site and week that have been seen so far to 1  
            start_time = time.time()

            while True:
                            
                rn_low  = rn
                
                #repeat from what is above
                try:
                    service = build("customsearch", "v1", developerKey=DK[DKnum])
                    query = "site:%s '%s'" %(media_sites[n],keywords[k])
                    res = service.cse().list(q = query, cx ='015907315053208763487:ihyujd_at7y', exactTerms = 'California', start = rn_low, dateRestrict = dateres).execute()
                    n_tot_res = int(res['searchInformation']['totalResults'])

                    # Get the number of results in the given query
                    n_res = res['queries']['request'][0]['count']

                    # step through each of the ten google api results
                    for index in range(n_res):
                        #try to use the api specific code, if not work, goes to more general trials
                        try:
                            media_type_1 = str(eval(commands['type'][n])) #adjust in excel for all three ways of extracting
                        except:
                            #try general, if not work, skip
                            try:
                                w = commands['type'][20]
                                w = w.split()
                                q = str(eval(w[0][1:-1]))
                                typ = str(eval(w[1][0:-1]))
                            except:
                                typ = 'pass'
                                error = error + 1
                        try:
                            title = eval(commands['title'][n]).encode('ascii','ignore')
                        except KeyError:
                            miss = miss + 1  
                        date = eval(commands['date'][n])
                        row = [site, keyword, title, date, media_type_1]
                        wtr.writerow(row)
                        rn += 1
                        rn_tot += 1
                except:
                    break
                if time.time() - start_time > 120:
                    print 'Request for results for %s to %s for keyword: "%s" and media source: "%s" timed out' %(refdate, today, keyword, site)
                    break

            print '%s results retrieved for keyword: "%s" and media source: "%s"' %(rn_tot-1, keyword, site)    
