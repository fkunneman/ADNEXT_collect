

import sys
import os
import configparser
from datetime import datetime, timedelta

import query_defs
import linewriter

configfile = sys.argv[1]
writedir = '/'.join(configfile.split('/')[:-1]) + '/'
if write[0] == '/':
    writedir = ''

cp = configparser.ConfigParser()
cp.read(configfile)

keyterms = cp['collect']['keyterms'].split('|')
tweetfiles = [writedir + 'tweets_' + kt for kt in keyterms] 
keyterm_tweetfile = dict(zip(keyterms, tweetfiles))
begin = cp['collect']['begin']
end = cp['collect']['end']
collectdir = cp['collect']['fromdir']

# collect all tweets with keyterms in time frame
current = datetime(int(begin[:4]),int(begin[4:6]),int(begin[6:8]),int(begin[8:]),0,0)
end = datetime(int(end[:4]),int(end[4:6]),int(end[6:8]),int(end[8:]),0,0)
while current <= end:
    year = str(current.year)
    month = str(current.month)
    day = str(current.day)
    hour = str(current.hour)
    if len(month) == 1:
        month = '0' + month
    if len(day) == 1:
        day = '0' + day
    if len(hour) == 1:
        hour = '0' + hour
    collectfile = collectdir + year + month + '/' + year + month + day + '-' + hour + '.out.gz'
    print(collectfile)
    tmpdir = writedir + 'tmp/'
    os.mkdir(tmpdir)
    content = query_defs.open_gz(collectfile)
    json_tweets_clean = query_defs.clean_json_tweets(content)
    tweets_text = query_defs.json_tweets2lowercase_text(json_tweets_clean):
    matching_tweets = query_defs.query_tweets(keyterms, tweets_text, json_tweets_clean, tmpdir)
    for keyterm in keyterms:
        lines_json = matching_tweets[keyterm]
        outfile = keyterm_tweetfile[keyterm]
        with open(outfile, 'a', encoding = 'utf-8') as tweets_out:
            tweets_out.write('\n'.join(lines_json) + '\n')
    current = current + timedelta(hours = 1)
