
#import sys
#import MySQLdb
#import locale
#import lxml.html
from flask import Flask, render_template, request, redirect 

#locale.setlocale(locale.LC_ALL, '')

#NOTE: this script was written in Python 2.7 some of the string formatting may not
#translate when used with older versions 

#Use the code below if the output is something other than UTF-8
"""
import codecs
if sys.stdout.encoding != 'UTF-8':
  sys.stdout = codecs.getwriter('cp850')(sys.stdout, 'strict')
if sys.stderr.encoding != 'UTF-8':
  sys.stderr = codecs.getwriter('cp850')(sys.stderr, 'strict')  
"""  

app = Flask(__name__)


def db_connect(symbol):
    
    #db = MySQLdb.connect(host = "cer-emdbl2",
    #                     user = "tclerk",
    #                     passwd = "flamengo",
    #                     db = "history")                 
    #cur = db.cursor()
    #try:
    #    cur.execute ("SELECT sum(buys+sells) FROM history.pos_matrix WHERE symbol = \'{0}\' AND tradedate=curdate();".format(symbol)) 
    #except MySQLdb.Error, e:
    #    try:
    #        print "MySQL Error {0}: {1}".format(e.args[0], e.args[1])
    #    except IndexError:
    #        print "MySQL Error: {}".format(str(e))
    
    #row = cur.fetchone()
    #vol = int(row[0])
    vol = 132000
    return vol
        

def web_scraper(symbol):
    url = ('http://finance.yahoo.com/q?s=' + symbol)
    doc = lxml.html.parse(url)
    #find the first table contaning any tr and a td with class yfnc_tabledata1
    table = doc.xpath("//table[tr/td[@class='yfnc_tabledata1']]")[1] 
    print "***" * 10
    print "Symbol: " + str.upper(symbol)
         
    text = []   
    for tr in table.xpath('./tr'):
        text.append(tr.text_content())
    split_txt = [i.split(':') for i in text]
    av_key = split_txt[3][0]
    av_val = split_txt[3][1]
    yvol_key = split_txt[2][0]
    yvol_val = split_txt[2][1]
    yvol = yvol_val.replace(',', '')
    em_vol =  db_connect(symbol) 
    market_share = float(em_vol) / int(yvol) * 100
    return market_share
    
    #print "%s: %s" % (av_key, av_val)
    #print "%s: %s" % (yvol_key, yvol_val)
    #print "EM Total Volume:", locale.format('%d', em_vol, 1)
    #print "EM Market Share: %.2f%%" % (market_share)
    #print "***" * 10




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    market_share = webscraper(symbol)
    return render_template('about.html', market_share=market_share)


@app.route('/market_share', methods = ['POST'])
def market_share():
    symbol = request.form['symbol']
    print ("The symbol is '" + symbol + "'")
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
    symbol = request.form['symbol']    
    web_scraper(symbol) 
