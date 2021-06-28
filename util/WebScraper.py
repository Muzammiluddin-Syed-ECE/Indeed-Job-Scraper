import requests
import json
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import time
import io
from Database import insert_list_into_db, print_databases, print_collections, print_everything_in_collection

BASE_URL    = "https://ca.indeed.com/jobs?q=Software%20Engineer"
JOB_URL     = "https://ca.indeed.com/viewjob?jk={}"
JOB_QUERY   = "&vjk={}"
PAGE_QUERY  = "&start={}"

class WebScraper:
    
    BASE_URL    = "https://ca.indeed.com/jobs?"
    JOB_URL     = "https://ca.indeed.com/viewjob?jk={}"
    JOB_QUERY   = "&vjk={}"
    PAGE_QUERY  = "&start={}"
    FILE_NAME   = "job_info.txt"

    def get_response(self, url):
        response = requests.get(url)
        time.sleep(2.5)
        return response

    def get_job_info_from_queries(self, queries={"q":"Software Engineering"}):
        query_suffix = ""
        for key, value in queries.items():
            print(key, value)
            query_suffix += "&{0}={1}".format(key, value)
        
        job_ids = self.get_job_ids_from_url(WebScraper.BASE_URL + query_suffix)
        jobs_info = self.get_job_infos_from_list_of_job_ids(job_ids=job_ids)
        self.export_to_json(job_info_list=jobs_info ,file_name=WebScraper.FILE_NAME)
        return jobs_info

    def migrate_jobs_from_file_to_mongo(self):
        job_list = self.import_from_json(file_name=WebScraper.FILE_NAME)
        insert_list_into_db(job_list)
        for obj in job_list:
            print(str(obj['title']).encode('utf-8'))

    def get_job_ids_from_url(self, url):
        job_ids = []
        url = url + "&start={}"
        previous_jobs = ["ignore_initial_value"]
        current_jobs = []
        num = 0
        while previous_jobs != current_jobs:
            previous_jobs = current_jobs
            page = self.get_response(url.format(num))
            page_soup = BeautifulSoup(page.text, "html.parser")
            current_jobs = self.get_job_ids_from_page(page_soup)
            job_ids = job_ids + current_jobs
            num = num + 10
        return job_ids

    def get_job_ids_from_page(self, soup):
        results = []
        for div in soup.find_all(name="div", attrs={"class":"jobsearch-SerpJobCard"}): 
            results.append(div['data-jk']) 
        return results
        
    def get_job_infos_from_list_of_job_ids(self, job_ids):
        job_infos = []
        for job_id in job_ids:
            url = JOB_URL.format(job_id)
            page = self.get_response(url)
            page_soup = BeautifulSoup(page.text, "html.parser")
            job_infos.append(self.extract_job_information_from_job(page_soup, job_id))
        return job_infos
    
    def extract_job_information_from_job(self, soup, job_id):
        job_info            = {}
        title_div           = soup.find("h1", {"class":"jobsearch-JobInfoHeader-title"})
        subtitle_div        = soup.find("div", {"class":"jobsearch-JobInfoHeader-subtitle"})
        description_div     = soup.find("div", {"class":"jobsearch-jobDescriptionText"})
        
        if title_div:
            job_info["title"]       = title_div.text
        
        if subtitle_div:
            job_info["subtitle"]    = []
            for res in subtitle_div:
                
                for subres in res:
                    if hasattr(subres, 'text'):
                        job_info["subtitle"].append(subres.text)
                    else:
                        job_info["subtitle"].append(res.text)

        if description_div:
            job_info["description"] = description_div.text
        
        job_info["jk"] = job_id

        return job_info

    def export_to_json(self, job_info_list, file_name):
        with open(file_name, "w") as jsonfile:
            json.dump(job_info_list, jsonfile)
    
    def import_from_json(self, file_name):
        with open(file_name, "r") as jsonfile:
            return json.load(jsonfile)
    
        
"""
def get_job_ids(soup):
    results = []
    for div in soup.find_all(name="div", attrs={"class":"jobsearch-SerpJobCard"}): 
        results.append(div['data-jk']) 
    return results

def get_soups(BASE_URL, JOB_QUERY, job_ids):
    num = 0
    while num < len(job_ids):
        URL = BASE_URL + JOB_QUERY
        URL = URL.format(job_ids[num])
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, "html.parser")
        print(URL)
        num += 1
        yield soup
        
    
    
    #specifying a desired format of “page" using the html parser - this allows python to read the various components of the page, rather than treating it as one long string.
    


def extract_job_title_from_result(soup): 
    jobs = []
    for div in soup.find_all(name="div", attrs={"class":"jobsearch-SerpJobCard"}):
        for a in soup.find_all(name="a", attrs={"class":"jobTitle"}):
            jobs.append(a["href"])
            print(a)
        file1.write(div)
    return(jobs)

def extract_urls_from_result(soup):
    urls = []
    mosaics = soup.find_all(name="div", attrs={"class":"mosaic-zone"})
    print(mosaics)
    for link in mosaics[0].find_all(name="a"):
        print("u")
        print(link.get('href'))

def extract_job_information_from_job(soup):
    job_info            = {}
    title_div           = soup.find("h1", {"class":"jobsearch-JobInfoHeader-title"})
    subtitle_div        = soup.find("div", {"class":"jobsearch-JobInfoHeader-subtitle"})
    description_div     = soup.find("div", {"class":"jobsearch-jobDescriptionText"})
    
    if title_div:
        job_info["title"]       = title_div.text
    
    if subtitle_div:
        job_info["subtitle"]    = []
        for res in subtitle_div:
            
            for subres in res:
                print(">>>>>",subres)
                if hasattr(subres, 'text'):
                    job_info["subtitle"].append(subres.text)
                else:
                    job_info["subtitle"].append(res.text)

            
    
    if description_div:
        job_info["description"] = description_div.text
    
    return job_info
           




page = requests.get(BASE_URL)

soup = BeautifulSoup(page.text, "html.parser")

job_ids = get_job_ids(soup=soup)

#print(job_ids) 
if len(job_ids) > 0:
    soup1 = BeautifulSoup(requests.get("https://ca.indeed.com/jobs?q=Software%20Engineer&vjk={}".format(job_ids[0])).text, "html.parser")
    extract_urls_from_result(soup1)
#print(soup1.prettify().encode("utf-8"))


file1 = open("myfile.html","w", encoding="utf-8")
if len(job_ids) > 0:
    for soup in get_soups(BASE_URL=BASE_URL, JOB_QUERY=JOB_QUERY, job_ids=[job_ids[0]]):
        file1.write(soup1.prettify())


jobs_information = []
if len(job_ids) > 0:
    for soup in get_soups(BASE_URL=JOB_URL, JOB_QUERY="", job_ids=job_ids):
        file.write(soup.prettify())
        jobs_information.append(extract_job_information_from_job(soup))

for i in range(len(jobs_information)):
    print(jobs_information[i]['title'])

def stop(i):
    return i > 0

def multiples(of, stop):
    """"""Yields all multiples of given integer.""""""
    x = of
    l = of
    while stop(l):
        print("of",of)
        yield x
        x += of
        l = l - 1

i = 3
for j in multiples(i, stop):
    print(j)
    i = i - 1"""

start = time.time()

print_databases()
print_collections()
print_everything_in_collection()
"""
scraper = WebScraper()
scraper.migrate_jobs_from_file_to_mongo()

list_of_stuff = scraper.get_job_info_from_queries(queries={"q":"Software Engineering"})
print(str(list_of_stuff).encode('utf-8'))"""


end = time.time()
print(f"Runtime: {end - start}")