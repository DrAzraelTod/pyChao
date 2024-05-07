# -*- coding: utf-8 -*-
import os.path
from pysqlite2 import dbapi2 as sqlite3
import string
import types


def format_trigger_output(params, output):
    ret = ''
    for word in string.split(output):
        if word == u'#person':
            ret = ret + ' ' + params.target
        elif word == u'#person:':
            ret = ret + ' %s:' % params.target
        elif word == u'#chan':
            ret = ret + ' ' + params.channel
        else:
            ret = ret + ' ' + word
    return ret[1:]


class ModTriggers(object):
    def __init__(self, parent, config):
        self.db_cursor = None
        self.db_conn = None
        self.parent = parent
        dbpath = os.path.join(os.path.dirname(__file__), config['dbpath']).replace('\\', '/')
        self.config = config
        self.connect_db(dbpath)
        self.config = config
        self.parent = parent
        parent.register_callback(u'!trigger', self.add_trigger, 'creates/edits userdefined triggered responses')
        parent.register_callback(u'!triggerinfo', self.info, 'reads information about triggers')
        all_triggers = self.get_all()
        for trigger in all_triggers:
            self.register_trigger(trigger[0], trigger[1], 'there is no help neo!')
            self.parent.print_notice(u'trigger %s registered' % trigger[0])

    def connect_db(self, dbpath):
        self.parent.print_notice("SQLite-Database: " + dbpath)
        self.db_conn = sqlite3.connect(dbpath)
        self.db_cursor = self.db_conn.cursor()

    def trigger_factory(self, trigger_id):
        tfunc = self.post_trigger

        def trigger_func(params):
            tfunc(params, trigger_id)

        return trigger_func

    def register_trigger(self, trigger_id, trigger_text, trigger_help):
        self.parent.register_callback(trigger_text, self.trigger_factory(trigger_id), trigger_help, True)

    def post_trigger(self, params, trigger_id):
        # self.parent.print_notice(u'Trigger %s has been triggered' % (trigger_id))
        try:
            sql = u"SELECT reaction FROM command_triggers where id = %s AND last_run <= datetime('now', '%s')" % (
                trigger_id, self.config['trigger_time'])
            trigger = self.db_cursor.execute(sql).fetchone()
            if type(trigger) != types.NoneType:
                msg = u'%s' % trigger
                msg = format_trigger_output(params, msg)
                # self.parent.print_notice(u'result: %s' % (trigger))
                self.parent.privmsg(msg, params.channel)
                self.update_last_run(trigger_id)
                return True
            else:
                # self.parent.print_notice(u'trigger %s zeitlich gebremst' % trigger_id)
                return False
        except:
            msg = u'[Fehler] Trigger-Fuckup §%s - Fnord has occured!' % trigger_id
            self.parent.privmsg(msg, params.channel)

    def update_last_run(self, trigger_id):
        self.db_cursor.execute(u"UPDATE command_triggers SET last_run = datetime('now') where id = %s" % trigger_id)
        self.db_conn.commit()

    def get_all(self):
        return self.db_cursor.execute(u"SELECT id, trigger FROM command_triggers ").fetchall()

    def add_trigger(self, params):
        if len(params.args) >= 2:
            if 'response:' in params.args:
                response = False
                trigger = params.args[0]
                reaction = ''
                for arg in params.args[1:]:
                    if response:
                        reaction = reaction + ' ' + arg
                    elif arg == 'response:':
                        response = True
                    else:
                        trigger = trigger + ' ' + arg
                reaction = reaction[1:]
                self.db_cursor.execute(
                    u"INSERT INTO command_triggers (created_by,trigger,reaction, created_at, last_run) VALUES (?, ?, ?, datetime('now'), datetime('now', '-2 days'))",
                    (params.target, trigger, reaction))
                now_id = self.db_cursor.lastrowid
                msg = u"%s: Trigger added [§%s] - %s = %s" % (params.target, now_id, trigger, reaction)
                self.db_conn.commit()
                self.register_trigger(now_id, trigger, reaction)
            else:
                msg = u'[Fehler] Keine Antwort definiert, bitte response: einfügen (kann Tags enthalten: #person, #chan)'
        else:
            msg = u'[Fehler] Zu wenig Text angegeben!'
        self.parent.privmsg(msg, params.channel)

    def info(self, params):
        # Kommando !fact, ruft einzelnes Zufälliges Fact ab oder sucht einzelnes Fact nach Text
        if len(params.args) >= 1:
            trigger = self.db_cursor.execute(
                u"SELECT id, reaction, trigger, last_run from command_triggers WHERE trigger like '%" + params.follow + "%' or reaction like '%" + params.follow + "%' ORDER BY Random() LIMIT 1").fetchall()
            if len(trigger) > 0:
                msg = u"[§%s gelaufen: %s] %s = %s" % (trigger[0][0], trigger[0][3], trigger[0][1], trigger[0][2])
            else:
                msg = u'[Fehler] Keine passenden Trigger gefunden!'
        else:
            msg = u'[Fehler] kein Suchstring angegeben!'
        self.parent.privmsg(msg, params.channel)
