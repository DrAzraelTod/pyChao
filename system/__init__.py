# -*- coding: utf-8 -*-
import math, time, random


class ModSystem:
    ping_times = {}

    def __init__(self, parent, config):
        self.channel = None
        self.parent = parent
        self.config = config
        self.parent.register_callback('!commands', self.command_list, u'Listet alle eingebundenen Befehle auf')
        self.parent.register_callback('!help', self.help, u'Zeigt eine Hilfe zu beliebigen Befehlen an')
        #        self.parent.register_callback('=',self.eval, u'Löst eine Gleichung und ähnliches via eval()')
        self.parent.register_callback('!join', self.join, u'Betritt einen Channel, !leave zum Rauswerfen')
        self.parent.register_callback('!leave', self.part, u'Verlässt den aktuellen Channel')
        self.parent.register_callback('!utf', self.return_utf8,
                                      u'Gibt den übergebenen Text wieder aus (UTF-8-Codierungstest)')
        self.parent.register_callback('!ping', self.ping, u'Sendet einen PING an den Server')

    def ping(self, params):
        rand = str(random.randint(9999, 100000))
        self.ping_times[rand] = time.time()
        self.parent.await_answer(['', 'PONG', '', ':%s' % rand], self.pong)
        self.parent.send('PING ' + rand)
        self.channel = params.channel
        self.parent.privmsg('[ping] warte...', params.channel)

    def pong(self, params):
        if len(params) >= 4:
            key = str(params[3][1:])
            if key in self.ping_times:
                t = self.ping_times[key]
                now = time.time()
                diff = (now - float(t)) * 1000
                self.parent.privmsg(u'[pong] eingetroffen nach %dms' % diff, self.channel)
            else:
                self.parent.privmsg(u'[pong] eingetroffen, messung aber unmöglich - %s' % str(key), self.channel)
        else:
            self.parent.privmsg('[pong] eingetroffen', self.channel)

    def return_utf8(self, params):
        if len(params.args) >= 1:
            self.parent.privmsg(params.follow, params.channel)

    def join(self, params):
        if len(params.args) >= 1:
            self.parent.join(params.args[0])
            self.parent.print_notice('Channel %s wurde erfolgreich betreten.' % params.args[0])
        else:
            msg = u'Nicht genug Parameter angegeben. Welcher Channel soll betreten werden?'
            self.parent.print_err('Join mit den Parametern "%s" erzeugte Fehler' % params.follow)
            self.parent.privmsg(msg, params.channel)

    def part(self, params):
        if len(params.args) >= 1:
            channel = params.args[0]
        else:
            channel = params.channel
        self.parent.part(channel)
        self.parent.print_notice('Channel %s wurde verlassen.' % channel)

    def help(self, params):
        msg = u'[Hilfe] '
        if len(params.args) >= 1:
            if self.parent.commands.has_key(params.args[0]):
                msg = msg + self.parent.commands[params.args[0]][1]
            else:
                msg = msg + u'Kommando %s konnte nicht gefunden werden. Geben sie !commands ein um eine Liste zu erhalten!' % \
                      params.args[0]
        else:
            msg = msg + u'Geben sie dieses Kommando gefolgt von einer anderen Befehls-Zeichenkette an um Informationen über Befehle zu erhalten. Eine Liste der Befehle erhalten sie via !commands.'
        if len(msg) > 8:
            self.parent.print_status(msg)
        else:
            self.parent.print_err('Hilfe leer - %s' % msg)
        self.parent.privmsg(msg, params.channel)

    def eval(self, params):
        safe_list = self.config['eval_allowed']
        safe_dict = dict([(k, locals().get(k, None)) for k in safe_list])
        safe_dict['abs'] = abs
        if len(params.follow) > 1:
            try:
                msg = '[Eval] %s' % eval(params.follow, {"__builtins__": None}, vars(math))
                self.parent.print_notice('eval("%s") erfolgreich ausgeführt' % params.follow)
            except:
                self.parent.print_err('Eval "%s" verursachte Kritischen Fehler' % params.follow)
                msg = 'Eval Fehlgeschlagen'
        else:
            msg = '[Fehler] Nicht genug Parameter angegeben. Was soll eval() tun?'
            self.parent.print_status('Eval ohne Parameter aufgerufen')
        self.parent.privmsg(msg, params.channel)

    def command_list(self, params):
        msg = u'[Befehle]'
        for command in self.parent.commands:
            if not self.parent.commands[command][2]:
                msg = msg + ' %s' % command
        if len(msg) > 10:
            self.parent.print_status(msg)
        else:
            self.parent.print_err('Befehlsliste - %s' % msg)
            msg = u'[Fehler] Keine Befehle gefunden... o0'
        self.parent.privmsg(msg, params.channel)
