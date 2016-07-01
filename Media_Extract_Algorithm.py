#California Drought and Water Consumption (California)

#Import necessary modules
import csv
import datetime
from googleapiclient.discovery import build
import ast
import numpy as np
from scipy.interpolate import interp1d
import time


media_sites = []
sites_key = []
keywords = []
keyword_list = [] #tags
commands = {}
#byday = [] an array named after the days ave been established
error = 0
d_media_byphrase_date_in = {} #d means this is organized by day, byphrase is signifying the key is the keyword
d_media_byphrase_number_in = {}
m_media_byphrase_date_in = {}
m_media_byphrase_number_in = {}
d_media_byphrase_date_ex = {}
d_media_byphrase_number_ex = {}
m_media_byphrase_date_ex = {}
m_media_byphrase_number_ex = {}
xmonth = []
media_byphrase_month_in = {}
media_byphrase_month_ex = {}
#title_list = [] named within loop
miss = 0
itval = 1

#DK is an array with all developer keys
DK = ['AIzaSyAcuvJhmNsmSeuIgUF6c_LzIcmxRHW8nUA',
    'AIzaSyAbT0JKJeWw9kBFnJA0xLb9oRhAb3eFUIE',
    'AIzaSyBilrGb3kC2QWto52SKKOATPiLOZsbhNro',
    'AIzaSyC05WyhgmafGYoaSPzw3oA5TqhInYi75pI']#,
    #'AIzaSyCfOCEo0UAgn4xxi8ujzwpLQz3rdjIOMYA']
DKnum = 0

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
with open('codes.csv','rb') as s:
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

#establish 1/1/2005 as day 0 and create an array of days (each day is first of month)
refdate = datetime.datetime(2005,1,1)
for year in range(2005,2016):
    for month in range(1,13):
        agg = datetime.datetime(year,month,1)
        aggref = int((agg-refdate).days)
        xmonth.append(aggref)

#set up variable dateres, used to restrict search results to after 1/1/2005
today = datetime.datetime.now()
daydelta = today - refdate
past = int(daydelta.days)
dateres = 'd%s' %(past)

lastday = int((datetime.datetime.now()-refdate).days)
xday = (np.linspace(0,lastday,lastday+1)).tolist()
byday = np.zeros(len(xday)) #xday is an array with the list of days that occured since 1/1/2005 (with 1/1/2005 being 0), creates an appendable array, byday, with each index being the day of interest


#____________________________________________________________________________________________________________________________
#for single phrase correlation
#____________________________________________________________________________________________________________________________

