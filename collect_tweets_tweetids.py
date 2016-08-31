#!/usr/bin/env 
###################################


import sys
import json
import configparser

import tweetcollector
import json_tweets_parser
import linewriter

configfile = sys.argv[1]
collectdir = '/'.join(configfile.split('/')[:-1]) + '/'

cp = configparser.ConfigParser()
cp.read(configfile)

password_file = cp['collect']['password_file']
with open(password_file) as pw:
    passwords = pw.read().split("\n")

idfile = cp['collect']['idfile']
outfile = cp['collect']['outfile']
jsonfile = outfile + '.json'
sparefile = cp['collect']['spare']
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

with open(idfile) as id_in:
    ids = id_in.read().split('\n')

tc = tweetcollector.Tweetcollector(passwords)

# if tweets have already been collected, extract their ids from the jsonfile and the sparefile
if cp['collect'].getboolean('resume'):
    jp = json_tweets_parser.Json_tweets_parser(jsonfile)
    jp.parse()
    jp.convert()
    collected_ids = [tweet[0] for tweet in jp.lines]
    with open(sparefile) as spare_in:
        spare_ids = spare_in.read().split('\n')
    past_ids = list(set(collected_ids) + set(spare_ids))
    print('Start ids:', len(ids), '; seen ids:', len(past_ids))
    ids = list(set(ids) - set(past_ids))
    print('Ids to go:', len(ids))

# start tweet collection
tweets = []
not_collected = []
rate = 0
for i, tid in enumerate(ids):
    print('Collecting tweet for id', i, 'of', len(ids))
    tweet = tweetcollector.collect_tweet_tweetid(tid)
    if not tweet:
        if rate > 180:
            # print intermediary output
            with io.open(jsonfile, 'a', encoding = 'utf-8') as tweetfile:
                for tweet in new_tweets:
                    json.dump(tweet, tweetfile, ensure_ascii = False)
                    tweetfile.write('\n')
            jp = json_tweets_parser.Json_tweets_parser(jsonfile)
            jp.parse()
            jp.convert()
            lw = linewriter.Linewriter(jp.lines)
            if 'xls' in formats:
                lw.write_xls(jp.columns, header_celltype, outfile + '.xls')
            if 'txt' in formats:
                lw.write_txt(outfile + '.txt')
            if 'csv' in formats:
                lw.write_csv(outfile + '.csv')
            with open(sparefile, 'a', encoding = 'utf-8') as spare_w:
                spare_w.write('\n'.join(not_collected))
            # resetting cursors
            tweets = []
            rate = 0
            print('Rate limit probably exceeded. Now sleeping for 15 minutes.')
            time.sleep(900)
            tweet = tweetcollector.collect_tweet_tweetid(tid)
            if not tweet:
                print('Failure to collect this tweet two times, probably the tweet has been removed or the account has been closed.')
                not_collected.append(tid)
                continue
        else:
            print('Bad output while within rate limit, continuing to next tweet id.')
            not_collected.append(tid)
            continue
    rate += 1
    tweets.append(tweet)

with io.open(jsonfile, 'a', encoding = 'utf-8') as tweetfile:
    for tweet in new_tweets:
        json.dump(tweet, tweetfile, ensure_ascii = False)
        tweetfile.write('\n')
jp = json_tweets_parser.Json_tweets_parser(jsonfile)
jp.parse()
jp.convert()
lw = linewriter.Linewriter(jp.lines)
if 'xls' in formats:
    lw.write_xls(jp.columns, header_celltype, outfile + '.xls')
if 'txt' in formats:
    lw.write_txt(outfile + '.txt')
if 'csv' in formats:
    lw.write_csv(outfile + '.csv')
with open(sparefile, 'a', encoding = 'utf-8') as spare_w:
    spare_w.write('\n'.join(not_collected))
