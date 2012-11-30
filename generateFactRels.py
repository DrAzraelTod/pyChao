#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
from pysqlite2 import dbapi2 as sqlite3
import re

class FrelImport(object):
    def __init__(self, dbpath):
      self.connectDB(dbpath)
      
      sql1 = u"SELECT fid, fact from fact WHERE fact like '%#%'"
      allfacts = self.DBcursor.execute(sql1).fetchall()
      r1 = ur"#([1-9][0-9]+)"
      reobject = re.compile(r1)
      for fact in allfacts:
        for fid in reobject.findall(fact[1]):
          sql2 = u"INSERT INTO fact_rels (fid,refs ) VALUES (%s,%s)" % (fact[0],fid)
          self.DBcursor.execute(sql2)
          print(sql2)
      self.DBconn.commit()
      
    def connectDB(self, dbpath):
      self.DBconn = sqlite3.connect(dbpath)
      self.DBcursor = self.DBconn.cursor()
      print u"DB \"%s\" wurde verbunden" % dbpath

if __name__ == '__main__':
  dbpath = os.path.join(os.path.dirname(__file__), u'db/fact.sqlite').replace(u'\\','/')
  importer = FrelImport(dbpath)
