
import sys
from collections import defaultdict
import configparser
import json
import re
import time

import tweetcollector
import docreader
import json_tweets_parser
import linewriter

configfile = sys.argv[1]
collectdir = '/'.join(configfile.split('/')[:-1]) + '/'

cp = configparser.ConfigParser()
cp.read(configfile)

password_file = cp['collect']['password_file']
with open(password_file) as pw:
    passwords = pw.read().split("\n")

keyterms = cp['collect']['keyterms'].split()
language = cp['collect']['language']

tc = tweetcollector.Tweetcollector(passwords)
unique_ids = defaultdict(list)
tweetfiles = [collectdir + 'tweets_' + kt for kt in keyterms] 
keyterm_tweetfile = dict(zip(keyterms, tweetfiles))

if cp['collect'].getboolean('resume'):
    for keyterm in keyterms:
        dr = docreader.Docreader()
        unique_ids[keyterm] = [x[0] for x in dr.parse_json(keyterm_tweetfile[keyterm] + '.json', [['id']])]

if cp['collect']['write'] != 'no':
    if cp['collect']['write'] == 'xls':
        write = 'xls'
        header_celltype = {
            'tweet_id' : 'general',
            'user_id' : 'general',
            'user_name' : 'general',
            'user_followers' : '0',
            'user_location' : 'general',
            'date' : 'dd-mm-yy',
            'time' : 'hh:mm:ss',
            'reply_to_user' : 'general',
            'retweet_to_user' : 'general',
            'tweet_text' : 'general'
        }
else:
    write = False

while True:
    for keyterm in keyterms:
        # collect tweets
        tweets = tc.search_keyterm(keyterm, language)
        # identify new tweets
        ids = [tweet["id"] for tweet in tweets]
        new_ids = list(set(ids) - set(unique_ids[keyterm]))
        print(keyterm, ': collected', len(new_ids), 'new_tweets')
        unique_ids[keyterm].extend(new_ids)
        new_tweets = [tweet for tweet in tweets if tweet['id'] in new_ids]
        # append new tweets to json file
        with open(keyterm_tweetfile[keyterm] + '.json', 'a') as tweetfile:
            for tweet in new_tweets:
                json.dump(tweet, tweetfile)
                tweetfile.write('\n')
        if write:
            # convert json
            jp = json_tweets_parser.Json_tweets_parser(keyterm_tweetfile[keyterm] + '.json')
            jp.parse()
            jp.convert()
            # write lines
            lw = linewriter.Linewriter(jp.lines)
            if write == 'xls':
                lw.write_xls(jp.columns, header_celltype, keyterm_tweetfile[keyterm] + '.xls')
    print('Sleeping')
    time.sleep(960)
