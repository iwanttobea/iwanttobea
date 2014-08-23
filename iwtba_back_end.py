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

def get_number_of_job_postings():
    return 10 #the higher this is, the better the results

# combine multiple word frequencies, and keep track of how many job postings each words was found in
def combine_dicts(wc_dicts):
    master_wc_dict = {} # word frequencies
    master_pc_dict = {} # job postings count
    for wc_dict in wc_dicts:
        for key, value in wc_dict.iteritems():
            if key not in master_wc_dict:
                master_wc_dict[key] = value
                master_pc_dict[key] = 1
            else:
                master_wc_dict[key] = master_wc_dict[key] + value
                master_pc_dict[key] = master_pc_dict[key] + 1
    return master_wc_dict, master_pc_dict

# get the links on an indeed job search page
def get_links(url):
    JOB_LINK_STRING = '/rc/clk?jk='
    INDEED_DOMAIN = 'http://www.indeed.com'
    http = httplib2.Http()
    status, response = http.request(url)
    job_links = []
    for link in BeautifulSoup(response, parse_only=SoupStrainer('a')):
        if link.has_attr('href') and JOB_LINK_STRING in link['href']:
            job_links.append(INDEED_DOMAIN + link['href'])
    return job_links

# get an indeed job search page
def gen_indeed_url(title,pagenum):
    JOB_URL_PRE = 'http://www.indeed.com/jobs?q='
    PAGE_SPECIFIER = '&start='
    search_term = title.lower()
    search_term = search_term.replace(" ","+")
    return JOB_URL_PRE + search_term + PAGE_SPECIFIER + str(np.random.randint(1, 50)*10)

# get the word frequencies for different job postings
def get_dicts(title):
    dicts_list = []
    job_pages = get_number_of_job_postings() #this is the number of job pages to look at
    for pagenum in range(job_pages): 
        print pagenum, "of", job_pages, "job postings"
        indeed_url = gen_indeed_url(title,pagenum+1)
        print indeed_url
        job_links = get_links(indeed_url)

        i = 0
        for link in job_links:
            link = job_links[int(np.random.rand())*len(job_links)]
            print link
            job_page_text = get_webpage_text(link)
            page_wc = get_freqct(job_page_text)
            dicts_list.append(page_wc)
            i+=1
            if i > 0: break
    
    return dicts_list

# parse page
def get_webpage_text(site):

    try: 
        web_page = urllib2.urlopen(site, timeout=1).read()
        soup = BeautifulSoup(web_page)
    except: 
        soup = BeautifulSoup('')
        pass

    for script in soup(["script", "style"]):
        script.extract()
    
    text = soup.get_text()
    
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text
 
# get word counts helper
def get_freqct(text):
    text = text.lower()
    text = text.encode('utf-8').translate(None, string.punctuation)
    text = text.split(' ')
    freqct = {}
    for s in text:
      if s not in freqct:
        freqct[s]=1
      else:
         freqct[s]+=1
    return freqct
 
# get word counts 
def word_count():
    text = get_webpage_text("http://www.indeed.com/rc/clk?jk=4d69e919dfdac3a3")
    text = text.lower()
    d = get_freqct(text.split(' '))
    sol = sorted(d.items(), key=itemgetter(1), reverse=True)

# main function 
def get_skills(job):
    wc_dicts = get_dicts(job) # get word frequencies from job postings
    master_wc, master_pc = combine_dicts(wc_dicts) # combine word frequencies and count num pages words appear on
    word_occurances = master_wc
    num_words = np.array(master_wc.values()).sum()
    word_score = {} # will store the relevancy score for each word

    print '**** Loading Pickle ****'

    indeed_word_props = pickle.load( open( "indeed_word_percentages_dict.p", "rb" ) )

    print '**** Calculating Scores ****'
        
    PENALTY_FACTOR = 2
    COMMON_WORD_CUTOFF = .001
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
        if '\n' not in so[0] and so[0].isalpha() and word_score[so[0]] != BAD_SCORE:
            print 'word: ', so[0], 'word count: ', master_wc[so[0]], 'page count', master_pc[so[0]], 'search prop: ', (master_wc[so[0]]/float(num_words)), 'indeed prop: ', indeed_word_props.get(so[0],0), 'score: ', so[1] 
            
            if high_score_flag == 0:
                highest_score = so[1]
                high_score_flag = 1

            skills.append([so[0],np.around(so[1]/float(highest_score), decimals=5)])
            enough_counter+=1
        if enough_counter > 9:
            break

    return skills










