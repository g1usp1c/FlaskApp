import os
import sqlite3
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
import datetime
from flask import Flask, render_template, redirect
from werkzeug.exceptions import abort
app = Flask(__name__)

@app.route("/")
def index():
    print('inizio index')
    # connessione al database
    conn = sqlite3.connect(os.path.realpath('C:/Users/piccione/OneDrive - ION/Desktop/Pyton/Database/DataBase.db'))
    # creazione del cursore
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    #
    # cancellazione feed letti
    #
    print('cancellazione dati letti')
    sql = ("delete from feedrss where stato=1;")
    conn.execute(sql)
    conn.commit()
    #
    # cancellazione feed del giorno prima
    #
    oggi=datetime.date.today() 
    dataieri = oggi.strftime("%Y-%m-%d %H:%M")
    sql = ("delete from feedrss where data < ?;")
    conn.execute(sql,[dataieri],)
    conn.commit()
    #
    # estrazione dell'ultima data di recupero dati
    #
    print('estrazione data')
    datalast = datetime.datetime.now()
    dataagg  = datalast.strftime("%Y-%m-%d %H:%M")
    qdata = "SELECT data FROM feeddata"
    c.execute(qdata, )
    row = c.fetchone()
    if  row is not None:
        datalast = row[0]
    #
    # estrazione delle fonti per le quali ricercere i feed
    #
    print('estrazione fonti')
    qfonti = "SELECT fonte,link FROM feedfonti"
    c.execute(qfonti, )
    row = c.fetchall()
    for riga in row:
        fonte = riga[0]
        link  = riga[1]
        try:
            pagina = requests.get(link)
            soup = BeautifulSoup(pagina.content, features='xml')
            articles = soup.findAll('item')
            for a in articles:
                titolo    = str(a.find('title').text).replace("/","")
                link      = a.find('link').text
                autore    = a.find('creator')
                if autore == None:
                   autore    = a.find('author')
                if autore == None:
                   autore = " "    
                autore = str(autore)
                autore = autore.replace("<dc:creator>", "").replace("</dc:creator>", "").replace("<name>", "").replace("</name>", "")
                datapub   = parse(a.find('pubDate').text)
                data      = datapub.strftime("%Y-%m-%d %H:%M")
                datapub   = datapub.strftime("%d-%m-%Y %H:%M")
                sommario = a.find('description').text
                immagine  = a.find('thumb')
                if  (immagine == None):
                    immagine  = a.find('thumb_intermedia')
                if  (immagine == None):
                    immagine = 'data:image/png;base64,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'                
                if  (sommario == None):
                    sommario = " "
                immagine = str(immagine)
                immagine = immagine.replace("<thumb>", "").replace("</thumb>", "")
                sommario = clean_text(str(sommario))
                sommario = sommario[:250]
                contenuto = ' '
                aggiorna_rss(fonte,data,titolo,autore,datapub,sommario,contenuto,link,immagine,datalast)   
        except:
            print("Lettura feed ko: ",fonte,link,pagina.status_code)
    #
    # aggiornamento data ultima estrazione feed
    #
    print('aggiornamento data')
    sql = ("update feeddata set data = ?;")
    datalast = datetime.datetime.now()
    dataagg  = datalast.strftime("%Y-%m-%d %H:%M")
    conn.execute(sql,[dataagg],)
    conn.commit()
    conn.close
    #
    # esposizione di tutti i nuovi fees
    #
    print('esposizione feed')
    feeds = conn.execute('SELECT fonte,titolo,pubblicato,autore,sommario,immagine,stato FROM feedrss order by data desc').fetchall()
    conn.close()
    return render_template('index.html', feeds=feeds)
#
# Aggiorno la tabella dei feed
#
def aggiorna_rss(fonte,data,titolo,autore,datapub,sommario,contenuto,link,immagine,datalast):
    #
    # definizione della query di inserimento
    #
    insert_query = "INSERT INTO feedrss (fonte,data,titolo,autore,pubblicato,sommario,contenuto,link,immagine,stato) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    conn = sqlite3.connect(os.path.realpath('C:/Users/piccione/OneDrive - ION/Desktop/Pyton/Database/DataBase.db'))
    conn.row_factory = sqlite3.Row
    if  (data >= datalast):
        dati = (fonte,data,titolo,autore,datapub,sommario,contenuto,link,immagine,0)
        conn.execute(insert_query, dati)
        conn.commit()
    return()
#
# Funzione per pulire il testo dai tag HTML
#
def clean_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    clean_text = soup.get_text()
    return clean_text

def get_feed(feed_id):
    print('Cerco il feed: ',feed_id)
    conn = sqlite3.connect(os.path.realpath('C:/Users/piccione/OneDrive - ION/Desktop/Pyton/Database/DataBase.db'))
    feed = conn.execute('SELECT * FROM feedrss WHERE titolo = ?',
                        (feed_id,)).fetchone()
    if feed is None:
        abort(404)
    else:
        sql = ("update feedrss set stato = 1 where titolo = ?;")
        conn.execute(sql,[feed_id],)
        conn.commit()
    conn.close() 
    fonte = feed[0]
    data = feed[4]
    titolo = feed[2]
    autore = feed[3]
    link = feed[7]
    contenuto = feed[6]
    contenuto = contenuto[0:100]
    paragraphs = ' '
    html_content = ' '
    feed = (fonte,data,titolo,link,autore,contenuto,paragraphs,html_content)
    return feed

@app.route("/<feed_id>")
def feed(feed_id):
    feed = get_feed(feed_id)
    link = feed[3]
    return redirect(link) 
