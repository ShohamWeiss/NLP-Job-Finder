from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import unquote, quote
from bs4 import BeautifulSoup
import pandas as pd
import time

# create webdriver object
# set chromium driver path
# set to headless mode
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# TODO: make proper enums
job_title = "Machine Learning Engineer"
location = "San Francisco, CA"
experience_level = "SENIOR_LEVEL"
education_level = {"BACHELORS_DEGREE":"FCGTU|HFDVW|QJZM9|UTPWG%2COR", \
                    "MASTERS_DEGREE":"EXSNN|FCGTU|HFDVW|QJZM9|UTPWG%2COR"}
job_type = "fulltime"

# TODO: make a function to build the url and have fields as optional
# build the url
url = f"""https://www.indeed.com/jobs?q={job_title}&l={location}&sc=0kf:attr({education_level["BACHELORS_DEGREE"]})explvl({experience_level})jt({job_type});"""

# TODO: make a function to run the whole scrape with file destination as optional
# go to indeed.com
driver.get(quote(url, safe=":/?=&"))
driver.implicitly_wait(5)

# Function to remove tags
def remove_tags(html):
 
    # parse html content
    soup = BeautifulSoup(html, "html.parser")
 
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()
 
    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)

df = pd.DataFrame(columns=["Job Title", "Location", "Experience",
                           "Education", "Job Type", "Job Description", "Job Link"])
# TODO: Fix bug of not finding the element
while (driver.find_element(By.XPATH, '//*[@data-testid="pagination-page-next"]') != None):
    list_of_jobs = [x.get_attribute('data-jk') for x in driver.find_element(By.CLASS_NAME, "jobsearch-ResultsList")\
                                                        .find_elements(By.CLASS_NAME, "jcs-JobTitle")]
    for job in list_of_jobs:
        driver.find_element(By.XPATH, f'//*[@data-jk="{job}"]').click()
        driver.implicitly_wait(5)
        time.sleep(2)
        # get div by XML path
        elem = driver.find_element(By.ID,"jobsearch-ViewjobPaneWrapper")
        elem2 = elem.find_element(By.TAG_NAME, "div")
        df.loc[len(df)] = [job_title, location, experience_level, education_level["BACHELORS_DEGREE"],
                           job_type, remove_tags(elem2.get_attribute("innerHTML")), driver.current_url]
    
    next_page = driver.find_element(By.XPATH, '//*[@data-testid="pagination-page-next"]')
    next_page.click()
    driver.implicitly_wait(5)
    
# save to csv
df.to_csv("indeed.csv")