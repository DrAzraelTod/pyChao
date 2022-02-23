#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import re
import codecs
import datetime
import time
from sqlite3 import dbapi2 as sqlite3

class export_web:
    def __init__(self, parent,config):
        dbpath = os.path.join(os.path.dirname(__file__), config['dbpath']).replace(u'\\','/')
        self.config = config
        self.parent = parent
        self.connectDB(dbpath)
        self.update_all()
        self.parent.export_web = self
        
        
    def update_all(self):
        facts = self.get_all()
        for f in facts:
            lines = self.render(f)
            self.write(lines, ('%s.html' % f[0]))
        self.parent.print_notice(u"Alle Fact-Seiten aktualisiert")

    def update_one(self, fid):
        fact = self.get(fid)
        lines = self.render(fact)
        self.write(lines, ('%s.html' % fact[0]))
        self.parent.print_notice(u"Fact-Seite #%s wurde aktualisiert" % fact[0])

    def connectDB(self, dbpath):
        self.parent.print_notice(u"SQLite-Database zur RSS-Ausgabe: "+dbpath)
        self.DBconn = sqlite3.connect(dbpath)
        self.DBcursor = self.DBconn.cursor()
        
    def get(self, fid):
        fact = self.DBcursor.execute(u'SELECT id, nickname, fact, date, channel from fact where id=%s limit 1' % id).fetchall()
        return fact[0]

    def get_all(self):
        facts = self.DBcursor.execute(u'SELECT id, nickname, fact, date, channel from fact ORDER BY date DESC').fetchall()
        return facts
        
    def write(self, lines, filename):
        hfile = codecs.open(self.config['dir']+filename, u'w', 'utf-8')
        for l in lines:
            hfile.write(l+'\n')
        hfile.flush()
        hfile.close()
        return True


    def page_prefix(self):
        lines = [
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">',
            '<html>',
            '<head>',
              '<title>pyChao Fact</title>',
              '<meta http-equiv="Content-Type" content="text/html;charset=utf-8">',
              '<link rel="alternate" type="application/atom+xml" title="Atom-Fact-Feed" href="%s" />' % self.config['feed'],
              self.stylesheets(),
            '</head>',
            '<body>'
        ]
        return lines
        
    def stylesheets(self):
        return '<link type="text/css" href="%s" rel="stylesheet"/>' % self.config['css']
    
    def page_end(self):
        now = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0100')
        lines = [
            ('<div class="footer">Stand: %s</div>' % now),
            self.analytics_tag(),
            '</body>',
            '</html>'
        ]
        return lines

    def analytics_tag(self):
        try:
            code = '''
                <script type="text/javascript">
                    var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
                    document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
                </script>
                <script type="text/javascript">
                    try {
                        var pageTracker = _gat._getTracker("'''+self.config['analytics']+'''");
                        pageTracker._trackPageview();
                    } catch(err) {}
                </script>
            '''
        except:
            code = ''
        return code
    
    
    def html_escape(self,text):
      html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
      }
      L=[]
      for c in text:
        L.append(html_escape_table.get(c,c))
      return "".join(L)

    def render(self, f):
        content = u'%s' % self.html_escape(f[2])
        
        r1 = r"[@#]([1-9][0-9]+)"
        r2 = r'<a href="/fact/\g<1>.html">#\g<1></a>'
        content = re.sub(r1,r2,content)
        
        r1 = r"\b(([A-Za-z]{3,5})://([-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|]))"
        r2 = r'<a rel="nofollow" target="_blank" href="\g<1>">\g<3></a>'
        content = re.sub(r1,r2,content)
        
        lines = self.page_prefix()
        lines.append('<div class="fact">')
        lines.append('<h2>Fact #%s von %s</h2>' % (f[0], f[1]))
        lines.append('<p class="infos">Geschrieben: %s in %s</p>' % (f[3], f[4]))
        lines.append('<p class="text">%s</p>' % content)
        id = u'%s' % f[0]
        sql = u"SELECT fid FROM fact_rels WHERE refs = %s" % f[0]
        related = self.DBcursor.execute(sql).fetchall()
        root_url = self.config['pub_root']
        if(len(related)>0):
          lines.append(u'<h3>Antworten</h3>')
          lines.append(u'<ul>')
          for r in related:
            lines.append(u'<li>')
            lines.append(u'<a href="%s/%s.html">#%s</a> ' % (root_url,r[0], r[0]))
            lines.append(u'</li>')
          lines.append(u'</ul>')
        lines.append('</div>')
        lines += self.page_end()
        return lines
