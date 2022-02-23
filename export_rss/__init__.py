#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import codecs
import datetime
import time
import re
from sqlite3 import dbapi2 as sqlite3

class export_rss:
    def __init__(self, parent,config):
        dbpath = os.path.join(os.path.dirname(__file__), config['dbpath']).replace(u'\\','/')
        self.config = config
        self.parent = parent
        self.connectDB(dbpath)
        self.run()
        self.parent.export_rss = self
        
    def get_last_time(self):
        facts = self.DBcursor.execute(u'SELECT date from fact ORDER BY date DESC LIMIT 1').fetchone()
        return self.parsetime(facts[0])
        
        
    def run(self):
        facts = self.get()
        lines = self.render(facts)
        self.write(lines)
        self.parent.print_notice(u"Fact-Stream (RSS) wurde aktualisiert")

    def connectDB(self, dbpath):
        self.parent.print_notice(u"SQLite-Database zur RSS-Ausgabe: "+dbpath)
        self.DBconn = sqlite3.connect(dbpath)
        self.DBcursor = self.DBconn.cursor()
        
    def get(self):
        count = self.config['length']
        facts = self.DBcursor.execute(u'SELECT id, nickname, fact, date from fact ORDER BY date DESC LIMIT %s' % count).fetchall()
        return facts
        
    def write(self, lines):
        rssfile = codecs.open(self.config['file'], u'w', 'utf-8')
        for l in lines:
            rssfile.write(l)
            #self.parent.print_notice(l)
        rssfile.flush()
        rssfile.close()
        return True

    def xml_escape(self,text):
      xml_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
      }
      L=[]
      for c in text:
        L.append(xml_escape_table.get(c,c))
      return "".join(L)


    def render(self, facts):
        #now = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0100')
        now = self.get_last_time()
        lines = [
            u'<?xml version="1.0" encoding="utf-8"?>\n',
            u'<?xml-stylesheet type="text/css" media="screen" href="http://feeds2.feedburner.com/~d/styles/itemcontent.css"?>',
            u'<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n',
            u' <channel>\n',
            (u' <atom:link href="%s" rel="self" type="application/rss+xml" />\n' % self.config['pub_url']),
            u' <title>pyChao-Facts</title>\n',
            (u' <link>%s</link>\n' % self.config['link']),
            (u' <description>%s</description>\n' % self.config['description']),
            u' <language>de-DE</language>\n',
            (u' <copyright>%s</copyright>\n' % self.config['rights']),
            (u' <pubDate>%s</pubDate>\n' % now)
          ]
        web = False
        try:
            a = self.parent.export_web
        except:
            web = False
        if 'a' in locals():
            web = True
        for f in facts:
            content = u'%s' % self.xml_escape(f[2])
            
            
            r1 = r"\b(([A-Za-z]{3,5})://([-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|]))"
            r2 = r'&lt;a rel="nofollow" target="_blank" href="\g<1>"&gt;\g<3>&lt;/a&gt;'
            lcontent = re.sub(r1,r2,content)
            
            r1 = r"#([1-9][0-9]+)"
            r2 = r'&lt;a href="http://home.g33ky.de/fact/\g<1>.html"&gt;#\g<1>&lt;/a&gt;'
            lcontent = re.sub(r1,r2,lcontent)

            
            lines.append(u'<item>\n')
            lines.append(u' <title>[#%s] {%s} %s </title>\n' % (f[0],f[1] , content))
            lines.append(u' <description>%s</description>\n' % lcontent)
            lines.append(u' <author>%s (%s)</author>' % (self.config['adm_mail'],f[1]))
            if web:
                lines.append(u' <guid>%s%s.html</guid>' % (self.config['web_url'],f[0]))
            else:
                lines.append(u' <guid isPermaLink="false">g33ky.de/%s</guid>' % f[0])
            lines.append(u' <pubDate>%s</pubDate>' % self.parsetime(f[3]))
            lines.append(u'</item>\n')
        lines.append(u'</channel>\n')
        lines.append(u'</rss>\n')
        return lines
        
    def parsetime(self, dt):
        try:
            ret = datetime.datetime.strptime(dt, "%Y-%m-%d")
        except:
            ret = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        return ret.strftime('%a, %d %b %Y %H:%M:%S +0100')
