#! /usr/bin/env python

import os
import sys
from collections import defaultdict
import configparser
import json
import re
import time
import io

sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/../functions'))
import tweetcollector
import docreader
import json_tweets_parser
import linewriter

userfile = open(sys.argv[1],"r",encoding = "utf-8")
passwordfile = open(sys.argv[2],"r",encoding = "utf-8")
outdir = sys.argv[3]
resume = int(sys.argv[4]) # 0 or 1
formats = sys.argv[5].split() # give a subset of json, xlsx, txt and csv within quotes, divided by a space

passwords = passwordfile.read().split("\n")
passwordfile.close()
users = [x.strip() for x in userfile.read().split("\n")]
userfile.close()

tc = tweetcollector.Tweetcollector(passwords)
unique_ids = defaultdict(list)
outfiles = [outdir + 'user_' + u for u in users] 
user_outfile = dict(zip(users, outfiles))

if resume:
    for user in users:
        dr = docreader.Docreader()
        unique_ids[user] = [x[0] for x in dr.parse_json(user_outfile[keyterm] + '.json', [['id']])]

if 'xlsx' in formats:
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

while True:
    for user in users:
        # Collect tweets
        tweets = tc.collect_user_timeline(user)
        # identify new tweets
        ids = [tweet["id"] for tweet in tweets]
        new_ids = list(set(ids) - set(unique_ids[keyterm]))
        print(user, ': collected', len(new_ids), 'new_tweets')
        unique_ids[keyterm].extend(new_ids)
        new_tweets = [tweet for tweet in tweets if tweet['id'] in new_ids]
        # append new tweets to json file
        with io.open(keyterm_tweetfile[keyterm] + '.json', 'a', encoding = 'utf-8') as tweetfile:
            for tweet in new_tweets:
                json.dump(tweet, tweetfile, ensure_ascii = False)
                tweetfile.write('\n')
        if write:
            # convert json
            jp = json_tweets_parser.Json_tweets_parser(keyterm_tweetfile[keyterm] + '.json')
            jp.parse()
            jp.convert()
            # write lines
            lw = linewriter.Linewriter(jp.lines)
            if 'xlsx' in formats:
                lw.write_xlsx(jp.columns, header_celltype, keyterm_tweetfile[keyterm] + '.xlsx')
            if 'txt' in formats:
                lw.write_txt(keyterm_tweetfile[keyterm] + '.txt')
            if 'csv' in formats:
                lw.write_csv(keyterm_tweetfile[keyterm] + '.csv')
    print('Sleeping')
    time.sleep(3600)
