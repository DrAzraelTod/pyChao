# -*- coding: utf-8 -*-
import re


def which(program):
    import os

    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    file_path, file_name = os.path.split(program)
    if file_path:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


class ModCalc(object):

    def __init__(self, parent, config):

        self.config = config
        self.parent = parent
        if which("bc") is None:
            parent.register_callback(u'=', self.mod_calc, 'Calculates Values')
        else:
            parent.register_callback(u'=', self.mod_calc_bc, 'Calculates Values')

    def mod_calc(self, params):
        if len(params.args) > 0:
            formel = str(params.follow)
            formel = formel.replace("^", "**")
            formel = re.sub('([a-zA-Z]|\:|\,|\$|\`|\!|\@|\#|\$|\&|\{|\}|\[|\]|\~|\?|\<|\>|\|)', "", formel)
            try:
                result = float(eval(formel))
            except:
                result = "Formel nicht Erlaubt!"
            self.parent.privmsg(u'result: ' + str(result), params.channel)
        else:
            self.parent.privmsg(u'Bitte !calc <Formel> eingeben', params.channel)

    def mod_calc_bc(self, params):
        import random, os
        from commands import getstatusoutput
        try:
            formel = str(params.follow)
            formel = re.sub('([a-zA-Z]|\,|\$|\`|\!|\@|\#|\$|\&|\{|\}|\[|\]|\~|\?|\<|\>|\|)', "", formel)
            filename = os.path.join(os.path.dirname(__file__), str(random.random())).replace(u'\\', '/')
            f = open(filename, 'w')
            f.write(formel + "\n")
            f.write("quit")
            f.close()
            result = getstatusoutput("bc --quiet --mathlib -- %s" % filename)
            os.unlink(filename)
            result = float(result[1])
        except:
            result = "Formel nicht Erlaubt!"

        self.parent.privmsg(u'result: ' + str(result), params.channel)
