
import json_tweets_parser
import linewriter
import sys

jsonfile = sys.argv[1]
outputformats = sys.argv[2:] # choose 'xlsx', 'txt' or 'csv' 

jtp = json_tweets_parser.Json_tweets_parser(jsonfile)
jtp.parse()
jtp.convert()

outfile_template = jsonfile[:-5]
lw = linewriter.Linewriter(jtp.lines)
if 'xlsx' in outputformats:
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
    out = outfile_template + '.xlsx'
    lw.write_xls(jtp.columns, header_celltype, out)
if 'txt' in outputformats:
    out = outfile_template + '.txt'
    lw.write_txt(out)
if 'csv' in outputformats:
    out = outfile_template + '.csv'
    lw.write_csv(out)
