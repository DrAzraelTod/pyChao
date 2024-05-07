#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import socket
import time
import config
import getopt
import re


class Parameters(object):
    def __init__(self, channel, command, target, message, args='', query=False):
        self.channel = channel
        self.command = command
        self.target = target
        self.message = message
        self.follow = " ".join(args)
        self.args \
            = args
        self.whole_string = command + ' ' + self.follow
        self.query = query


class Logger(object):
    def __init__(self, file):
        self.file = file

    def log(self, message):
        '''Write a message to the file.'''
        timestamp = time.strftime('[%H:%M:%S]', time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


def get_int(stringvar):
    try:
        return int(stringvar)
    except:
        return 0


def encode_msg(msg):
    encodings = (
        'utf-8', 'latin_1', 'latin2', 'iso8859_15', 'windows-1250', 'windows-1252', 'ascii', 'utf-16', 'cp037',
        'cp437',
        'cp500', 'cp852', 'cp850', 'cp1140')
    for enc in encodings:
        try:
            return msg.decode(enc)
        except:
            if enc == encodings[-1]:
                return msg
            continue


class PyChao(object):
    def __init__(self, conf):
        self.msgwaitlist = []
        self.config = conf.data

        self.commands = {}

        self.import_modules()
        self.connect()

    def print_err(self, error):
        if 'error' in self.config['show messages']:
            print(u'[Fehler] %s' % error)

    def print_notice(self, ntc):
        if 'notice' in self.config['show messages']:
            print(u'[Anmerkung] %s' % encode_msg(ntc))

    def print_status(self, status):
        if 'routine' in self.config['show messages']:
            print(status)

    def import_modules(self):
        cfg = self.config['modules']
        for mod in cfg:
            tempmod = __import__(cfg[mod]['file'], )
            tempinst = getattr(
                tempmod, cfg[mod]['class'])(self, cfg[mod]['config'])

    def register_callback(self, command, callback, helptext, regex=False):
        if command in self.commands:
            return
        self.commands[command] = [callback, helptext, regex]

    def await_answer(self, msg_array, callback):
        self.msgwaitlist.append([msg_array, callback])
        self.print_status('Eintrag zur Waitlist hinzugefügt: %s' % msg_array)

    def identify_yourself(self):
        self.privmsg('identify %s' % self.config['password'], 'nickserv')

    def connect(self):
        self.print_status("connecting to " + self.config['host'] + ':' + str(self.config['port']))
        for res in socket.getaddrinfo(self.config['host'], self.config['port'], socket.AF_UNSPEC):
            af, socktype, proto, canonname, sa = res
            self.socket = None
            try:
                self.print_status("trying: " + str(res))
                self.socket = socket.socket(af, socktype, proto)
                self.socket.settimeout(500)
            except socket.error as msg:
                self.print_err(msg)
                continue
            try:
                self.print_status("establishing connection")
                self.socket.connect(sa)
            except socket.error as msg:
                self.print_err(msg)
                self.socket.close()
                continue
            break
        self.send('NICK %s\r\n' % self.config['nickname'])
        self.send('USER %s %s bla :%s\r\n' % (self.config['ident'], self.config['host'],
                                              self.config['realname']))
        for channel in self.config['channels']:
            self.join(channel)
        self.identify_yourself()
        readbuffer = ''
        while True:
            readbuffer = readbuffer + self.socket.recv(1024).decode('utf-8')
            temp = readbuffer.split('\n')
            readbuffer = temp.pop()

            for line in temp:
                self.print_status(line)
                line = encode_msg(line)
                line = line.rstrip()
                line = line.split()
                if line[0] == 'PING':
                    self.send('PONG %s' % line[1])
                if line[1] == 'PONG':
                    self.print_status('PONG-Recieved! %s' % line[3][1:])
                # ERROR :Closing Link:
                if line[0] == 'ERROR' and line[1] == ':Closing' and line[2] == 'Link:':
                    print("[Fehler] Verbindung extern getrennt")
                    sys.exit(2)
                if len(line) >= 4:
                    params = self.decode_msg(line)
                    # :NickServ!services@euirc.net NOTICE Sacred-Chao :This nickname is registered and protected.[…]
                    if line[1] == 'NOTICE':
                        if params.whole_string.startswith(u'This nickname is registered and protected.'):
                            self.identify_yourself()
                    if line[1] == 'PRIVMSG':
                        self.parse_cmd(params)
                i = 0
                for msg_callback_pair in self.msgwaitlist:
                    found = True
                    j = 0
                    for act_elem in msg_callback_pair[0]:
                        if act_elem != "" and act_elem != line[j]:
                            found = False
                        j = j + 1
                    if found:
                        msg_callback_pair[1](line)
                        self.print_status('Antwort gefunden: %s ' % msg_callback_pair[0])
                        self.msgwaitlist.remove(msg_callback_pair)

    def decode_msg(self, line):
        channel = line[2]
        command = line[3][1:]
        message = line[3:][1:]
        if len(line) >= 5:
            command_args = line[4:]
        else:
            command_args = []
        target = line[0][1:line[0].find('!')]
        query = False
        if channel.lower() == self.config['nickname'].lower():
            channel = target
            query = True
        return Parameters(channel, command, target, message, command_args, query)

    def parse_cmd(self, params):
        if params.command in self.commands:
            self.commands[params.command][0](params)
        else:
            ret = False
            for command_str in self.commands:
                command = self.commands[command_str]
                if command[2] and ret == False:
                    try:
                        if re.search(command_str, params.whole_string, re.I):
                            # self.print_status('Regex success: %s' % command_str)
                            ret = command[0](params)
                    except:
                        self.print_err('Invalid regex: %s' % command_str)

    def privmsg(self, line, target):
        text = u'PRIVMSG %s :%s' % (target, line)
        self.send(text)
        self.print_status(text)

    def join(self, channel):
        message = 'JOIN %s' % channel
        self.print_notice(message)
        self.send(message)

    def part(self, channel):
        message = 'PART %s' % channel
        self.print_notice(message)
        self.send(message)

    def send(self, msg):
        msg2 = msg.encode('utf-8') + '\r\n'.encode('utf-8')
        self.socket.send(msg2)


def usage():
    print("Folgende Parameter stehen zur Auswahl:")
    print(" -h --help               -> Zeigt diese Hilfe an")
    print(" -d --debug              -> Schaltet den Debugmodus ein")
    print(" -m --mode  <Parameter>  -> Aktiviert einen nutzerspezifischen Modus")
    print("Debug- und nutzerspezifischer Modus schließen sich aus")


if __name__ == '__main__':
    shortOptions = 'dm:h'
    longOptions = ['debug', 'mode=', 'help']
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortOptions, longOptions)
    except getopt.GetoptError as err:
        print("[Parameter-Fehler]  %s" % err)
        usage()
        sys.exit(2)
    mode = 'default'
    for o, a in opts:
        if o in ("--debug", "-d"):
            print('[Status] Debugmodus aktiv')
            mode = 'debug'
        elif o in ("--help", "-h"):
            usage()
            sys.exit()
        elif o in ("--mode", "-m"):
            if a != '':
                mode = a
            else:
                print('[Fehler] Nutzerspezifischer Modus soll aktiviert werden, es ist aber kein Modus ausgewählt.')
                sys.exit(2)
        else:
            print("[Fehler] Fehlerhafter Parameter")
            sys.exit(2)
    bot = PyChao(config.Config(mode))
