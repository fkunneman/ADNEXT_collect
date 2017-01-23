
import requests
import datetime
import time

class Twiqscollector:

    def __init__(self, passwords, ip):
        self.pw = passwords
        self.ip = ip
        self.requestloop = 60
        self.requestwait = 3
        self.get_cookie()

    def get_cookie(self):
        self.session = requests.Session()
        r = self.session.post('http://' + self.ip + '/cgi-bin/twitter', data = {'NAME' : self.pw[0], 'PASSWD' : self.pw[1]})
    
    def request_tweets(self, parameters):
        try:
            retrieve = requests.get('http://' + self.ip + '/cgi-bin/twitter', params = parameters, cookies = self.session.cookies)
        except:
            retrieve = False
        
        return retrieve

    def process_request(self, begin, end, keyterm):
        payload = {'SEARCH' : keyterm, 'DATE' : begin + "-" + end, 'DOWNLOAD' : True, 'SHOWTWEETS' : True}
        print('fetching', payload['SEARCH'], 'in', payload['DATE'], 'from twiqs')
        output = False
        while not output:
            output = self.request_tweets(payload)
        num_lines = len(output.text.split('\n'))
        i = 0
        while num_lines <= 2:
            time.sleep(1800)             
            print(keyterm.encode('utf-8'), 'attempt', i)
            output = self.request_tweets(payload)
            if output:
                num_lines = len(output.text.split('\n'))
            else:
                print('output False')
                return False
                    
        return self.convert_tweets(output.text)

    def convert_tweets(self, output):
        tweetlines = [line.split('\t') for line in output.split('\n')]
        new_tweets = []
        for line in tweetlines[1:]:
            if len(line) == 1 and line[0] == '':
                continue
#            try:
#                print(line)
#            except:
#                continue
            datecol = line[2]
            timecol = line[3]
            usercol = line[6]
            idcol = line[1]
            date = datetime.date(int(datecol[:4]), int(datecol[5:7]), int(datecol[8:]))
            time = datetime.time(int(timecol[:2]), int(timecol[3:5]), int(timecol[6:8]))
            # generate tweet url
            url = 'https://twitter.com/' + usercol + '/status/' + idcol
            # assemble new line and add to new lines
            new_tweets.append([line[1],line[0],usercol,0,'-',date,time,line[4],line[5],url,line[7]])
        return new_tweets
