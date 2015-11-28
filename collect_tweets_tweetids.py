#!/usr/bin/env 

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

#for infile in infiles:
#    print(infile)
with open(infile, 'r', encoding = 'utf-8') as idfile:
    ids = idfile.read().split('\n')

tweets = []
for i, tid in enumerate(ids):
    tweet = twitter_devs3.return_tweet(api, tid)
    if not tweet:
        time.sleep(1801)
        tweet = twitter_devs3.return_tweet(api, tid)
        if not tweet:
            print('Failure to collect this tweet two times, probably the tweet has been removed or the account has been closed')
            continue
    tweets.append(tweet)

with open(outfile, 'w', encoding = 'utf-8') as out_w:
    for tweet in tweets:
        out_w.write('\t'.join(tweet) + '\n')
