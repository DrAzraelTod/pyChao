# -*- coding: utf-8 -*-
import math
import pysvn
import time

class mod_system:
    def __init__(self, parent,config):
        self.parent = parent
        self.config = config
        self.parent.register_callback('!commands',self.command_list,u'Listet alle eingebundenen Befehle auf')
        self.parent.register_callback('!help',self.help,u'Zeigt eine Hilfe zu beliebigen Befehlen an')
#        self.parent.register_callback('=',self.eval, u'Löst eine Gleichung und ähnliches via eval()')
        self.parent.register_callback('!join',self.join, u'Betritt einen Channel, !leave zum Rauswerfen')
        self.parent.register_callback('!leave',self.part, u'Verlässt den aktuellen Channel')
        self.parent.register_callback('!lversion', self.long_version, u'Zeigt die aktuelle Version an')
        self.parent.register_callback('!version', self.short_version, u'Zeigt die aktuelle Version an')
        self.parent.register_callback('!utf', self.returnutf8, u'Gibt den übergebenen Text wieder aus (UTF-8-Codierungstest)')
        self.parent.register_callback('!ping', self.ping, u'Sendet einen PING an den Server')

    def ping(self,params):
        rand = "123456"
        self.parent.await_answer(['','PONG','', ':%s' % rand],self.pong)
        self.parent.send('PING '+rand)
        self.channel = params.channel
        self.parent.privmsg('[ping] warte...',params.channel)
        
    def pong(self,line):
        self.parent.privmsg('[pong] eingetroffen',self.channel)
        
    def returnutf8(self,params):
        if(len(params.args)>=1):
            self.parent.privmsg(params.follow,params.channel)
        
    def join(self,params):
        if(len(params.args)>=1):
            self.parent.join(params.args[0])
            self.parent.print_notice('Channel %s wurde erfolgreich betreten.' % params.args[0])
        else:
            msg = u'Nicht genug Parameter angegeben. Welcher Channel soll betreten werden?'
            self.parent.print_err('Join mit den Parametern "%s" erzeugte Fehler' % params.follow)
            self.parent.privmsg(msg,params.channel)
    
    def part(self,params):
        if(len(params.args)>=1):
            channel = params.args[0]
        else:
            channel = params.channel
        self.parent.part(channel)
        self.parent.print_notice('Channel %s wurde verlassen.' % channel)
                
    def help(self,params):
        msg = u'[Hilfe] '
        if(len(params.args)>=1):
            if self.parent.commands.has_key(params.args[0]):
                msg = msg + self.parent.commands[params.args[0]][1]
            else:
                msg = msg + u'Kommando %s konnte nicht gefunden werden. Geben sie !commands ein um eine Liste zu erhalten!' % params.args[0]
        else:
            msg = msg + u'Geben sie dieses Kommando gefolgt von einer anderen Befehls-Zeichenkette an um Informationen über Befehle zu erhalten. Eine Liste der Befehle erhalten sie via !commands.'
        if len(msg)>8:
            self.parent.print_status(msg)
        else:
            self.parent.print_err('Hilfe leer - %s' % msg)
        self.parent.privmsg(msg,params.channel)

    def eval(self,params):
        safe_list = self.config['eval_allowed']
        safe_dict = dict([ (k, locals().get(k, None)) for k in safe_list ])
        safe_dict['abs'] = abs
        if len(params.follow)>1:
            try:
                msg = '[Eval] %s' % eval(params.follow,{"__builtins__":None},vars(math))
                self.parent.print_notice('eval("%s") erfolgreich ausgeführt' % params.follow)
            except:
                self.parent.print_err('Eval "%s" verursachte Kritischen Fehler' % params.follow)
                msg = 'Eval Fehlgeschlagen'
        else:
            msg = '[Fehler] Nicht genug Parameter angegeben. Was soll eval() tun?'
            self.parent.print_status('Eval ohne Parameter aufgerufen')
        self.parent.privmsg(msg,params.channel)
        
        
    def command_list(self,params):
        msg = u'[Befehle]'
        for command in self.parent.commands:
            if (self.parent.commands[command][2] == False):
                msg = msg + ' %s' % command
        if len(msg)>10:
            self.parent.print_status(msg)
        else:
            self.parent.print_err('Befehlsliste - %s' % msg)
            msg = u'[Fehler] Keine Befehle gefunden... o0'
        self.parent.privmsg(msg,params.channel)

    def short_version(self, params):
        c = pysvn.Client()
        e = c.info('.')
        self.parent.privmsg(u'pyChao, rev: ' + str(e.revision.number) + ', committed by: ' + e.commit_author, params.channel)

    def long_version(self, params):
        c = pysvn.Client()
        e = c.info('.')
        self.parent.privmsg(u'URL       : ' + e.url, params.channel)
        self.parent.privmsg(u'Revision  : ' + str(e.revision.number), params.channel)
        self.parent.privmsg(u'Committer : ' + e.commit_author, params.channel)
        self.parent.privmsg(u'Time      : ' + time.strftime(u'%a, %d %b %Y %H:%M:%S', time.localtime(e.commit_time)), params.channel)

