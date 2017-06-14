
###############################################################
#  parse_bodynet.py
#       by Florian Kunneman
#       http://applejack.science.ru.nl/languagemachines/team/fkunneman/
#       Language Machines
#       Radboud University
#
#       Licensed under GPLv3
#
# This is a Python script for parsing forum pages on the forum.bodynet.nl website. 
# Usage: python parse_bodynet.py [outputdir] [dir_with_html-pages]/*
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
Parseer functie die de posthead in bodynet pagina's doorloopt

Input:

ph   : BeautifulSoup tag object
"""
def parse_posthead(ph):
    for c in ph.children:
        ph_souped = BeautifulSoup(c.__str__(), 'html.parser') # parseer met BeautifulSoup
        for span in ph_souped.find_all('span'): # onderscheid de verschillende informatie-eenheden
            if 'class' in span.attrs: 
                if span['class'][0] == 'date': # de eenheid met klasse 'date' geeft de datum
                    date = span.contents[0].split(',')[0].strip()
                elif span['class'][0] == 'time': # de eenheid met klasse 'time' geeft de tijd
                    time = span.contents[0].strip()
                elif span['class'][0] == 'nodecontrols': # de eenheid met klass 'nodecontrols' bevat de index van de post
                    nc_souped = BeautifulSoup(span.__str__(), 'html.parser')
                    url = nc_souped.a['href']
                    key = nc_souped.a['name'][4:] # om alleen het nummer te bewaren
                    index = int(nc_souped.a.contents[0][1:])
    return date + ' ' + time, url, key, index

"""
Parseer functie die de postdetails (gedeelte met de auteursnaam) in bodynet pagina's doorloopt

Input:

pd   : BeautifulSoup tag object
"""
def parse_postdetails(pd):
    candidates = re.findall(r'>[^<]+<', pd.__str__()) # We zijn op zoek naar de username, alles wat tussen tags staat kan de username zijn
    for candidate in candidates:
        txt = re.search(r'>(.+)<', candidate).groups()[0].strip()
        if len(txt) > 0: # als er inhoud is, is het de userhttps://www.facebook.com/events/1720638621296124/?acontext=%7B%22action_history%22%3A%22%5B%7B%5C%22surface%5C%22%3A%5C%22external%5C%22%2C%5C%22mechanism%5C%22%3A%5C%22social_plugin%5C%22%2C%5C%22extra_data%5C%22%3A%5B%5D%7D%5D%22%7D
            user = txt
            break
    try:
        return user
    except:
        return '-'

"""
Functie die de paragrafen uit een posttekst haalt 

Input:

postbody   : str
"""
def postbody2paragraphs(postbody):
    paragraphs = postbody.split(r'<br/> <br/>') # paragrafen zijn gedefinieerd als secties onderscheiden door een witregel
    return paragraphs

def clean_text(raw_text):
    cleaned_text = re.sub(r'<[^>]+>', '', raw_text)
    cleaned_text = re.sub(r' {2,}', ' ', cleaned_text)
    return cleaned_text.strip()

"""
Parseer functie die de postbody in bodynet pagina's doorloopt

Input:

pb   : BeautifulSoup tag object
"""
def parse_postbody(pb):

    pb_souped = BeautifulSoup(pb.__str__(), 'html.parser') # parseer de tag om hierbinnen verder te zoeken
    parent = '-' # geef een startwaarde voor de parent, mocht deze niet aanwezig zijn
    for div in pb_souped.find_all('div'): # doorzoek de tag op de div met klasse 'content'
        if 'class' in div.attrs.keys(): 
            if div['class'][0] == 'content': # als deze gevonden is
                for c in div.contents: # doorloop contents (afgebakende stukken binnen tags)
                    if re.search('blockquote', c.__str__()): # als 'blockquote' hierin genoemd wordt
                        bq_souped = BeautifulSoup(c.__str__().encode('utf-8', errors='replace'), 'html.parser') # parseer andermaal de string
                        for d in bq_souped.find_all('div'): # doorzoek divs op de bbcode container
                            if 'class' in d.attrs.keys():
                                if d['class'][0] == 'bbcode_container': 
                                    for i, bc in enumerate(d.contents): # zoek binnen deze tag naar '#post' (duidt op een parent)
                                        if re.search(r'#post\d+', bc.__str__()):
                                            m = re.findall(r'post\d+', bc.__str__())
                                            parent = re.findall(r'\d+', m[0])[0]
                                    d.replaceWith('')
                                    c = bq_souped.get_text() # haal alle tekst binnen de tag binnen
                        text = c.__str__()
                        paragraphs = postbody2paragraphs(text) # haal de paragrafen uit de tekst
                        paragraphs_cleaned = []
                        for p in paragraphs:
                            cleaned_paragraph = clean_text(p) # schoon de paragrafen op (verwijder tags, witregels)
                            if not cleaned_paragraph == '': # tenzij niets is overgebleven na het opschonen, bewaar de paragraaf
                                paragraphs_cleaned.append(cleaned_paragraph)

    return paragraphs_cleaned, parent

"""
Parseer functie die een hele pagina doorloopt.
Gaat alle posts af en extraheert de verschillende informatie-eenheden.  

