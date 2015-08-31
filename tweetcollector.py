
import twython

class Tweetcollector:

    def __init__(self, passwords):
        self.pw = passwords

    def connect(self):
        return twython.Twython(self.pw[0], self.pw[1], self.pw[2], self.pw[3])

    def search_keyterm(self, keyterm, language):
        api = self.connect()
        tweets = api.search(q = keyterm, result_type = "mixed", lang = language)["statuses"]
        return tweets