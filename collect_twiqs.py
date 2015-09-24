
import sys
import configparser
import datetime

import twiqscollector
import json_tweets_parser
import linewriter

configfile = sys.argv[1]
collectdir = '/'.join(configfile.split('/')[:-1]) + '/'

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
    keyterms = cp['collect']['keyterms'].split()
begin = cp['collect']['begin']
end = cp['collect']['end']
tweetfiles = [collectdir + 'tweets_' + kt for kt in keyterms] 
keyterm_tweetfile = dict(zip(keyterms, tweetfiles))

if cp['collect']['write'] != 'no':
    write = True
    formats = cp['collect']['write']
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
            'tweet_text' : 'general'
        }
else:
    write = False

if keyterms:
    for keyterm in keyterms:
        tweets = process_request(begin, end, keyterm)
        if tweets != "":
            if write:
                # convert json
                jp = json_tweets_parser.Json_tweets_parser(keyterm_tweetfile[keyterm] + '.json')
                jp.parse()
                jp.convert()
                # write lines
                lw = linewriter.Linewriter(jp.lines)
                if 'xls' in formats:
                    lw.write_xls(jp.columns, header_celltype, keyterm_tweetfile[keyterm] + '.xls')
                if 'txt' in formats:
                    lw.write_txt(keyterm_tweetfile[keyterm] + '.txt')
                if 'csv' in formats:
                    lw.write_csv(keyterm_tweetfile[keyterm] + '.csv')
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
        if tweets != "":
            if write:
                # convert json
                jp = json_tweets_parser.Json_tweets_parser(timeobj + '.json')
                jp.parse()
                jp.convert()
                # write lines
                lw = linewriter.Linewriter(jp.lines)
                if 'xls' in formats:
                    lw.write_xls(jp.columns, header_celltype, keyterm_tweetfile[keyterm] + '.xls')
                if 'txt' in formats:
                    lw.write_txt(keyterm_tweetfile[keyterm] + '.txt')
                if 'csv' in formats:
                    lw.write_csv(keyterm_tweetfile[keyterm] + '.csv')
