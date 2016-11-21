
import os
import sys
from bs4 import BeautifulSoup
import re
from collections import defaultdict

from forum_xml_classes import Forum, Thread, Post

def postbody2paragraphs(postbody):
    paragraphs = re.split(r'\s{2,}',postbody)
    return [x for x in paragraphs if (x != '') and (x != '(adsbygoogle = window.adsbygoogle || []).push({});')]

def clean_text(raw_text):
    cleaned_text = re.sub(r'<[^>]+>', '', raw_text)
    cleaned_text = re.sub(r' {2,}', ' ', cleaned_text)
    return cleaned_text.strip()

def parse_author(pa):
    author_souped = BeautifulSoup(pa.__str__(), 'html.parser')
    #authorname = author_souped.find_all('span', {'class':'left msgLabel tmUserTitle '})[0].text
    for a in author_souped.find_all('a'):
        if a['class'][0] == 'username':
            authorname = a.text
    #print(author_souped.attrs, author_souped.contents)
    return authorname

def parse_postbody(pb):
    body_souped = BeautifulSoup(pb.__str__(), 'html.parser')
    text = body_souped.text
    paragraphs = postbody2paragraphs(text)
    return paragraphs

def parse_posttail(pt):
    tail_souped = BeautifulSoup(pt.__str__(), 'html.parser')
    dt_info = tail_souped.find_all('span', {'class':'DateTime'})[0]
    datetime = dt_info['title']
    message_index = tail_souped.find_all('a', {'class':'item muted postNumber hashPermalink OverlayTrigger'})[0].text[1:]
    return datetime, message_index   

def parse_post(post):

    post_souped = BeautifulSoup(post.__str__(), 'html.parser')
    parent = '-'
    pid = post['id'][5:]
    print('ID',pid)
    author = post_souped.find_all('div', {'class':'messageUserBlock '})[0]
    authorname = parse_author(author)
    print('Authorname',authorname)
    postbody = post_souped.find_all('div', {'class':'messageContent'})[0]
    # index, text, datetime = parse_postbody(postbody)
    text = parse_postbody(postbody)
    print('Text',text)
    posttail = post_souped.find_all('div', {'class':'messageMeta ToggleTriggerAnchor'})[0]
    dt, tid = parse_posttail(posttail)
    print('Datetime',dt)
    print('Message index',tid)
    #post = Post(pid, authorname, datetime, text, index, '-', '-', '-')
    post = Post(pid, authorname, dt, text, tid, '-', '-', '-')
    return post

def parse_thread(thr):

    posts = []
    souped = BeautifulSoup(thr, 'html.parser')
    for message in souped.find_all('li', { 'class':'message   '}): # message level
        posts.append(parse_post(message))

    return posts

outdir = sys.argv[1]
forum_name = sys.argv[2]
threads = sys.argv[3:]

thread_title_match = re.compile(r'(.+)m(\d+)(-p(\d+))?')
id_match = re.compile(r'subject(\d+)')

thread_dict = defaultdict(list)
for thread in threads:
    if os.path.exists(thread):
        with open(thread, 'r', encoding='iso-8859-1') as t_open:
            thr_str = t_open.read()
            thread_title = thread.split('/')[-2].split('.')
            thread_name = ''.join(thread_title[:-1])
            thread_id = thread_title[-1]
            thread_details = thread.split('/')[-1].split('.')[0]
            print(thread,thread_name,thread_id)
            thread_item = Thread(thread_id, thread_title, '-', '-')
            try:
                posts = parse_thread(thr_str)
            except:
                print('Error parsing',thread,'skipping...')
                continue
            thread_item.posts = posts
            thread_dict[thread_id].append(thread_item)

for thread_id in thread_dict.keys():
    thread_items = thread_dict[thread_id]
    thread_complete = Thread(thread_id, thread_items[0].title, '-', '-')
    for ti in thread_items:
        for post in ti.posts:
            thread_complete.addPost(post)
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    out = open(outdir + '/' + thread_id + '.xml', 'w', encoding = 'iso-8859-1', errors = 'replace')
    #out = open(outdir + '/' + thread_id + '.xml', 'w', encoding = 'ascii', errors='ignore')
    out.write("<?xml version='1.0' encoding='iso-8859-1'?>\n")
    out.write(r"<forum type='forum' name='" + forum_name + "'>\n")
    thread_complete.printXML(out)
    out.write('</forum>\n')
    out.close()
