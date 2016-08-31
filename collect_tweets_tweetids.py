#!/usr/bin/env 
###################################


import sys
import json
import twitter_devs3
import twython

passwordfile = open(sys.argv[1],encoding="utf-8")
outfile = sys.argv[2]
infile = sys.argv[3]

passwords = passwordfile.read().split("\n")
passwordfile.close()
api = twython.Twython(passwords[0],passwords[1],passwords[2],passwords[3])
out = open(outfile, 'a', encoding = 'utf-8')

with open(infile, 'r', encoding = 'utf-8') as idfile:
    ids = idfile.read().split('\n')

tweets = []
rate = 0
for i, tid in enumerate(ids):
    print('Collecting tweet for id', i, 'of', len(ids))
    tweet = twitter_devs3.return_tweet(api, tid)
    if not tweet:
        if rate > 180:
            with open(outfile, 'a', encoding = 'utf-8') as out_w:
                for tweet in tweets:
                    out_w.write('\t'.join(tweet) + '\n')
            tweets []
            rate = 0
            print('Rate limit probably exceeded. Now sleeping for 15 minutes.')
            time.sleep(1800)
            tweet = twitter_devs3.return_tweet(api, tid)
            if not tweet:
                print('Failure to collect this tweet two times, probably the tweet has been removed or the account has been closed.')
                continue
    rate += 1
    tweets.append(tweet)

