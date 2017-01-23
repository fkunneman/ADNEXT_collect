# python json2xml_fb.py  NL_GIST_forum
# Suzan Verberne
import re

class Forum:
    def __init__ (self,forum_id,name,description):
        self.forum_id = forum_id
        self.name = name
        self.description = description

    def addThread(self,thread):
        self.threads.append(thread)

    def getNrOfThreads(self):
        return len(self.threads)

    def printXML(self,out):
        out.write('<forum type="bb" id="'+self.forum_id+'>\n')
        out.write('<name>'+self.name+'</name>')
        out.write('<description>'+self.description+'</description>')
        for thread in self.threads:
            thread.printXML(out)
        out.write('</forum>')

class Thread:

    def __init__(self,thread_id,title,category,ttype):
        self.thread_id = thread_id
        self.title = title
        self.posts = []
        self.category = category
        self.ttype = ttype

    def addPost(self,post):
        self.posts.append(post)

    def getNrOfPosts(self):
        return len(self.posts)

    def strip_duplicates(self):
        postdict = {}
        for post in self.posts:
            postdict[post.postid] = post
        self.posts = postdict.values()

    def sort_posts(self):
        self.posts = sorted(self.posts, key = lambda k : k.index)

    def printXML(self,out):
        self.strip_duplicates()
        self.sort_posts()
        out.write("<thread id=\""+self.thread_id+"\">\n<category>"+self.category+"</category>\n<title>"+self.title+"</title>\n<posts>\n")
        for post in self.posts:
            post.clean_body()
            post.printXML(out)
        out.write("</posts>\n</thread>\n")


class Post:
    postid=""
    author=""
    timestamp=""
    body=""
    parent_id=""

    def __init__(self,postid,author,timestamp,body,index,parentid,ups,downs):
        self.postid = postid
        self.author = author
        self.timestamp = timestamp
        self.body = body
        self.index = index
        self.parentid = parentid
        self.ups = ups
        self.downs = downs

    def clean_body(self):
        for i, paragraph in enumerate(self.body):
            #print('BEFORE', paragraph.encode('cp1252'))
            paragraph = re.sub('&amp#39;','\'',paragraph)
            #print(paragraph.encode('cp1252'))
            self.body[i] = re.sub('&amp#39;','\'',paragraph)
#'&amp;#39;'
#            self.body[i] = re.sub('&amp;#33;','!',paragraph)
#            self.body[i] = re.sub("#","&#35;",paragraph)
#            self.body[i] = re.sub("&","&amp;",paragraph)
#            self.body[i] = re.sub("<","&lt;",paragraph)
#            self.body[i] = re.sub(">","&gt;",paragraph)
#            self.body[i] = re.sub("=","&#61;",paragraph)
#            self.body[i] = re.sub("http[^ ]*","[URL]",paragraph)
 #           print('AFTER', paragraph.encode('iso-8859-1'))


    def printXML(self,out):
        out.write("<post id=\""+self.postid+"\">\n<author>"+self.author+"</author>\n<timestamp>"+str(self.timestamp)+"</timestamp>\n<postindex>"+str(self.index)+"</postindex>\n<parentid>"+self.parentid+"</parentid>\n<body>\n")
        for paragraph in self.body:
            out.write("<paragraph>"+paragraph+"</paragraph>\n")
        out.write("</body>\n<upvotes>"+str(self.ups)+"</upvotes>\n<downvotes>"+str(self.downs)+"</downvotes>\n</post>\n")
