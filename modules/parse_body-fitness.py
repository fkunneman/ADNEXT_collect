
import os
import sys
from bs4 import BeautifulSoup
import re
from collections import defaultdict

from forum_xml_classes import Forum, Thread, Post

def postbody2paragraphs(postbody):
    paragraphs = re.split(r'\s{2,}',postbody)
    return paragraphs

def clean_text(raw_text):
    cleaned_text = re.sub(r'<[^>]+>', '', raw_text)
    cleaned_text = re.sub(r' {2,}', ' ', cleaned_text)
    return cleaned_text.strip()

def parse_author(pa):
    author_souped = BeautifulSoup(pa.__str__(), 'html.parser')
    #authorname = author_souped.find_all('span', {'class':'left msgLabel tmUserTitle '})[0].text
    for div in author_souped.find_all('div'):
        if div['class'][0] == 'left':
            authorname = div.text.split()[0]
    #print(author_souped.attrs, author_souped.contents)
    return authorname

def parse_postbody(pb):
    body_souped = BeautifulSoup(pb.__str__(), 'html.parser')
    #print(body_souped.contents)
    for span in body_souped.find_all('span'):
        if span.has_attr('id'):
            if re.match(r'^msgNum\d+',span['id']):
                index = int(span['id'][6:])
        if span.has_attr('class'):
            if span['class'][0] == 'performdateformat':
                datetime = span.text
    text = body_souped.find_all('div', {"class":"msgSection"})[0].text.strip()
    paragraphs = postbody2paragraphs(text)
    #datetime = body_souped.find_all('span', {"class":"performdateformat"})[0].text

    #     print('SPAN',span.contents)
    return index, paragraphs, datetime

def parse_post(post):

    post_souped = BeautifulSoup(post.__str__(), 'html.parser')
    parent = '-'
    pid = post['id'][3:]
    author = post_souped.find_all('div', {'class':'essentialAuthorLine'})[0]
    authorname = parse_author(author)
    postbody = post_souped.find_all('div', {'class':'item essential msgcontent'})[0]
    index, text, datetime = parse_postbody(postbody)
    post = Post(pid, authorname, datetime, text, index, '-', '-', '-')
    return post

def parse_thread(thr):

    posts = []
    souped = BeautifulSoup(thr, 'html.parser')
    for message in souped.find_all('td', { 'class':'msgtable item '}): # message level
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
            thread_details = thread.split('/')[-1].split('.')[0]
            try:
                thread_search = thread_title_match.search(thread_details).groups()
                thread_title = thread_search[0].replace('-',' ').strip()
                thread_id = thread_search[1]
                if thread_search[3] != None:
                    thread_index = thread_search[3]
                else:
                    thread_index = 1
                thread_item = Thread(thread_id, thread_title, '-', '-')
                try:
                    posts = parse_thread(thr_str)
                except:
                    print('Error parsing',thread,'skipping...')
                    continue
                thread_item.posts = posts
                thread_dict[thread_id].append(thread_item)
            except:
                print('Wrongly formed file name',thread,'skipping...')
                continue
	
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
