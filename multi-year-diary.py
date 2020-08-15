from datetime import date
import json
import os
import sys
import time

from flask import Flask, request, render_template, make_response

from facebook_archive import FacebookArchive, Post


FACEBOOK_ARCHIVE_FILE = None

for d in os.scandir('.'):
    if os.path.basename(d).startswith('facebook-') and os.path.basename(d).endswith('.zip'):
        FACEBOOK_ARCHIVE_FILE = d.name
        print('Facebook archive file "{}" found.'.format(FACEBOOK_ARCHIVE_FILE))
        break

if not FACEBOOK_ARCHIVE_FILE:
    print('facebook-<user>.zip not found.')
    sys.exit(1)

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/diary')
def api_diary():
    month = int(request.args.get('month'))
    day = int(request.args.get('day'))

    if not month:
        month = date.today().month
    if not day:
        day = date.today().day
    
    a = FacebookArchive(FACEBOOK_ARCHIVE_FILE)

    resp = {}
    resp['status'] = "Looking back on month={}, day={}...\n".format(month, day)
    resp['entries'] = []
    for i,p in enumerate(a.posts(month=month, day=day)):
#        print(i)
        if not p.text:
            continue

        r = p.to_dict()
        r['datetime'] = time.strftime('%Y-%m-%d %H:%M:%S', p.timestamp)
        resp['entries'].append(r)
#        print(time.strftime('%Y-%m-%d %H:%M:%S', p.timestamp))
#        print(p.text)
#        print('\n---\n')

    return json.dumps(resp, indent=2)

@app.route('/api/image')
def api_image():
    filename = request.args.get('filename')

    a = FacebookArchive(FACEBOOK_ARCHIVE_FILE)

    if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
        content_type =  'image/jpeg'
    else:
        raise Exception("unsupported image format: {}".format(filename))

    resp = make_response(a.image(filename))
    resp.headers['Content-type'] = content_type
    return resp


import urllib.request
import json

@app.route('/diary')
def diary():
    month = request.args.get('month')
    day = request.args.get('day')
    if not month:
        month = date.today().month
    if not day:
        day = date.today().day
    month = int(month)
    day = int(day)

    url = 'http://localhost:5000/api/diary?month={}&day={}'.format(month, day)
    print(url)

    try:
        with urllib.request.urlopen(url) as response:
            body = json.loads(response.read())
            headers = response.getheaders()
            status = response.getcode()
            print(headers)
            print(status)
    except urllib.error.URLError as ex:
         print(ex.reason)

    month2 = month
    day2 = day + 1
    if day2 > 31 and month2 in (1,3,5,7,8,10):
        month2 += 1
        day2 = 1
    elif day2 > 30 and month2 in (4,6,9,11):
        month2 += 1
        day2 = 1
    elif day2 > 29 and month2 == 2:
        month2 += 1
        day2 = 1
    elif day2 > 31 and month2 == 12:
        month2 = 1
        day2 = 1
    url = 'http://localhost:5000/api/diary?month={}&day={}'.format(month2, day2)
    print(url)

    try:
        with urllib.request.urlopen(url) as response:
            body2 = json.loads(response.read())
            headers = response.getheaders()
            status = response.getcode()
            print(headers)
            print(status)
    except urllib.error.URLError as ex:
         print(ex.reason)

    month1 = month
    day1 = day - 1
    if day1 == 0:
        if month1 in (2,4,6,9,11):
            month1 -= 1
            day1 = 31
        elif month1 in (5,7,10,12):
            month1 -= 1
            day1 = 30
        elif month1 == 3:
            month1 -= 1
            day1 = 29
        elif month1 == 1:
            month1 = 12
            day1 = 31
    url = 'http://localhost:5000/api/diary?month={}&day={}'.format(month1, day1)
    print(url)

    try:
        with urllib.request.urlopen(url) as response:
            body1 = json.loads(response.read())
            headers = response.getheaders()
            status = response.getcode()
            print(headers)
            print(status)
    except urllib.error.URLError as ex:
         print(ex.reason)

    return render_template('diary.html',
                            entries=body['entries'],
                            entries1=body1['entries'],
                            entries2=body2['entries'])


if __name__ == '__main__':
    app.run(host='localhost', port=5000, threaded=True)
