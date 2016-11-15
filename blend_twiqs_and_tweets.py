
import sys
import operator

import docreader
import linewriter

twiqsfile = sys.argv[1]
tweetsfile = sys.argv[2]
outfile = sys.argv[3]

twiqsorder = {0:1, 1:0, 2:5, 3:6, 4:7, 5:8, 6:2, 7:9, 8:10}
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
headers = ['tweet_id','user_id','user_name','user_followers','user_location','date','time','reply_to_user','retweet_to_user','tweet_url','tweet_text']

#read in files
twiqsdr = docreader.Docreader()
twiqsdr.parse_doc(twiqsfile)
tweetsdr = docreader.Docreader()
tweetsdr.parse_doc(tweetsfile)

print('len tweets',len(tweetsdr.lines),'len twiqs',len(twiqsdr.lines))

tweets = tweetsdr.lines[1:]
tweet_ids = [x[0] for x in tweets]
for twiqs in twiqsdr.lines[1:]:
    if not twiqs[1] in tweet_ids:
        tweetobj = ([''] * 3) + [0] + ([''] * 7)
        for i in twiqsorder.keys():
            tweetobj[twiqsorder[i]] = twiqs[i]
        tweets.append(tweetobj)

tweets = sorted(tweets, key = operator.itemgetter(5, 6))
print('len blend',len(tweets))

lw = linewriter.Linewriter(tweets)
lw.write_xls(headers,header_celltype,outfile)
