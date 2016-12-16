
import twython

class Tweetcollector:

    def __init__(self, passwords):
        self.pw = passwords

    def connect(self):
        return twython.Twython(self.pw[0], self.pw[1], self.pw[2], self.pw[3])

    def search_keyterm(self, keyterm, language, c=1):
        api = self.connect()
        tweets = api.search(q = keyterm, lang = language, result_type = "recent", count = 100, page = c)["statuses"]
        return tweets

    def collect_user_timeline(self, user):
        api = self.connect()
        no_tweets = False
        tweets_total = []
        c = 1
        while not no_tweets:
            try:
                tweets = api.get_user_timeline(screen_name = user, count = 200, page = c)
                if len(tweets) < 1:
                    no_tweets = True
                else:
                    tweets_total.extend(tweets)
                c += 1
                if c >= 1000:
                    no_tweets = True
            except:
                print('Limit exceeded')
                return [False]
                break

        return tweets_total

    def collect_tweet_id(self, tid):
        api = self.connect()
        try:
            tweet = api.show_status(id = tid)
            return tweet
        except:
            return False

##########TODO##############

    def collect_user_followers(self, user):
        pass
        
