# -*- coding: utf-8 -*-
import re

class mod_calc(object):

    def which(self, program):
        import os
        def is_exe(fpath):
            return os.path.exists(fpath) and os.access(fpath, os.X_OK)
        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file
        return None
    
    
    def __init__(self,parent,config):
       
        self.config = config
        self.parent = parent
        if self.which("bc") == None:
            parent.register_callback(u'=', self.modcalc, 'Calculates Values')
        else:
            parent.register_callback(u'=', self.modcalcbc, 'Calculates Values')

    def modcalc(self, params):
        if len(params.args) > 0:
            formel = str(params.follow)
            formel = formel.replace("^","**")
            formel = re.sub('([a-zA-Z]|\:|\,|\$|\`|\!|\@|\#|\$|\&|\{|\}|\[|\]|\~|\?|\<|\>|\|)',"",formel)
            try:
                result = float(eval(formel))
            except:
                result = "Formel nicht Erlaubt!"
            self.parent.privmsg(u'result: '+str(result), params.channel)
        else:
            self.parent.privmsg(u'Bitte !calc <Formel> eingeben', params.channel)
            
    def modcalcbc(self, params):
        import random, os
        from commands import getstatusoutput
        try:
            formel = str(params.follow)
            formel = re.sub('([a-zA-Z]|\,|\$|\`|\!|\@|\#|\$|\&|\{|\}|\[|\]|\~|\?|\<|\>|\|)',"",formel)
            filename = os.path.join(os.path.dirname(__file__), str(random.random())).replace(u'\\','/')
            f = open(filename, 'w')
            f.write(formel+"\n")
            f.write("quit")
            f.close()
            result = getstatusoutput("bc --quiet --mathlib -- %s" % filename)
            os.unlink(filename)
            result = float(result[1])
        except:
            result = "Formel nicht Erlaubt!"
        
        self.parent.privmsg(u'result: '+str(result), params.channel)
    
    
    
    
    
    
    
    
    

