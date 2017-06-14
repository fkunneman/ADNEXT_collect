###############################################################
#  parse_body-fitness.py
#       by Florian Kunneman
#       http://applejack.science.ru.nl/languagemachines/team/fkunneman/
#       Language Machines
#       Radboud University
#
#       Licensed under GPLv3
#
# This is a Python script for parsing forum pages on the forum.body-fitness.nl website. 
# Usage: python parse_body-fitness.py [outputdir] [dir_with_html-pages]/*
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
    paragraphs = re.split(r'\s{2,}',postbody) # paragrafen zijn gedefinieerd als secties onderscheiden door een witregel
    return paragraphs

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
    for div in author_souped.find_all('div'):
        if div['class'][0] == 'left':
            authorname = div.text.split()[0]
    return authorname

"""
Parseer functie die de beschikbare informatie extraheert uit de body van een post

Input:

pb   : BeautifulSoup tag object
"""
def parse_postbody(pb):
    body_souped = BeautifulSoup(pb.__str__(), 'html.parser') # parseer de post-tag om hierbinnen verder te zoeken
    for span in body_souped.find_all('span'): # parseer de post-tag om hierbinnen verder te zoeken
        if span.has_attr('id'):
            if re.match(r'^msgNum\d+',span['id']): # het ID is te vinden met msgNum
                index = int(span['id'][6:]) 
        if span.has_attr('class'):
            if span['class'][0] == 'performdateformat': # de datum en tijd staan binnen de tag met klasse 'performdateformat' 
                datetime = span.text
    text = body_souped.find_all('div', {"class":"msgSection"})[0].text.strip() # de tekst staat binnen de div-tag met klasse 'msgSection'
    paragraphs = postbody2paragraphs(text) # extraheer de paragraven uit de tekst

    return index, paragraphs, datetime

"""
Parseer functie die de beschikbare informatie extraheert uit de verschillende componenten van een post

Input:

post   : BeautifulSoup tag object
"""
def parse_post(post):
    post_souped = BeautifulSoup(post.__str__(), 'html.parser') # parseer de post-tag om hierbinnen verder te zoeken
    parent = '-' # parent informatie is niet beschikbaar, dus altijd '-'
    pid = post['id'][3:] # de identifier van de post is direct uit een attribuut te halen
    author = post_souped.find_all('div', {'class':'essentialAuthorLine'})[0] # het auteursveld
    authorname = parse_author(author) # extraheer de username uit dit veld
    postbody = post_souped.find_all('div', {'class':'item essential msgcontent'})[0] # gedeelte met de tekst en tijd
    index, text, datetime = parse_postbody(postbody) # parseer de informatie uit dit blok
    post = Post(pid, authorname, datetime, text, index, '-', '-', '-') # maak een Post object aan met de geëxtraheerde informatie
    return post

"""
Parseer functie die een hele pagina doorloopt.
Gaat alle posts af en extraheert daar de beschikbare velden uit  

Input:

thr    : str object
"""
def parse_thread(thr):
    posts = [] # initieer een lijst met posts
    souped = BeautifulSoup(thr, 'html.parser') # Gebruik Beautifulsoup om de html te parseren 
    for message in souped.find_all('td', { 'class':'msgtable item '}): # voor alle tags 'td' met klasse 'msgtable item ' 
        posts.append(parse_post(message)) 

    return posts

##############################################################
### Input
##############################################################

outdir = sys.argv[1] # de directory om geparseerde threats in weg te schrijven
threads = sys.argv[2:] # alle pagina's die je wil parseren, gedownload van het web


##############################################################
### Procedure
##############################################################

forum_name = 'body-fitness'

# reguliere expressie om de naam van een thread te extraheren
thread_title_match = re.compile(r'(.+)m(\d+)(-p(\d+))?')

# maak een dictionary aan om threads te koppelen aan geparseerde posts; 
# een thread kan uit meerdere pagina's bestaan, en we willen de posts van de verschillende pagina's op deze manier bij elkaar brengen
thread_dict = defaultdict(list)
for thread in threads: # voor ieder bestand
    if os.path.exists(thread):
        with open(thread, 'r', encoding='iso-8859-1') as t_open:
            thr_str = t_open.read() # lees het in
            thread_details = thread.split('/')[-1].split('.')[0] 
            try:
                # extraheer titel en id van de thread
                thread_search = thread_title_match.search(thread_details).groups()
                thread_title = thread_search[0].replace('-',' ').strip()
                thread_id = thread_search[1]
                if thread_search[3] != None:
                    thread_index = thread_search[3]
                else:
                    thread_index = 1
                # maak een thread object aan
                thread_item = Thread(thread_id, thread_title, '-', '-')
                try:
                    # parseer de posts en bijbehorende informatie uit de pagina
                    posts = parse_thread(thr_str)
                except:
                    print('Error parsing',thread,'skipping...')
                    continue
                # voeg posts to aan het thread
                thread_item.posts = posts
                thread_dict[thread_id].append(thread_item)
            except:
                print('Wrongly formed file name',thread,'skipping...')
                continue
	
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
