from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import unquote, quote
from bs4 import BeautifulSoup
import pandas as pd
import time
from search_enums import ExperienceLevel, EducationLevel, JobType, EducationLevelMap
from random import randint
import os
from datetime import datetime

class IndeedScraper:
    ''' Class to scrape indeed.com for jobs '''
    
    def __init__(self, headless=False) -> None:
        self.scrape_finished = False
        self.checkpoint = None
        self.headless = headless
        self.page = -1
        self.Init()
    
    def Init(self):
        ''' create webdriver object
            install chromium driver if not installed
            set to headless mode '''
        self.chrome_options = webdriver.ChromeOptions()
        if self.headless:
            self.chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=self.chrome_options)
    
    def remove_tags(self, html) -> str:
        '''Function to remove tags from html content'''
    
        # parse html content
        soup = BeautifulSoup(html, "html.parser")
    
        for data in soup(['style', 'script']):
            # Remove tags
            data.decompose()
    
        # return data by retrieving the tag content
        return ' '.join(soup.stripped_strings)
    
    def build_url(self, job_title, location, education_level=None, experience_level=None, job_type=None):
        base = f"https://www.indeed.com/jobs?q={job_title}&l={location}"
        query = ""
        if (education_level != None):
            edu_mapped = EducationLevelMap[education_level]
            query += f"attr({edu_mapped})"
        if (experience_level != None):
            query += f"explvl({experience_level})"
        if (job_type != None):
            query += f"jt({job_type})"
        if (query != ""):
            base += f"&sc=0kf:{query};"
        return quote(base, safe=":/?=&")
    
    def Scrape(self, job_title:str, location:str, experience_level:ExperienceLevel,
               education_level:EducationLevel, job_type:JobType, save_dir:str="data.csv",
               on_page=False):
        print("Working on: ", job_title, location, experience_level, education_level, job_type)
        # get the driver
        driver = self.driver
        # create a checkpoint
        self.checkpoint = [job_title, location, experience_level, education_level, job_type, save_dir]
        if (not on_page):
            # build the url
            url = self.build_url(job_title, location, experience_level=experience_level,
                                education_level=education_level, job_type=job_type)
            # go to indeed.com
            driver.get(url)
            driver.implicitly_wait(3)

        # create dataframe to store data
        df = pd.DataFrame(columns=["job_id","job_title", "location", "experience",
                                "education", "job_type", "job_description", "job_link"])
        
        curr_page = 0
        next_page_button = 1
        num_of_jobs = 0
        try:
            num_jobs_elem = driver.find_element(By.CLASS_NAME, 'jobsearch-JobCountAndSortPane-jobCount')
            num_of_jobs = int(num_jobs_elem.text.split(" ")[0])
            print("Number of jobs:", num_jobs_elem.text)
        except:
            print("ERROR: No jobs found")
            self.scrape_finished = False
            return
        while (next_page_button != None):
            if (num_of_jobs > 15):
                try:
                    next_page_button = driver.find_element(By.XPATH, '//*[@data-testid="pagination-page-next"]')
                except:
                    next_page_button = None
            else:
                next_page_button = None
            if (curr_page > self.page):
                try:
                    self.ReadJobsOnPage(driver, df, job_title, location, experience_level, education_level, job_type)
                except:
                    # save to csv
                    if (os.path.exists(save_dir)):
                        df.to_csv(save_dir, mode='a', header=False)
                    else: 
                        df.to_csv(save_dir)
                    # save checkpoint
                    self.checkpoint = [job_title, location, experience_level,
                                       education_level, job_type,
                                       save_dir.replace(".csv", f"_checkpoint_{curr_page}.csv")]
                    self.driver.close()
                    self.Init()
                    self.scrape_finished = False
                    self.page = curr_page
                    return
            else:
                print("skipping page: ", curr_page)
            if (next_page_button != None):
                next_page_button.click()
                driver.implicitly_wait(3)
            curr_page += 1
        # save to csv
        if (os.path.exists(save_dir)):
            df.to_csv(save_dir, mode='a', header=False)
        else: 
            df.to_csv(save_dir)
        self.page = -1
        self.scrape_finished = True
    
    def ReadJobsOnPage(self, driver, df, job_title, location, experience_level, education_level, job_type):
        # Get a list of all job ids on the page
            list_of_jobs = [x.get_attribute('data-jk') for x in driver.find_element(By.CLASS_NAME, "jobsearch-ResultsList")\
                                                                .find_elements(By.CLASS_NAME, "jcs-JobTitle")]
            print("Number of jobs on page: ", len(list_of_jobs))
            for job in list_of_jobs:
                # Click on the job
                driver.find_element(By.XPATH, f'//*[@data-jk="{job}"]').click()
                driver.implicitly_wait(3)
                time.sleep(1)
                # get div by XML path
                elem = driver.find_element(By.ID,"jobsearch-ViewjobPaneWrapper")
                elem2 = elem.find_element(By.TAG_NAME, "div")
                df.loc[len(df)] = [job, job_title, location, experience_level, education_level,
                                job_type, self.remove_tags(elem2.get_attribute("innerHTML")), driver.current_url]
    
    def ScrapeCombos(self, job_title:list, location:list, experience_level:list,
                     education_level:list, job_type:list):
        ''' Scrape all combinations of experience, education, and job type '''
        scraped_files = os.listdir("scraped_data_2")
        for loc in location:
            for job in job_title:
                # Go to indeed.com and search for job title and location
                url = self.build_url(job, loc)
                self.driver.get(url)
                self.driver.implicitly_wait(5)
                options = {"explvl": [], "edulvl": [], "jobtype": []}
                # Check the filters
                try:
                    self.check_filter("explvl", options)
                except:
                    continue
                for exp in list(set(experience_level)&set(options["explvl"])): # intersection
                    url = self.build_url(job, loc, experience_level=exp)
                    self.driver.get(url)
                    self.driver.implicitly_wait(5)
                    try:
                        self.check_filter("edulvl", options)
                    except:
                        continue
                    for edu in list(set(education_level)&set(options["edulvl"])): # intersection
                        url = self.build_url(job, loc, experience_level=exp, education_level=edu)
                        self.driver.get(url)
                        self.driver.implicitly_wait(5)
                        try:
                            self.check_filter("jobtype", options)
                        except:
                            continue
                        for job_t in list(set(job_type)&set(options["jobtype"])): # intersection
                            if (f"{job}_{loc}_{exp}_{edu}_{job_t.lower()}.csv" in scraped_files):
                                print("Catching up on: ", job, loc, exp, edu, job_t)
                                continue
                            save_dir = f"scraped_data_2/{job}_{loc}_{exp}_{edu}_{job_t.lower()}.csv"
                            url = self.build_url(job, loc, experience_level=exp, education_level=edu, job_type=job_t.lower())
                            self.driver.get(url)
                            self.driver.implicitly_wait(5)
                            self.Scrape(job, loc, exp, edu, job_t, save_dir, on_page=True)
                            while (self.scrape_finished == False):
                                url = self.build_url(job, loc, experience_level=exp, education_level=edu, job_type=job_t.lower())
                                self.driver.get(url)
                                self.driver.implicitly_wait(5)
                                print(f"At {datetime.now()} Scrape failed, trying again...")
                                self.Scrape(job, loc, exp, edu, job_t, save_dir, on_page=True)
                            # if finished_job.txt does not exist, create it
                            if (not os.path.exists("finished_jobs.txt")):
                                with open("finished_jobs.txt", "w") as f:
                                    f.write("")
                            # save to file current finished job
                            with open("finished_jobs.txt", "a") as f:
                                f.write(f"{job}_{loc}_{exp}_{edu}_{job_t}.csv")
    
    def check_filter(self, filter, options):
        elem = self.driver.find_element(By.XPATH, f'//*[@id="filter-{filter}-menu"]')
        options[filter] = []
        for li in elem.find_elements(By.TAG_NAME, "li"):
            a = li.find_element(By.TAG_NAME, "a")
            t = a.get_attribute("innerHTML")
            options[filter].append("_".join(t.split(" ")[:-1]) \
                .upper().replace("'", "").replace("-", ""))