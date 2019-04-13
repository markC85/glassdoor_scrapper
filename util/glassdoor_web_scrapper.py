# -*- coding: utf-8 -*-
'''
Created on Jan 15, 2019

Author: Mark Conrad

Description: Scrapping data from Glassdoor for jobs
'''
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import random
import pickle
from pprint import pprint
import os
import datetime

    
def search_jobs(driver, job_title_input, location_input):
    '''
    Enter query terms into search box and run job search
    '''
    #add the job title varible
    job_title = driver.find_element_by_id("sc.keyword")
    job_title.send_keys(job_title_input)
    
    #add the location varible
    location = driver.find_element_by_id("sc.location")
    location.clear()
    
    #click the search button
    location.send_keys(location_input)
    driver.find_element_by_id("HeroSearchButton").click()

def close_popup(driver):
    '''
    This will try and close the pop up about creating job alerts
    '''
    try:
        driver.find_element_by_class_name("ModalStyle__xBtn___34qya").click()
    except:
        pass

def read_listings(driver, listings, idx, results):
    '''
    take a list of job listings and record the title, company name, location, and description in a dictionary.
    Return the dictionary and an index representing the number of job listings stored
    '''
    for listing in listings:
        print '\n>> looking at listing %i'%idx
        #check for the pop-up
        close_popup(driver)
        #for listing in listings also running into odd characters so I am runing a utf8 encoder on the text:
        #get the job title
        title = listing.find_element_by_css_selector(".flexbox.jobTitle").text.encode('utf8')
        
        #get the company name
        company = listing.find_element_by_css_selector(".flexbox.empLoc").text.encode('utf8')
        
        #get salary
        try:
            payRange = listing.find_element_by_css_selector(".green.small").text.encode('utf8')
        except:
            payRange = None
        
        listing.click()
        sleep(5)
        sleep(random.randint(5,10))
        
        #check for the pop-up
        close_popup(driver)
        
        #get the description
        description = driver.find_element_by_css_selector(".jobDescriptionContent.desc").text.encode('utf8')
        
        results[idx] =  {
            'title' : title,
            'company' : company,
            'pay_range' : payRange,
            'description' : description,
            }
        idx += 1
        print ">> Just scraped",title
        
    return idx, results

def find_glassdoor_jobs():
    #start the script timer
    startTime = datetime.datetime.now()
    
    #create the driver
    chromeDriverPath = os.path.dirname(os.path.realpath(__file__))+'\\chromedriver.exe'
    url = 'https://www.glassdoor.com/sitedirectory/title-jobs.htm'
    
    #launch the chrome driver
    driver = webdriver.Chrome(chromeDriverPath)
    
    #tell the driver to wait 30 seconds before trying to find element on a web page
    driver.implicitly_wait(30)
    #go to the URL for the driver
    driver.get(url)
    
    #define job posting search varibles
    job_title_input = 'Animator'
    location_input = 'Los Angeles, CA'
    
    #start the url
    driver.get(url)
    
    
    #search for animation jobs on glassdoor
    search_jobs(driver, job_title_input, location_input)
    
    #start looping through the job posts
    idx = 1
    results = {}
    jobCount = int(driver.find_element_by_class_name("jobsCount").text[:-5].replace(',',''))
    results['jobs_found']=jobCount
    print '>> Number of jobs found',jobCount
    
    #get all the listing on the site
    listings = driver.find_elements_by_class_name("jl")
    
    while True:
        #let user know the scraping has started
        print ">> Starting Job Scraping"
        
        #find job listing elements on web page
        listings = driver.find_elements_by_class_name("jl")
        
        #read through job listings and store index and results
        idx, results = read_listings(driver, listings, idx, results)
        
        
        #find "next" button to go to next page of job listings
        next_btn = driver.find_element_by_class_name("next")
        
        #if the job listing index is higher than the total number of job postings found from the search, finish the search
        if idx > jobCount:
            print ">> end of search, final index: %i"%idx
            break
        else:
            if not driver.find_element_by_class_name("next").find_elements_by_class_name("disabled "):
                #click the next button
                next_btn.click()
                
                #tell webdriver to wait until it finds the job listing elements on the new page
                WebDriverWait(driver, 100).until(lambda driver: driver.find_elements_by_class_name("jl"))
                
                #let the user know how many job listings have been scraped
                print ">> Finished Web Scraping a page moving onto the next one, new index: %i"%idx
    
    #get the script finish time
    finished = datetime.datetime.now()-startTime
    results['script_run_time']=finished
    print 'Finished Glassdoor script',finished
    
    #pickle results
    pickleFile = os.path.dirname(os.path.realpath(__file__))+'\\glassdoor_scrapping_results.pickle'
    with open(pickleFile, 'wb') as handle:
        pickle.dump(results, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print '>> Pickeled file',pickleFile
    
    #close the driver
    driver.quit()
    
if __name__ == '__main__':
    find_glassdoor_jobs()