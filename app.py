import flask
from flask_cors import CORS

app = flask.Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

app.config["DEBUG"] = True
from bs4 import BeautifulSoup
import requests
from flask import request, jsonify
import datetime
import time
from datetime import date
import re
from collections import defaultdict, OrderedDict

def downloadUserPage(username):
    URL = "https://www.codechef.com/users/" + username
    web_page = None

    try:
        web_page = requests.get(URL,headers={'User-Agent': 'Mozilla/5.0'})
    except IOError:
        raise IOError('Cannot connect to codechef.com')

    for response in web_page.history:
        if response.status_code == 302:
            raise Exception('User not found.')

    return BeautifulSoup(web_page.content, 'html5lib')

def downloadRecentActivity(username, pageno):
    URL = "https://www.codechef.com/recent/user?user_handle=" + username +"&page="+str(pageno)
    web_page = None
    try:
        web_page = requests.get(URL,headers={'User-Agent': 'Mozilla/5.0'})
    except IOError:
        raise IOError('Cannot connect to codechef.com')

    for response in web_page.history:
        if response.status_code == 302:
            raise Exception('User not found.')

    return BeautifulSoup(web_page.content, 'html5lib')

@app.route('/', methods=['GET'])
def home():

    if not 'username' in request.args:
        return jsonify([{'error': 'No username in params'}])
    username = request.args['username']
    soupUser = downloadUserPage(username)
    soupRecent = downloadRecentActivity(username, 0)
    maxPage = int(soupRecent(text=re.compile('max_page'))[0][12:soupRecent(text=re.compile('max_page'))[0].find(',')])
    print(maxPage)
    # tds = trs[0].find_all('td')
    #print(tds[0].text)
    #print(table.prettify())
    rating = soupUser.find('div',class_='rating-number').text
    page = 0
    today = date.today()
    today.strftime("%d/%m/%Y")
    today = str(today)
    solvedToday = set()
    fullySolved = int(soupUser(text=re.compile('Fully Solved'))[0][14:soupUser(text=re.compile('Fully Solved'))[0].find(')')])
    partiallySolved = int(soupUser(text=re.compile('Partially Solved'))[0][18:soupUser(text=re.compile('Partially Solved'))[0].find(')')])
    print(partiallySolved)
    #fullySolved = int()
    submissionsToday = 0
    submissions = []
    while page<=min(5,maxPage):
        table = soupRecent.find('table')
        trs = table.tbody.findAll('tr')
        for ele in trs:
            data = {}
            tds = ele.findAll('td')
            data['time'] = tds[0].text
            probDate = tds[0].text[9:]
            if tds[0].text.find('hours ago')!=-1:
                submissionsToday+=1
                if tds[2].find('span').title!="wrong answer":
                    solvedToday.add(tds[1])
            # if probDate[:2]==today[:2] and probDate[4:6]==today[3:5] and probDate[8:]==today[8:]:
            #     solvedToday+=1
            data['code'] = tds[1].text
            if tds[2].find('span') and (tds[2].find('span').text.find('pts')!=-1):
                data['solved'] = True
            else:
                data['solved'] = False

            submissions.append(data)
        print(page)
        page+=1
        soupRecent = downloadRecentActivity(username, page)
    
    submissionsTimeline = OrderedDict()
    solvedTimeline = OrderedDict()
    for ele in submissions:
        #print(submissionsTimeline)
        if not ele['time'][9:21] in submissionsTimeline:
            submissionsTimeline[ele['time'][9:21]] = 1
        else:
            submissionsTimeline[ele['time'][9:21]]+=1
        if ele['solved']:
            if not ele['time'][9:21] in solvedTimeline:
                solvedTimeline[ele['time'][9:21]] = 1
            else:
                solvedTimeline[ele['time'][9:21]]+=1
    result = [{
        'username': username,
        'rating': rating,
        'submissions': submissions,
        'submissionsToday': submissionsToday,
        'solvedToday': len(solvedToday),
        'fullySolved': fullySolved,
        'partiallySolved': partiallySolved,
        'submissionsTimeline': submissionsTimeline,
        'solvedTimeline': solvedTimeline
    }]
    return jsonify(result)

#app.run()