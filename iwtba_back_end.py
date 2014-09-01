from iwanttobea import *

import httplib 
import httplib2
from operator import itemgetter
from bs4 import BeautifulSoup, SoupStrainer
import re
import urllib2
import pandas as pd
import csv
import string
import numpy as np
import pickle

def get_number_of_job_pages():
    return 25 # the higher this is, the better the results and longer it takes

# combine multiple word frequencies, and keep track of how many job pages each word was found in
def combine_dicts(wc_dicts):
    master_wc_dict = {} # word frequencies
    master_pc_dict = {} # job pages count
    for wc_dict in wc_dicts:
        for key, value in wc_dict.iteritems():
            if key not in master_wc_dict:
                master_wc_dict[key] = value
                master_pc_dict[key] = 1
            else:
                master_wc_dict[key] = master_wc_dict[key] + value
                master_pc_dict[key] = master_pc_dict[key] + 1
    return master_wc_dict, master_pc_dict

# get an indeed job search page
def gen_indeed_url_api(title,pagenum):
    search_term = title.lower()
    search_term = search_term.replace(" ","+")
    city = 'toronto'
    state = 'on'
    country = 'ca'
    start = str(pagenum * 25) # displays only 25 max
    # check out the indeed API for xml results for details on the below
    url = 'http://api.indeed.com/ads/apisearch?publisher=4397075004841351&q=' + search_term + '&l=' + city + '%2C+' + state + '&sort=&radius=&st=&jt=&start=' + start + '&limit=25&fromage=100&filter=&latlong=1&co=' + country + '&chnl=&userip=1.2.3.4&useragent=Mozilla/%2F4.0%28Firefox%29&v=2'

    return url

# get the word frequencies for different job postings
def get_dicts_api(title):
    dicts_list = []
    job_pages = get_number_of_job_pages() # this is the number of job pages to look at
    for pagenum in range(job_pages): 
        print pagenum, "of", job_pages, "job pages"
        indeed_url = gen_indeed_url_api(title,pagenum)
        print indeed_url
        job_page_text = get_webpage_text_api(indeed_url)
        page_wc = get_freqct_api(job_page_text)
        dicts_list.append(page_wc)
    
    return dicts_list

# parse page
def get_webpage_text_api(site):

    web_page = urllib2.urlopen(site).read()
    soup = BeautifulSoup(web_page)

    snippets = soup.find_all('snippet')

    doc = ''
    for snippet in snippets:
        newstr = str(snippet.get_text().encode("utf-8"))
        newstr = "".join(c for c in newstr if c not in ('!','.',':',',','(',')',';',':')).lower()
        doc = doc + newstr
    
    return doc
 
# get word counts helper
def get_freqct_api(text):
    text = text.split(' ')
    freqct = {}
    for s in text:
      if s not in freqct:
        freqct[s]=1
      else:
         freqct[s]+=1
    return freqct

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

# main function 
def get_skills(job):
    print '%%%%%%%%%%%%%%%%%%%%%%%%% testing API %%%%%%%%%%%%%%%%%%%%%%%%%'
    wc_dicts = get_dicts_api(job) # get word frequencies from job postings
    master_wc, master_pc = combine_dicts(wc_dicts) # combine word frequencies and count num pages words appear on
    word_occurances = master_wc
    num_words = np.array(master_wc.values()).sum()
    word_score = {} # will store the relevancy score for each word

    print '**** Loading Pickle ****'

    indeed_word_props = pickle.load( open( "indeed_word_percentages_dict_api.p", "rb" ) ) # word freqs from random indeed posts

    print '**** Calculating Scores ****'
        
    PENALTY_FACTOR = 2
    COMMON_WORD_CUTOFF = .0005
    BAD_SCORE = -1 * PENALTY_FACTOR
    MIN_NUM_OF_PAGES = 1

    for key in master_wc.keys():
        ## the algorithm
        # make sure it's not a really common word (COMMON_WORD_CUTOFF)
        # make sure that it occurs on multiple pages (MIN_NUM_OF_PAGES)
        # then assign it a score which is the difference between the job search freq and the indeed word freq

        if indeed_word_props.get(key,0) < COMMON_WORD_CUTOFF and master_pc[key] > MIN_NUM_OF_PAGES:
            word_score[key] = (master_wc[key]/float(num_words)) - PENALTY_FACTOR *(indeed_word_props.get(key, 0))
        else:
            word_score[key] = BAD_SCORE

    skills = []

    print '**** Sorting ****'

    sol = sorted(word_score.items(), key=itemgetter(1), reverse=True)

    enough_counter = 0
    high_score_flag = 0
    for i in range(len(sol)):
        print "*******Looking for good words..."
        so = sol[i]
        if '\n' not in so[0] and len(so[0])>0 and is_ascii(so[0]) and so[0][0].isalpha() and word_score[so[0]] != BAD_SCORE: # filter results a bit   
            print 'word: ', so[0], 'word count: ', master_wc[so[0]], 'page count', master_pc[so[0]], 'search prop: ', (master_wc[so[0]]/float(num_words)), 'indeed prop: ', indeed_word_props.get(so[0],0), 'score: ', so[1] 
            
            if high_score_flag == 0:
                highest_score = so[1]
                high_score_flag = 1

            skills.append([so[0],np.around(so[1]/float(highest_score), decimals=5)])
            enough_counter+=1
        if enough_counter > 9:
            break

    return skills










