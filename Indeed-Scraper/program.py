from indeed_scraper import IndeedScraper
from search_enums import ExperienceLevel, EducationLevel, JobType


if __name__ == "__main__":
    titles = ["Software Engineer", "Machine Learning Engineer","Data Scientist", "Data Analyst", "Data Engineer", "Data Architect"]
    locations = ["Austin, TX", "Dallas, TX", "San Francisco, CA", "San Diego, CA", "Chicago, IL", "Seattle, WA", "Los Angelese, CA"]
    experience_levels = [ExperienceLevel.ENTRY_LEVEL, ExperienceLevel.MID_LEVEL, ExperienceLevel.SENIOR_LEVEL]
    education_level = [EducationLevel.BACHELORS_DEGREE, EducationLevel.MASTERS_DEGREE, EducationLevel.DOCTORAL_DEGREE]
    job_types = [JobType.FULLTIME, JobType.PARTTIME, JobType.CONTRACT, JobType.INTERNSHIP, JobType.TEMPORARY]
    
    indeedScraper = IndeedScraper()
    
    indeedScraper.ScrapeCombos(titles, locations, experience_levels, education_level, job_types)