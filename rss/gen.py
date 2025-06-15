#pip install feedgen

from oauth2client.tools import argparser, run_flow
from feedgen.feed import FeedGenerator
from datetime import datetime
from datetime import date
import json
import sys
sys.path.insert(0, 'c:/devinpiano/')
import config 
import html
import pathlib

def parseAnswer(answer):
    esc = html.escape(answer)
    return esc

if __name__ == '__main__':
    today = date. today()
    today = today. strftime("%Y%m%d")

    argparser.add_argument("--d", help="Date for gen", default=today)
    args = argparser.parse_args()
    
    RSS_FOLDER = "rss/data/"

    qas = []
    with open(RSS_FOLDER + args.d + ".json", "r") as f:
        qas = json.load(f)
    
    
    if (len(qas) > 0):
        fg = FeedGenerator()
        y = args.d[0:4]
        fg.id('https://misterrubato.com/rss/' + y + '/' + args.d)
        fg.title(args.d)
        fg.author( {'name':config.cfg['RSS']['AUTHOR'],'email':config.cfg['RSS']['EMAIL']} )
#        fg.link( href=config.cfg['RSS']['WEBSITE'], rel='alternate' )
        fg.link(href='https://misterrubato.com/rss/' + y + '/' + args.d, rel='alternate')
        fg.logo(config.cfg['RSS']['LOGO'])
        fg.subtitle('This is a cool feed!')
        fg.language('en')
        qnum = 0
        for qa in qas:
            qnum = qnum + 1
            fe = fg.add_entry()
            fe.id('https://misterrubato.com/rss/' + y + '/' + args.d + '/' + str(qnum))
            print(qa)
            fe.link(href='https://misterrubato.com/rss/view.html?date=' + args.d + "&id=" + str(qnum), rel='alternate')
            fe.title(qa["question"])
#            fe.author({"name": qa["author"], "uri": "https://www.youtube.com/channel/" + qa["authorchannel"]})
            fe.content(qa["answer"])

    atomfeed = fg.atom_str(pretty=True) # Get the ATOM feed as string
    rssfeed  = fg.rss_str(pretty=True) # Get the RSS feed as string
    pathlib.Path('web/public/rss/data/' + y + '/' + args.d).mkdir(parents=True, exist_ok=True) 
    fg.atom_file('web/public/rss/data/' + y + '/' + args.d + '/atom.xml') # Write the ATOM feed to a file
    fg.rss_file('web/public/rss/data/' + y + '/' + args.d + '/rss.xml') # Write the RSS feed to a file

