# -*- coding: utf-8 -*-
import feedparser

class mod_rss:
    def __init__(self,parent,config):
        self.config = config
        self.parent = parent
        for key in config['feeds'].keys():
            self.parent.print_notice('[Newsfeed registriert] %s - %s' % (key,config['feeds'][key]))
            parent.register_callback('!%s'%key,self.rss_factory(config['feeds'][key]),config['help']+" (%s verweist auf %s)" % (key, config['feeds'][key]))

    def rss_factory(self, url):
        prss = self.postrss
        def rss_func(params):
            prss(params, url)
        return rss_func

    def rsstextsearch(self,params,feed):
        msg = u''
        i = 1
        for e in feed['entries']:
            if i <= self.config['defaultlines']:
                if e.title.lower().find(params.follow.lower())!=-1:
                    self.postfeeditem(e,params)
                    i = i+1
        if i <= 1:
            msg = '[Fehler] Text konnte nicht gefunden Werden'
        if msg!='':
            self.parent.privmsg(msg,params.channel)
    
    def postrss(self, params, url):
        didit = False
        ignore = False
        e = feedparser.parse(url)
        blah = u'dieserfeedistziemlichsehrleerSDFAFIASDIASDAsadaAWD"§QASDA"qdasDASA'
        if(e.feed.get('title', blah) == blah):
            self.parent.print_err('Feed "%s" nicht gefunden?' % url)
            msg = '[Fehler] Feed "%s" ist leer' % url
        else:
            if(len(params.args)==0):
                first = 1
                last = self.config['defaultlines']
            else:
                farg = self.parent.get_int(params.args[0])
                if farg!=0:
                    if(len(params.args)>=2):
                        larg = self.parent.get_int(params.args[1])
                        if farg!=0:
                            first = farg
                        else:
                            first = 1
                        if larg!=0:
                            last = larg
                        else:
                            last = first + self.config['defaultlines']
                    else:
                            first = 1
                            last = farg
                else:
                    self.rsstextsearch(params,e)
                    first = 123
                    last = 0
                    ignore = True
            self.parent.print_notice(u'Newsfeed %s wird mit first=%s und last=%s abgerufen' % (url, first, last))
            if(last-first<self.config['maxlines']) and (last-first>=0) and not ignore:
                if(len(e['entries'])>=last):
                    first = first -1
                    last = last -1
                    didit = True
                    while (first<=last):
                        f=e['entries'][first]
                        self.postfeeditem(f,params)
                        first = first+1
                else:
                    msg = u'[Fehler] zu wenig Einträge gefunden um bis zum %s. Element zu iterieren' % last
            else:
                msg = u'[Fehler] fehlerhafte Parameter (Anzahl oder Start und Endpunkt), evtl. aus Spamschutzgründen abgefangen'
        if not (didit or ignore):
            self.parent.privmsg(msg,params.channel)

    def postfeeditem(self,item,params):
        self.parent.print_status('Title: %s' % item.title)
        
        if (hasattr(item, 'title')):
            title = item.title
        else:
            title = 'Titel leer'
        
        if (hasattr(item, 'link')):
            link = item.link
        else:
            link = 'Kein Link gefunden'

        title = title.replace(u'\n',u' ') 
        if len(title) >= self.config['maxtitlelen']:
            title = title[:self.config['maxtitlelen']]+u'...'
            msg = u'[%s] %s' % (title, link)
        else:    
            msg = u'[%s] %s' % (title, link)
        
        self.parent.privmsg(msg,params.channel)