Input:

thr    : str object
"""
def parse_thread(thr):
    posts = [] # initieer een lijst met posts
    souped = BeautifulSoup(thr, 'html.parser') # Gebruik Beautifulsoup om de html te parseren 
    for div in souped.find_all('div'): # voor alle div-tags
        if 'class' in div.attrs.keys(): # als aan de tag een class is toegeschreven
            if div['class'][0] == 'posthead': # als de waarde van 'class' 'posthead' is
                dt, url, key, index = parse_posthead(div) # extraheer de datum en tijd, de url en de index van de post 
            elif div['class'][0] == 'username_container': # als de waarde van 'class' 'username_container' is
                user = parse_postdetails(div) # extraheer de naam van de gebruiker
            elif div['class'][0] == 'postbody': # als de waarde van 'class' 'postbody' is
                paragraphs, parent = parse_postbody(div) # extraheer de inhoud van de post (paragrafen) en de mogelijke parent (post waarop de post reageert)
                post = Post(key, user, dt, paragraphs, index, parent, '-', '-') # maak een Post object aan
                posts.append(post) # Voeg toe aan de lijst met posts
    return posts

##############################################################
### Input
##############################################################

outdir = sys.argv[1] # directory om de output naar weg te schrijven
threads = sys.argv[2:] # alle pagina's die je wil parseren, gedownload van het web


##############################################################
### Procedure
##############################################################

Forumname = 'Bodynet'

# maak een dictionary aan om threads te koppelen aan geparseerde posts; 
# een thread kan uit meerdere pagina's bestaan, en we willen de posts van de verschillende pagina's op deze manier bij elkaar brengen
thread_dict = defaultdict(list) 
for thread in threads: # doorloop alle bestanden
    if os.path.exists(thread): # check of het bestand bestaat
        with open(thread, 'r', encoding='cp1252') as t_open: # lees het bestand in (cp1252 encoding is hier belangrijk)
            thr_str = t_open.read()
            # identificeer de thread
            thread_details = thread.split('/')[-1].split('.')[0].split('-')
            if re.match(r'\d+', thread_details[0]):
                thread_id = thread_details[0]
            else: 
                print('No proper thread id for', thread, ', skipping')
                continue

            # sla bestanden over die toch geen verwachte threat zijn
            if re.match('print', thread_details[-1]):
                continue
            elif re.search(r'post\d+', thread_details[-1]):
                continue
            # als het formaat goed is, extraheer de titel en index van de thread
            elif re.match(r'$\d+^', thread_details[-1]):
                thread_index = int(thread_details[-1])
                thread_title = ' '.join(thread_details[1:-1])
            else:
                thread_index = 1
                thread_title = ' '.join(thread_details[1:])
            # maak een Thread object aan met de geëxtraheerde informatie
            thread_item = Thread(thread_id, thread_title, '-', '-')
            # parseer de posts in de thread
            posts = parse_thread(thr_str)
            thread_item.posts = posts # koppel de posts aan het thread item
            thread_dict[thread_id].append(thread_item) # voeg het thread item toe aan de dictionary
	

print('Writing xml')
for thread_id in thread_dict.keys(): # doorloop alle opgeslage thread id's
    thread_items = thread_dict[thread_id]
    # bundel alle geparseerde posts van het thread id
    thread_complete = Thread(thread_id, thread_items[0].title, '-', '-')
    for ti in thread_items:
        for post in ti.posts:
            thread_complete.addPost(post)
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    # schrijf de thread naar een bestand in XML
    out = open(outdir + '/' + thread_id + '.xml', 'w', encoding = 'cp1252', errors = 'replace')
    out.write("<?xml version='1.0' encoding='iso-8859-1'?>\n")
    out.write(r"<forum type='forum' name='" + forum_name + "'>\n")
    thread_complete.printXML(out)
    out.write('</forum>\n')
    out.close()
