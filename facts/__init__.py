# -*- coding: utf-8 -*-
import os.path
from pysqlite2 import dbapi2 as sqlite3
import re


class ModFacts:
    def __init__(self, parent, config):
        self.db_cursor = None
        self.db_conn = None
        self.parent = parent
        parent.register_callback('!fact', self.fact,
                                 u'Zeigt ein zufälliges Fact an oder sucht eines anhand eines Textschnipsels')
        parent.register_callback('!fid', self.fact_by_id, u'Zeigt ein Fact anhand seiner FID an')
        parent.register_callback('!fname', self.fact_by_name,
                                 u'Zeigt ein zufälliges Fact anhand eines Autorennamens an')
        parent.register_callback('!addfact', self.add_fact, u'Fügt ein Fact zur Datenbank hinzu')
        parent.register_callback('!fs', self.facts, u'Sucht Facts anhand eines Textschnipsels und zeigt ihre FIDs an')
        parent.register_callback('!fsname', self.facts_by_name,
                                 u'Sucht Facts anhand eines Autorennamens und zeigt ihre FIDs an')
        parent.register_callback('!finf', self.fact_info, u'Zeigt Informationen zu einem Fact anhand seiner FID an')
        parent.register_callback('!fdel', self.delete_fact, u'Löscht ein Fact anhand seiner FID')
        parent.register_callback('!fcount', self.fact_count, u'Zeigt die Anzahl der Facts in der Datenbank an')
        dbpath = os.path.join(os.path.dirname(__file__), config['dbpath']).replace('\\', '/')
        self.config = config
        self.connect_db(dbpath)

    def connect_db(self, dbpath):
        self.parent.print_notice("SQLite-Database: " + dbpath)
        self.db_conn = sqlite3.connect(dbpath)
        self.db_cursor = self.db_conn.cursor()

    def fact(self, params):
        # Kommando !fact, ruft einzelnes Zufälliges Fact ab oder sucht einzelnes Fact nach Text
        if len(params.args) >= 1:
            fact = self.db_cursor.execute(
                u"SELECT id, nickname, fact from fact WHERE fact like '%" + params.follow + "%' ORDER BY Random() LIMIT 1").fetchall()
        else:
            fact = self.db_cursor.execute(u'SELECT id, nickname, fact from fact ORDER BY Random() LIMIT 1').fetchall()
        if len(fact) > 0:
            msg = self.render_fact(fact)
        else:
            msg = u'[Fehler] Keine passenden Facts gefunden!'
        self.parent.privmsg(msg, params.channel)

    def fact_by_id(self, params):
        # Kommando !factbyid, ruft einzelnes Fact nach id ab
        if len(params.args) >= 1:
            temp = self.parent.get_int(params.args[0])
            if temp != 0:
                fact = self.db_cursor.execute(
                    u"SELECT id, nickname, fact from fact WHERE id =%s LIMIT 1" % temp).fetchall()
                if len(fact) > 0:
                    msg = self.render_fact(fact)
                else:
                    msg = u'[Fehler] Keine passenden Facts gefunden!'
            else:
                msg = u'[Fehler] Keine Zahl übergeben!'
        else:
            msg = u'[Fehler] Parameter fehlt'
        self.parent.privmsg(msg, params.channel)

    def render_fact(self, fact):
        id = u"#%s" % fact[0][0]
        msg = u"[#%s] <%s> %s" % (fact[0][0], fact[0][1], fact[0][2])
        sql = u"SELECT count(*) from fact WHERE fact like '%" + id + u" %' or fact like '%" + id + u",%' or fact like '%" + id + u";%' or fact like '%" + id + u".%' or fact like '%" + id + u"+%' or fact like '%" + id + u"]%' or fact like '%" + id + u")%' or fact like '%" + id + u"}%' or fact like '%" + id + u"/%' or fact like '%" + id + u"\%' or fact like '%" + id + u"'"
        related = self.db_cursor.execute(sql).fetchall()
        if (related[0][0] >= 1):
            msg = msg + u" [%s related]" % (related[0][0])
        return msg

    def fact_by_name(self, params):
        # Kommando !factbyname, ruft einzelnes Zufälliges Fact nach Autor ab
        if len(params.args) >= 1:
            fact = self.db_cursor.execute(
                u"SELECT id, nickname, fact from fact WHERE nickname like '%" + params.follow + "%' ORDER BY Random() LIMIT 1").fetchall()
            if len(fact) > 0:
                msg = self.render_fact(fact)
            else:
                msg = u'[Fehler] Keine passenden Facts gefunden!'
        else:
            msg = u'[Fehler] Parameter fehlt'
        self.parent.privmsg(msg, params.channel)

    def delete_fact(self, params):
        if len(params.args) == 1:
            temp = self.parent.get_int(params.args[0])
            if temp != 0:
                allowed = False
                for user in self.config['deleting_users']:
                    if user.lower() == params.target.lower():
                        allowed = True
                if allowed:
                    temp = self.parent.get_int(params.args[0])
                    if temp != 0:
                        self.db_cursor.execute(u"DELETE FROM fact WHERE id =%s" % temp)
                        msg = u"[Gelöscht] Fact mit der FID %s wurde gelöscht" % temp
                        self.parent.print_notice(u"Nutzer %s löschte Fact %s" % (params.target, temp))
                        self.db_cursor.execute(u"DELETE FROM fact_rels WHERE fid = %s " % temp)
                        self.db_conn.commit()
                else:
                    msg = u"[Fehler] Vergiss es! Das darfst du nicht."
                    self.parent.print_err(u"Nutzer %s versuchte Fact %s zu löschen" % (params.target, params.args[0]))
            else:
                msg = u"[Fehler] Bitte nur Zahlen übergeben!"
        else:
            msg = u"[Fehler] Parameter fehlt (fid)"
            self.parent.print_notice(u"Nutzer %s versuchte Fact ohne Parameter zu löschen" % params.target)
        self.parent.privmsg(msg, params.channel)

    def add_fact(self, params):
        # Kommando !addfact, fügt neues fact ein
        if len(params.follow) >= 1:
            self.db_cursor.execute(u"INSERT INTO fact (nickname,channel,fact, date) VALUES (?, ?, ?, datetime('now'))",
                                   (params.target, params.channel, params.follow))
            now_id = self.db_cursor.lastrowid
            msg = u"%s: Fact added [#%s] - %s" % (params.target, now_id, (self.config['fact_url'] % now_id))
            r1 = "[@#]([1-9][0-9]+)"
            referred = re.findall(r1, params.follow)
            for fid in referred:
                sql2 = u"INSERT INTO fact_rels (fid,refs ) VALUES (%s,%s)" % (now_id, fid)
                self.db_cursor.execute(sql2)
            self.db_conn.commit()
        else:
            msg = u'[Fehler] Kein Text angegeben!'
        self.parent.privmsg(msg, params.channel)

    def facts(self, params):
        # Kommando !facts, zeigt Fact-IDs anhand von Suchtext an
        if len(params.args) >= 1:
            fact = self.db_cursor.execute(
                u"SELECT id from fact WHERE fact like '%" + params.follow + "%' ORDER BY Random() LIMIT 50").fetchall()
            count = self.db_cursor.execute(
                u"SELECT count(*) from fact WHERE fact like '%" + params.follow + "%'").fetchall()
            if len(fact) > 0:
                msg = u"[%s Facts] " % count[0][0]
                for nf in fact:
                    msg = msg + u" #%s;" % nf[0]
            else:
                msg = u'[Fehler] Keine passenden Facts gefunden!'
        else:
            msg = u'[Fehler] Parameter fehlt'
        self.parent.privmsg(msg, params.channel)

    def facts_by_name(self, params):
        # Kommando !factsbyname, ruft Zufällige Facts nach Autor ab und gibt IDs aus
        if len(params.args) >= 1:
            fact = self.db_cursor.execute(
                u"SELECT id from fact WHERE nickname like '%" + params.follow + "%' ORDER BY Random() LIMIT 50").fetchall()
            count = self.db_cursor.execute(
                u"SELECT count(*) from fact WHERE nickname like '%" + params.follow + "%'").fetchall()
            if len(fact) > 0:
                msg = u"[%s Facts] " % count[0][0]
                for nf in fact:
                    msg = msg + u" #%s;" % nf[0]
            else:
                msg = u'[Fehler] Keine passenden Facts gefunden!'
        else:
            msg = u'[Fehler] Parameter fehlt'
        self.parent.privmsg(msg, params.channel)

    def fact_info(self, params):
        # Kommando !factinfo, ruft informationen zu einzelnem Fact nach ID
        if len(params.args) >= 1:
            temp = self.parent.get_int(params.args[0])
            if temp:
                if len(params.args) >= 1:
                    fact = self.db_cursor.execute(
                        u'SELECT id, nickname, date, channel from fact where id=%s' % temp).fetchall()
                    if fact:
                        msg = u"[Fact #%s] Verfasst von %s, Datum: %s im Channel %s" % (
                            fact[0][0], fact[0][1], fact[0][2], fact[0][3])
                    else:
                        msg = u'[Fehler] Keine passenden Facts gefunden!'
                else:
                    msg = u'[Fehler] Parameter fehlt'
            else:
                msg = u'[Fehler] Keine Zahl übergeben (oder FID=0)'
        else:
            msg = u'[Fehler] Keine FID übergeben'
        self.parent.privmsg(msg, params.channel)

    def fact_count(self, params):
        count = self.db_cursor.execute(u"SELECT count(*) FROM fact").fetchall()
        self.parent.privmsg(u"[%s Facts]" % count[0][0], params.channel)
