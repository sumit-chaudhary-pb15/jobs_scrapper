import requests
from bs4 import BeautifulSoup

import pandas as pd
import re
import datetime

headers = {
    "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}

skill = 'data science'
place = 'mumbai, maharastra'
no_of_pages = 50

indeed_posts = []

for page in range(no_of_pages):
    url = 'https://www.indeed.co.in/jobs?q=' + skill + \
          '&l=' + place + '&sort=date' + '&start=' + str(page * 10)
    response = requests.get(url, headers=headers, verify=False)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    outer_most_point = soup.find('div', attrs={'id': 'mosaic-provider-jobcards'})
    for i in outer_most_point:
        job_title = i.find('h2', {'class': 'jobTitle jobTitle-newJob css-bdjp2m eu4oa1w0'})
        if job_title != None:
            jobs = job_title.find('span').text

        if i.find('span', {'class': 'companyName'}) != None:
            company = i.find('span', {'class': 'companyName'}).text

        if i.find('a') != None:
            links = i.find('a', {'class': 'jcs-JobTitle'})['href']

        if i.find('div', {'class': 'attribute_snippet'}) != None:
            salary = i.find('div', {'class': 'attribute_snippet'}).text
        else:
            salary = 'No Salary'

        if i.find('span', attrs={'class': 'date'}) != None:
            post_date = i.find('span', attrs={'class': 'date'}).text

        indeed_posts.append([company, jobs, links, salary, post_date])

indeed_spec = ['Company', 'job', 'link', 'Salary', 'Job_Posted_Date']
df = pd.DataFrame(indeed_posts, columns=indeed_spec)


def get_date(job_date):
    if re.findall(r'[0-9]', job_date):
        b = ''.join(re.findall(r'[0-9]', job_date))
        return (datetime.datetime.today() - datetime.timedelta(int(b))).strftime("%d-%m-%Y")
    else:
        return datetime.datetime.today().strftime("%d-%m-%Y")


df['job_post_date'] = df['Job_Posted_Date'].apply(get_date)


def get_job_description(link):
    url_href = 'https://in.indeed.com' + link
    response_ = requests.get(url_href, headers=headers, verify=False)
    html_ = response_.text
    soup_ = BeautifulSoup(html_, 'html')

    for ii in soup_.find('div', {'class': 'jobsearch-jobDescriptionText'}):
        try:
            return ''.join(ii.text.strip())
        except AttributeError:
            return ''


df['job_description'] = df['link'].apply(get_job_description)


def correct_salary(text):
    return text if '₹' in text else 'No Salary'


df['salary'] = df['Salary'].apply(correct_salary)

df.drop_duplicates(inplace=True)

df.to_excel("indeed_data.xlsx", index=False)
