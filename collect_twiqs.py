
import sys
import configparser
import datetime

import twiqscollector
import json_tweets_parser
import linewriter

configfile = sys.argv[1]
collectdir = '/'.join(configfile.split('/')[:-1]) + '/'
if collectdir[0] == '/':
    collectdir = ''

cp = configparser.ConfigParser()
cp.read(configfile)

inlog_file = cp['collect']['password_file']
with open(inlog_file) as inf:
    inlog = inf.read().split("\n")
ip = cp['collect']['ip']
tc = twiqscollector.Twiqscollector(inlog, ip)

if cp['collect']['keyterms'] == 'no':
    keyterms = False
else:
    keyterms = cp['collect']['keyterms'].split('|')
    tweetfiles = [collectdir + 'tweets_' + str(i) for i, kt in enumerate(keyterms)] 
    keyterm_tweetfile = dict(zip(keyterms, tweetfiles))
begin = cp['collect']['begin']
end = cp['collect']['end']

formats = cp['collect']['write'].split()
if 'xls' in formats:
    header_celltype = {
        'tweet_id' : 'general',
        'user_id' : 'general',
        'user_name' : 'general',
        'user_followers' : '0',
        'user_location' : 'general',
        'date' : 'dd-mm-yyyy',
        'time' : 'hh:mm:ss',
        'reply_to_user' : 'general',
        'retweet_to_user' : 'general',
        'tweet_url' : 'general',
        'tweet_text' : 'general'
    }
    columns = ['user_id', 'tweet_id', 'date', 'time', 'reply_to_user', 'retweet_to_user', 'user_name', 'tweet_url', 'tweet_text']
    
if keyterms:
    for keyterm in keyterms:
        tweets = tc.process_request(begin, end, keyterm)
        lw = linewriter.Linewriter(tweets)
        if 'xls' in formats:
            lw.write_xls(columns, header_celltype, collectdir + keyterm + '.xls')
        if 'txt' in formats:
            lw.write_txt(collectdir + keyterm + '.txt')
        if 'csv' in formats:
            lw.write_csv(collectdir + keyterm + '.csv')

else: # collect all tweets in time frame
    current = datetime.datetime(int(begin[:4]),int(begin[4:6]),int(begin[6:8]),int(begin[8:]),0,0)
    end = datetime.datetime(int(end[:4]),int(end[4:6]),int(end[6:8]),int(end[8:]),0,0)
    while current <= end:
        year = str(current.year)
        month = str(current.month)
        day = str(current.day)
        hour = str(current.hour)
        if len(month) == 1:
            month = "0" + month
        if len(day) == 1:
            day = "0" + day
        if len(hour) == 1:
            hour = "0" + hour
        timeobj = year + month + day + hour
        tweets = tc.process_request(timeobj, timeobj, 'echtalles')
        tweetlines = [line.split('\t') for line in tweets.split('\t')]
        lw = linewriter.Linewriter(tweetlines)
        if 'xls' in formats:
            lw.write_xls(columns, header_celltype, keyterm_tweetfile[keyterm] + '.xls')
        if 'txt' in formats:
            lw.write_txt(keyterm_tweetfile[keyterm] + '.txt')
        if 'csv' in formats:
            lw.write_csv(keyterm_tweetfile[keyterm] + '.csv')