with open('media_results_day_in.csv', 'wb') as f:
    print 'here'
    wtr = csv.writer(f)
    for k in range(0,len(keywords)): #for each keyword there is another dictionary
        #key for these dictionaries will be the specific site (example: d_media_byphrase_date_in[keyword][mediasite])
        d_media_byphrase_date_in[keywords[k]] = {}
        d_media_byphrase_number_in[keywords[k]] = {}
        m_media_byphrase_date_in[keywords[k]] = {}
        m_media_byphrase_number_in[keywords[k]] = {}
        wtr.writerow([keywords[k]])
        for n in range(0,len(media_sites)): #for each site, creating a new dictionary
            title_list = ['first'] #creating an array to be changed later
            d_media_byphrase_date_in[keywords[k]][sites_key[n]] = {}
            d_media_byphrase_number_in[keywords[k]][sites_key[n]] = {}
            r = 1 #this is the number of results that have been seen so far (indexed at 1)
            print 'yay'
            print DK
            #try to establish connection and get results from google api, if cannot, switch DK (developer keys)
            try:
                service = build("customsearch", "v1", developerKey=DK[DKnum])
                query = "site:%s '%s'" %(media_sites[n],keywords[k])
                res = service.cse().list(q = query, cx ='015907315053208763487:ihyujd_at7y', exactTerms = 'California', dateRestrict = dateres).execute()
            except:
                current_day = datetime.datetime.now().day
                if DKnum < len(DK) - 1:
                    DKnum = DKnum + 1
                else:
                    while DKnum != 0:
                        DKnum = input('Change DK array index to beginning. Please type 0: ')
                while datetime.datetime.now().day == current_day:
                    time.sleep(300) #sleep for 300 seconds
                    
            #step thruogh each of the ten google api results
            for index in range(0,9):
                #try to use the api specific code, if not work, goes to more general trials
                try:
                    typ = str(eval(commands['type'][n])) #adjust in excel for all three ways of extracting
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
    
                #if found and type is article...
                if typ == 'article':
                    #extract title
                    try:
                        title = eval(commands['title'][n]).encode('ascii','ignore')
                        #if not in list of titles previously extracted: add to title list, get date, convert date to datetime and extract the number day since 1/1/2005
                        if title not in title_list:
                            title_list.append(title[0])
                            ####keyword_to_add = eval(commands['keyword'][n])
                            ####keyword_list.append(keyword_to_add)
                            w = commands['date'][n]
                            w = w.split()
                            s = eval(w[0][1:-1])
                            day = eval(w[1][0:-1] + ', ' + w[2][0:-1] + ', ' + w[3][0:-1])
                            day = int((day-refdate).days)
                            #if day lies within our desired time range, add to byday
                            if day > 0:
                                byday[day] = byday[day] + 1
                    #if not able to be evaluated, counts as a miss
                    except KeyError:
                        miss = miss + 1
                r = r + itval
            results = int(res['searchInformation']['totalResults']) #results is used to estimate number of search to look through
            
            while r < results:
                #attempt to step through each page
                startindex = r
                
                #repeat from what is above
                try:
                    service = build("customsearch", "v1", developerKey=DK[DKnum])
                    query = "site:%s '%s'" %(media_sites[n],keywords[k])
                    res = service.cse().list(q = query, cx ='015907315053208763487:ihyujd_at7y', exactTerms = 'California', lowRange = lowr, highRange = highr, dateRestrict = dateres).execute()
                except:
                    r = r + itval
                
                #step through each result given by api query
                for index in range(0,res['queries']['request'][0]['count']):
                    try:
                        typ = str(eval(commands['type'][n]))
                    except:
                        try:
                            w = commands['type'][4]
                            w = w.split()
                            q = str(eval(w[0][1:-1]))
                            typ = str(eval(w[1][0:-1]))
                        except:
                            typ = 'pass'
                            error = error + 1
                    if typ == 'article':
                        try:
                            title = eval(commands['title'][n]).encode('ascii','ignore')
                            if title in title_list:
                                title_list.append(title[0])
                                w = commands['date'][n]
                                w = w.split()
                                s = eval(w[0][1:-1])
                                day = eval(w[1][0:-1] + ', ' + w[2][0:-1] + ', ' + w[3][0:-1])
                                day = int((day-refdate).days)
                                if day > 0:
                                    try:
                                        byday[day] = byday[day] + 1
                                    except KeyError:
                                        byday[day] = 1
                        except KeyError:
                            miss = miss + 1
                    r = r + itval
            
            d_media_byphrase_date_in[keywords[k]][sites_key[n]] = xday #day (each day since 1/1/2005) (could have 0 articles)
            d_media_byphrase_number_in[keywords[k]][sites_key[n]] = [] #set up array to be appended
            for dictkey in xday:
                d_media_byphrase_number_in[keywords[k]][sites_key[n]].append(byday[dictkey])
            
            xw = np.asarray(d_media_byphrase_date_in[keywords[k]][sites_key[n]])
            yw = np.asarray(d_media_byphrase_number_in[keywords[k]][sites_key[n]])
            row = ['sources']+xw.tolist()
            wtr.writerow(row)
            nxtrow = [sites_key[n]]+yw.tolist()
            wtr.writerow(nxtrow)
            
        #____________________________________________________________________________________________________________________
        #for aggregation
        #____________________________________________________________________________________________________________________
    
        for n in range(0,len(media_sites)):
            m_media_byphrase_date_in[keywords[k]][sites_key[n]] = []
            m_media_byphrase_number_in[keywords[k]][sites_key[n]] = []
            for frst in range(0,len(xmonth)-1):
                m_media_byphrase_date_in[keywords[k]][sites_key[n]].append(xmonth[frst+1]-1) #saves first day of month
                collect = []
                for var in xday:
                    if var >= xmonth[frst] and var < xmonth[frst+1]:
                        try:
                            collect.append(d_media_byphrase_number_in[keywords[k]][sites_key[n]][d_media_byphrase_date_in[keywords[k]][sites_key[n]].index(var)])
                        except ValueError:
                            collect.append(0)
                m_media_byphrase_number_in[keywords[k]][sites_key[n]].append(sum(collect))
    

    
#____________________________________________________________________________________________________________________________
#write to file (month and article database)
#____________________________________________________________________________________________________________________________
            
            
with open('media_results_month_in.csv', 'wb') as f:
    wtr = csv.writer(f)
    for k in range(0,len(keywords)):
        wtr.writerow([keywords[k]])
        for n in range(0,len(sites_key)):
            xw = np.asarray(m_media_byphrase_date_in[keywords[k]][sites_key[n]])
            yw = np.asarray(m_media_byphrase_number_in[keywords[k]][sites_key[n]])
            row = ['sources']+xw.tolist()
            wtr.writerow(row)
            nxtrow = [sites_key[n]]+yw.tolist()
            wtr.writerow(nxtrow)
            
with open('article_information', 'wb') as f:
    wtr = csv.writer(f)
    for k in range(0,len(keywords)):    
        wtr.writerow([keywords[k]])
        for n in range(title_list):
            wtr.writerow([title_list[n]])