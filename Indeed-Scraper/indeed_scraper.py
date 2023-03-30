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

job_title = "Machine Learning Engineer"
location = "San Francisco, CA"
experience_level = ExperienceLevel.ENTRY_LEVEL
education_level = EducationLevel.BACHELORS_DEGREE
job_type = JobType.FULLTIME

class IndeedScraper:
    ''' Class to scrape indeed.com for jobs '''
    
    def __init__(self, headless=False) -> None:
        self.scrape_finished = False
        self.checkpoint = None
        self.Init(headless)
    
    def Init(self, headless=False):
        ''' create webdriver object
            install chromium driver if not installed
            set to headless mode '''
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=chrome_options)
    
    def remove_tags(self, html) -> str:
        '''Function to remove tags from html content'''
    
        # parse html content
        soup = BeautifulSoup(html, "html.parser")
    
        for data in soup(['style', 'script']):
            # Remove tags
            data.decompose()
    
        # return data by retrieving the tag content
        return ' '.join(soup.stripped_strings)
    
    def build_url(self, job_title, location, experience_level, education_level, job_type):
        return f"""https://www.indeed.com/jobs?q={job_title}&l={location}&sc=0kf:attr({education_level})explvl({experience_level})jt({job_type});"""
    
    def Scrape(self, job_title:str, location:str, experience_level:ExperienceLevel,
               education_level:EducationLevel, job_type:JobType, page:int=0, save_dir:str="data.csv"):
        # get the driver
        driver = self.driver
        # create a checkpoint
        self.checkpoint = [job_title, location, experience_level, education_level, job_type, page, save_dir]
        # build the url
        url = self.build_url(job_title, location, experience_level, education_level, job_type)
        
        # go to indeed.com
        driver.get(quote(url, safe=":/?=&"))
        driver.implicitly_wait(5)

        # create dataframe to store data
        df = pd.DataFrame(columns=["job_id","job_title", "location", "experience",
                                "education", "job_type", "job_description", "job_link"])
        
        curr_page = 0
        next_page_button = 1
        while (next_page_button != None):
            try:
                next_page_button = driver.find_element(By.XPATH, '//*[@data-testid="pagination-page-next"]')
            except:
                next_page_button = None
            
            if (curr_page >= page):
                try:
                    self.ReadJobsOnPage(driver, df)
                except:
                    # save to csv
                    df.to_csv(save_dir)
                    # save checkpoint
                    self.checkpoint = [job_title, location, experience_level,
                                       education_level, job_type, curr_page,
                                       save_dir.replace(".csv", f"_checkpoint_{curr_page}.csv")]
                    driver.close()
                    self.Init()
                    self.scrape_finished = False
                    return
            
            if (next_page_button != None):
                next_page_button.click()
                driver.implicitly_wait(5)
            curr_page += 1
        # save to csv
        df.to_csv(save_dir)
        self.scrape_finished = True
    
    def ReadJobsOnPage(self, driver, df):
        # Get a list of all job ids on the page
            list_of_jobs = [x.get_attribute('data-jk') for x in driver.find_element(By.CLASS_NAME, "jobsearch-ResultsList")\
                                                                .find_elements(By.CLASS_NAME, "jcs-JobTitle")]
            for job in list_of_jobs:
                # Click on the job
                driver.find_element(By.XPATH, f'//*[@data-jk="{job}"]').click()
                driver.implicitly_wait(5)
                time.sleep(randint(1, 4))
                # get div by XML path
                elem = driver.find_element(By.ID,"jobsearch-ViewjobPaneWrapper")
                elem2 = elem.find_element(By.TAG_NAME, "div")
                df.loc[len(df)] = [job, job_title, location, experience_level, education_level,
                                job_type, self.remove_tags(elem2.get_attribute("innerHTML")), driver.current_url]
    
    def ScrapeCombos(self, job_title:list, location:list, experience_level:list,
                     education_level:list, job_type:list, save_dir:str):
        ''' Scrape all combinations of experience, education, and job type '''
        save_dir_stripped = save_dir.replace(".csv", "")
        for job in job_title:
            for loc in location:
                for exp in experience_level:
                    for edu in education_level:
                        for job_t in job_type:
                            edu_mapped = EducationLevelMap[edu]
                            save_dir = f"{save_dir_stripped}_{job}_{loc}_{exp}_{edu}_{job_t}.csv"
                            self.Scrape(job, loc, exp, edu_mapped, job_t, 0, save_dir)
                            if (self.scrape_finished == False):
                                self.Scrape(*self.checkpoint)
                                self.scrape_finished = True
                            # if finished_job.txt does not exist, create it
                            if (not os.path.exists("finished_jobs.txt")):
                                with open("finished_jobs.txt", "w") as f:
                                    f.write("")
                            # save to file current finished job
                            with open("finished_jobs.txt", "a") as f:
                                f.write(f"{job}_{loc}_{exp}_{edu}_{job_t}.csv")