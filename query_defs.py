

import gz
import re
import json
from collections import defaultdict

import coco

def open_gz(filename):
    f = gzip.open(filename,'rb')
    file_content = f.readlines()
    return file_content

def clean_json_tweets(json_tweets):

    # check if last tweet is incomplete, if so: throw away
    erikt = re.compile('}$')
    if not erikt.match(tweets[len(json_tweets)-1]):
        json_tweets.pop()

    # check json tweets and throw away badly formatted and non-dutch tweets
    json_tweets_cleaned = []
    for tweet in json_tweets:
        if not re.match(r'^{', tweet):
            tweet = '{' + '{'.join(tweet.split('{')[1:])
        try:
            decoded = json.loads(tweet)
            if len(decoded.keys()) > 2:
                if ('twinl_lang' in decoded and decoded['twinl_lang'] != 'dutch'):
                    continue
                else:
                    json_tweets_cleaned.append(tweet)
        except:
            print('error occurred at line \n', tweet.encode('utf-8'), 'skipping tweet')
            continue

    return json_tweets_cleaned

def json_tweets2lowercase_text(json_tweets):

    tweets_text = []
    for tweet in json_tweets:
        decoded = json.loads(tweet)
        text = decoded['text'].replace('\n','')   
        tweets_text.append(text.lower())
    return tweets_text

def query_tweets(query_terms, tweets_text, tweets_json, tmpdir):
    """
    Function to query tweets 
    
    parameters
    -----
    query_terms : list
        list of query_terms
    tweets_text : list
        list of tweets, represented as str
    tweets_json : list
        list of original tweets
    tmpdir      : str
        directory to write the temporal coco files to

    returns
    -----
    matches : dict
        dictionary with the query_terms as keys, and a list of the matching json tweets as value
    """
    cc = coco.Coco(tmpdir)
    cc.set_lines(tweets)
    cc.simple_tokenize()
    cc.set_file()
    cc.model_ngramperline(query_terms)
    matches = cc.match(query_terms)

    query_term_matching_tweets = defaultdict(list)
    for k in matches.keys():
        query_term_matching_tweets[k] = [tweets_json[m] for m in matches[k]]

    return query_term_matching_tweets
