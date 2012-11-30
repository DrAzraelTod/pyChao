# -*- coding: utf-8 -*-
from ddate import *
from datetime import *

class mod_ddate(object):
    def __init__(self,parent,config):
        parent.register_callback('!date',self.date,u'Show Date')
        parent.register_callback('!time',self.time,u'Show Time')
        self.parent = parent
        self.config = config

    def date(self,params):
        self.parent.print_notice(u'Date aufgerufen')
        x = ddate()
        msg = u""
        if(len(params.args) == 0):
            x.fromDate(date.today())
            msg = u'Today is ' + str(x)
        else:
            try:
                self.parent.print_notice(params.args)
                d = datetime.strptime(params.args[0], "%d.%m.%Y").date()
                x.fromDate(d)
                msg = str(x)
            except Exception, inst:
                self.parent.print_notice(inst)
                msg = params.target + u': FNORD!'
        self.parent.privmsg(msg, params.channel)

    def time(self,params):
        self.parent.print_notice(u'Time aufgerufen')
        self.parent.privmsg("In my timezone it is " + datetime.now().strftime("%H:%M:%S"), params.channel)    
