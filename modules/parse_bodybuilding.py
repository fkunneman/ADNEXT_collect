
###############################################################
#  parse_bodybuilding.py
#       by Florian Kunneman
#       http://applejack.science.ru.nl/languagemachines/team/fkunneman/
#       Language Machines
#       Radboud University
#
#       Licensed under GPLv3
#
# This is a Python script for parsing forum pages on the forum.bodybuilding.nl website. 
# Usage: python parse_bodybuilding.py [outputdir] [dir_with_html-pages]/*
#
###############################################################

import os
import sys
from bs4 import BeautifulSoup
import re
from collections import defaultdict

from forum_xml_classes import Forum, Thread, Post

##############################################################
### Parseer functies
##############################################################

"""
Functie die de paragrafen uit een posttekst haalt 

Input:

postbody   : str
"""
def postbody2paragraphs(postbody):
    paragraphs = re.split(r'\s{2,}',postbody)
    return [x for x in paragraphs if (x != '') and (x != '(adsbygoogle = window.adsbygoogle || []).push({});')]

"""
Functie die tekst opschoont door tags en langere stukken whitespace te verwijderen

Input:

raw_text   : str
"""
def clean_text(raw_text):
    cleaned_text = re.sub(r'<[^>]+>', '', raw_text)
    cleaned_text = re.sub(r' {2,}', ' ', cleaned_text)
    return cleaned_text.strip()

"""
Parseer functie die de auteursnaam extraheert uit de auteurssectie van een post

Input:

pa   : BeautifulSoup tag object
"""
def parse_author(pa):
    author_souped = BeautifulSoup(pa.__str__(), 'html.parser')
    for a in author_souped.find_all('a'):
        if a['class'][0] == 'username': # De auteursnaam wordt gegeven in de 'a' tag met klasse 'username'
            authorname = a.text
    return authorname

"""
Parseer functie die de beschikbare informatie extraheert uit de body van een post

Input:

pb   : BeautifulSoup tag object
"""
def parse_postbody(pb):
    body_souped = BeautifulSoup(pb.__str__(), 'html.parser')
    text = body_souped.text # de tekst in deze postbody betreft exclusief het bericht
    paragraphs = postbody2paragraphs(text) # extraheer de paragraven uit de tekst
    return paragraphs

"""
Parseer functie die de beschikbare informatie extraheert uit het onderste gedeelte van een post

Input:

pt   : BeautifulSoup tag object
"""
def parse_posttail(pt):
    tail_souped = BeautifulSoup(pt.__str__(), 'html.parser')
    # extraheer de datum en tijd door te zoeken op tag 'span' en klasse 'DateTime'
    dta = tail_souped.find_all('span', {'class':'DateTime'}) 
    if len(dta) > 0:
        dt_info = dta[0]
        datetime = dt_info['title']
    else:
        datetime = tail_souped.find_all('abbr', {'class':'DateTime'})[0].text
    # identificeer de message index als de inhoud van tag 'a' met klasse 'item muted postNumber hashPermalink OverlayTrigger'
    message_index = tail_souped.find_all('a', {'class':'item muted postNumber hashPermalink OverlayTrigger'})[0].text[1:]
    return datetime, message_index   

"""
Parseer functie die de beschikbare informatie extraheert uit de verschillende componenten van een post

Input:

post   : BeautifulSoup tag object
"""
def parse_post(post):
    post_souped = BeautifulSoup(post.__str__(), 'html.parser') # parseer de tag om hierbinnen verder te zoeken
    parent = '-' # parent informatie is niet beschikbaar, dus altijd '-'
    pid = post['id'][5:] # het id staat in de tag 'id'
    a1 = post_souped.find_all('div', {'class':'messageUserBlock '}) # auteursinfo staat in de div-tag met klasse 'messageUserBlock'
    if len(a1) > 0:
        author = a1[0]
    else:
        author = post_souped.find_all('div', {'class':'messageUserBlock online'}) # alternatieve tag
    authorname = parse_author(author) # extraheer de username met de functie 'parse_author'
    postbody = post_souped.find_all('div', {'class':'messageContent'})[0] # het hoofddeel is binnen deze tag te vinden
    text = parse_postbody(postbody)
    posttail = post_souped.find_all('div', {'class':'messageMeta ToggleTriggerAnchor'})[0] # ook de tail bevat nog nuttige informatie, de datum en index
    dt, tid = parse_posttail(posttail)
    # maak een Post-object aan met de opgehaalde informatie; niet alle informatie is beschikbaar (parentid, upvotes en downvotes blijven leeg)
    post = Post(pid, authorname, dt, text, tid, '-', '-', '-')
    return post

"""
Parseer functie die een hele pagina doorloopt.
Gaat alle posts af en extraheert de verschillende informatie-eenheden.  

Input:

thr    : str object
"""
def parse_thread(thr):
    posts = [] # initieer een lijst met posts
    souped = BeautifulSoup(thr, 'html.parser') # Gebruik Beautifulsoup om de html te parseren 
    for message in souped.find_all('li', { 'class':'message   '}): # loop langs de losse berichten
        posts.append(parse_post(message)) # extraheer de beschikbare informatie uit deze berichten
    return posts

##############################################################
### Input
##############################################################

outdir = sys.argv[1] # directory om de output naar weg te schrijven
threads = sys.argv[2:] # alle pagina's die je wil parseren, gedownload van het web


##############################################################
### Procedure
##############################################################

forum_name = 'Bodybuilding'

# maak een dictionary aan om threads te koppelen aan geparseerde posts; 
# een thread kan uit meerdere pagina's bestaan, en we willen de posts van de verschillende pagina's op deze manier bij elkaar brengen
thread_dict = defaultdict(list)
for thread in threads: # doorloop alle bestanden
    if os.path.exists(thread): # check of het bestand bestaat
        with open(thread, 'r', encoding='iso-8859-1') as t_open:
            thr_str = t_open.read() # lees het in
            # extraheer informatie over de thread
            thread_title = thread.split('/')[-2].split('.')
            thread_name = ''.join(thread_title[:-1])
            thread_id = thread_title[-1]
            thread_details = thread.split('/')[-1].split('.')[0]
            thread_item = Thread(thread_id, thread_name, '-', '-')
            # parseer de thread en sla de posts op
            posts = parse_thread(thr_str)
            thread_item.posts = posts
            thread_dict[thread_id].append(thread_item)

# voor iedere thread
for thread_id in thread_dict.keys():
    thread_items = thread_dict[thread_id]
    thread_complete = Thread(thread_id, thread_items[0].title, '-', '-')
    # combineer de posts
    for ti in thread_items:
        for post in ti.posts:
            thread_complete.addPost(post)
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    # schrijf de threats als XML naar een bestand in de output directory
    out = open(outdir + '/' + thread_id + '.xml', 'w', encoding = 'iso-8859-1', errors = 'replace')
    out.write("<?xml version='1.0' encoding='iso-8859-1'?>\n")
    out.write(r"<forum type='forum' name='" + forum_name + "'>\n")
    thread_complete.printXML(out)
    out.write('</forum>\n')
    out.close()
