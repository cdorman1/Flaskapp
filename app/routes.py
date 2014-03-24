# -*- coding: utf-8 -*-

import MySQLdb

import locale
import lxml.html
import sqlalchemy as sa
import sqlalchemy.orm as saorm
import sqlalchemy.exc as saexc
import sqlalchemy.ext.declarative as sadec
from flask import Flask, render_template, request

locale.setlocale(locale.LC_ALL, '')

#NOTE: this script was written in Python 2.7 some of the string formatting
#may not translate when used with older versions 

#Use the code below if the output is something other than UTF-8
"""
import codecs
if sys.stdout.encoding != 'UTF-8':
  sys.stdout = codecs.getwriter('cp850')(sys.stdout, 'strict')
if sys.stderr.encoding != 'UTF-8':
  sys.stderr = codecs.getwriter('cp850')(sys.stderr, 'strict')  
"""  

app = Flask(__name__)

#engine = sa.create_engine('mysql://collector:collector@cer-emdbl2/history',
#        pool_recycle=1800, echo=True)
#Session = saorm.scoped_session(saorm.sessionmaker(bind=engine))
#Base = sadec.declarative_base(engine)
#
#
#class Command(Base):
#    __table__ = 'history.pos_matrix'
#
#    symbol = sa.Column(sa.String(32), primary_key=False, nullable=False)
#    buys = sa.Column(sa.String(32), primary_key=False, nullable=False)
#    sells = sa.Column(sa.String(32), primary_key=False, nullable=False)
#    TradeDate = sa.Column(sa.DATE, primary_key=True, nullable=False)
    
    





def db_con(symbol):
    
    
    db = MySQLdb.connect(host = "cer-emdbl2",
                         user = "tclerk",
                         passwd = "flamengo",
                         db = "history")                 
    cur = db.cursor()
    try:
        cur.execute ("SELECT sum(buys+sells) FROM history.pos_matrix WHERE symbol = \'{0}\' AND tradedate=curdate();".format(symbol)) 
    except MySQLdb.Error, e:
        try:
            print "MySQL Error {0}: {1}".format(e.args[0], e.args[1])
        except IndexError:
            print "MySQL Error: {}".format(str(e))
    
    row = cur.fetchone()
    vol = int(row[0])
    return vol
        

def web_scraper(symbol):
    url = ('http://finance.yahoo.com/q?s=' + symbol)
    doc = lxml.html.parse(url)
    #find the first table contaning any tr and a td with class yfnc_tabledata1
    table = doc.xpath("//table[tr/td[@class='yfnc_tabledata1']]")[1]        
    text = []   
    for tr in table.xpath('./tr'):
        text.append(tr.text_content())
    split_txt = [i.split(':') for i in text]
    em_vol =  db_con(symbol) 
    ms = float(em_vol) / int(split_txt[2][1].replace(',', '')) * 100
    symbol = str(symbol)
    sym = "Symbol: %s" % (str.upper(symbol))
    avg_vol =  "%s: %s" % (split_txt[3][0], split_txt[3][1])
    sym_vol = "%s: %s" % (split_txt[2][0], split_txt[2][1])
    em_tvol = "EM Total Volume: %s" % (locale.format('%d', em_vol, 1))
    market_share = "EM Market Share: %.2f%%" % (ms)
    return sym, avg_vol, sym_vol, em_tvol, market_share


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('index.html')


#@app.route('/about')
#def about():
#    return render_template('about.html')


@app.route('/', methods = ['POST'])
def marketshare():
    symbol = request.form['symbol']
    data = web_scraper(symbol)
    print data
    return render_template('index.html', data=data, symbol=symbol) 


if __name__ == '__main__':
    app.run(debug=True)
