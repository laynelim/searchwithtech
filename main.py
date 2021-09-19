import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__) # Create an Instance

# gets an url based on position and location (Indeed)
def get_url_indeed(position, location):
    template = "https://ca.indeed.com/jobs?q={}&l={}"
    template = "https://ca.indeed.com/{}-jobs-in-{}"
    position = position.replace(' ', '-')
    location = location.replace(' ', '-')
    url = template.format(position, location)
    return url

# extract job data from a single record (Indeed)
def get_record_indeed(card):
    try:
        job_title = card.find('h2', 'jobTitle').text
        if job_title[0:3] == 'new':
            job_title = job_title[3:]
    except AttributeError:
        job_title = ''
    try:
        job_url = 'https://ca.indeed.com' + card.get('href')
    except AttributeError:
        job_url = ''
    try:
        company = card.find('span', 'companyName').text
    except AttributeError:
        company = ''
    try:
        job_location = card.find('div', 'companyLocation').text
    except AttributeError:
        job_location = ''
    try:
        job_summary = card.find('div', 'job-snippet').text.strip()
    except AttributeError:
        job_summary = ''
    try:
        post_date = card.find('span', 'date').text
    except AttributeError:
        post_date = ''

    record = (job_title, company, job_location, post_date, job_summary, job_url)
    return record

# gets an url based on position and location (Workopolis)
def get_url_worko(position, location):
    template = "https://www.workopolis.com/jobsearch/find-jobs?ak={}&l={}"
    position = position.replace(' ', '+')
    location = location.replace(' ', '+')
    url = template.format(position, location)
    return url

# extract job data from a single record (Workopolis)
def get_record_worko(card):
    atag = card.h2
    try:
        job_title = atag.get('title')
    except AttributeError:
        job_title = ''
    try:
        job_url = 'https://www.workopolis.com' + atag.find('a')['href']
    except AttributeError:
        job_url = ''
    try:
        company = card.find('div', 'JobCard-property').text.strip()
    except AttributeError:
        company = ''
    try:
        job_location = card.find('span', 'JobCard-property').text.strip()
        job_location = job_location[2:]
    except AttributeError:
        job_location = ''
    try:
        job_summary = card.find('div', 'JobCard-snippet').text.strip()
    except AttributeError:
        job_summary = ''
    try:
        post_date = card.find('time', 'JobCard-property JobCard-age').text
    except AttributeError:
        post_date = ''

    record = (job_title, company, job_location, post_date, job_summary, job_url)
    return record

# Route the Function
@app.route('/', methods=["GET", "POST"])
def main():
  if request.method == "GET":
    return render_template('index.html')
  else:
    return render_template('results.html')

@app.route('/results', methods=["POST"])
def get_results(): # Run the function
    # track job urls to avoid collecting duplicate records
    unique_jobs = set()
    position = request.form['position']
    location = request.form['location']
    records = []

    url = get_url_indeed(position, location)
    while True:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('a', 'tapItem')
        for card in cards:
            record = get_record_indeed(card)
            if not (record[0], record[1]) in unique_jobs:
                records.append(record)
                unique_jobs.add((record[0], record[1]))
        try:
            url = 'https://ca.indeed.com' + soup.find('a', {'aria-label': 'Next'}).get('href')
        except AttributeError:
            break

    url = get_url_worko(position, location)
    while True:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('article', 'JobCard')
        for card in cards:
            record = get_record_worko(card)
            if not (record[0], record[1]) in unique_jobs:
                records.append(record)
                unique_jobs.add((record[0], record[1]))
        try:
            url = 'https://www.workopolis.com' + soup.find('a', {'title': 'Next'}).get('href')
        except AttributeError:
            break

    # Render the template
    return render_template('results.html', records=records) 

# Run the Application (in debug mode)
app.run(host='0.0.0.0', port=5000, debug=True)