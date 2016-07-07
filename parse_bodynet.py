
import sys
from bs4 import BeautifulSoup
import re
from collections import defaultdict

from forum_xml_classes import Forum, Thread, Post

def parse_posthead(ph):

    for c in ph.children:
        ph_souped = BeautifulSoup(c.__str__(), 'html.parser')
        for span in ph_souped.find_all('span'):
            if 'class' in span.attrs:
                if span['class'][0] == 'date':
                    date = span.contents[0].split(',')[0]
                elif span['class'][0] == 'time':
                    time = span.contents[0]
                elif span['class'][0] == 'nodecontrols':
                    nc_souped = BeautifulSoup(span.__str__(), 'html.parser')
                    url = nc_souped.a['href']
                    key = nc_souped.a['name'][4:] # to maintain only the number
                    index = int(nc_souped.a.contents[0][1:])
    return date + ' ' + time, url, key, index

def parse_postdetails(pd):
    pd_souped = BeautifulSoup(pd.__str__(), 'html.parser')
    for a in pd_souped.find_all('a'):
        user = a['href'].split('/')[-1].split('.html')[0]
    try:
        return user
    except:
        return '-'

def parse_text(raw_text):
    cleaned_text = re.sub(r'<[^>]+>', '', raw_text)
    #cleaned_text = re.sub(r'\n', '', cleaned_text)
    cleaned_text = re.sub(r' {2,}', ' ', cleaned_text)
    return cleaned_text

def parse_postbody(pb):

    pb_souped = BeautifulSoup(pb.__str__(), 'html.parser')
    for div in pb_souped.find_all('div'):
        if 'class' in div.attrs.keys():
            if div['class'][0] == 'content':
                for c in div.contents:
                    if re.search('blockquote', c.__str__()):
                        text = parse_text(c.__str__())
    return text

def parse_thread(thr):

    posts = []
    souped = BeautifulSoup(thr, 'html.parser')
    # for script in souped.find_all('script'):
    #     print(script)
    #     script_souped = BeautifulSoup(script, 'javascript.parser')
    # for link in souped.find_all('link'):
    #     print(link)
    #     if 'rel' in link.attrs.keys():
    #         if link['rel'][0] == 'alternate':
    #             if re.search('forumid', link['href']):
    #                 forumname = link['title']
    #                 forumid = link['href'].split('&')[1].split('=')[1]
    for div in souped.find_all('div'):
        if 'class' in div.attrs.keys():
            if div['class'][0] == 'posthead':
                dt, url, key, index = parse_posthead(div)
            if div['class'][0] == 'postdetails':
                user = parse_postdetails(div)
            elif div['class'][0] == 'postbody':
                text = parse_postbody(div)
                post = Post(key, user, dt, text, index, '-', '-', '-')
                posts.append(post)
    return posts

outdir = sys.argv[1]
forum_name = sys.argv[2]
threads = sys.argv[3:]

thread_dict = defaultdict(list)
for thread in threads:
    with open(thread, 'r', encoding = 'iso-8859-1') as t_open:
        thr_str = t_open.read()

    thread_details = thread.split('/')[-1].split('.')[0].split('-')
    if re.match(r'\d+', thread_details[0]):
        thread_id = thread_details[0]
    else: 
        print('No proper thread id for', thread, ', skipping')
        continue

    if re.match('print', thread_details[-1]):
#        print('page title ends with \"print\", skipping')
        continue
    elif re.search(r'post\d+', thread_details[-1]):
#        print('page title ends with \"post\", skipping')
        continue
    elif re.match(r'$\d+^', thread_details[-1]):
        thread_index = int(thread_details[-1])
        thread_title = ' '.join(thread_details[1:-1])
    else:
        thread_index = 1
        thread_title = ' '.join(thread_details[1:])
    thread_item = Thread(thread_id, thread_title, '-', '-')

    posts = parse_thread(thr_str)
    thread_item.posts = posts
    thread_dict[thread_id].append(thread_item)

print('Writing xml')
for thread_id in thread_dict.keys():
    print('WRITE thread_id', outdir, thread_id)
    thread_items = thread_dict[thread_id]
    thread_complete = Thread(thread_id, thread_items[0].title, '-', '-')
    for ti in thread_items:
        for post in ti.posts:
            thread_complete.addPost(post)
    try:   
        out = open(outdir + '/' + thread_id + '.xml', 'w', encoding = 'iso-8859-1')
        out.write("<?xml version='1.0' encoding='iso-8859-1'?>\n")
        out.write(r"<forum type='forum' name='" + forum_name + "'>\n")
        thread_complete.printXML(out)
        out.write('</forum>\n')
        out.close()
    except UnicodeEncodeError:
        try:
            out = open(outdir + '/' + thread_id + '.xml', 'w', encoding = 'cp1252')
            out.write("<?xml version='1.0' encoding='iso-8859-1'?>\n")
            out.write(r"<forum type='forum' name='" + forum_name + "'>\n")
            thread_complete.printXML(out)
            out.write('</forum>\n')
            out.close()
        except UnicodeEncodeError:
            out = open(outdir + '/' + thread_id + '.xml', 'w', encoding = 'utf-8', errors = 'ignore')
            out.write("<?xml version='1.0' encoding='iso-8859-1'?>\n")
            out.write(r"<forum type='forum' name='" + forum_name + "'>\n")
            thread_complete.printXML(out)
            out.write('</forum>\n')
            out.close()
