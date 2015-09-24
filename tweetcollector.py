
import twython

class Tweetcollector:

    def __init__(self, passwords):
        self.pw = passwords

    def connect(self):
        return twython.Twython(self.pw[0], self.pw[1], self.pw[2], self.pw[3])

    def search_keyterm(self, keyterm, language):
        api = self.connect()
        tweets = api.search(q = keyterm, lang = language, result_type = "mixed", count = 100)["statuses"]
        return tweets

##########TODO##############

    def collect_tweet_id(self, user, id):
        pass

    def collect_user_timeline(self, user):
        pass

    def collect_user_followers(self, user):
        pass
        