
import requests
import time

class Twiqscollector:

    def __init__(self, passwords, ip):
        self.pw = passwords
        self.ip = ip
        self.requestloop = 5
        self.requestwait = 15
        self.get_cookie()

    def get_cookie(self):
        session = requests.Session()
        r = session.post('http://' + self.ip + '/cgi-bin/twitter', data = {'NAME' : self.pw[0], 'PASSWD' : self.pw[1]})
        self.cookie = session.cookies
    
    def request_tweets(self, parameters):
        try:
            retrieve = requests.get('http://' + self.ip + '/cgi-bin/twitter', params = parameters, cookies = self.cookie)
        except:
            retrieve = False
        
        return retrieve

    def process_request(self, begin, end, keyterm):
        payload = {'SEARCH' : keyterm, 'DATE' : begin + "-" + end, 'DOWNLOAD' : True, 'SHOWTWEETS' : True, 'JSON' : True}
        print('fetching', payload['SEARCH'], 'in', payload['DATE'], 'from twiqs')
        output = False
        while not output:
            output = self.request_tweets(payload)
        dumpoutput = '#user_id\t#tweet_id\t#date\t#time\t#reply_to_tweet_id\t#retweet_to_tweet_id\t#user_name\t#tweet\t#DATE=' + \
            payload['DATE'] + '\t#SEARCHTOKEN=' + keyterm + '\n'
        print(dumpoutput)
        if output.text[:1000] == dumpoutput: #If there isn't any tweet try the request again for x times.
            for i in range(0, self.requestloop):
                print('attempt', i)
                output = self.request_tweets(payload)
                while not output:
                    time.sleep(60 * self.requestwait) #Wait for the search done at twiqs.nl before the next request
                    output = self.request_tweets(payload)
                    if output.text != dumpoutput:
                        break

        print('output', output.text)
        return output.text
