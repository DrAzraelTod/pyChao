# -*- coding: utf-8 -*-
import os
import sqlite3


class ModNicknames(object):
    def __init__(self, parent, config):
        db_file = "mod_nicknames.db"
        db = os.path.join(os.path.dirname(__file__), db_file).replace(u'\\', '/')

        if not os.path.exists(db):
            parent.print_notice("###################### NEW DATABASE ########################")
            create_string = 'CREATE  TABLE "main"."user" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "nickname" VARCHAR NOT NULL , "vorname" VARCHAR NOT NULL , "channel" VARCHAR NOT NULL , "hinzu" DATETIME NOT NULL  DEFAULT CURRENT_DATE, "hinzuvon" VARCHAR NOT NULL )'
            create_index_1 = 'CREATE  INDEX "main"."user_nickname_index" ON "user" ("nickname" ASC)'
            create_index_2 = 'CREATE  INDEX "main"."user_vorname_index" ON "user" ("vorname" ASC)'
            conn = sqlite3.connect(db)
            c = conn.cursor()
            c.execute(create_string)
            c.execute(create_index_1)
            c.execute(create_index_2)
            conn.commit()
            c.close()
            conn.close()
            del c, conn, create_string, create_index_1, create_index_2
            parent.print_notice("################## NEW DATABASE CREATED ####################")

        self.config = config
        self.parent = parent
        self.db = db

        parent.register_callback(u'!nickname', self.nickname, 'Several small fuckups')
        parent.register_callback(u'!vorname', self.vorname, 'Several small fuckups')
        parent.register_callback(u'!addvorname', self.add_vorname, 'Several small fuckups')

    def nickname(self, params):
        if len(params.args) > 0:
            conn = sqlite3.connect(self.db)
            csr = conn.cursor()
            csr.execute("select nickname from user where vorname LIKE '%" + params.args[0] + "%'")
            result = csr.fetchall()
            nickname_string = ""
            for nickname in result:
                nickname_string = nickname_string + nickname[0] + " "
            csr.close()
            conn.close()
            if len(nickname_string) == 0:
                nickname_string = "Keine Treffer"
            self.parent.privmsg(u'Folgende Nicknamen passen zum Vornamen: ' + nickname_string, params.channel)
        else:
            self.parent.privmsg(u'Bitte !nickname <vorname> eingeben!', params.channel)

    def vorname(self, params):
        if len(params.args) > 0:
            conn = sqlite3.connect(self.db)
            csr = conn.cursor()
            csr.execute("select vorname from user where nickname LIKE '%" + params.args[0] + "%'")
            result = csr.fetchall()
            nickname_string = ""
            for nickname in result:
                nickname_string = nickname_string + nickname[0] + " "
            csr.close()
            conn.close()
            if len(nickname_string) == 0:
                nickname_string = "Keine Treffer"
            self.parent.privmsg(u'Folgende Vornamen passen zum Nickname: ' + nickname_string, params.channel)
        else:
            self.parent.privmsg(u'Bitte !vorname <nickname> eingeben!', params.channel)

    def add_vorname(self, params):
        if len(params.args) == 2:
            conn = sqlite3.connect(self.db)
            csr = conn.cursor()
            csr.execute("select id from user where ((nickname LIKE '%" + params.args[0] + "%') AND (nickname LIKE '%" +
                        params.args[1] + "%') AND (channel LIKE '%" + params.channel + "%'))")
            if csr.fetchall() > 0:
                csr.close()
                csr = conn.cursor()
                csr.execute(
                    "INSERT INTO user ('nickname','vorname','channel','hinzu','hinzuvon') VALUES (?,?,?,CURRENT_DATE,?)",
                    (params.args[0], params.args[1], params.channel, params.target))
                conn.commit()
                self.parent.privmsg(u'Benutzer eingetragen!', params.channel)
            else:
                self.parent.privmsg(u'Der Benutzer existiert bereits!', params.channel)
            csr.close()
            conn.close()
        else:
            self.parent.privmsg(u'Bitte !addvorname <nickname> <vorname> eingeben!', params.channel)
