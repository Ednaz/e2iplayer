# -*- coding: utf-8 -*-
 
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.ihost import IHost, CDisplayListItem, RetHost, CUrlItem
import Plugins.Extensions.IPTVPlayer.libs.pCommon as pCommon
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, CSearchHistoryHelper, CSelOneLink, GetTmpDir, GetCookieDir, iptv_system, GetPluginDir, byteify
from Plugins.Extensions.IPTVPlayer.iptvdm.iptvdh import DMHelper
from Plugins.Extensions.IPTVPlayer.libs.urlparser import urlparser 
from Plugins.Extensions.IPTVPlayer.tools.iptvfilehost import IPTVFileHost
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _, SetIPTVPlayerLastHostError, GetIPTVSleep, GetIPTVNotify
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.utils import clean_html 
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import decorateUrl, getDirectM3U8Playlist, unpackJSPlayerParams, TEAMCASTPL_decryptPlayerParams
###################################################
# FOREIGN import
###################################################
import re, urllib, urllib2, base64, math, hashlib, random
try:
    import simplejson
except:
    import json as simplejson   
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.config import config, ConfigSelection, ConfigYesNo, ConfigText, ConfigInteger, getConfigListEntry, ConfigPIN, ConfigDirectory
from time import sleep, time as time_time
from os import remove as os_remove, path as os_path, system as os_system
import urlparse
###################################################
# E2 GUI COMMPONENTS 
###################################################
from Plugins.Extensions.IPTVPlayer.tools.e2ijs import js_execute
###################################################
# Config options for HOST
###################################################
config.plugins.iptvplayer.xxxwymagajpin = ConfigYesNo(default = True)
config.plugins.iptvplayer.xxxlist = ConfigDirectory(default = "/hdd/")
config.plugins.iptvplayer.xxxsortuj = ConfigYesNo(default = True)
config.plugins.iptvplayer.xxxsearch = ConfigYesNo(default = False)
config.plugins.iptvplayer.xxxsortmfc = ConfigYesNo(default = False)
config.plugins.iptvplayer.xxxsortall = ConfigYesNo(default = True)
config.plugins.iptvplayer.camsoda = ConfigSelection(default="0", choices = [("0",_("https")), ("1",_("rtmp"))])
config.plugins.iptvplayer.xhamstertag = ConfigYesNo(default = False)
config.plugins.iptvplayer.bonga = ConfigSelection(default="0", choices = [("0",_("https")), ("1",_("rtmp"))])
config.plugins.iptvplayer.cam4 = ConfigSelection(default="0", choices = [("0",_("https")), ("1",_("rtmp"))])
config.plugins.iptvplayer.fotka = ConfigSelection(default="0", choices = [("0",_("https")), ("1",_("rtmp"))])
config.plugins.iptvplayer.xxxupdate = ConfigYesNo(default = False)
config.plugins.iptvplayer.xxxzbiornik = ConfigYesNo(default = False)
config.plugins.iptvplayer.xxx4k = ConfigYesNo(default = False)

def GetConfigList():
    optionList = []
    optionList.append( getConfigListEntry(_("Pin protection for plugin")+" :", config.plugins.iptvplayer.xxxwymagajpin ) )
    optionList.append( getConfigListEntry(_("Path to xxxlist.txt :"), config.plugins.iptvplayer.xxxlist) )
    optionList.append( getConfigListEntry(_("Sort xxxlist :"), config.plugins.iptvplayer.xxxsortuj) )
    optionList.append( getConfigListEntry(_("Sort Myfreecams :"), config.plugins.iptvplayer.xxxsortmfc) )
    optionList.append( getConfigListEntry(_("Global search :"), config.plugins.iptvplayer.xxxsearch) )
    optionList.append( getConfigListEntry(_("Global sort :"), config.plugins.iptvplayer.xxxsortall) )
    optionList.append( getConfigListEntry(_("Bongacams stream :"), config.plugins.iptvplayer.bonga) )
    optionList.append( getConfigListEntry(_("Cam4 stream :"), config.plugins.iptvplayer.cam4) )
    optionList.append( getConfigListEntry(_("Camsoda stream :"), config.plugins.iptvplayer.camsoda) )
    optionList.append( getConfigListEntry(_("Fotka.pl stream :"), config.plugins.iptvplayer.fotka) )
    optionList.append( getConfigListEntry(_("Add tags to XHAMSTER :"), config.plugins.iptvplayer.xhamstertag) )
    optionList.append( getConfigListEntry(_("Show Profiles in ZBIORNIK MINI :"), config.plugins.iptvplayer.xxxzbiornik) )
    optionList.append( getConfigListEntry(_("Show changelog :"), config.plugins.iptvplayer.xxxupdate) )
    optionList.append( getConfigListEntry(_("Playback UHD :"), config.plugins.iptvplayer.xxx4k) )

    return optionList
###################################################

###################################################
# Title of HOST
###################################################
def gettytul():
    return 'XXX'

class IPTVHost(IHost):
    LOGO_NAME = 'XXXlogo.png'
    PATH_TO_LOGO = resolveFilename(SCOPE_PLUGINS, 'Extensions/IPTVPlayer/icons/logos/' + LOGO_NAME )

    def __init__(self):
        printDBG( "init begin" )
        self.host = Host()
        self.prevIndex = []
        self.currList = []
        self.prevList = []
        printDBG( "init end" )
        
    def isProtectedByPinCode(self):
        return config.plugins.iptvplayer.xxxwymagajpin.value
    
    def getLogoPath(self):  
        return RetHost(RetHost.OK, value = [self.PATH_TO_LOGO])

    def getInitList(self):
        printDBG( "getInitList begin" )
        self.prevIndex = []
        self.currList = self.host.getInitList()
        self.host.setCurrList(self.currList)
        self.prevList = []
        printDBG( "getInitList end" )
        return RetHost(RetHost.OK, value = self.currList)

    def getListForItem(self, Index = 0, refresh = 0, selItem = None):
        printDBG( "getListForItem begin" )
        self.prevIndex.append(Index)
        self.prevList.append(self.currList)
        self.currList = self.host.getListForItem(Index, refresh, selItem)
        printDBG( "getListForItem end" )
        return RetHost(RetHost.OK, value = self.currList)

    def getPrevList(self, refresh = 0):
        printDBG( "getPrevList begin" )
        if(len(self.prevList) > 0):
            self.prevIndex.pop()
            self.currList = self.prevList.pop()
            self.host.setCurrList(self.currList)
            printDBG( "getPrevList end OK" )
            return RetHost(RetHost.OK, value = self.currList)
        else:
            printDBG( "getPrevList end ERROR" )
            return RetHost(RetHost.ERROR, value = [])

    def getCurrentList(self, refresh = 0):
        printDBG( "getCurrentList begin" )
        printDBG( "getCurrentList end" )
        return RetHost(RetHost.OK, value = self.currList)

    def getLinksForVideo(self, Index = 0, item = None):
        return RetHost(RetHost.NOT_IMPLEMENTED, value = [])
        
    def getResolvedURL(self, url):
        printDBG( "getResolvedURL begin" )
        if url != None and url != '':        
            ret = self.host.getResolvedURL(url)
            if ret != None and ret != '':        
               printDBG( "getResolvedURL ret: "+str(ret))
               list = []
               list.append(ret)
               printDBG( "getResolvedURL end OK" )
               return RetHost(RetHost.OK, value = list)
            else:
               printDBG( "getResolvedURL end" )
               return RetHost(RetHost.NOT_IMPLEMENTED, value = [])                
        else:
            printDBG( "getResolvedURL end" )
            return RetHost(RetHost.NOT_IMPLEMENTED, value = [])

    def getSearchResults(self, pattern, searchType = None):
        printDBG( "getSearchResults begin" )
        printDBG( "getSearchResults pattern: " +pattern)
        self.prevIndex.append(0)
        self.prevList.append(self.currList)
        self.currList = self.host.getSearchResults(pattern, searchType)
        printDBG( "getSearchResults end" )
        return RetHost(RetHost.OK, value = self.currList)

    ###################################################
    # Additional functions on class IPTVHost
    ###################################################

class Host:
    XXXversion = "2018.12.04.1"
    XXXremote  = "0.0.0.0"
    currList = []
    MAIN_URL = ''
    SEARCH_proc = ''
    
    def __init__(self):
        printDBG( 'Host __init__ begin' )
        self.cm = pCommon.common()
        self.up = urlparser() 
        self.history = CSearchHistoryHelper('xxx')
        self.currList = []
        printDBG( 'Host __init__ end' )

    def setCurrList(self, list):
        printDBG( 'Host setCurrList begin' )
        self.currList = list
        printDBG( 'Host setCurrList end' )
        return 

    def getInitList(self):
        printDBG( 'Host getInitList begin' )
        _url = 'https://gitlab.com/iptv-host-xxx/iptv-host-xxx/raw/master/IPTVPlayer/hosts/hostXXX.py'
        query_data = { 'url': _url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        try:
           data = self.cm.getURLRequestData(query_data)
           #printDBG( 'Host init data: '+data )
           r=self.cm.ph.getSearchGroups(data, '''XXXversion = ['"]([^"^']+?)['"]''', 1, True)[0]
           if r:
              printDBG( 'XXXremote = '+r )
              self.XXXremote=r
        except:
           printDBG( 'Host init query error' )
        self.currList = self.listsItems(-1, '', 'main-menu')
        printDBG( 'Host getInitList end' )
        return self.currList

    def getListForItem(self, Index = 0, refresh = 0, selItem = None):
        printDBG( 'Host getListForItem begin' )
        valTab = []
        if len(self.currList[Index].urlItems) == 0:
           return valTab
        valTab = self.listsItems(Index, self.currList[Index].urlItems[0], self.currList[Index].urlSeparateRequest)
        self.currList = valTab
        printDBG( 'Host getListForItem end' )
        return self.currList

    def getSearchResults(self, pattern, searchType = None):
        printDBG( "Host getSearchResults begin" )
        printDBG( "Host getSearchResults pattern: " +pattern)
        valTab = []
        valTab = self.listsItems(-1, pattern, 'SEARCH')
        self.currList = valTab
        printDBG( "Host getSearchResults end" )
        return self.currList

    def _cleanHtmlStr(self, str):
        str = str.replace('<', ' <').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        return clean_html(str).strip()

    def getPage(self, baseUrl, cookie_domain, cloud_domain, params={}, post_data=None):
        COOKIEFILE = os_path.join(GetCookieDir(), cookie_domain)
        self.USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.120 Chrome/37.0.2062.120 Safari/537.36'
        self.HEADER = {'User-Agent': self.USER_AGENT, 'Accept': 'text/html'}
        params['cloudflare_params'] = {'domain':cloud_domain, 'cookie_file':COOKIEFILE, 'User-Agent':self.USER_AGENT}
        return self.cm.getPageCFProtection(baseUrl, params, post_data)

    def getPage4k(self, baseUrl, cookie_domain, cloud_domain, params={}, post_data=None):
        COOKIEFILE = os_path.join(GetCookieDir(), cookie_domain)
        self.USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0'
        def _getFullUrl(url):
            if self.cm.isValidUrl(url):
                return url
            else:
                return urlparse.urljoin(baseUrl, url) 
        if params == {}: params = dict(self.defaultParams)
        params['cookie_items'] = {'xxx':'ok'}
        #params['cloudflare_params'] = {'domain':self.up.getDomain('http://movie4k.org/'), 'cookie_file':COOKIEFILE, 'User-Agent':self.USER_AGENT, 'full_url_handle':_getFullUrl}

        params['cloudflare_params'] = {'domain':cloud_domain, 'cookie_file':COOKIEFILE, 'User-Agent':self.USER_AGENT, 'full_url_handle':_getFullUrl}
        return self.cm.getPageCFProtection(baseUrl, params, post_data)

    def _getPage(self, url, addParams = {}, post_data = None):
        
        try:
            import httplib
            def patch_http_response_read(func):
                def inner(*args):
                    try:
                        return func(*args)
                    except httplib.IncompleteRead, e:
                        return e.partial
                return inner
            prev_read = httplib.HTTPResponse.read
            httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)
        except Exception: printExc()
        sts, data = self.cm.getPage(url, addParams, post_data)
        try: httplib.HTTPResponse.read = prev_read
        except Exception: printExc()
        return sts, data

    def get_Page(self, baseUrl, addParams={}, post_data=None):
        if addParams == {}: addParams = dict(self.defaultParams)
        return self.cm.getPage(baseUrl, addParams, post_data)

    def listsItems(self, Index, url, name = ''):
        printDBG( 'Host listsItems begin' )
        printDBG( 'Host listsItems url: '+url )
        valTab = []
        self.format4k = config.plugins.iptvplayer.xxx4k.value

        if name == 'main-menu':
           printDBG( 'Host listsItems begin name='+name )
           if self.XXXversion <> self.XXXremote and self.XXXremote <> "0.0.0.0":
              valTab.append(CDisplayListItem('---UPDATE---','UPDATE MENU',        CDisplayListItem.TYPE_CATEGORY,           [''], 'UPDATE',  '', None)) 
           valTab.append(CDisplayListItem('XHAMSTER',       'xhamster.com',       CDisplayListItem.TYPE_CATEGORY, ['https://xhamster.com/categories'],     'xhamster','http://eu-st.xhamster.com/images/tpl2/logo.png', None)) 
           valTab.append(CDisplayListItem('HOME MOVIES TUBE',     'http://www.homemoviestube.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.homemoviestube.com/channels/'],'HomeMoviesTube', 'http://www.homemoviestube.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('ZBIORNIK MINI',     'https://mini.zbiornik.com', CDisplayListItem.TYPE_CATEGORY, ['https://mini.zbiornik.com/filmy'],'ZBIORNIKMINI', 'https://static.zbiornik.com/upimg/0160d9c44a354d20e81f0e6df5fe832e.jpg', None)) 
           valTab.append(CDisplayListItem('HCLIPS',     'http://www.hclips.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.hclips.com/categories/'],'HCLIPS', 'http://www.hclips.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('4TUBE',          'www.4tube.com',      CDisplayListItem.TYPE_CATEGORY, ['https://www.4tube.com'],          'FUX',   'http://cdn1.ht.ui.4tube.com/assets/img/layout/4tube-logo-1f503fd81c.png', None)) 
           valTab.append(CDisplayListItem('EPORNER',        'www.eporner.com',    CDisplayListItem.TYPE_CATEGORY, ['http://www.eporner.com/categories/'],   'eporner', 'http://static.eporner.com/new/logo.png', None)) 
           valTab.append(CDisplayListItem('TUBE8',          'www.tube8.com',      CDisplayListItem.TYPE_CATEGORY, ['http://www.tube8.com/categories.html'], 'tube8',   'http://cdn1.static.tube8.phncdn.com/images/t8logo.png', None)) 
           valTab.append(CDisplayListItem('YOUPORN',        'wwww.youporn.com',   CDisplayListItem.TYPE_CATEGORY, ['http://www.youporn.com/categories/alphabetical/'],'youporn', 'https://fs.ypncdn.com/cb/bundles/youpornwebfront/images/l_youporn_black.png?v=9b34af679da9f8f8279fb875c7bcea555a784ec3', None)) 
           valTab.append(CDisplayListItem('PORNHUB',        'www.pornhub.com',    CDisplayListItem.TYPE_CATEGORY, ['http://www.pornhub.com/categories'],    'pornhub', 'https://bi.phncdn.com/www-static/images/press/logos/Pornhub.png', None)) 
           valTab.append(CDisplayListItem('HDPORN',         'www.hdporn.net',     CDisplayListItem.TYPE_CATEGORY, ['http://www.hdporn.net/channels/'],      'hdporn',  'http://www.hdporn.com/gfx/logo.jpg', None)) 
           valTab.append(CDisplayListItem('REDTUBE',        'www.redtube.com',    CDisplayListItem.TYPE_CATEGORY, ['http://www.redtube.com/categories'],      'redtube', 'http://img02.redtubefiles.com/_thumbs/design/logo/redtube_260x52_black.png', None)) 
           valTab.append(CDisplayListItem('HENTAIGASM',     'hentaigasm.com',     CDisplayListItem.TYPE_CATEGORY, ['http://hentaigasm.com'],                'hentaigasm','http://hentaigasm.com/wp-content/themes/detube/images/logo.png', None)) 
           valTab.append(CDisplayListItem('XVIDEOS',        'www.xvideos.com',    CDisplayListItem.TYPE_CATEGORY, ['http://www.xvideos.com'],               'xvideos', 'http://emblemsbf.com/img/31442.jpg', None)) 
           valTab.append(CDisplayListItem('XNXX',           'www.xnxx.com',       CDisplayListItem.TYPE_CATEGORY, ['http://www.xnxx.com'],                  'xnxx',    'http://www.naughtyalysha.com/tgp/xnxx/xnxx-porn-recip.jpg', None)) 
           valTab.append(CDisplayListItem('BEEG',           'beeg.com',           CDisplayListItem.TYPE_CATEGORY, ['https://beeg.com'],                      'beeg',    'http://staticloads.com/img/logo/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNRABBIT',     'www.pornrabbit.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.pornrabbit.com/page/categories/'],'pornrabbit','https://www.pornrabbit.com/static/pornrabbit/img/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNHD',     'www.pornhd.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.pornhd.com/category'],'pornhd','https://pbs.twimg.com/profile_images/527104689444093952/PbRNZmMT_400x400.png', None)) 
           valTab.append(CDisplayListItem('AH-ME',     'www.ah-me.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.ah-me.com/channels.php'],'AH-ME','http://ahmestatic.fuckandcdn.com/ah-me/ahmestatic/v20/common/ah-me/img/logo.jpg', None)) 
           valTab.append(CDisplayListItem('AMATEURPORN',     'www.amateurporn.net', CDisplayListItem.TYPE_CATEGORY, ['http://www.amateurporn.net/channels/'],'AMATEURPORN', 'http://www.amateurporn.net/images/amateur-porn.png', None)) 
           valTab.append(CDisplayListItem('YOUJIZZ',     'http://www.youjizz.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.youjizz.com/categories'],'YOUJIZZ', 'http://www.sample-made.com/cms/content/uploads/2015/05/youjizz_logo-450x400.jpg', None)) 
           valTab.append(CDisplayListItem('DACHIX',     'http://www.dachix.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.dachix.com/categories'],'DACHIX', 'http://thumbs.dachix.com/images/dachixcom_logo_noir.png', None)) 
           valTab.append(CDisplayListItem('DRTUBER',     'http://www.drtuber.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.drtuber.com/categories'],'DRTUBER', 'http://static.drtuber.com/templates/frontend/mobile/images/logo.png', None)) 
           valTab.append(CDisplayListItem('TNAFLIX',     'https://www.tnaflix.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.tnaflix.com/categories'],'TNAFLIX', 'https://pbs.twimg.com/profile_images/1109542593/logo_400x400.png', None)) 
           valTab.append(CDisplayListItem('EL-LADIES - JUST-EROPROFILE',     'http://search.el-ladies.com', CDisplayListItem.TYPE_CATEGORY, ['http://search.el-ladies.com'],'EL-LADIES', 'http://amateurblogs.eroprofile.com/img/ep_new_gallery_header.png', None)) 
           valTab.append(CDisplayListItem('EXTREMETUBE',     'http://www.extremetube.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.extremetube.com/video-categories'],'EXTREMETUBE', 'http://www.wp-tube-plugin.com/feed-images/extremetube.png', None)) 
           valTab.append(CDisplayListItem('RUS.PORN',     'http://rus.porn', CDisplayListItem.TYPE_CATEGORY, ['http://rus.porn/'],'RUSPORN', 'http://mixporn24.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('PORN720',     'http://porn720.net/', CDisplayListItem.TYPE_CATEGORY, ['http://porn720.net/'],'PORN720', 'http://porn720.net/wp-content/themes/porn720/img/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNTREX',     'http://www.porntrex.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.porntrex.com/categories/'],'PORNTREX', 'https://www.porntrex.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNDOE',     'http://www.porndoe.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.porndoe.com/categories'],'PORNDOE', 'http://porndoe.com/themes/frontend/white/assets/images/logo_fb.jpg', None)) 
           valTab.append(CDisplayListItem('PORNfromCZECH',     'http://www.pornfromczech.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.pornfromczech.com/'],'PORNFROMCZECH', 'https://www.bing.com/th?id=OIP.LA7c-hQkzRto2v_bqXV1MQHaBJ&pid=Api', None)) 
           valTab.append(CDisplayListItem('FILMYPORNO',     'http://www.filmyporno.tv', CDisplayListItem.TYPE_CATEGORY, ['http://www.filmyporno.tv/channels/'],'FILMYPORNO', 'http://www.filmyporno.tv/templates/default_tube2016/images/logo.png', None)) 
           valTab.append(CDisplayListItem('CLIPHUNTER',     'http://www.cliphunter.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.cliphunter.com/categories/'],'CLIPHUNTER', 'http://www.cliphunter.com/gfx/new/logo.png', None)) 
           valTab.append(CDisplayListItem('EMPFLIX',     'http://www.empflix.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.empflix.com/categories.php'],'EMPFLIX', 'http://pornoracle.com/wp-content/uploads/2013/11/empflix1.jpg', None)) 
           #valTab.append(CDisplayListItem('PORNOHUB.SU',     'http://pornohub.su/', CDisplayListItem.TYPE_CATEGORY, ['https://pornohub.su/'],'PORNOHUB', 'http://st.pornohub.su/pornohub.png', None)) 
           valTab.append(CDisplayListItem('THUMBZILLA',     'http://www.thumbzilla.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.thumbzilla.com/'],'THUMBZILLA', 'https://cdn-d-static.pornhub.com/tz-static/images/pc/logo.png?cache=2016111010', None)) 
           valTab.append(CDisplayListItem('YUVUTU',     'http://www.yuvutu.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.yuvutu.com/categories/'],'YUVUTU', 'http://www.yuvutu.com/themes/yuvutu_v2/images/yuvutu_logo.png', None)) 
           valTab.append(CDisplayListItem('BEFUCK',     'http://befuck.com', CDisplayListItem.TYPE_CATEGORY, ['http://befuck.com/categories'],'BEFUCK', 'https://i.ytimg.com/vi/dmfQXL2HOfU/hqdefault.jpg', None)) 
           valTab.append(CDisplayListItem('PORNICOM',     'http://pornicom.com', CDisplayListItem.TYPE_CATEGORY, ['http://pornicom.com/categories/'],'PORNICOM', 'http://pornicom.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('HDZOG',     'http://www.hdzog.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.hdzog.com/categories/'],'HDZOG', 'https://pbs.twimg.com/profile_images/484686238402629632/5fzwWkJQ_bigger.png', None)) 
           valTab.append(CDisplayListItem('PORNOMENGE',     'https://www.pornomenge.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.pornomenge.com/kategorien/'],'PORNOMENGE', 'https://th.servitubes.com/videos/8/1/b/5/1/81b51795337b047be07d3b3790b97c923535dffb.mp4-preview-3.jpg', None)) 
           valTab.append(CDisplayListItem('TUBEPORNCLASSIC',     'http://tubepornclassic.com/', CDisplayListItem.TYPE_CATEGORY, ['http://tubepornclassic.com/categories/'],'TUBEPORNCLASSIC', 'http://www.tubepornclassic.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('KOLOPORNO',     'https://www.koloporno.com/', CDisplayListItem.TYPE_CATEGORY, ['https://www.koloporno.com/kategoriach/'],'KOLOPORNO', 'https://pbs.twimg.com/profile_images/638608521072934912/sqy78GQm.png', None)) 
           valTab.append(CDisplayListItem('REALGFPORN',     'https://www.realgfporn.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.realgfporn.com/channels/'],'REALGFPORN', 'https://www.realgfporn.com/assets/img/logo.png', None)) 
           #valTab.append(CDisplayListItem('FAAPY',     'http://faapy.com', CDisplayListItem.TYPE_CATEGORY, ['http://faapy.com'],'FAAPY', 'https://faapy.com/images_new/logo.png', None)) 
           valTab.append(CDisplayListItem('FUX',     'http://www.fux.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.fux.com'],'fux', 'https://cdn1-ht-ui.fux.com/assets/img/layout/fux-logo-dd6d006c2e.png', None)) 
           valTab.append(CDisplayListItem('PORNTUBE',     'http://www.porntube.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.porntube.com'],'PORNTUBE', 'https://designmodo.com/wp-content/uploads/2010/08/Porn-Tube-logo.png', None)) 
           valTab.append(CDisplayListItem('PORNERBROS',     'http://www.pornerbros.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.pornerbros.com'],'pornerbros', 'https://cdn1-ht-assets.pornerbros.com/PornerBros.png', None)) 
           valTab.append(CDisplayListItem('UPDATE TUBE',     'www.updatetube.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.updatetube.com'],'UpdateTube', 'http://updatetube.com/res/updatetube_com/img/logo.png', None)) 
           valTab.append(CDisplayListItem('PINKROD',     'www.pinkrod.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.pinkrod.com'],'UpdateTube', 'http://pinkrod.com/res/pinkrod_com/img/logo.png', None)) 
           valTab.append(CDisplayListItem('HOTSHAME',     'www.hotshame.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.hotshame.com'],'UpdateTube', 'http://hotshame.com/res/hotshame_com/img/logo.png', None)) 
           valTab.append(CDisplayListItem('THE NEW PORN',     'www.thenewporn.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.thenewporn.com'],'UpdateTube', 'http://thenewporn.com/res/thenewporn_com/img/logo.png?rnd=1', None)) 
           valTab.append(CDisplayListItem('MOVIEFAP',     'http://www.moviefap.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.moviefap.com/browse/'],'MOVIEFAP', 'http://www.moviefap.com/images/logo.gif', None)) 
           valTab.append(CDisplayListItem('YOURPORN.SEXY',     'https://yourporn.sexy', CDisplayListItem.TYPE_CATEGORY, ['https://yourporn.sexy/'],'yourporn', 'http://cdn.itsyourporn.com/assets/images/logo.jpg', None)) 
           valTab.append(CDisplayListItem('FREEOMOVIE',     'http://www.freeomovie.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.freeomovie.com'],'freeomovie', 'http://www.freeomovie.com/wp-content/uploads/2013/04/logo.png', None)) 
           valTab.append(CDisplayListItem('KATESTUBE',     'http://www.katestube.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.katestube.com/categories/'],'KATESTUBE', 'https://www.katestube.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('VPORN',     'https://www.vporn.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.vporn.com/tags/#'],'vporn', 'https://image.spreadshirtmedia.com/image-server/v1/mp/compositions/1012679167/views/1,width=300,height=300,backgroundColor=E8E8E8,version=1485256808/vporn-brand-dark.jpg', None)) 
           valTab.append(CDisplayListItem('HOTMOVS',     'http://hotmovs.com', CDisplayListItem.TYPE_CATEGORY, ['http://hotmovs.com/categories/'],'hotmovs', 'http://hotmovs.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNOXO',     'https://www.pornoxo.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.pornoxo.com'],'pornoxo', 'https://t.pornoxo.com/pxo/www/img/pxo/logo-b.gif', None)) 
           valTab.append(CDisplayListItem('PORNFREE',     'http://pornfree.tv', CDisplayListItem.TYPE_CATEGORY, ['http://pornfree.tv/categories/'],'pornfree', 'http://pornfree.tv/wp-content/uploads/2016/12/logo.png', None)) 
           valTab.append(CDisplayListItem('PINFLIX',     'http://www.pinflix.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.pinflix.com/category'],'pinflix', 'https://pbs.twimg.com/profile_images/568766044114657280/JYh2ZSF_.png', None)) 
           valTab.append(CDisplayListItem('UPORNIA',     'http://www.upornia.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.upornia.com/categories/'],'upornia', 'https://pbs.twimg.com/profile_images/603525677451640833/AE2qwJ5C_400x400.png', None)) 
           valTab.append(CDisplayListItem('TXXX',     'http://www.txxx.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.txxx.com/categories/'],'txxx', 'https://www.txxx.com/images/desktop-logo.png', None)) 
           valTab.append(CDisplayListItem('SUNPORNO',     'https://www.sunporno.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.sunporno.com/channels/'],'sunporno', 'https://sunstatic.fuckandcdn.com/sun/sunstatic/v31/common/sunporno/img/logo_top.png', None)) 
           valTab.append(CDisplayListItem('SEXU',     'http://sexu.com', CDisplayListItem.TYPE_CATEGORY, ['http://sexu.com/'],'sexu', 'http://sexu.com/images/ico-logo.png', None)) 
           valTab.append(CDisplayListItem('MOVIE4K  XXX',     'https://movie4k.org/xxx', CDisplayListItem.TYPE_CATEGORY, ['http://movie4k.org/xxx-updates.html'],'movie4k', 'https://i.imgur.com/KcrsgQi.png', None)) 
           valTab.append(CDisplayListItem('TUBEWOLF',     'http://www.tubewolf.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.tubewolf.com'],'tubewolf', 'http://images.tubewolf.com/logo.png', None)) 
           valTab.append(CDisplayListItem('ALPHAPORNO',     'http://www.alphaporno.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.alphaporno.com'],'tubewolf', 'http://images.alphaporno.com/logo.png', None)) 
           valTab.append(CDisplayListItem('ZEDPORN',     'http://zedporn.com', CDisplayListItem.TYPE_CATEGORY, ['https://zedporn.com'],'tubewolf', 'http://images.zedporn.com/new-logo.png', None)) 
           #valTab.append(CDisplayListItem('CROCOTUBE',     'http://crocotube.com', CDisplayListItem.TYPE_CATEGORY, ['http://crocotube.com'],'tubewolf', 'http://crocotube.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('ASHEMALETUBE',     'https://www.ashemaletube.com/', CDisplayListItem.TYPE_CATEGORY, ['https://www.ashemaletube.com/tags/'],'ASHEMALETUBE', 'https://adminex.ashemaletube.com/images/logo/ast.png', None)) 
           valTab.append(CDisplayListItem('MULEMAX',     'https://mulemax.com', CDisplayListItem.TYPE_CATEGORY, ['https://mulemax.com/categories'],'MULEMAX', 'https://mulemax.com/images/logo/logo.png', None)) 
           valTab.append(CDisplayListItem('STREAMPORN',     'https://streamporn.pw', CDisplayListItem.TYPE_CATEGORY, ['https://streamporn.pw'],'streamporn', 'https://streamporn.pw/wp-content/uploads/2018/05/fsfsfsf-1.png', None)) 
           valTab.append(CDisplayListItem('ONLINEPORNFREE',     'https://onlinepornfree.xyz/', CDisplayListItem.TYPE_CATEGORY, ['https://onlinepornfree.xyz/'],'onlinepornfree', 'https://onlinepornfree.xyz/wp-content/uploads/2018/09/onlinepornfree-1.png', None)) 

           if config.plugins.iptvplayer.xxxsortall.value:
               valTab.sort(key=lambda poz: poz.name)

           if config.plugins.iptvplayer.xxxsearch.value:
               self.SEARCH_proc=name
               valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
               valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),             CDisplayListItem.TYPE_SEARCH,             [''], '',        '', None)) 

           valTab.append(CDisplayListItem('FOTKA-PL-KAMERKI',     'http://www.fotka.pl/kamerki', CDisplayListItem.TYPE_CATEGORY, ['http://api.fotka.pl/v2/cams/get?page=1&limit=100&gender=f'],'FOTKA-PL-KAMERKI', 'https://pbs.twimg.com/profile_images/3086758992/6fb5cc2ee2735c334d0363bcb01a52ca_400x400.png', None)) 
           #valTab.append(CDisplayListItem('SMOTRI',     'http://smotri.com', CDisplayListItem.TYPE_CATEGORY, ['http://smotri.com/broadcast/list/'],'SMOTRI', 'http://www.userlogos.org/files/logos/Rog/smotri.com_01.png', None)) 
           valTab.append(CDisplayListItem('CHATURBATE',     'chaturbate.com', CDisplayListItem.TYPE_CATEGORY, ['https://chaturbate.com'],'CHATURBATE','http://www.adultcamfriendx.com/wp-content/uploads/2016/11/chaturbate-cams-logo.png', None)) 
           #valTab.append(CDisplayListItem('XHAMSTERLIVE',       "Kamerki",       CDisplayListItem.TYPE_CATEGORY,['http://xhamsterlive.com'], 'xhamster-cams', 'https://cdn.stripchat.com/assets/common/images/favicon_xh.png',None))
           valTab.append(CDisplayListItem('CAM4 - KAMERKI',     'http://www.cam4.pl', CDisplayListItem.TYPE_CATEGORY, ['http://www.cam4.pl/female'],'CAM4-KAMERKI', 'https://www.cam4models.com/images/c4logo_white.png', None)) 
           valTab.append(CDisplayListItem('MYFREECAMS',     'http://www.myfreecams.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.myfreecams.com/#Homepage'],'MYFREECAMS', 'http://www.adultcamfriendx.com/wp-content/uploads/2016/11/myfreecams-webcams-logo.png', None)) 
           #valTab.append(CDisplayListItem('LIVEJASMIN',     'http://new.livejasmin.com', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/girl/free+chat?selectedFilters=12'],'LIVEJASMIN', 'http://livejasmins.fr/livejasmin-france.png', None)) 
           valTab.append(CDisplayListItem('BONGACAMS',     'https://pl.bongacams.com/', CDisplayListItem.TYPE_CATEGORY, ['https://pl.bongacams.com/'],'BONGACAMS', 'http://i.bongacams.com/images/bongacams_logo3_header.png', None)) 
           valTab.append(CDisplayListItem('RAMPANT',     'https://www.rampant.tv', CDisplayListItem.TYPE_CATEGORY, ['https://www.rampant.tv/channels'],'RAMPANT', 'https://www.rampant.tv/images/rampant_logo.png', None)) 
           valTab.append(CDisplayListItem('SHOWUP   - live cams',       'showup.tv',          CDisplayListItem.TYPE_CATEGORY, ['http://showup.tv'],                     'showup',  'http://mamstartup.pl/i/articles/3619_newl.jpg', None)) 
           valTab.append(CDisplayListItem('ZBIORNIK - live cams',       'zbiornik.tv',       CDisplayListItem.TYPE_CATEGORY, ['http://zbiornik.com/live/'],            'zbiornik','http://static.zbiornik.com/images/zbiornikBig.png', None)) 
           valTab.append(CDisplayListItem('CAMSODA',       'http://www.camsoda.com',       CDisplayListItem.TYPE_CATEGORY, ['http://www.camsoda.com/api/v1/browse/online'],            'CAMSODA','https://cachew.camsoda.com/assets/img/camsoda-logo-160x50.png', None)) 
           valTab.append(CDisplayListItem('STREAMATE',       'https://streamate.com',       CDisplayListItem.TYPE_CATEGORY, ['https://streamate.com'],            'STREAMATE','https://m2.nsimg.net/3.0/auto/skin/sm/assets/ffe71-1453326178-logo.png', None)) 
           valTab.append(CDisplayListItem('CAMSTER',       'http://new.naked.com',       CDisplayListItem.TYPE_CATEGORY, ['http://new.naked.com/'],            'NAKED','http://media4.nk-img.com/images/siteImages/textImages/common/phtml/whiteLabel/new.naked/logo.png', None)) 
           #valTab.append(CDisplayListItem('ADULT-CHANNELS',     'http://adult-channels.com', CDisplayListItem.TYPE_CATEGORY, ['http://adult-channels.com/free-sex-channels/'],'ADULT', 'http://adult-channels.com/wp-content/uploads/2015/09/adult-channels-logo.png', None)) 
           #valTab.append(CDisplayListItem('OKLIVETV ADULT-18',     'http://oklivetv.com/genre/adult-18/', CDisplayListItem.TYPE_CATEGORY, ['http://oklivetv.com/genre/adult-18/?orderby=title'],'OKLIVETV', 'http://oklivetv.com/wp-content/uploads/2015/01/logo2.png', None)) 
           valTab.append(CDisplayListItem('MIAMI TV',     'https://miamitvhd.com', CDisplayListItem.TYPE_CATEGORY, ['https://miamitvhd.com/?channel=miamitv'],'MIAMI', 'https://miamitvhd.com/assets/miamitv-8fcf2efe186508c88b6ebd5441452254a32c410d1d18ea7f82ffbb0d26b35271.png', None)) 
           valTab.append(CDisplayListItem('+++ XXXLIST +++   XXXversion = '+str(self.XXXversion), '+++ XXXLIST +++   XXXversion = '+str(self.XXXversion), CDisplayListItem.TYPE_CATEGORY, [''],'XXXLIST', '', None)) 
           if config.plugins.iptvplayer.xxxupdate.value:
               valTab.append(CDisplayListItem('CHANGELOG',                    'CHANGELOG',   CDisplayListItem.TYPE_CATEGORY, ['https://gitlab.com/iptv-host-xxx/iptv-host-xxx/commits/master.atom'], 'UPDATE-ZMIANY', '', None)) 
           return valTab

        # ########## #
        if 'HISTORY' == name:
           printDBG( 'Host listsItems begin name='+name )
           for histItem in self.history.getHistoryList():
               valTab.append(CDisplayListItem(histItem['pattern'], 'Szukaj ', CDisplayListItem.TYPE_CATEGORY, [histItem['pattern'],histItem['type']], 'SEARCH', '', None))          
            
           return valTab           
        # ########## #
        if 'SEARCH' == name:
           printDBG( 'Host listsItems begin name='+name )
           pattern = url 
           if Index==-1: 
              self.history.addHistoryItem( pattern, 'video')
           if self.SEARCH_proc == '': return []               
           if self.SEARCH_proc == 'main-menu':
              valTab=[]
              self.MAIN_URL = 'https://www.4tube.com'
              valtemp = self.listsItems(-1, url, '4TUBE-search')
              for item in valtemp: item.name='4TUBE - '+item.name
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'ahme-search')
              for item in valtemp: item.name='AH-ME - '+item.name
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'BEFUCK-search')
              for item in valtemp: item.name='BEFUCK - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.cliphunter.com' 
              valtemp = self.listsItems(-1, url, 'CLIPHUNTER-search')
              for item in valtemp: item.name='CLIPHUNTER - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.dachix.com' 
              valtemp = self.listsItems(-1, url, 'DACHIX-search')
              for item in valtemp: item.name='DACHIX - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.drtuber.com' 
              valtemp = self.listsItems(-1, url, 'DRTUBER-search')
              for item in valtemp: item.name='DRTUBER - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.eporner.com' 
              valtemp = self.listsItems(-1, url, 'eporner-search')
              for item in valtemp: item.name='EPORNER - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = '' 
              valtemp = self.listsItems(-1, url, 'FAAPY-search')
              for item in valtemp: item.name='FAAPY - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'https://www.fux.com'
              valtemp = self.listsItems(-1, url, '4TUBE-search')
              for item in valtemp: item.name='FUX - '+item.name
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'hdzog-search')
              for item in valtemp: item.name='HDZOG - '+item.name              
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.homemoviestube.com'
              valtemp = self.listsItems(-1, url, 'HomeMoviesTube-search')
              for item in valtemp: item.name='HomeMoviesTube - '+item.name
              valTab = valTab + valtemp

#              self.MAIN_URL = 'http://www.hotshame.com'
#              valtemp = self.listsItems(-1, url, 'UpdateTube-search')
#              for item in valtemp: item.name='HOTSHAME - '+item.name
#              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'KATESTUBE-search')
              for item in valtemp: item.name='KATESTUBE - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'https://www.koloporno.com' 
              valtemp = self.listsItems(-1, url, 'KOLOPORNO-search')
              for item in valtemp: item.name='KOLOPORNO - '+item.name
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'MOVIEFAP-search')
              for item in valtemp: item.name='MOVIEFAP - '+item.name
              valTab = valTab + valtemp

#              self.MAIN_URL = 'http://www.pinkrod.com'
#              valtemp = self.listsItems(-1, url, 'UpdateTube-search')
#              for item in valtemp: item.name='PINKROD - '+item.name
#              valTab = valTab + valtemp

              self.MAIN_URL = 'http://porndoe.com' 
              valtemp = self.listsItems(-1, url, 'porndoe-search')
              for item in valtemp: item.name='PORNDOE - '+item.name              
              valTab = valTab + valtemp 

              self.MAIN_URL = 'https://www.pornerbros.com'
              valtemp = self.listsItems(-1, url, '4TUBE-search')
              for item in valtemp: item.name='PORNERBROS - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.pornhd.com' 
              valtemp = self.listsItems(-1, url, 'pornhd-search')
              for item in valtemp: item.name='PORNHD - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.pornhub.com' 
              valtemp = self.listsItems(-1, url, 'pornhub-search')
              for item in valtemp: item.name='PORNHUB - '+item.name              
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'pornicom-search')
              for item in valtemp: item.name='PORNICOM - '+item.name              
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'PORNOHUB-search')
              for item in valtemp: item.name='PORNOHUB - '+item.name              
              valTab = valTab + valtemp 

              self.MAIN_URL = 'https://www.porntube.com'
              valtemp = self.listsItems(-1, url, '4TUBE-search')
              for item in valtemp: item.name='PORNTUBE - '+item.name
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'PORNFROMCZECH-search')
              for item in valtemp: item.name='PORNFROMCZECH - '+item.name              
              valTab = valTab + valtemp 

              valtemp = self.listsItems(-1, url, 'REALGFPORN-search')
              for item in valtemp: item.name='REALGFPORN - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.redtube.com' 
              valtemp = self.listsItems(-1, url, 'redtube-search')
              for item in valtemp: item.name='REDTUBE - '+item.name
              valTab = valTab + valtemp

#              self.MAIN_URL = 'http://www.thenewporn.com'
#              valtemp = self.listsItems(-1, url, 'UpdateTube-search')
#              for item in valtemp: item.name='THE NEW PORN - '+item.name
#              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.thumbzilla.com' 
              valtemp = self.listsItems(-1, url, 'THUMBZILLA-search')
              for item in valtemp: item.name='THUMBZILLA - '+item.name              
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.tube8.com' 
              valtemp = self.listsItems(-1, url, 'tube8-search')
              for item in valtemp: item.name='TUBE8 - '+item.name
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'TUBEPORNCLASSIC-search')
              for item in valtemp: item.name='TUBEPORNCLASSIC - '+item.name
              valTab = valTab + valtemp

#              self.MAIN_URL = 'http://www.updatetube.com' 
#              valtemp = self.listsItems(-1, url, 'UpdateTube-search')
#              for item in valtemp: item.name='UpdateTube - '+item.name
#              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'xhamster-search')
              for item in valtemp: item.name='XHAMSTER - '+item.name              
              valTab = valTab + valtemp 
 
              self.MAIN_URL = 'http://www.xnxx.com' 
              valtemp = self.listsItems(-1, url, 'xnxx-search')
              for item in valtemp: item.name='XNXX - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.xvideos.com' 
              valtemp = self.listsItems(-1, url, 'xvideos-search')
              for item in valtemp: item.name='XVIDEOS - '+item.name              
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.youjizz.com' 
              valtemp = self.listsItems(-1, url, 'YOUJIZZ-search')
              for item in valtemp: item.name='YOUJIZZ - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = 'http://www.youporn.com' 
              valtemp = self.listsItems(-1, url, 'youporn-search')
              for item in valtemp: item.name='YOUPORN - '+item.name
              valTab = valTab + valtemp
 
              self.MAIN_URL = 'https://yourporn.sexy'
              valtemp = self.listsItems(-1, url, 'yourporn-search')
              for item in valtemp: item.name='YOURPORN.SEXY - '+item.name
              valTab = valTab + valtemp

              self.MAIN_URL = '' 
              return valTab
           valTab = self.listsItems(-1, url, self.SEARCH_proc)
           return valTab

        if 'UPDATE' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab.append(CDisplayListItem(self.XXXversion+' - Local version',   'Local  XXXversion', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
           valTab.append(CDisplayListItem(self.XXXremote+ ' - Remote version',  'Remote XXXversion', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
           valTab.append(CDisplayListItem('Changelog',                    'Changelog',   CDisplayListItem.TYPE_CATEGORY, ['https://gitlab.com/iptv-host-xxx/iptv-host-xxx/commits/master.atom'], 'UPDATE-ZMIANY', '', None)) 
           valTab.append(CDisplayListItem('Update Now',                         'Update Now',        CDisplayListItem.TYPE_CATEGORY, [''], 'UPDATE-NOW',    '', None)) 
           valTab.append(CDisplayListItem('Update Now & Restart Enigma2',                         'Update Now & Restart Enigma2',        CDisplayListItem.TYPE_CATEGORY, ['restart'], 'UPDATE-NOW',    '', None)) 
           return valTab
        if 'UPDATE-ZMIANY' == name:
           printDBG( 'Host listsItems begin name='+name )
           try:
              data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phCats = re.findall("<entry>.*?<title>(.*?)</title>.*?<updated>(.*?)</updated>.*?<name>(.*?)</name>", data, re.S)
           if phCats:
              for (phTitle, phUpdated, phName ) in phCats:
                  phUpdated = phUpdated.replace('T', '   ')
                  phUpdated = phUpdated.replace('Z', '   ')
                  phUpdated = phUpdated.replace('+01:00', '   ')
                  phUpdated = phUpdated.replace('+02:00', '   ')
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phUpdated: '+phUpdated )
                  printDBG( 'Host listsItems phName: '+phName )
                  valTab.append(CDisplayListItem(phUpdated+' '+phName+'  >>  '+phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [''],'', '', None)) 
           return valTab
        if 'UPDATE-NOW' == name:
           printDBG( 'HostXXX listsItems begin name='+name )
           _url = 'https://gitlab.com/iptv-host-xxx/iptv-host-xxx'
           query_data = { 'url': _url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
              #printDBG( 'Host init data: '+data )
              r=self.cm.ph.getSearchGroups(data, '''/iptv-host-xxx/iptv-host-xxx/commit/([^"^']+?)['"]''', 1, True)[0]
              if r:
                 printDBG( 'crc = '+r )
                 crc=r
           except:
              printDBG( 'Host init query error' )

           tmpDir = GetTmpDir() 
           source = os_path.join(tmpDir, 'iptv-host-xxx.tar.gz') 
           dest = os_path.join(tmpDir , '') 
           _url = 'https://gitlab.com/iptv-host-xxx/iptv-host-xxx/repository/archive.tar.gz?ref=master'              
           output = open(source,'wb')
           query_data = { 'url': _url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              output.write(self.cm.getURLRequestData(query_data))
              output.close()
              os_system ('sync')
              printDBG( 'HostXXX pobieranie iptv-host-xxx.tar.gz' )
           except:
              if os_path.exists(source):
                 os_remove(source)
              printDBG( 'HostXXX Błąd pobierania iptv-host-xxx.tar.gz' )
              valTab.append(CDisplayListItem('ERROR - Blad pobierania: '+_url,   'ERROR', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
              return valTab
           if os_path.exists(source):
              printDBG( 'HostXXX Jest plik '+source )
           else:
              printDBG( 'HostXXX Brak pliku '+source )

           cmd = 'tar -xzf "%s" -C "%s" 2>&1' % ( source, dest )  
           try: 
              os_system (cmd)
              os_system ('sync')
              printDBG( 'HostXXX rozpakowanie  ' + cmd )
           except:
              printDBG( 'HostXXX Błąd rozpakowania iptv-host-xxx.tar.gz' )
              os_system ('rm -f %s' % source)
              os_system ('rm -rf %siptv-host-xxx-%s' % (dest, crc))
              valTab.append(CDisplayListItem('ERROR - Blad rozpakowania %s' % source,   'ERROR', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
              return valTab


           try:
              od = '%siptv-host-xxx-master-%s/'% (dest, crc)
              do = resolveFilename(SCOPE_PLUGINS, 'Extensions/') 
              cmd = 'cp -rf "%s"/* "%s"/ 2>&1' % (os_path.join(od, 'IPTVPlayer'), os_path.join(do, 'IPTVPlayer'))
              printDBG('HostXXX kopiowanie1 cmd[%s]' % cmd)
              os_system (cmd)
              #printDBG('HostXXX kopiowanie2 cmd[%s]' % cmd)
              #iptv_system(cmd)
              os_system ('sync')
           except:
              printDBG( 'HostXXX blad kopiowania' )
              os_system ('rm -f %s' % source)
              os_system ('rm -rf %siptv-host-xxx-master-%s' % (dest, crc))
              valTab.append(CDisplayListItem('ERROR - blad kopiowania',   'ERROR', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
              return valTab


           ikony = GetPluginDir('icons/PlayerSelector/')
           if os_path.exists('%sXXX100' % ikony):
              printDBG( 'HostXXX Jest '+ ikony + 'XXX100 ' )
              os_system('mv %sXXX100 %sXXX100.png' % (ikony, ikony)) 
           if os_path.exists('%sXXX120' % ikony):
              printDBG( 'HostXXX Jest '+ ikony + 'XXX120 '  )
              os_system('mv %sXXX120 %sXXX120.png' % (ikony, ikony))
           if os_path.exists('%sXXX135' % ikony):
              printDBG( 'HostXXX Jest '+ ikony + 'XXX135 '  )
              os_system('mv %sXXX135 %sXXX135.png' % (ikony, ikony))

           try:
              cmd = GetPluginDir('hosts/hostXXX.py')
              with open(cmd, 'r') as f:  
                 data = f.read()
                 f.close() 
                 wersja = re.search('XXXversion = "(.*?)"', data, re.S)
                 aktualna = wersja.group(1)
                 printDBG( 'HostXXX aktualna wersja wtyczki '+aktualna )
           except:
              printDBG( 'HostXXX error openfile ' )


           printDBG( 'HostXXX usuwanie plikow tymczasowych' )
           os_system ('rm -f %s' % source)
           os_system ('rm -rf %siptv-host-xxx-master-%s' % (dest, crc))

           if url:
              try:
                 msg = 'Zaraz nastąpi Restart GUI .\n \n Wersja hostXXX w tunerze %s' % aktualna
                 GetIPTVNotify().push('%s' % msg, 'info', 20)
                 from enigma import quitMainloop
                 quitMainloop(3)
              except: pass
           valTab.append(CDisplayListItem('Update End. Please manual restart enigma2',   'Restart', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
           printDBG( 'HostXXX listsItems end' )
           return valTab

##################################################################
        if 'tube8' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.tube8.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'tube8.cookie')
           host = 'Mozilla/5.0 (Windows NT 6.1; rv:44.0) Gecko/20100101 Firefox/44.0'
           header = {'User-Agent': host, 'Accept':'application/json', 'Accept-Language':'de,en-US;q=0.7,en;q=0.3', 'X-Requested-With':'XMLHttpRequest', 'Content-Type':'application/json'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'categories-subnav', '</ul>', False)[1]
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-thumb=['"]([^"^']+?)['"]''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'tube8-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem('--- Featured videos ---', 'Featured videos', CDisplayListItem.TYPE_CATEGORY, ['http://www.tube8.com'], 'tube8-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Most Viewed ---', 'Most Viewed',               CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/most-viewed/page/1/'],      'tube8-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Top Rated ---', 'Top Rated',                 CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/top/page/1/'],       'tube8-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Longest ---', 'Longest', CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/longest/page/1/'],      'tube8-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- New Videos ---',  'New Videos',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/newest/page/1/'],       'tube8-clips', '', None)) 
           self.SEARCH_proc='tube8-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'tube8-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.tube8.com/searches.html?q='+url.replace(' ','+'), 'tube8-clips')
           return valTab              
        if 'tube8-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.tube8.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'tube8.cookie')
           host = 'Mozilla/5.0 (Windows NT 6.1; rv:44.0) Gecko/20100101 Firefox/44.0'
           header = {'User-Agent': host, 'Accept':'application/json', 'Accept-Language':'de,en-US;q=0.7,en;q=0.3', 'X-Requested-With':'XMLHttpRequest', 'Content-Type':'application/json'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           nextPage = self.cm.ph.getDataBeetwenMarkers(data, '<div class="footer-pagination"', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'videoid=', 'boxVideo')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''data-video_url=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-thumb=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,'['+phTime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.findall('href="(.*?)"', nextPage, re.S)
           if match:
              phUrl = match[-1]
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))                
           return valTab

        if 'xnxx' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.xnxx.com' 
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('"categories":(.*?),"more_links"', data, re.S)
           if not parse: return valTab
           #printDBG( 'Host listsItems parse.group(1): '+parse.group(1) )
           result = simplejson.loads(parse.group(1))
           if result:
              for item in result:
                 phUrl = str(item["url"].replace('\/','/'))  
                 phTitle = str(item["label"]) 
                 if not 'jpg' in phTitle:
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'xnxx-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem('--- Hits ---', 'Hits',               CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/hits/'],      'xnxx-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Hot ---', 'Hot',                 CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/hot/'],       'xnxx-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Best Videos ---', 'Best Videos', CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/best/'],      'xnxx-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- New Videos ---',  'New Videos',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL],       'xnxx-clips', '', None)) 
           self.SEARCH_proc='xnxx-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),_('Search'),                  CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'xnxx-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.xnxx.com/?k='+url.replace(' ','+'), 'xnxx-clips')
           return valTab              
        if 'xnxx-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.xnxx.com' 
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           match = re.search("pagination(.*?)Next", data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'id="video', '</p></div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/video[^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''duration-mark">([^>]+?)<''', 1, True)[0] 
              if not phTime: phTime = self.cm.ph.getSearchGroups(item, '''<p class="metadata">([^>]+?)-''', 1, True)[0].strip()

              valTab.append(CDisplayListItem(decodeHtml(phTitle),phTime+'\n'+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           if match: match = re.findall('href="(.*?)"', match.group(1), re.S)
           if match:
              phUrl = match[-1]
              #printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl], name, '', None))                
           return valTab

        if 'zbiornik' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://zbiornik.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'zbiornik.cookie')
           try: data = self.cm.getURLRequestData({ 'url': 'http://zbiornik.tv/accept/yes/Lw==', 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           sex = ''
           hash = ''
           ph1 = re.search('var streams = (.*?)}];', data, re.S)
           if ph1: 
              ph1 = ph1.group(1)+'}]'
              #printDBG( 'Host listsItems json: '+ph1 )
              result = simplejson.loads(ph1)
              if result:
                 for item in result:
                     phash = re.search('"phash":"(.*?)"', data, re.S)
                     if phash: hash=phash.group(1)
                     if str(item["accType"])=='1': sex = 'male'
                     if str(item["accType"])=='2': sex = 'female'
                     if str(item["accType"])=='3': sex = 'couple'
                     phImage = 'http://camshot.zbiornik.com/'+str(item["broadcasturl"])+'-224.jpg'
                     rtmpUrl = 'rtmp://'+str(item["server"])+'/videochat/?'+hash
                     playpath = str(item["broadcasturl"])
                     swfUrl = 'https://zbiornik.tv/wowza.swf?v50&b=100'
                     baseUrl = 'https://zbiornik.tv/'+str(item["nick"])
                     app = 'videochat/?'+hash
                     flashVer = ' flashVer=WIN 28,0,0,161'
                     #streamUrl = 'rtmp://'+str(item["server"])+'/videochat/?'+hash+' playpath='+str(item["broadcasturl"])+' swfUrl=http://zbiornik.tv/wowza.swf?v50&b=100 pageUrl=http://zbiornik.tv/'+str(item["nick"])+' live=1'
                     streamUrl = rtmpUrl + ' playpath=' + playpath +  ' tcUrl=' + rtmpUrl + ' swfUrl=' + swfUrl + ' pageUrl=' + baseUrl + ' app='+app+' live=1 conn=S:OK'+ flashVer
                     if str(item["accType"])<>'1':
                        valTab.append(CDisplayListItem(str(item["nick"])+'    {'+sex+'}',str(item["nick"]),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', streamUrl, 0)], 0, phImage, None)) 
           return valTab

        if 'showup' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://showup.tv' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'showup.cookie')
           try: data = self.cm.getURLRequestData({ 'url': 'http://showup.tv/site/accept_rules/yes?ref=http://showup.tv/', 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li data-equalizer-watch class="stream"', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = phUrl[1:] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phDesc = self.cm.ph.getSearchGroups(item, '''<p>([^>]+?)</p>''', 1, True)[0]
              transcoderaddr = self.cm.ph.getSearchGroups(item, '''transcoderaddr=['"]([^"^']+?)['"]''', 1, True)[0] 
              streamid = self.cm.ph.getSearchGroups(item, '''streamid=['"]([^"^']+?)['"]''', 1, True)[0] 
              uid = self.cm.ph.getSearchGroups(item, '''uid=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl =  'rtmp://'+transcoderaddr+':1935/webrtc/'+streamid+'_aac'
              phImage = 'http://showup.tv/'+phImage
              valTab.append(CDisplayListItem(phTitle,phTitle+'     '+decodeHtml(phDesc),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 0)], 0, phImage, None)) 
           return valTab

        if 'xvideos' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.xvideos.com' 
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="dyn', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''href=.*?>([^>]+?)</a>''', 1, True)[0].strip()
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'xvideos-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name) 
           valTab.insert(0,CDisplayListItem('--- Pornstars ---',   'Pornstars',   CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/pornstars'], 'xvideos-pornstars', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Best Videos ---', 'Best Videos', CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/best/'],     'xvideos-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- New Videos ---',  'New Videos',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL],              'xvideos-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- 100% Verified ---',  '100% Verified',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/verified/videos'],              'xvideos-clips', '', None)) 
           #valTab.insert(0,CDisplayListItem('--- Channels ---',  'Channels',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/channels'],              'xvideos-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Porno po polsku ---',  'Porno po polsku',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/porn/polski'],              'xvideos-clips', '', None)) 
           self.SEARCH_proc='xvideos-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'xvideos-pornstars' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.xvideos.com' 
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phCats = re.findall('class="thumb"><a href="(/profiles/.*?)".*?img src="(.*?)".*?href="/profiles/.*?">(.*?)<', data, re.S)
           if phCats:
              for (phUrl, phImage, phTitle) in phCats:
                  valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl.replace('pornstars-click/3','profiles')+'#_tabVideos'],'xvideos-clips', phImage, None)) 
           return valTab
        if 'xvideos-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.xvideos.com/?k='+url.replace(' ','+'), 'xvideos-clips')
           return valTab              
        if 'xvideos-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.xvideos.com' 
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, '"active" href=', '</ul></div>', False)[1]
           next = self.cm.ph.getSearchGroups(next, '''href=['"](/[^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'id="video', '</p></div>')
           for item in data:
              phTitle = re.compile('''title=['"]([^'^"]+?)['"]''').findall(item) 
              phTitle = phTitle[-1]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/video[^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime.strip()+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           if next:
              valTab.append(CDisplayListItem('Next', 'Page: '+self.MAIN_URL+next, CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+next], name, '', None))                
           return valTab

        if 'hentaigasm' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://hentaigasm.com' 
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('Genres(.*?)</div></div>', data, re.S|re.I)
           if not parse: return valTab
           phCats = re.findall("<a href='(.*?)'.*?>(.*?)<", parse.group(1), re.S)
           if phCats:
              for (phUrl, phTitle) in phCats:
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'hentaigasm-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- New ---", "New",        CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL], 'hentaigasm-clips', '',None))
           return valTab
        if 'hentaigasm-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('<div class="thumb">.*?title="(.*?)" href="(.*?)".*?<img src="(.*?)"', data, re.S)
           if phMovies:
              for (phTitle, phUrl, phImage) in phMovies:
                  phImage = phImage.replace(' ','%20')
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.search("<div class='wp-pagenavi'>(.*?)</div>", data, re.S)
           if match: match = re.findall("href='(.*?)'", match.group(1), re.S)
           if match:
                  phUrl = match[-1]
                  valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))                
           return valTab

        if 'youporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.youporn.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'youporn.cookie')
           host = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/17.0'
           header = {'Cookie': 'age_verified=1', 'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a data-espnode=', '</a>')
           for item in data:
              #phTitle = self.cm.ph.getSearchGroups(item, '''categories.([^"^']+?)['"]''', 1, True)[0]
              phTitle = self.cm.ph.getSearchGroups(item, '''ListElement">([^>]+?)<''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/category/[^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phTitle and phUrl: 
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'youporn-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Discussed ---",     "Most Discussed",     CDisplayListItem.TYPE_CATEGORY,["https://www.youporn.com/most_discussed/"],                   'youporn-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Favorited ---",     "Most Favorited",     CDisplayListItem.TYPE_CATEGORY,["https://www.youporn.com/most_favorited/"],                   'youporn-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---",        "Most Viewed",        CDisplayListItem.TYPE_CATEGORY,["https://www.youporn.com/most_viewed/"],                      'youporn-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",          "Top Rated",          CDisplayListItem.TYPE_CATEGORY,["https://www.youporn.com/top_rated/"],                        'youporn-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",                "New",                CDisplayListItem.TYPE_CATEGORY,["https://www.youporn.com/"],                                  'youporn-clips', '',None))
           self.SEARCH_proc='youporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'youporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.youporn.com/search/?query=%s' % url.replace(' ','+'), 'youporn-clips')
           return valTab              
        if 'youporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.youporn.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'youporn.cookie')
           host = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/17.0'
           header = {'Cookie': 'age_verified=1', 'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           next = re.findall('class="skip next".*?class="prev-next".*?href="(.*?)" data-page-number', data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-video-id', '<i class="icon-thin-x">')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?jpg)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0] 
              phUrl = phUrl.replace("&amp;","&")
              if phUrl.startswith('/'): phUrl = 'https://www.youporn.com' + phUrl
              if len(phUrl)>5:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime.strip()+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              next = next[0].replace("&amp;","&")
              if next.startswith('/'): next = 'https://www.youporn.com' + next
              valTab.append(CDisplayListItem('Next', 'Next: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           self.MAIN_URL = '' 
           return valTab

        if 'redtube' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.redtube.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'redtube.cookie')
           host = 'Mozilla/5.0 (Windows NT 6.1; rv:44.0) Gecko/20100101 Firefox/44.0'
           header = {'User-Agent': host, 'Accept':'application/json', 'Accept-Language':'de,en-US;q=0.7,en;q=0.3', 'X-Requested-With':'XMLHttpRequest', 'Content-Type':'application/x-www-form-urlencoded'} 
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li id="category', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-thumb_url=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'redtube-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Favored ---", "Most Favored", CDisplayListItem.TYPE_CATEGORY,["http://www.redtube.com/mostfavored?period=alltime"], 'redtube-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---",  "Most Viewed",  CDisplayListItem.TYPE_CATEGORY,["http://www.redtube.com/mostviewed?period=alltime"],  'redtube-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",    "Top Rated",    CDisplayListItem.TYPE_CATEGORY,["http://www.redtube.com/top?period=alltime"],         'redtube-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---",       "Newest",       CDisplayListItem.TYPE_CATEGORY,["http://www.redtube.com/"],                           'redtube-clips', '',None))
           self.SEARCH_proc='redtube-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'redtube-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.redtube.com/?search=%s' % url.replace(' ', '+'), 'redtube-clips')
           return valTab      
        if 'redtube-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.redtube.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'redtube.cookie')
           host = 'Mozilla/5.0 (Windows NT 6.1; rv:44.0) Gecko/20100101 Firefox/44.0'
           header = {'User-Agent': host, 'Accept':'application/json', 'Accept-Language':'de,en-US;q=0.7,en;q=0.3', 'X-Requested-With':'XMLHttpRequest', 'Content-Type':'application/x-www-form-urlencoded'} 
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           match = re.findall('<link rel="next" href="(.*?)"', data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="videoblock_list"', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-mediumthumb=['"]([^"^']+?)['"]''', 1, True)[0]
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-thumb_url=['"]([^"^']+?)['"]''', 1, True)[0]
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              phRuntime = self.cm.ph.getDataBeetwenMarkers(item, '<span class="duration">', '<div class="video_title">', False)[1]
              phRuntime = self._cleanHtmlStr(phRuntime).strip() 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if match:
              valTab.append(CDisplayListItem('Next', match[0], CDisplayListItem.TYPE_CATEGORY, [match[0]], name, '', None))                
           return valTab

        if 'xhamster' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://xhamster.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'xhamster.cookie')
           host = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'en,en-US;q=0.7,en;q=0.3'} 
           query_data = { 'url': url, 'header': header, 'Referer':'https://xhamster.com', 'Origin':'https://xhamster.com', 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'letter-block', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phTitle = self._cleanHtmlStr(item).strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https://xhamster.com/categories/[^"^']+?)['"]''', 1, True)[0]
              if config.plugins.iptvplayer.xhamstertag.value and not phUrl:
                 phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https://xhamster.com/tags/[^"^']+?)['"]''', 1, True)[0] 
                 if phUrl and phTitle: phTitle = phTitle+'   (tags)'
              if phUrl and phTitle:
                 valTab.append(CDisplayListItem(phTitle.strip(),phTitle.strip(),CDisplayListItem.TYPE_CATEGORY, [phUrl],'xhamster-clips', '', None)) 
           valTab.insert(0,CDisplayListItem("--- HD ---",       "HD",       CDisplayListItem.TYPE_CATEGORY,["http://xhamster.com/categories/hd-videos"], 'xhamster-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Best monthly ---",       "Best monthly",       CDisplayListItem.TYPE_CATEGORY,["http://xhamster.com/best/monthly"], 'xhamster-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Pornstars ---",       "Pornstars",       CDisplayListItem.TYPE_CATEGORY,["http://xhamster.com/pornstars"], 'xhamster-pornostars', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",       "New",       CDisplayListItem.TYPE_CATEGORY,["http://xhamster.com/"], 'xhamster-clips', '',None))
           self.SEARCH_proc='xhamster-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'xhamster-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.xhamster.com/search.php?from=suggestion&q=%s&qcat=video' % url.replace(' ','+'), 'xhamster-clips')
           return valTab              
        if 'xhamster-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'xhamster.cookie')
           host = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'en,en-US;q=0.7,en;q=0.3'} 
           query_data = { 'url': url, 'header': header, 'Referer':'https://xhamster.com', 'Origin':'https://xhamster.com', 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''data-page="next"\shref=['"]([^"^']+?)['"]''', 1, True)[0] 
           if not next: next = self.cm.ph.getSearchGroups(data, '''rel="next"\shref=['"]([^"^']+?)['"]''', 1, True)[0] 
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="thumb-list__item video-thumb video-thumb--dated">', '</div><div')
           if not data2: data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="thumb-list__item video-thumb">', '</div><div')
           for item in data2:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              next = next.replace('&amp;','&')
              if next.startswith('/'): next = 'https://xhamster.com' + next
              valTab.append(CDisplayListItem('Next', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))
           data2 = None
           return valTab
        if 'xhamster-pornostars' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'xhamster.cookie')
           host = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'en,en-US;q=0.7,en;q=0.3'} 
           query_data = { 'url': url, 'header': header, 'Referer':'https://xhamster.com', 'Origin':'https://xhamster.com', 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'letter-block', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phTitle = self._cleanHtmlStr(item).strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https://xhamster.com/pornstars/[^"^']+?)['"]''', 1, True)[0]
              if phUrl:
                 valTab.append(CDisplayListItem(phTitle.strip(),phTitle.strip(),CDisplayListItem.TYPE_CATEGORY, [phUrl],'xhamster-clips', '', None)) 
           return valTab

        if 'xhamster-cams' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://xhamsterlive.com' 
           url='http://xhamsterlive.com/api/front/models'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('"models":(.*?),"ttl":', data, re.S) 
           if not parse: return valTab
           result = simplejson.loads(parse.group(1))
           if result:
              for item in result:
                 ID = str(item["id"]) 
                 Name = str(item["username"])
                 BroadcastServer = str(item["broadcastServer"])
                 Image = str(item["previewUrl"].replace('\/','/'))  
                 status = str(item["status"])
                 if status == "public":
                    valTab.append(CDisplayListItem(Name,Name,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', ID, 1)], 0, Image, None)) 
           return valTab

        if 'eporner' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.eporner.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'div class="categoriesbox', '</div> </div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = phTitle.replace(' movies', '').replace('Porn Videos', '')
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'eporner-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- 4k ---",        "4k",        CDisplayListItem.TYPE_CATEGORY,["https://www.eporner.com/category/4k-porn/"], 'eporner-clips', '','/4k/'))
           valTab.insert(0,CDisplayListItem("--- HD ---",        "HD",        CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/hd/"], 'eporner-clips', '','/hd/'))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---", "Top Rated", CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/top_rated/"], 'eporner-clips', '','/top_rated/'))
           valTab.insert(0,CDisplayListItem("--- Popular ---",   "Popular",   CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/weekly_top/"], 'eporner-clips', '','/weekly_top/'))
           valTab.insert(0,CDisplayListItem("--- On Air ---",    "On Air",    CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/currently/"], 'eporner-clips', '','/currently/'))
           valTab.insert(0,CDisplayListItem("--- New ---",       "New",       CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/"], 'eporner-clips', '',''))
           self.SEARCH_proc='eporner-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'eporner-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.eporner.com/search/%s/' % url.replace(' ','+'), 'eporner-clips')
           return valTab    
        if 'eporner-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           self.MAIN_URL = 'http://www.eporner.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           match = re.findall('<div class="numlist2">.*?>NEXT', data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="mb', '</div> </div> </div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''mbtim">([^>]+?)<''', 1, True)[0]
              size = self.cm.ph.getSearchGroups(item, '''<span>([^>]+?)</span>''', 1, True)[0]
              valTab.append(CDisplayListItem(decodeHtml(phTitle)+'    '+size,'['+phRuntime+'] '+decodeHtml(phTitle)+'    '+size,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           if match:
              match = re.findall("<a href=(.*?)title", match[0], re.S)
              if match:
                 phUrl = match[-1].replace("'","").replace('"','')
                 valTab.append(CDisplayListItem('Next', 'Next', CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl], name, '', catUrl))                
           return valTab

        if 'pornhub' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornhub.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornhub.cookie')
           host = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
           header = {'User-Agent': host, 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'en,en-US;q=0.7,en;q=0.3','X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="cat', '</li>')
           #printDBG( 'Host2 getResolvedURL data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'pornhub-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- HD ---",         "HD",          CDisplayListItem.TYPE_CATEGORY,["http://www.pornhub.com/video?c=38"], 'pornhub-clips', 'http://cdn1a.static.pornhub.phncdn.com/images/categories/38.jpg',None))
           valTab.insert(0,CDisplayListItem("--- Longest ---",    "Longest",     CDisplayListItem.TYPE_CATEGORY,["http://www.pornhub.com/video?o=lg"], 'pornhub-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",  "Top Rated",   CDisplayListItem.TYPE_CATEGORY,["http://www.pornhub.com/video?o=tr"], 'pornhub-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---","Most Viewed", CDisplayListItem.TYPE_CATEGORY,["http://www.pornhub.com/video?o=mv"], 'pornhub-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Recent ---","Most Recent", CDisplayListItem.TYPE_CATEGORY,["http://www.pornhub.com/video?o=mr"], 'pornhub-clips', '',None))
           self.SEARCH_proc='pornhub-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornhub-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.pornhub.com/video/search?search=%s' % url.replace(' ','+'), 'pornhub-clips')
           return valTab    
        if 'pornhub-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornhub.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornhub.cookie')
           host = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
           header = {'User-Agent': host, 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'en,en-US;q=0.7,en;q=0.3','X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host2 getResolvedURL data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''"page_next"><a href=['"]([^"^']+?)['"]''')[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'videoblock', '</li>')
           #printDBG( 'Host2 getResolvedURL data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&') 
              phImage = self.cm.ph.getSearchGroups(item, '''data-mediumthumb=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''"duration">([^"^']+?)<''', 1, True)[0] 
              phAdded = self.cm.ph.getSearchGroups(item, '''class="added">([^"^']+?)<''', 1, True)[0] 
              OldImage = self.cm.ph.getSearchGroups(item, '''data-image=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.MAIN_URL+phUrl
              if not OldImage:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] [Added: '+phAdded+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              valTab.append(CDisplayListItem('Next', 'Next '+re.sub('.+page=', '', next), CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+next.replace('&amp;','&')], name, '', None))        
           return valTab

        if 'hdporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.hdporn.net'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phCats = re.findall('class="content">.*?href="(.*?)".*?src="(.*?)".*?alt="(.*?)"', data, re.S)
           if phCats:
              for (phUrl, phImage, phTitle) in phCats:
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'hdporn-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",           CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/top-rated/"]  , 'hdporn-clips','', None))
           return valTab
        if 'hdporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           printDBG( 'Host listsItems cat-url: '+catUrl )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('class="content.*?href="(.*?)".*?itle="(.*?)".*?src="(.*?)".*?TIME:  (.*?)</div>', data, re.S)
           if phMovies:
              for (phUrl, phTitle, phImage, phRuntime) in phMovies:
                  valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           match = re.findall('<div id="pagination">.*?</div>', data, re.S)
           if not match: return valTab
           match = re.findall("</a><a href='(.*?)'>", match[0], re.S)
           if not match: return valTab
           if len(match)>0:
              valTab.append(CDisplayListItem('Next', 'Next Page', CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+catUrl+match[0]], 'hdporn-clips', '', catUrl))                
           return valTab
  
        if 'beeg' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://beeg.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'beeg.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER}
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+data )
           self.beeg_version = self.cm.ph.getSearchGroups(data, '''cpl/(\d+)\.js''', 1, True)[0] 
           printDBG( 'Host beeg_version: '+str(self.beeg_version) )
           url = 'https://beeg.com/static/cpl/%s.js' % self.beeg_version
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data2: '+data )
           self.beeg_salt = self.cm.ph.getSearchGroups(data, '''beeg_salt=['"]([^"^']+?)['"]''', 1, True)[0] 
           self.beeg_api = '//beeg.com/api/v6/' 

           printDBG( 'Host self.beeg_salt: '+self.beeg_salt )
           printDBG( 'Host self.beeg_api: '+self.beeg_api )

           url = 'https:%s%s/index/main/0/mobile' % (self.beeg_api, self.beeg_version)
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data3: '+data )
           result = byteify(simplejson.loads(data))
           for item in result["tags"]:
              phTitle = str(item["tag"]).title()
              phUrl = 'https:%s%s/index/tag/$PAGE$/mobile?tag=%s' % (self.beeg_api, self.beeg_version, phTitle.lower())
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'beeg-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           return valTab
        if 'beeg-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           printDBG( 'Host listsItems cat-url: '+str(catUrl) )
           next = url
           if catUrl == None: 
              self.page = 0
           else:
              self.page += 1
           url = url.replace('$PAGE$', '%s' % str(self.page))
           printDBG( 'Host current url: '+url )
           printDBG( 'Host current next: '+next )
           printDBG( 'Host current page: '+ str(self.page) )
           COOKIEFILE = os_path.join(GetCookieDir(), 'beeg.cookie')
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              if result:
                 for item in result["videos"]:
                    phTitle = str(item["title"])
                    phVideoId = str(item["id"])
                    phUrl = 'https:%s%s/video/%s' % (self.beeg_api, self.beeg_version, phVideoId)
                    phImage = 'http://img.beeg.com/236x177/%s.jpg' % phVideoId
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           except Exception:
              printExc()
           valTab.append(CDisplayListItem('Next', 'Page: '+str(self.page+2), CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'Next'))                
           return valTab

        if 'pornrabbit' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornrabbit.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phCats = re.findall('<div class="cat">.*?href="(.*?)".*?<h2>(.*?)<small>(.*?)<.*?img src="(.*?)"', data, re.S)
           if phCats:
              for (phUrl, phTitle,phTitle2,phImage) in phCats:
                  valTab.append(CDisplayListItem(phTitle+phTitle2,phUrl,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'pornrabbit-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Recent ---", "Most Recent", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos/'], 'pornrabbit-clips', '','/videos/'))
           return valTab
        if 'pornrabbit-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           x = 0
           Movies = re.findall('class="video">.*?<a href="(.*?)" title="(.*?)".*?<img.*?src="(.*?)".*?views: <b>(.*?)</b>.*?runtime: <b>(.*?)</b>', data, re.S)
           if Movies:
              for (Url, Title, Image, Views, Runtime) in Movies:
                  valTab.append(CDisplayListItem(decodeHtml(Title),'['+Runtime+'] '+decodeHtml(Title),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+Url, 1)], 0, Image, None)) 
                  x = x + 1
           match = re.findall(r'&nbsp;<a href="(.*?)"', data, re.S)
           if match:
              valTab.append(CDisplayListItem('Next', self.MAIN_URL+catUrl+match[0].replace(r'../',''), CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+catUrl+match[0].replace(r'../','')], name, '', catUrl))                
           return valTab

        if 'pornhd' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornhd.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="tag-150', 'class="footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="category">', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, ['http://www.pornhd.com/'+phUrl],'pornhd-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Channel ---",       "Channel",       CDisplayListItem.TYPE_CATEGORY,["https://www.pornhd.com/channel"], 'pornhd-channel', '',None))
           valTab.insert(0,CDisplayListItem("--- Pornstars ---",       "Pornstars",       CDisplayListItem.TYPE_CATEGORY,["https://www.pornhd.com/pornstars"], 'pornhd-pornstars', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",       "New",       CDisplayListItem.TYPE_CATEGORY,["https://www.pornhd.com/"], 'pornhd-clips', '',None))
           self.SEARCH_proc='pornhd-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornhd-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.pornhd.com/search?search=%s' % url.replace(' ','+'), 'pornhd-clips')
           return valTab
        if 'pornhd-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, '<li class="next', '</li>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li  data', '</li>')
           for item in data:
              Title = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              Image = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not Image: Image = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Runtime = self.cm.ph.getSearchGroups(item, '''<time>([^"^']+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(decodeHtml(Title),'['+Runtime+'] '+decodeHtml(Title),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+Url, 1)], 0, Image, None)) 
           if next:
              next = self.cm.ph.getSearchGroups(next, '''value=['"]([^"^']+?)['"]''', 1, True)[0] 
              url = re.sub('\?page.+', '', url)
              next = url+'?page='+next
              valTab.append(CDisplayListItem('Next', 'Page : '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', catUrl))                
           return valTab
        if 'pornhd-channel' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornhd.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="tag', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              Title = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              Image = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if Url.startswith('/'): Url = 'http://www.pornhd.com' + Url 
              if Title:
                 valTab.append(CDisplayListItem(decodeHtml(Title),decodeHtml(Title),CDisplayListItem.TYPE_CATEGORY, [Url],'pornhd-clips', Image, None)) 
           return valTab
        if 'pornhd-pornstars' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornhd.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, '<li class="next', '</li>', False)[1]
           data = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="pornstar', '</ul>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="pornstar', '</li>')
           for item in data:
              Title = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              Image = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if Url.startswith('/'): Url = 'http://www.pornhd.com' + Url 
              valTab.append(CDisplayListItem(decodeHtml(Title),decodeHtml(Title),CDisplayListItem.TYPE_CATEGORY, [Url],'pornhd-clips', Image, None)) 
           if next:
              next = self.cm.ph.getSearchGroups(next, '''value=['"]([^"^']+?)['"]''', 1, True)[0] 
              url = re.sub('\?page.+', '', url)
              next = url+'?page='+next
              valTab.append(CDisplayListItem('Next', 'Page : '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'AH-ME' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.ah-me.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="moviec', '</div>')
           #printDBG( 'Host2 data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'AH-ME-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Long movies ---",       "Long movies",       CDisplayListItem.TYPE_CATEGORY,["https://www.ah-me.com/long-movies/page1.html"], 'AH-ME-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top rated ---",       "Top rated",       CDisplayListItem.TYPE_CATEGORY,["https://www.ah-me.com/top-rated/page1.html"], 'AH-ME-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- High definition ---",       "High definition",       CDisplayListItem.TYPE_CATEGORY,["https://www.ah-me.com/high-definition/page1.html"], 'AH-ME-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most favorited ---",       "Most favorited",       CDisplayListItem.TYPE_CATEGORY,["https://www.ah-me.com/mostfavorites/page1.html"], 'AH-ME-clips', '',None))
           self.SEARCH_proc='ahme-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'ahme-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.ah-me.com/search/%s/' % url.replace(' ','+'), 'AH-ME-clips')
           return valTab
        if 'AH-ME-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           self.MAIN_URL = 'http://www.ah-me.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'next"><a class="color" href="', '">Next', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="moviec', '/span></p>')
           #printDBG( 'Host2 data: '+str(data) )
           for item in data:
              Title = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              Image = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Runtime = self.cm.ph.getSearchGroups(item, '''class="time">([^"^']+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(decodeHtml(Title),'['+Runtime+'] '+decodeHtml(Title),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, Image, None)) 
           if next:
              printDBG( 'Host next: '+next )
              valTab.append(CDisplayListItem('Next', 'Next', CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'CHATURBATE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://chaturbate.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           valTab.append(CDisplayListItem('Featured', 'Featured',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('Female', 'Female',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/female-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('Couple', 'Couple',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/couple-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('Transsexual', 'Transsexual',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/transsexual-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('HD', 'HD',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/hd-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('Teen (18+)', 'Teen',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/teen-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('18 to 21', '18 to 21',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/18to21-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('20 to 30', '20 to 30',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/20to30-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('30 to 50', '30 to 50',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/30to50-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('Euro Russian', 'Euro Russian',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/euro-russian-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('Exhibitionist', 'Exhibitionist',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/exhibitionist-cams/'],'CHATURBATE-clips', '', None)) 
           return valTab
        if 'CHATURBATE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           match = re.search('class="endless_separator".*?<li><a href="(.*?)"', data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="room_list_room', 'viewers</li>')
           #printDBG( 'Host2 data: '+str(data) )
           for item in data:
              Title = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              Image = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Gender=''
              Age=self.cm.ph.getSearchGroups(item, '''<span class="age gender.">([^>]+?)<''', 1, True)[0]
              Description=''
              Location=self.cm.ph.getSearchGroups(item, '''location" style="display: none;">([^>]+?)<''', 1, True)[0]
              Viewers=''
              bitrate = self.cm.ph.getSearchGroups(item, '''thumbnail_label.*?>([^>]+?)<''', 1, True)[0]
              if Url.startswith('/'): Url = self.MAIN_URL + Url 
              valTab.append(CDisplayListItem(decodeHtml(Title),decodeHtml(Title)+'   [Age: '+Age+']           [Location: '+decodeHtml(Location)+']   [info: '+bitrate+']',CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, Image, None)) 
           if match:
              printDBG( 'Host listsItems Next: '  +match.group(1) )
              if match.group(1).startswith('/'): Url = self.MAIN_URL + match.group(1) 
              valTab.append(CDisplayListItem('Next', match.group(1), CDisplayListItem.TYPE_CATEGORY, [Url], name, '', None))                
           return valTab

        if 'AMATEURPORN' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.amateurporn.net' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('channellist(.*?)searchbox', data, re.S)
           if parse:
              phCats = re.findall('<a href="(.*?)"\stitle=".*?">(.*?)</a>', parse.group(1), re.S)
           if phCats:
              for (phUrl, phTitle) in phCats: 
                  valTab.append(CDisplayListItem(phTitle,self.MAIN_URL+phUrl,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'AMATEURPORN-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           return valTab
        if 'AMATEURPORN-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next = url
           Movies = re.findall('class="video">.*?<a\shref="(.*?)".*?<img src="(.*?)"\salt="(.*?)".*?margin-top:2px;">(.*?)\sviews</span>.*?text-align:right;\'>(.*?)<br\s/>', data, re.S) 
           if Movies:
              for (Url, Pic, Title, Views, Runtime) in Movies:
                  Pic = Pic.replace(' ','%20')
                  Runtime = Runtime.strip()
                  valTab.append(CDisplayListItem(decodeHtml(Title),'['+Runtime+'] '+Title,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, Pic, None)) 
           match = re.findall("href='page(.*?)'>&raquo", data, re.S)
           if match:
              printDBG( 'Host listsItems next: '+next )
              next = next.replace(next.split('/')[-1],'')
              valTab.append(CDisplayListItem('Next', 'Page : '+match[-1], CDisplayListItem.TYPE_CATEGORY, [next+'page'+match[-1]], name, '', 'Next'))                
           return valTab

        if 'FOTKA-PL-KAMERKI' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = url 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           parse = re.search('"rooms":(.*?),"status":"OK"', data, re.S)
           if not parse: return valTab
           #printDBG( 'Host listsItems parse.group(1): '+parse.group(1) )
           result = simplejson.loads(parse.group(1))
           if result:
              for item in result:
                 try:
                    Name = str(item["name"])
                    Age = str(item["age"])
                    Url = str(item["streamUrl"].replace('\/','/'))+' live=1'
                    Title = str(item["title"])
                    Viewers = str(item["viewers"])
                    Image = str(item["av_126"].replace('\/','/'))
                    hls = str(item["streamMPEGHLSUrl"].replace('\/','/'))
                    try:
                       Image = str(item["av_640"].replace('\/','/'))
                    except Exception: printExc()
                    if config.plugins.iptvplayer.fotka.value == '0': Url = hls.replace('https','http').replace('manifest.hls','index.m3u8')
                    valTab.append(CDisplayListItem(Name,'[Age : '+Age+']'+'   [Views:  '+Viewers+']      '+Title, CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 0)], 0, Image, None)) 
                 except Exception: printExc()
           return valTab

        if 'CAM4-KAMERKI' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.cam4.pl' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           valTab.insert(0,CDisplayListItem("--- HD ---",       "HD",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/cams/hd"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Poland ---",       "Polskie",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/poland-cams"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Couples ---",       "Pary",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/couple"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Male ---",       "Mężczyźni",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/male"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Transsexual ---",       "Transseksualiści",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/shemale"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",       "Nowe",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/new"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Female ---",       "Kobiety",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/female"], 'CAM4-KAMERKI-clips', '',None))
           return valTab 
        if 'CAM4-KAMERKI-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           vr=''
           next = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="profileDataBox', '</div> </div> </div>')
           for item in data:
              #phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-profile=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phCountry = self.cm.ph.getSearchGroups(item, '''flag.+?title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = phUrl.strip('/')
              if config.plugins.iptvplayer.cam4.value == '1':
                  stream = '-rtmp-'
              else:
                  stream = '-m3u8-'
              phImage = urlparser.decorateUrl(phImage, {'Referer': 'https://www.cam4.com'})
              valTab.append(CDisplayListItem(phTitle+vr,phTitle+vr+'   [Country: '+phCountry+']   '+stream,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', stream+'http://www.cam4.pl'+phUrl, 1)], 0, phImage, None)) 
           if next:
              valTab.append(CDisplayListItem('Next ', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab 

        if 'CAMSODA' == name:
            printDBG( 'Host listsItems begin name='+name )
            self.MAIN_URL = 'https://www.camsoda.com/' 
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
            try: data = self.cm.getURLRequestData(query_data)
            except Exception as e:
                printExc()
                msg = _("Last error:\n%s" % str(e))
                GetIPTVNotify().push('%s' % msg, 'error', 20)
                printDBG( 'Host listsItems query error url:'+url )
                return valTab
            #printDBG( 'Host listsItems data: '+data )
            #"template":["username","display_name","connections","sort_value","subject_html","stream_name","tsize","server_prefix"]
            dane = re.search('"results":(.*?)}]', data, re.S)
            if dane: 
                dane = dane.group(1)+'}]'
                printDBG( 'Host listsItems json: '+dane )
                try:
                    result = simplejson.loads(dane)
                    tsize = ''
                    if result:
                        for item in result:
                            subject_html = ''
                            try:
                                Name = str(item["tpl"][1]) #.encode("utf-8")
                            except Exception: printExc()
                            try:
                                stream_name = str(item["tpl"][5]) #.encode("utf-8")
                            except Exception: printExc()
                            try:
                                tsize = str(item["tpl"][6])
                            except Exception: printExc()
                            try:
                                subject_html = str(item["tpl"][4])
                            except Exception: printExc()
                            try:
                                enc = stream_name.split('-')[-1]
                            except Exception: printExc()
                            try:
                                username = str(item['tpl'][0])
                            except Exception: printExc()
                            #printDBG( 'Host Name: '+Name )
                            #printDBG( 'Host stream_name: '+stream_name )
                            #printDBG( 'Host tsize: '+tsize )
                            #printDBG( 'Host enc: '+enc )
                            #printDBG( 'Host username: '+username )
                            Image = 'https://thumbs-orig.camsoda.com/thumbs/'+stream_name+'/'+enc+'/'+tsize+'/null/'+username+'.jpg'
                            videourl = "https://www.camsoda.com/api/v1/video/vtoken/" + username + "?username=guest_" + str(random.randrange(100, 55555))
                            if Image.startswith('//'): Image = 'http:' + Image 
                            if config.plugins.iptvplayer.camsoda.value == '1':
                                videourl = 'rtmp'+videourl
                                stream = 'rtmp'
                            else:
                                stream = 'm3u8'
                            if stream_name:
                                valTab.append(CDisplayListItem(Name, Name+'   '+stream+'\n'+subject_html, CDisplayListItem.TYPE_VIDEO, [CUrlItem('', videourl, 1)], 0, Image, None)) 
                except Exception: printExc()
            return valTab 

        if 'STREAMATE' == name:
            printDBG( 'Host listsItems begin name='+name ) 
            self.MAIN_URL = 'https://streamate.com' 
            COOKIEFILE = os_path.join(GetCookieDir(), 'streamate.cookie')
            query_data = { 'url': url,  'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
            try:
                data = self.cm.getURLRequestData(query_data)
            except Exception as e:
                printExc()
                return valTab 
            printDBG( 'Host listsItems data: '+data )
            data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="cats__content">', 'class="recents__list">', False)[1]
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
            for item in data:
                Title = self._cleanHtmlStr(item).split(' ')[1]
                Title = self.cm.ph.getDataBeetwenMarkers(item, '</span>', '</a>', False)[1]
                Title = str(Title).strip()
                Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
                if Url.startswith('/'): Url = 'https://streamate.com' + Url 
                valTab.append(CDisplayListItem(decodeHtml(Title),decodeHtml(Title),CDisplayListItem.TYPE_CATEGORY, [Url],'STREAMATE-clips', '', None)) 
            return valTab 
        if 'STREAMATE-clips' == name:
            printDBG( 'Host listsItems begin name='+name ) 
            self.MAIN_URL = 'https://streamate.com' 
            COOKIEFILE = os_path.join(GetCookieDir(), 'streamate.cookie')
            query_data = { 'url': url,  'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
            try:
                data = self.cm.getURLRequestData(query_data)
            except Exception as e:
                printExc()
                return valTab 
            printDBG( 'Host listsItems data: '+data )
            next = self.cm.ph.getDataBeetwenMarkers(data, 'class="pagination">', 'Next', False)[1]
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="js-dynamicsearch" data-status="online"', '</figure>')
            for item in data:
                phTitle = self.cm.ph.getSearchGroups(item, '''data-name=['"]([^"^']+?)['"]''', 1, True)[0] 
                phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
                phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
                phImage = self.cm.ph.getSearchGroups(item, '''data-thumbid=['"]([^"^']+?)['"]''', 1, True)[0] 
                age = self.cm.ph.getSearchGroups(item, '''"year">([^>]+?)<''', 1, True)[0].strip()
                if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
                if phImage.startswith('//'): phImage = 'http:' + phImage
                phImage = 'http://m2.nsimg.net/biopic/original4x3/' + phImage
                valTab.append(CDisplayListItem(decodeHtml(phTitle), decodeHtml(phTitle)+'  [Age:'+age+']', CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phTitle, 1)], 0, phImage, None)) 
            if next:
                next = re.compile('''href=['"]([^'^"]+?)['"]''').findall(next) 
                if next:
                    next = next[-1]
                    if next.startswith('/'): next = 'https://streamate.com' + next
                    valTab.append(CDisplayListItem('Next', 'Page : '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None)) 
            return valTab 

        if 'NAKED' == name:
            printDBG( 'Host listsItems begin name='+name ) 
            self.MAIN_URL = 'http://new.naked.com' 
            COOKIEFILE = os_path.join(GetCookieDir(), 'naked.cookie')
            host = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Mobile Safari/537.36'
            header = {'User-Agent': host, 'Accept':'application/json','Accept-Language':'en,en-US;q=0.7,en;q=0.3','X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded'} 
            query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
            try:
                data = self.cm.getURLRequestData(query_data)
            except Exception as e:
                printExc()
                return valTab 
            printDBG( 'Host listsItems data: '+data )
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-model-card', '<div class="each-model" data-cam-score=')
            for item in data:
                phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
                phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
                phImage = self.cm.ph.getSearchGroups(item, '''data-profile-image=['"]([^"^']+?)['"]''', 1, True)[0] 
                Video = self.cm.ph.getSearchGroups(item, '''data-live-feed=['"]([^"^']+?)['"]''', 1, True)[0] 
                age = self.cm.ph.getSearchGroups(item, '''model-age">([^>]+?)<''', 1, True)[0] 
                if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
                if phImage.startswith('//'): phImage = 'http:' + phImage
                valTab.append(CDisplayListItem(decodeHtml(phTitle), decodeHtml(phTitle), CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Video, 0)], 0, phImage, None)) 
            return valTab 

        if 'YOUJIZZ' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.youjizz.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'category">', '</ul>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           #printDBG( 'Host2 data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''">([^"^']+?)<''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'YOUJIZZ-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- HD ---",       "HD",       CDisplayListItem.TYPE_CATEGORY,["http://www.youjizz.com/search/HighDefinition-1.html#"], 'YOUJIZZ-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",       "Top Rated",       CDisplayListItem.TYPE_CATEGORY,["http://www.youjizz.com/top-rated/1.html"], 'YOUJIZZ-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---",       "Newest",       CDisplayListItem.TYPE_CATEGORY,["http://www.youjizz.com/newest-clips/1.html"], 'YOUJIZZ-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Popular ---",       "Popular",       CDisplayListItem.TYPE_CATEGORY,["http://www.youjizz.com/most-popular/1.html"], 'YOUJIZZ-clips', '',None))
           self.SEARCH_proc='YOUJIZZ-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'YOUJIZZ-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.youjizz.com/search/%s-1.html' % url.replace(' ','+'), 'YOUJIZZ-clips')
           return valTab
        if 'YOUJIZZ-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           self.MAIN_URL = 'http://www.youjizz.com' 
           url = url.replace(' ','%20')
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next=''
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', '</div>', False)[1]
           next_page = self.cm.ph.getAllItemsBeetwenMarkers(next_page, '<li', '</li>')
           for item in next_page:
              next = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
           if next.startswith('/'): next = self.MAIN_URL + next
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video-thumb', 'format-views')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''html'>([^"^']+?)</a>''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''"time">([^"^']+?)<''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle).strip(),'['+phRuntime+'] '+decodeHtml(phTitle).strip(),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           if next:
              valTab.append(CDisplayListItem('Next', 'Next', CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))
           return valTab

        if 'DACHIX' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.dachix.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="listing-categories">', '</div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl+"/videos"],'DACHIX-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---",       "Longest",       CDisplayListItem.TYPE_CATEGORY,["http://www.dachix.com/videos?sort=longest"], 'DACHIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---",       "Most Popular",       CDisplayListItem.TYPE_CATEGORY,["http://www.dachix.com/videos?sort=popular"], 'DACHIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---",       "Most Viewed",       CDisplayListItem.TYPE_CATEGORY,["http://www.dachix.com/videos?sort=viewed"], 'DACHIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",       "Top Rated",       CDisplayListItem.TYPE_CATEGORY,["http://www.dachix.com/videos?sort=rated"], 'DACHIX-clips', '',None))
           self.SEARCH_proc='DACHIX-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'DACHIX-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.dachix.com/s/%s' % url.replace(' ','+'), 'DACHIX-clips')
           return valTab
        if 'DACHIX-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a class=\'thumb_container video\'', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              phRuntime = self.cm.ph.getSearchGroups(item, '''S">([^>]+?)[-<]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = 'http://www.dachix.com' + phUrl
              if phUrl.startswith('www'): phUrl = 'http://' + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              if next.startswith('/'): next = 'http://www.dachix.com' + next
              valTab.append(CDisplayListItem('Next', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))
           return valTab

        if 'DRTUBER' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.drtuber.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'contain_cols', '<div class="drop_inner">', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'DRTUBER-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='DRTUBER-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'DRTUBER-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.drtuber.com/search/videos/%s' % url.replace(' ','+'), 'DRTUBER-clips')
           return valTab
        if 'DRTUBER-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''class="next"><a href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href="/video/', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''([\d]?\d\d:\d\d)''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = 'http://www.drtuber.com' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              if next.startswith('/'): next = self.MAIN_URL + next 
              valTab.append(CDisplayListItem('Next', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))
           return valTab

        if 'MYFREECAMS' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.myfreecams.com' 
           #url = 'https://www.myfreecams.com/mfc2/php/online_models_splash.php'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class=slm_c>', '</div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = phUrl.split('/')[-1]
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phTitle, 1)], 0, phImage, None)) 
           if config.plugins.iptvplayer.xxxsortmfc.value: valTab.sort(key=lambda poz: poz.name)
           return valTab 

#           phCats = re.findall('model_detail=(.*?)&.*?img src=(.*?jpg).*?</div>', data, re.S) 
#           if phCats:
#              for (phTitle, phImage) in phCats: 
#                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phTitle, 1)], 0, phImage, None)) 
#                  if config.plugins.iptvplayer.xxxsortmfc.value: valTab.sort(key=lambda poz: poz.name)
#           return valTab 

        if 'TNAFLIX' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.tnaflix.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'Categories</h', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].strip()
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'TNAFLIX-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Featured ---",       "Featured",       CDisplayListItem.TYPE_CATEGORY,["https://www.tnaflix.com/featured/?d=all&period=all"], 'TNAFLIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---",       "Most Popular",       CDisplayListItem.TYPE_CATEGORY,["https://www.tnaflix.com/popular/?d=all&period=all"], 'TNAFLIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",       "Top Rated",       CDisplayListItem.TYPE_CATEGORY,["https://www.tnaflix.com/toprated/?d=all&period=all"], 'TNAFLIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",       "New",       CDisplayListItem.TYPE_CATEGORY,["https://www.tnaflix.com/new/?d=all&period=all"], 'TNAFLIX-clips', '',None))
           self.SEARCH_proc='TNAFLIX-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'TNAFLIX-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.tnaflix.com/search.php?what=%s&tab=' % url.replace(' ','+'), 'TNAFLIX-clips')
           return valTab
        if 'TNAFLIX-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-vid=', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip()
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''videoDuration'>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              if next.startswith('/'): next = 'https://www.tnaflix.com' + next
              valTab.append(CDisplayListItem('Next', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))
           return valTab

        if 'LIVEJASMIN' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab.insert(0,CDisplayListItem('--- Transgender ---', 'Transgender', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/transgender'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Couple ---', 'Couple', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/couple'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Mature ---', 'Mature', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/mature'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Fetish ---', 'Fetish', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/fetish'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Lesbian ---', 'Lesbian', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/lesbian'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Soul_mate ---', 'Soul_mate', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/soul_mate'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Hot_flirt ---', 'Hot_flirt', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/hot_flirt'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Girl ---', 'Girl', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/girl'], 'LIVEJASMIN-clips', '', None))
           return valTab 
        if 'LIVEJASMIN-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://new.livejasmin.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           sessionID = self.cm.ph.getSearchGroups(data, '''"jsm2session":['"]([^"^']+?)['"]''')[0] 
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'listPagePerformers =', '];', False)[1]
           result = simplejson.loads(data2+']')
           phImage = ''
           if result:
              for item in result:
                 try:
                    phTitle = str(item["pid"])
                    phUrl = 'http://new.livejasmin.com/en/chat/'+phTitle+'?session='+sessionID
                    try:
                       ID = str(item["id"])
                       phImage = self.cm.ph.getDataBeetwenMarkers(data, 'container_'+ID, '</picture>', False)[1]
                       phImage = self.cm.ph.getSearchGroups(phImage, '''jpg-src=['"]([^"^']+?)['"]''')[0] 
                       #printDBG( 'Host phImage: '+str(phImage) )
                    except Exception:
                       printExc()
                    try:
                       conn = urllib2.urlopen('http://109.71.162.191/'+phTitle)
                       conn.close()
                    except Exception:
                       printExc()
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
                 except Exception:
                    printExc()
           data2 = None
           return valTab 

        if 'EL-LADIES' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://search.el-ladies.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('<select id="selSearchNiche"(.*?)</select>', data, re.S)  
           if parse:
              genre = re.findall('<option value="(\d{0,2})">(.*?)<', parse.group(1), re.S) 
              if genre:
                 for ID, phTitle in genre: 
                    if not re.match('(Bizarre|Gay|Men|Piss|Scat)', phTitle):
                       phTitle = decodeHtml(phTitle)
                       phUrl = '%s/?search=%s&fun=0&niche=%s&pnum=%s&hd=%s' % (self.MAIN_URL, phTitle, ID, str(1), 1) 
                       valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'EL-LADIES-clips', '', None)) 
                       valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- New ---",       "New",       CDisplayListItem.TYPE_CATEGORY,["http://just.eroprofile.com/rss.xml"], 'EL-LADIES-new', '',None))
           self.SEARCH_proc='EL-LADIES-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'EL-LADIES-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://search.el-ladies.com/?hd=0&search=%s&fun=0&niche=0' % url.replace(' ','+'), 'EL-LADIES-clips')
           return valTab
        if 'EL-LADIES-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'class="pageNav"', 'next', False)[1]
           match = re.findall('href="(.*?)"', next, re.S)
           phMovies = re.findall('<a\shref="http://just.eroprofile.com/play/(.*?)".*?<img\ssrc="(.*?)".*?<div>(.*?)</div>', data, re.S) 
           if phMovies:
              for (ID, phImage, Cat) in phMovies:
                  phImage = phImage.replace('&amp;','&') 
                  phTitle = decodeHtml(Cat) + ' - ' + ID
                  #query_data = { 'url': 'http://just.eroprofile.com/play/'+ID, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
                  #try:
                  #   data = self.cm.getURLRequestData(query_data)
                  #except:
                  #   printDBG( 'Host listsItems query error' )
                  #   printDBG( 'Host listsItems query error url: '+url )
                  #   return valTab
                  #printDBG( 'Host listsItems title: '+data )
                  #tytul = re.search('<title>(.*?)</title>', data, re.S)  
                  phTitle2 = phTitle #tytul.group(1)
                  valTab.append(CDisplayListItem(phTitle,phTitle2,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', 'http://just.eroprofile.com/play/'+ID, 1)], 0, phImage, None)) 
           if match:
              phUrl = decodeHtml(match[-1])
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, ['http://search.el-ladies.com/'+phUrl], name, '', None))
           return valTab
        if 'EL-LADIES-new' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('CDATA\[(.*?)\].*?src="(.*?)".*?<link>(.*?)</link>', data, re.S) 
           if phMovies:
              for (phTitle, phImage, phUrl) in phMovies:
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           return valTab

        if 'EXTREMETUBE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.extremetube.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'extremetube.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'Categories</h1>', 'footer', False)[1]
           printDBG( 'Host listsItems data: '+data )
           if '<option value' in data:
              data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<option value', '</option>')
           elif 'fromPage=categories' in data:
              data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a class="thumb-cat', '</a>')
           else:
              data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phTitle: phTitle = self._cleanHtmlStr(item) 
              phUrl = self.cm.ph.getSearchGroups(item, '''value=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phUrl: phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              phUrl = phUrl.replace('?fromPage=categories', '') + '?format=json&page=$PAGE$'
              if not 'json' in phUrl: phUrl = phUrl + '?format=json&page=$PAGE$'
              if phTitle != "Select a Category":
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'EXTREMETUBE-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='EXTREMETUBE-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'EXTREMETUBE-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.extremetube.com/videos?search=%s&format=json&page=$PAGE$' % url.replace(' ','+'), 'EXTREMETUBE-clips')
           return valTab
        if 'EXTREMETUBE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           printDBG( 'Host listsItems cat-url: '+str(catUrl) )
           next = url
           if catUrl == None: 
              self.page = 1
           else:
              self.page += 1
           url = url.replace('$PAGE$', '%s' % str(self.page))
           COOKIEFILE = os_path.join(GetCookieDir(), 'extremetube.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data2 = self.cm.ph.getDataBeetwenMarkers(data, '"items":', ',"our_friends"', False)[1]
           #printDBG( 'Host listsItems data2: '+str(data2) )
           try:
              result = byteify(simplejson.loads(data2))
              if result:
                 for item in result:
                    phTitle = str(item["specialchars_title"])
                    phUrl = str(item["video_link"])
                    phImage = str(item["thumb_url"])
                    Runtime = str(item["duration"])
                    if phUrl.startswith('//'): phUrl = 'http:' + phUrl
                    if phImage.startswith('//'): phImage = 'http:' + phImage
                    valTab.append(CDisplayListItem(phTitle,'['+Runtime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
              valTab.append(CDisplayListItem('Next', 'Page: '+str(self.page+1), CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'Next'))                
           except Exception:
              printExc()
           return valTab

        if 'XXXLIST' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'xxxlist.txt' 
           URLLIST_FILE    = 'xxxlist.txt'
           self.filespath = config.plugins.iptvplayer.xxxlist.value
           self.sortList = config.plugins.iptvplayer.xxxsortuj.value
           self.currFileHost = IPTVFileHost() 
           self.currFileHost.addFile(self.filespath + URLLIST_FILE, encoding='utf-8')
           tmpList = self.currFileHost.getGroups(self.sortList)
           for item in tmpList:
               if '' == item: title = (_("Other"))
               else:          title = item
               valTab.append(CDisplayListItem(title,title,CDisplayListItem.TYPE_CATEGORY, [title],'XXXLIST-clips', '', None)) 
           return valTab
        if 'XXXLIST-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           desc = ''
           icon = ''
           tmpList = self.currFileHost.getAllItems(self.sortList)
           for item in tmpList:
               if item['group'] == url:
                   Title = item['title_in_group']
                   Url = item['url']
                   if item.get('icon', '') != '':
                      icon = item.get('icon', '')
                   if item.get('desc', '') != '':
                      desc = item['desc']
                   if Url.endswith('.mjpg') or Url.endswith('.cgi'):
                      valTab.append(CDisplayListItem(Title, Url,CDisplayListItem.TYPE_PICTURE, [CUrlItem('', Url, 1)], 0, '', None)) 
                   else:
                      valTab.append(CDisplayListItem(Title, Url+'\n'+desc,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, icon, None)) 
               elif url == (_("Other")) and item['group'] == '':
                   Title = item['full_title']
                   Url = item['url']
                   if item.get('icon', '') != '':
                      icon = item.get('icon', '')
                   if item.get('desc', '') != '':
                      desc = item['desc']
                   if Url.endswith('.mjpg') or Url.endswith('.cgi'):
                      valTab.append(CDisplayListItem(Title, Url,CDisplayListItem.TYPE_PICTURE, [CUrlItem('', Url, 1)], 0, '', None)) 
                   else:
                      valTab.append(CDisplayListItem(Title, Url+'\n'+desc,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, icon, None)) 
           return valTab

        if 'RAMPANT' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.rampant.tv' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'rampant.cookie')
           url = 'http://api.rampant.tv/player_schedule2.php?type=2&affid=726&bustCache=20130708&json'
           host = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
           header = {'User-Agent': host, 'Accept':'application/json','Accept-Language':'en,en-US;q=0.7,en;q=0.3','X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              return valTab
           #printDBG( 'data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              if result:
                 for item in result["stream"]["channel"]: 
                    #printDBG( 'item: '+str(item) )
                    streamName = str(item["@attributes"]["streamName"])
                    application = str(item["@attributes"]["application"])
                    performername = str(item["@attributes"]["performername"])
                    title = str(item["@attributes"]["title"])
                    mbr = str(item["@attributes"]["mbr"])
                    phImage = str(item["@attributes"]["logo"]).replace('{SIZE}', '80x65')
                    if phImage.startswith('//'): phImage = 'http:' + phImage
                    live = '0'
                    try:
                       live = str(item["@attributes"]["live"])
                    except Exception:
                       printExc()
                    if live <> '0':
                       if mbr<>'0': streamName=streamName+mbr
                       if 'passionxxx' in streamName:   
                          phUrl = 'http://publish.thewebstream.co:1935/%s/_definst_/rampanttv_%s/playlist.m3u8' % (application, streamName)
                       else:
                          phUrl = 'http://publish.thewebstream.co:1935/%s/%s/playlist.m3u8' % (application, streamName)
                       phUrl = urlparser.decorateUrl(phUrl, {'User-Agent': host, 'Referer': 'https://iptv.firestormmedia.tv/iframes/firecall-responsive'})
                       if self.cm.isValidUrl(phUrl): 
                          tmp = getDirectM3U8Playlist(phUrl)
                          for item in tmp:
                             #printDBG( 'Host listsItems valtab: '  +str(item))
                             if item['bitrate'] != 'unknown':
                                valTab.append(CDisplayListItem(title,performername,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 0)], 0, phImage, None))
           except Exception:
              printExc()
           return valTab 

        if 'BONGACAMS' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://pl.bongacams.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'bongacams.cookie')
           host = 'Mozilla/5.0 (iPad; CPU OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B466 Safari/600.1.4'
           header = {'User-Agent': host, 'Accept':'application/json','Accept-Language':'en,en-US;q=0.7,en;q=0.3','X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded'} 
           query_data = { 'url': url, 'header': header, 'Referer':'https://pl.bongacams.com/', 'Origin':'https://pl.bongacams.com', 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              return valTab
           printDBG( 'First Bonga data: '+data )  
           if config.plugins.iptvplayer.bonga.value == '0': 
              self.bongastream = 'm3u8'
           else:
              self.bongastream = 'rtmp'
           valTab.insert(0,CDisplayListItem("--- Couples ---", "Pary   stream:"+self.bongastream,       CDisplayListItem.TYPE_CATEGORY,["couples"], 'BONGACAMS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Male ---",       "Mężczyźni   stream:"+self.bongastream,       CDisplayListItem.TYPE_CATEGORY,["male"], 'BONGACAMS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Transsexual ---",       "Transseksualiści   stream:"+self.bongastream,       CDisplayListItem.TYPE_CATEGORY,["transsexual"], 'BONGACAMS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",       "Nowe   stream:"+self.bongastream,       CDisplayListItem.TYPE_CATEGORY,["new"], 'BONGACAMS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Female ---",       "Kobiety   stream:"+self.bongastream,       CDisplayListItem.TYPE_CATEGORY,["females"], 'BONGACAMS-clips', '',None))
           return valTab 
        if 'BONGACAMS-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           printDBG( 'Host listsItems cat-url: '+str(catUrl) )
           next = url
           if catUrl == None: 
              self.page = 1
           else:
              self.page += 1
           COOKIEFILE = os_path.join(GetCookieDir(), 'bongacams.cookie')
           Url = 'https://en.bongacams.com/tools/listing_v3.php?livetab=%s&online_only=true&offset=%s&category=%s' % (url, str((self.page*24)-24), url)
           #Url = 'https://pl.bongacams.com/tools/listing_v3.php?tag=&page=1&lang=&countryId=&countryLangs=&online_only=1&category={0}&livetab={0}&pageCount=&mls_width=&_save=1&model_search%5Bper_page%5D=999&model_search%5Bdisplay%5D=auto&model_search%5Bth_type%5D=live&mls_th_per_row=5&model_search%5Bbase_sort%5D=camscore'.format(urllib.quote(url, ''))
           host = 'Mozilla/5.0 (iPad; CPU OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B466 Safari/600.1.4'
           header = {'User-Agent': host, 'Accept':'application/json','Accept-Language':'en,en-US;q=0.7,en;q=0.3','X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded'} 
           query_data = { 'url': Url, 'header': header, 'Referer':'https://pl.bongacams.com/', 'Origin':'https://pl.bongacams.com', 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              return valTab
           printDBG( 'second bonga-clips data: '+data )  
           swfUrl = self.cm.ph.getSearchGroups(data, '''(/swf/chat/BCamChat[^"^']+?)['"]''', 1, True)[0] 
           if swfUrl: 
              swfUrl = self.MAIN_URL+swfUrl
           else:
              swfUrl = 'https://pl.bongacams.com/swf/BCamPlayer.swf?201706271102'
           parse = re.search('"models":(.*?),"online_count', data, re.S)
           if not parse: return valTab
           data = parse.group(1).replace('\\','')
           data = re.sub('"about_me":"(.*?),"vq', '"vq', data)

           printDBG( 'Host data2: '+data )
           x = 0
           phImage = ''
           try:
              result = simplejson.loads(data)
           except:
              printDBG( 'Host error load json ' )
              return valTab
           if result:
              try:
                 for item in result:
                    online = str(item["online"])  
                    room = str(item["room"])  
                    phTitle = str(item["username"]) 
                    phTitle2 = str(item["display_name"]) 
                    try:
                       phImage = str(item["thumb_image"]) 
                       if phImage.startswith('//'): phImage = 'http:' + phImage
                    except Exception:
                       printExc()
                    bitrate = '' 
                    try:
                       bitrate = str(item["vq"]) 
                    except Exception:
                       printExc()
                    printDBG( 'Host phTitle: '+phTitle )
                    printDBG( 'Host online: '+online )
                    printDBG( 'Host room: '+room )
                    phUrl = 'rtmp://dedNUMER_SERWERA-bongacams.com:1935/bongacams playpath=stream_%s?uid=SKROT_MD5 swfUrl=%s pageUrl=https://pl.bongacams.com/ ' % (phTitle, swfUrl)
                    if room != 'vip' and online == 'True':
                       x += 1
                       valTab.append(CDisplayListItem(phTitle2+'   ['+bitrate.upper()+']',phTitle2+'  ('+phTitle+')   '+bitrate.upper(),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
                 printDBG( 'Host ile: '+str(x) )
              except Exception:
                 printExc() 
           valTab.append(CDisplayListItem('Next', 'Page: '+str(self.page+1), CDisplayListItem.TYPE_CATEGORY, [next], name, '', 'Next'))                

           return valTab 

        if 'RUSPORN' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://rusporn.tv' 
           query_data = { 'url': 'http://mixporn24.com', 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'category-list', '<div class="cls">', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)[<"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              valTab.append(CDisplayListItem(phTitle,phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'RUSPORN-clips', '', phUrl)) 
           self.SEARCH_proc='RUSPORN-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'RUSPORN-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://mixporn24.com/search/%s/' % url.replace(' ','+'), 'RUSPORN-clips')
           return valTab
        if 'RUSPORN-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="item', '</strong>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if 'base64' in phImage:  phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'http:' + phImage
              Time = self.cm.ph.getSearchGroups(item, '''</i>([^>]+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time.strip()+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           return valTab

        if 'PORN720' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://porn720.net' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'id="menu-menu', 'class="sub-header', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self._cleanHtmlStr(item)
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              valTab.append(CDisplayListItem(phUrl.split('/')[-1],phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORN720-clips', '', phUrl)) 
           return valTab
        if 'PORN720-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = re.search('rel="next".*?href="(.*?)"', data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<figure', '</figure>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''clock-o"></i>([^>]+?)<''', 1, True)[0].strip()
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              phUrl = next.group(1)
              valTab.append(CDisplayListItem('Next ', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', catUrl))                
           return valTab

        if 'PORNTREX' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.porntrex.com' 
           self.format4k = config.plugins.iptvplayer.xxx4k.value
           COOKIEFILE = os_path.join(GetCookieDir(), 'porntrex.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="list-categories', 'footer', False)[1]
           #printDBG( 'Host2 getResolvedURL data: '+str(data) )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="item"', 'class="rating')
           printDBG( 'Host3 getResolvedURL data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'https:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': 'https://www.porntrex.com'})
              except: pass
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNTREX-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           return valTab
        if 'PORNTREX-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           COOKIEFILE = os_path.join(GetCookieDir(), 'porntrex.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video-item', '</ul>')
           #printDBG( 'Host2 getResolvedURL data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''fa-clock-o"></i>([^"^']+?)<''', 1, True)[0]
              if phImage.startswith('//'): phImage = 'https:' + phImage
              try:
                 phImage = urlparser.decorateUrl(phImage, {'Referer': 'https://www.porntrex.com'})
              except: pass
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           return valTab

        if 'PORNDOE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://porndoe.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self._cleanHtmlStr(item).strip()
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/category/[^"^']+?)['"]''', 1, True)[0] 
              if phUrl:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'PORNDOE-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- By duration ---", "By duration", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=duration-down'], 'PORNDOE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most popular ---", "Most popular", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=likes-down'], 'PORNDOE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most viewed ---", "Most viewed", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=views-down'], 'PORNDOE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most recent ---", "Most recent", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos'], 'PORNDOE-clips', '',None))
           self.SEARCH_proc='porndoe-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'porndoe-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://porndoe.com/search?keywords=%s' % url.replace(' ','+'), 'PORNDOE-clips')
           return valTab
        if 'PORNDOE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           self.MAIN_URL = 'http://porndoe.com' 
           host = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''page\snext"><a\shref=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-id=', 'item -->')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''img src=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('/'): phUrl = 'https://www.porndoe.com'+ phUrl

              phImage = urlparser.decorateUrl(phImage, {'Referer': phUrl, 'User-Agent': host}) 

              Time = self.cm.ph.getSearchGroups(item, '''([\d]?\d\d:\d\d)''', 1, True)[0] 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem('Next ', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
            
           return valTab

        if 'PORNFROMCZECH' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornfromczech.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornfromczech.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornfromczech.cookie', 'pornfromczech.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li id="menu-item', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNFROMCZECH-clips', '', phUrl)) 
           self.SEARCH_proc='PORNFROMCZECH-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'PORNFROMCZECH-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://pornfromczech.com/?s=%s&x=0&y=0' % url.replace(' ','+'), 'PORNFROMCZECH-clips')
           return valTab              
        if 'PORNFROMCZECH-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornfromczech.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornfromczech.cookie', 'pornfromczech.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+str(data) )
           Movies = re.findall('<div\sclass="thumb">.*?<a\shref="(.*?)".*?title="(.*?)">.*?<img\ssrc="(.*?)".*?<p class="duration">(.*?)</p>', data, re.S) 
           if Movies:
              for (phUrl, phTitle, phImage, Time) in Movies:
                  Time = Time.strip()
                  phImage = urlparser.decorateUrl(phImage, {'Referer': url})
                  valTab.append(CDisplayListItem(decodeHtml(phTitle), '['+Time+']    '+decodeHtml(phTitle), CDisplayListItem.TYPE_CATEGORY, [phUrl], 'PORNFROMCZECH-serwer', phImage, decodeHtml(phTitle)))                
           match = re.search('rel="next" href="(.*?)"', data, re.S)
           if match:
              phUrl = match.group(1)
              valTab.append(CDisplayListItem('Next ', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))                
           return valTab
        if 'PORNFROMCZECH-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornfromczech.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornfromczech.cookie', 'pornfromczech.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+str(data) )
           phserwer = ''
           phName = catUrl 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<iframe', '</iframe>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phserwer = phUrl.split('/')[2]+' - '
              if 'strdef.world' in phUrl: break
              valTab.append(CDisplayListItem(phserwer+phName,phUrl,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, '', None)) 
           return valTab

        if 'FILMYPORNO' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.filmyporno.tv' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, '<h2>Kategorie', 'footer-top-col', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'item--channel col', '</div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img\ssrc=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'FILMYPORNO-clips', phImage, phUrl)) 
           valTab.insert(0,CDisplayListItem("--- NAJDŁUŻSZE ---",       "NAJDŁUŻSZE",                    CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/longest/"], 'FILMYPORNO-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- NAJCZĘŚCIEJ DYSKUTOWANE ---","NAJCZĘŚCIEJ DYSKUTOWANE", CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/most-discussed/"], 'FILMYPORNO-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- NAJLEPIEJ OCENIONE ---",     "NAJLEPIEJ OCENIONE",      CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/top-rated/"], 'FILMYPORNO-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- NAJPOPULARNIEJSZE ---",      "NAJPOPULARNIEJSZE",       CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/most-viewed/"], 'FILMYPORNO-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- NOWE FILMY ---",             "NOWE FILMY",              CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/videos/"], 'FILMYPORNO-clips', '',None))
           return valTab
        if 'FILMYPORNO-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'rel="next"', '/>', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'item-col col', '</div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''time">([^"^']+?)<''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'http:' + phImage
              Time = Time.strip()
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              url = re.sub('page.+', '', url)
              valTab.append(CDisplayListItem('Next ', 'Page: '+url+next_page, CDisplayListItem.TYPE_CATEGORY, [url+next_page], name, '', None))                
           return valTab

        if 'CLIPHUNTER' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.cliphunter.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('id="submenu-categories">(.*?)</div>', data, re.S)
           if parse:
              phCats = re.findall('href="(/categories/.*?)".*?>(.*?)<', parse.group(1), re.S)
              if phCats:
                 for (phUrl, phTitle) in phCats:
                     phUrl = 'http://www.cliphunter.com%s/' % phUrl.replace(' ','%20')
                     if phTitle <> "More ... ": 
                        valTab.append(CDisplayListItem(decodeHtml(phTitle),phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'CLIPHUNTER-clips', '', phUrl)) 
           self.SEARCH_proc='CLIPHUNTER-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'CLIPHUNTER-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.cliphunter.com/search/%s' % url.replace(' ','+'), 'CLIPHUNTER-clips')
           return valTab
        if 'CLIPHUNTER-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           Movies = re.findall('class="t"\shref="(.*?)".*?class="i"\ssrc="(.*?)".*?class="tr">(.*?)</div>.*?class="vttl.*?">(.*?)</a>', data, re.S) 
           if Movies:
              for (phUrl, phImage, Time, phTitle) in Movies:
                 Time = Time.strip()
                 phImage = urlparser.decorateUrl(phImage, {'Referer': url})
                 if Time[:2]<>'00': 
                    valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', 'http://www.cliphunter.com'+phUrl, 1)], 0, phImage, None)) 
           match = re.search('rel="next" href="(.*?)"', data, re.S)
           if match:
              phUrl = match.group(1)
              valTab.append(CDisplayListItem('Next ', 'Page: '+'http://www.cliphunter.com'+phUrl, CDisplayListItem.TYPE_CATEGORY, ['http://www.cliphunter.com'+phUrl], name, '', None))                
           return valTab

        if 'EMPFLIX' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.empflix.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           genre = re.findall('"thumb"\shref="(.*?)".*?src="(.*?)".*?title="(.*?)"', data, re.S) 
           if genre:
              for (phUrl, phImage, phTitle) in genre:
                 phTitle = decodeHtml(phTitle).strip()
                 phImage = 'http:'+phImage
                 if not phTitle == "All": 
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'EMPFLIX-clips', phImage, None)) 
           return valTab
        if 'EMPFLIX-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall("data-vid='.*?data-name='(.*?)'.*?href='(.*?)'.*?data-original='(.*?)'.*?videoDuration\'>(.*?)<", data, re.S)  
           if phMovies:
              for ( phTitle, phUrl, phImage, phRuntime) in phMovies:
                  if phUrl[:2] == "//":
                     phUrl = "http:" + phUrl
                  else:
                     phUrl = self.MAIN_URL + phUrl
                  valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.findall('<a class="llNav".*?href="(.*?)"', data, re.S)
           if match:
              phUrl = match[0]
              printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl], name, '', None))
           return valTab

        if 'PORNOHUB' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://pornohub.su' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornohub.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           parse = re.search('<a href="#">Categories<(.*?)pornohub.su/my-list/', data, re.S)
           if parse:
              phCats = re.findall('href="(.*?)"', parse.group(1), re.S) 
              if phCats:
                 for (phUrl) in phCats:
                    phTitle = decodeHtml(phUrl).replace ('https://pornohub.su/','').replace('/','')
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNOHUB-clips', '', None)) 
           #valTab.insert(0,CDisplayListItem("--- PORNSTARS ---",      "PORNSTARS", CDisplayListItem.TYPE_CATEGORY,["http://pornohub.su/pornstars/"], 'PORNOHUB-pornstars', '',None))
           #valTab.insert(0,CDisplayListItem("--- PREMIUM SELECTION ---",     "PREMIUM SELECTION",      CDisplayListItem.TYPE_CATEGORY,["http://pornohub.su/porn/premium-selection/"], 'PORNOHUB-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- MOFOS HD 720 ---","MOFOS HD 720", CDisplayListItem.TYPE_CATEGORY,["http://pornohub.su/porn/mofos/"], 'PORNOHUB-clips', '',None))
           #valTab.insert(0,CDisplayListItem("--- BRAZZERS ---",       "BRAZZERS",  CDisplayListItem.TYPE_CATEGORY,["http://pornohub.su/porn/brazzers/"], 'PORNOHUB-clips', '',None))
           self.SEARCH_proc='PORNOHUB-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'PORNOHUB-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://pornohub.su/?s=%s' % url.replace(' ','+'), 'PORNOHUB-clips')
           return valTab
        if 'PORNOHUB-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://pornohub.su' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornohub.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           parse = re.search('<div class="td-category-grid">(.*?)page-nav', data, re.S)
           if parse:
              #printDBG( 'Host listsItems parse: '+parse.group(1) )
              if not '/page/' in url:
                 hot5 = self.cm.ph.getDataBeetwenMarkers(parse.group(1), '<div class="td-container">', '"entry-thumb99">', False)[1]
                 hot5 = self.cm.ph.getAllItemsBeetwenMarkers(hot5, '"td-module-thumb">', 'Article">')
                 for item in hot5:
                    phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
                    phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
                    phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
                    phTitle = decodeHtml(phTitle)
                    phRuntime = '-'
                    if phImage.startswith('//'): phImage = 'http:' + phImage
                    valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           hot5 = self.cm.ph.getAllItemsBeetwenMarkers(data, '"entry-thumb99">', 'Article">')
           for item in hot5:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''"time">([^>]+?)<''', 1, True)[0] 
              phTitle = decodeHtml(phTitle)
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           hot5 = None  
           match = re.findall('</a><a href="(.*?)"', data, re.S)
           if match:
              phUrl = match[-1]
              if '#' in phUrl: phUrl = match[-2]
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))
           return valTab
        if 'PORNOHUB-pornstars' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornohub.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('"td-module-image44">.*?href="(.*?)".*?title="(.*?)".*?src="(.*?)".*?camera"></i>(.*?)</div>', data, re.S)  
           if phMovies:
              for ( phUrl, phTitle, phImage, phRuntime) in phMovies:
                  if phImage.startswith('//'): phImage = 'http:' + phImage
                  valTab.append(CDisplayListItem(decodeHtml(phTitle), 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl+'#videos'], 'PORNOHUB-pornstars-clips', phImage, None))
           match = re.findall('</a><a href="(.*?)"', data, re.S)
           if match:
              phUrl = match[-1]
              printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))
           return valTab
        if 'PORNOHUB-pornstars-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornohub.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('td-block-span.*?"time">(.*?)<.*?href="(.*?)".*?title="(.*?)".*?src="(.*?)"', data, re.S)  
           if phMovies:
              for ( phRuntime, phUrl, phTitle, phImage) in phMovies:
                  if phImage.startswith('//'): phImage = 'http:' + phImage
                  valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           phMovies = re.findall('WPcommentSearch.*?href="(.*?)".*?src="(.*?)".*?alt="(.*?)"', data, re.S)  
           if phMovies:
              for ( phUrl, phImage, phTitle ) in phMovies:
                  phRuntime = '-'
                  if phImage.startswith('//'): phImage = 'http:' + phImage
                  valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           return valTab

        if 'THUMBZILLA' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.thumbzilla.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           Cats = re.findall('href="(/categories/.*?)".*?click\',\s\'(.*?)\'', data, re.S) 
           if Cats:
              for (phUrl, phTitle) in Cats:
                 phTitle = decodeHtml(phTitle)
                 if not phTitle == "All": 
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'THUMBZILLA-clips', '', None)) 
           valTab.insert(0,CDisplayListItem("--- Homemade ---",     "Homemade",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/homemade"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- HD Videos ---","HD Videos", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/hd"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Popular Videos ---",     "Popular Videos",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/popular"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Videos ---",     "Top Videos",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/top"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Trending ---",     "Trending",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/trending"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---",     "Newest",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/newest"], 'THUMBZILLA-clips', '',None))
           self.SEARCH_proc='THUMBZILLA-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'THUMBZILLA-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.thumbzilla.com/tags/%s' % url.replace(' ','+'), 'THUMBZILLA-clips')
           return valTab          
        if 'THUMBZILLA-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.thumbzilla.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('href="(/video/.*?)".*?src="(.*?)".*?"title">(.*?)<.*?"duration">(.*?)<', data, re.S)  
           if phMovies:
              for ( phUrl, phImage, phTitle, phRuntime) in phMovies:
                  if phUrl[:2] == "//":
                     phUrl = "http:" + phUrl
                  else:
                     phUrl = self.MAIN_URL + phUrl
                  if phImage[:2] == "//":
                     phImage = "http:" + phImage
                  valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.findall('"next" href="(.*?)"', data, re.S)
           if match:
              phUrl = match[0]
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))
           self.MAIN_URL = '' 
           return valTab

        if 'ADULT' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://adult-channels.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'adult.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           match = re.findall('rel="next" href="(.*?)"', data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article id=', '</article>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phImage.startswith('/'): phImage = 'http://adult-channels.com' + phImage
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = 'http://adult-channels.com' + phUrl
              if 'Online' in phTitle or 'TV' in phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if match:
              phUrl = match[0]
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))
           return valTab

        if 'YUVUTU' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.yuvutu.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           self.page = 1
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="yv-element', 'videos</span>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              phTitle = re.sub(' - .+', '', phTitle)
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'YUVUTU-clips', phImage, None)) 
           return valTab
        if 'YUVUTU-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           self.page += 1
           phMovies = re.findall('class="thumb-image">.*?href="(.*?)".*?src="(.*?)".*?title="(.*?)"', data, re.S)  
           if phMovies:
              for ( phUrl, phImage, phTitle ) in phMovies:
                  phTitle = phTitle.replace(' - ','')
                  valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           url = re.sub('page.+', '', url)
           valTab.append(CDisplayListItem('Next', 'Page: '+str(self.page), CDisplayListItem.TYPE_CATEGORY, [url+'page/'+str(self.page)+'/'], name, '', None))
           return valTab

        if 'BEFUCK' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://befuck.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<figure>', '</figure>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'BEFUCK-clips', '', None))
           self.SEARCH_proc='BEFUCK-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'BEFUCK-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://befuck.com/search/%s' % url.replace(' ','+'), 'BEFUCK-clips')
           return valTab
        if 'BEFUCK-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = ''
           next = self.cm.ph.getDataBeetwenMarkers(data, '<nav id="pgn">', '</nav>', False)[1]
           next = self.cm.ph.getDataBeetwenMarkers(next, 'class="active"', 'class="next"', False)[1]
           if next:
              next_page = self.cm.ph.getSearchGroups(next, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<figure>', '</figure>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''<span>([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']   '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab

        if 'PORNICOM' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://pornicom.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="item">', '<div class="info">')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNICOM-clips', phImage, None))
           valTab.insert(0,CDisplayListItem("--- Most popular ---", "Most popular", CDisplayListItem.TYPE_CATEGORY,['http://www.pornicom.com/most-popular/'], 'PORNICOM-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Latest updates ---", "Latest updates", CDisplayListItem.TYPE_CATEGORY,['http://www.pornicom.com/latest-updates/'], 'PORNICOM-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top rated ---", "Top rated", CDisplayListItem.TYPE_CATEGORY,['http://www.pornicom.com/top-rated/'], 'PORNICOM-clips', '',None))
           self.SEARCH_proc='pornicom-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornicom-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.pornicom.com/search/?q=%s' % url.replace(' ','+'), 'PORNICOM-clips')
           return valTab
        if 'PORNICOM-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://pornicom.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', '</div>', False)[1]
           next_page = self.cm.ph.getDataBeetwenMarkers(next_page, '</span>', 'Page', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="image', '<div class="g_clear">')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-poster=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''class="length">([^"^']+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,'['+Time+']   '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              numer = next_page.split('/')[-2]
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab

        if 'HDZOG' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.hdzog.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'hdzog.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host query error url: '+url )
              return valTab
           #printDBG( 'Host getResolvedURL data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="thumbs-categories">', 'video thumbs list', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''"title">([^"^']+?)<''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'HDZOG-clips', phImage, None))
           valTab.insert(0,CDisplayListItem("--- Longest ---", "Longest", CDisplayListItem.TYPE_CATEGORY,['http://www.hdzog.com/longest/'], 'HDZOG-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Popular ---", "Popular", CDisplayListItem.TYPE_CATEGORY,['http://www.hdzog.com/popular/'], 'HDZOG-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---", "Newest", CDisplayListItem.TYPE_CATEGORY,['http://www.hdzog.com/new/'], 'HDZOG-clips', '',None))
           self.SEARCH_proc='hdzog-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'hdzog-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.hdzog.com/search/?q=%s' % url.replace(' ','+'), 'HDZOG-clips')
           return valTab
        if 'HDZOG-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'class="next">', '</li>', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = 'http://www.hdzog.com' + next_page
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="thumbs-videos">', 'video thumbs list', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''class="time">([^"^']+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,'['+Time+']   '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              numer = next_page.split('/')[-2]
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab

        if 'HCLIPS' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.hclips.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'hclips.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="thumb_holder', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Image = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = 'http://www.hclips.com' + phUrl
              if Image.startswith('//'): Image = 'http:' + Image
              if phUrl:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'HCLIPS-clips', Image, None))
           valTab.insert(0,CDisplayListItem("--- Longest ---", "Longest", CDisplayListItem.TYPE_CATEGORY,['http://www.hclips.com/longest/'], 'HCLIPS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Popular ---", "Popular", CDisplayListItem.TYPE_CATEGORY,['http://www.hclips.com/most-popular/'], 'HCLIPS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top ---", "Top", CDisplayListItem.TYPE_CATEGORY,['http://www.hclips.com/top-rated/'], 'HCLIPS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---", "Newest", CDisplayListItem.TYPE_CATEGORY,['http://www.hclips.com/latest-updates/'], 'HCLIPS-clips', '',None))
           self.SEARCH_proc='HCLIPS-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'HCLIPS-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.hclips.com/search/?q=%s&p=0' % url.replace(' ','+'), 'HCLIPS-clips')
           return valTab
        if 'HCLIPS-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'class="next">', 'Next', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="thumb_holder">', 'js-pagination', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''"dur">([^"^']+?)<''', 1, True)[0] 
              valTab.append(CDisplayListItem(phTitle,'['+Time+']   '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              numer = next_page.split('/')[-2]
              if 'search' in next_page: next_page = next_page + url.split('/')[-1]
              valTab.append(CDisplayListItem('Next', 'Next: '+next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab

        if 'PORNOMENGE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.pornomenge.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-escena">', '</h4>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''">([^"^']+?)</a>''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNOMENGE-clips', '', None))
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Kanale ---", "Kanale", CDisplayListItem.TYPE_CATEGORY,['https://www.pornomenge.com/websites/videos/'], 'PORNOMENGE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Pornostars ---", "Pornostars", CDisplayListItem.TYPE_CATEGORY,['https://www.pornomenge.com/pornostars/'], 'PORNOMENGE-Pornostars', '',None))
           valTab.insert(0,CDisplayListItem("--- Beste Videos ---", "Beste Videos", CDisplayListItem.TYPE_CATEGORY,['https://www.pornomenge.com/am-meisten-gestimmt/m/'], 'PORNOMENGE-clips', '',None))
           return valTab
        if 'PORNOMENGE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'rel="next"', '/>', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-escena">', 'class="votar-escena')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duracion">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']   '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              numer = next_page.split('/')[-1]
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab
        if 'PORNOMENGE-Pornostars' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'rel="next"', '/>', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-chica">', 'class="clear"></div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duracion">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNOMENGE-clips', '', None))
           if next_page: 
              numer = next_page.split('/')[-1]
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab

        if 'TUBEPORNCLASSIC' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://tubepornclassic.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'tubepornclassic.cookie')
           host = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
           header = {'Cookie': 'language=en', 'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host getResolvedURL query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, 'name="category_dirs', '</li>')
           if not data2:
              data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="list-item', '</li>')
           for item in data2:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = 'http://tubepornclassic.com' + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'TUBEPORNCLASSIC-clips', '', None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---", "Most Viewed", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/most-popular/'], 'TUBEPORNCLASSIC-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---", "Top Rated", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/top-rated/'], 'TUBEPORNCLASSIC-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Latest ---", "Latest", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/latest-updates/'], 'TUBEPORNCLASSIC-clips', '',None))
           self.SEARCH_proc='TUBEPORNCLASSIC-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           data2 = None
           return valTab
        if 'TUBEPORNCLASSIC-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://en.tubepornclassic.com/search/%s/?mode=async&function=get_block&block_id=list_videos_videos_list_search_result&from_videos=1' % url.replace(' ', '+'), 'TUBEPORNCLASSIC-clips')
           return valTab
        if 'TUBEPORNCLASSIC-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://tubepornclassic.com' 
           #url = url.replace('//tubepornclassic.com','//de.tubepornclassic.com')
           COOKIEFILE = os_path.join(GetCookieDir(), 'tubepornclassic.cookie')
           host = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, '<li class="next">', '</li>', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = 'http://tubepornclassic.com' + next_page
           data2 = self.cm.ph.getDataBeetwenMarkers(data, '<div class="list-videos">', 'class="footer', False)[1]
           if not data2:
              data2 = self.cm.ph.getDataBeetwenMarkers(data, '<div class="list-videos">', 'class="pagination"', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data2, '<a', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duration">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if phTitle: 
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']   '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page<>'#search' and next_page<>'': 
              numer = next_page.split('/')[-2]
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           data2 = None
           return valTab

        if 'KOLOPORNO' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.koloporno.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-escena">', '</h4>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''">([^"^']+?)</a>''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNOMENGE-clips', '', None))
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Pornstars ---", "Pornstars", CDisplayListItem.TYPE_CATEGORY,['https://www.koloporno.com/pornstars/'], 'KOLOPORNO-Pornostars', '',None))
           valTab.insert(0,CDisplayListItem("--- Najlepsze Filmy ---", "Najlepsze Filmy", CDisplayListItem.TYPE_CATEGORY,['https://www.koloporno.com/najlepiej-oceniane/m/'], 'KOLOPORNO-clips', '',None))
           self.SEARCH_proc='KOLOPORNO-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'KOLOPORNO-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.koloporno.com/search/?q=%s' % url.replace(' ','+'), 'KOLOPORNO-clips')
           return valTab
        if 'KOLOPORNO-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.koloporno.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'rel="next"', '/>', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-escena">', 'class="votar-escena')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duracion">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']   '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              numer = next_page.split('/')[-1]
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab
        if 'KOLOPORNO-Pornostars' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'rel="next"', '/>', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-chica">', 'class="clear"></div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duracion">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNOMENGE-clips', '', None))
           if next_page: 
              numer = next_page.split('/')[-1]
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab

        if 'SMOTRI' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://smotri.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'smotri.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url,'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host getResolvedURL query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data1: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'videoItemTd">', 'class="NoticeText"')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              phName = phUrl.split('/')[-2]
              valTab.append(CDisplayListItem(phName,decodeHtml(phUrl)+'\n'+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           return valTab 

        if 'REALGFPORN' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.realgfporn.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video-spot">', 'clearfix')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'REALGFPORN-clips', phImage, None))
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---", "Longest", CDisplayListItem.TYPE_CATEGORY,['https://www.realgfporn.com/longest/'], 'REALGFPORN-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---", "Most Viewed", CDisplayListItem.TYPE_CATEGORY,['https://www.realgfporn.com/most-viewed/'], 'REALGFPORN-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---", "Top Rated", CDisplayListItem.TYPE_CATEGORY,['https://www.realgfporn.com/top-rated/'], 'REALGFPORN-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Recent ---", "Most Recent", CDisplayListItem.TYPE_CATEGORY,['https://www.realgfporn.com/most-recent/'], 'REALGFPORN-clips', '',None))
           self.SEARCH_proc='REALGFPORN-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'REALGFPORN-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.realgfporn.com/search/%s/page1.html' % url.replace(' ','+'), 'REALGFPORN-clips')
           return valTab
        if 'REALGFPORN-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.realgfporn.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', 'Next', False)[1]
           next_page = re.compile('href="(.*?)"').findall(next_page)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video-spot', '</strong>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https://www.realgfporn.com/videos/[^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0].replace(' ','%20') 
              Time = self.cm.ph.getSearchGroups(item, '''duration">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              if Time<>'Link' and phUrl:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']   '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              url = re.sub('page.+', '', url)
              valTab.append(CDisplayListItem('Next', url+next_page[-1], CDisplayListItem.TYPE_CATEGORY, [url+next_page[-1]], name, '', None))
           return valTab

        if 'FAAPY' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://faapy.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="categories-drop">', '</ul>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'FAAPY-clips', '', None))
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Channels ---", "Channels", CDisplayListItem.TYPE_CATEGORY,['http://faapy.com/channels'], 'FAAPY-channels', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---", "Most Popular", CDisplayListItem.TYPE_CATEGORY,['http://faapy.com/most-popular/'], 'FAAPY-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---", "Top Rated", CDisplayListItem.TYPE_CATEGORY,['http://faapy.com/top-rated/'], 'FAAPY-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Latest ---", "Latest", CDisplayListItem.TYPE_CATEGORY,['http://faapy.com/'], 'FAAPY-clips', '',None))
           self.SEARCH_proc='FAAPY-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'FAAPY-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://faapy.com/search/?q=%s' % url.replace(' ','+'), 'FAAPY-clips')
           return valTab
        if 'FAAPY-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://faapy.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'class="pagination"', '</ul>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a itemprop', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img\ssrc=['"]([^"^']+?)['"]''', 1, True)[0].replace(' ','%20') 
              Time = self.cm.ph.getSearchGroups(item, '''duration">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              match = re.compile('href="(.*?)"').findall(next_page)
              if match:
                 next_page = self.MAIN_URL+match[-1]
                 printDBG( 'Host listsItems next_page: '  +next_page )
                 valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           return valTab
        if 'FAAPY-channels' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://faapy.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="thumbs channels"', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'FAAPY-clips', phImage, None))
           return valTab

        if 'FUX' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = url
           s='s'
           if 'fux' in url: s=''
           url = url + '/tag' +s
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, '>Categories<', '>Channels<', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].lower().replace('sex movies','')
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phTitle:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'FUX-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Channels ---","Channels",   CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/channel"+s]  ,         'FUX-channels', '',None))
           valTab.insert(0,CDisplayListItem("--- Pornstars ---","Pornstars", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/pornstar"+s],          'FUX-channels','',None))
           valTab.insert(0,CDisplayListItem("--- Most viewed ---","Most viewed",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/video%s?sort=views&time=month" % s],             'FUX-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Highest Rated ---","Highest Rated", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/video%s?sort=rating&time=month" % s],             'FUX-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Lastest ---","Lastest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/video"+s],             'FUX-clips',    '',None))
           self.SEARCH_proc='4TUBE-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if '4TUBE-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search?q=%s' % url.replace(' ','+'), 'FUX-clips')
           return valTab              
        if 'FUX-channels' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''<link\srel="next"\shref=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a class="thumb-link"', '</div></a></div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phVid = self.cm.ph.getSearchGroups(item, '''icon-video"></i>([^"^']+?)<''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img\sdata-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,'[Video: '+phVid+']   '+phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl], 'FUX-clips', phImage, None)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'FUX-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           self.MAIN_URL = url.split('com/')[0]+'com'
           next_page = self.cm.ph.getSearchGroups(data, '''<link\srel="next"\shref=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="col thumb_video"', '</div></div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''img data-master=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''"duration-top">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'HomeMoviesTube' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.homemoviestube.com'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="films', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="category-item', 'category-counter')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'HomeMoviesTube-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/longest/"],          'HomeMoviesTube-clips','',None))
           valTab.insert(0,CDisplayListItem("--- Most viewed ---","Most viewed",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/most-viewed/"],             'HomeMoviesTube-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/top-rated/"],             'HomeMoviesTube-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Recent ---","Most Recent",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/most-recent/"],             'HomeMoviesTube-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Latest Videos ---","Latest Videos",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             'HomeMoviesTube-clips',    '',None))
           self.SEARCH_proc='HomeMoviesTube-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'HomeMoviesTube-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search/%s/page1.html' % url.replace(' ','+'), 'HomeMoviesTube-clips')
           return valTab              
        if 'HomeMoviesTube-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.homemoviestube.com'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''<li\sclass='next'><a href=['"]([^"^']+?)['"]''', 1, True)[0] 
           if re.search('id="featured-videos"', data, re.S):
              data = self.cm.ph.getDataBeetwenMarkers(data, '<!-- featured-end', '</html>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="film-item', 'stat-rated')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''this\.src=['"]([^"^']+?)['"]''', 1, True)[0].replace(' ','%20')
              phRuntime = self.cm.ph.getSearchGroups(item, '''"film-time">([^"^']+?)<''', 1, True)[0]
              added = self.cm.ph.getSearchGroups(item, '''"stat-added">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,'['+phRuntime+']  '+phTitle+'\n'+added,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('page'): next_page = '/' + next_page
              next_page = re.sub('page.+', '', url)+next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'UpdateTube' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = url
           url = url+'/categories/'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<figure>', '</figure>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'UpdateTube-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/most-popular/"],             'UpdateTube-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/top-rated/"],             'UpdateTube-clips',    '',None))
           #valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL],             'UpdateTube-clips',    '',None))
           self.SEARCH_proc='UpdateTube-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'UpdateTube-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search/?q=%s' % url.replace(' ','+'), 'UpdateTube-clips')
           return valTab              
        if 'UpdateTube-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'class="active"', 'Next', False)[1]
           next_page = self.cm.ph.getSearchGroups(next, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<figure>', '</figure>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if 'empty' in phImage: phImage = self.cm.ph.getSearchGroups(item, '''data-src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phRuntime = self.cm.ph.getSearchGroups(item, '''"film-time">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,'['+phRuntime+']  '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'MOVIEFAP' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.moviefap.com'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'Categories</h1>', '</ul>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'MOVIEFAP-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Recent ---","Most Recent",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/browse/?category=mr&page="],             'MOVIEFAP-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/browse/?category=tr&page="],             'MOVIEFAP-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Being Watched ---","Being Watched",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/browse/?category=bw&page="],             'MOVIEFAP-clips',    '',None))
           self.SEARCH_proc='MOVIEFAP-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'MOVIEFAP-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search/%s' % url.replace(' ','+'), 'MOVIEFAP-clips')
           return valTab              
        if 'MOVIEFAP-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.moviefap.com'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'class="current"', 'next', False)[1]
           next_page = self.cm.ph.getSearchGroups(next, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video', '</div></div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img\ssrc=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phRuntime = self.cm.ph.getSearchGroups(item, '''"videoleft">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,'['+phRuntime+']  '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'yourporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://yourporn.sexy'
           COOKIEFILE = os_path.join(GetCookieDir(), 'yourporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           #printDBG( 'Host listsItems data: '+str(data) )
           cats = '[{"title":"Fantasy-Massage","url":"/blog/Fantasy-Massage/0.html?sc"},\
           {"title":"POV","url":"/blog/POV/0.html?ht"},{"title":"Blowjob","url":"/blog/blowjob/0.html?ht"},\
           {"title":"Anal","url":"/blog/anal/0.html?ht"},{"title":"Porn","url":"/blog/porn/0.html?ht"},\
           {"title":"Black","url":"/blog/black/0.html?ht"},{"title":"Interracial","url":"/blog/interracial/0.html?ht"},\
           {"title":"BigAss","url":"/blog/BigAss/0.html?ht"},{"title":"BigTits","url":"/blog/BigTits/0.html?ht"},\
           {"title":"Facial","url":"/blog/facial/0.html?ht"},{"title":"Bukkake","url":"/blog/bukkake/0.html?ht"},\
           {"title":"PAWG","url":"/blog/PAWG/0.html?ht"},{"title":"Milf","url":"/blog/milf/0.html?ht"},\
           {"title":"Massage","url":"/blog/Massage/0.html?ht"},{"title":"Artporn","url":"/blog/artporn/0.html?ht"},\
           {"title":"Group","url":"/blog/Group/0.html?ht"},{"title":"Czech","url":"/blog/Czech/0.html?ht"},\
           {"title":"Casting","url":"/blog/Casting/0.html?ht"},{"title":"Real-Wife-Stories","url":"/blog/Real-Wife-Stories/0.html?sc"},\
           {"title":"Naughty-Rich-Girls","url":"/blog/Naughty-Rich-Girls/0.html?sc"},{"title":"Bang-Bus","url":"/blog/Bang-Bus/0.html?sc"},\
           {"title":"Swallowed","url":"/blog/Swallowed/0.html?sc"},{"title":"Evil-Angel","url":"/blog/Evil-Angel/0.html?sc"},\
           {"title":"Blacks-On-Blondes","url":"/blog/Blacks-On-Blondes/0.html?sc"},{"title":"Big-Wet-Butts","url":"/blog/Big-Wet-Butts/0.html?sc"},\
           {"title":"Box-Truck-Sex","url":"/blog/Box-Truck-Sex/0.html?sc"},{"title":"Bums-Besuch","url":"/blog/Bums-Besuch/0.html?sc"},\
           {"title":"Shes-Brand-New","url":"/blog/Shes-Brand-New/0.html?sc"},{"title":"Czech-Casting","url":"/blog/Czech-Casting/0.html?sc"},\
           {"title":"Footjob","url":"/blog/footjob/0.html?ht"},{"title":"Handjob","url":"/blog/handjob/0.html?ht"},\
           {"title":"Ultra-Films","url":"/blog/Ultra-Films/0.html?sc"},{"title":"Wild-On-Cam","url":"/blog/Wild-On-Cam/0.html?sc"},\
           {"title":"Sex-Art","url":"/blog/Sex-Art/0.html?sc"},\
           {"title":"Brown","url":"/blog/brown/0.html?ht"},{"title":"ATK-Girlfriends","url":"/blog/ATK-Girlfriends/0.html?sc"}]'
           result = simplejson.loads(cats)
           for item in result:
              title = str(item["title"])
              url = str(item["url"])
              url = self.MAIN_URL+url
              valTab.append(CDisplayListItem(title,title,CDisplayListItem.TYPE_CATEGORY, [url],'yourporn-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Viewed ---","Top Viewed",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/popular/top-viewed.html"],             'yourporn-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/popular/top-rated.html"],             'yourporn-clips',    '',None))
           self.SEARCH_proc='yourporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'yourporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://yourporn.sexy/%s.html?mode=videos' % url.replace(' ','+'), 'yourporn-clips')
           return valTab              
        if 'yourporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://yourporn.sexy'
           COOKIEFILE = os_path.join(GetCookieDir(), 'yourporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           #printDBG( 'Host listsItems data: '+str(data) )
           next_page = self.cm.ph.getSearchGroups(data, '''<link rel='next' href=['"]([^"^']+?)['"]''', 1, True)[0] 
           #data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-vid=', '<div class="vid_wl')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class=\'pes_wl', '</span></a></div>')
           for item in data:
              printDBG( 'Host listsItems item: '+str(item) )
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/post/[^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"](//[^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''html\'\stitle=['"]([^"^']+?)['"]''', 1, True)[0]
              printDBG( 'Host phTitle1: '+phTitle )
              if len(phTitle)<4: phTitle = self.cm.ph.getSearchGroups(item, '''class=\'tdn\'\stitle=['"]([^"^'^{]+?)['"}]''', 1, True)[0]
              printDBG( 'Host phTitle2: '+phTitle )
              if ' porn blog' in phTitle or len(phTitle)<4: phTitle = self.cm.ph.getSearchGroups(item, '''blog">([^"^']+?)<''', 1, True)[0] 
              printDBG( 'Host phTitle3: '+phTitle )
              if len(phTitle)<4: phTitle = self.cm.ph.getSearchGroups(item, '''title\'>([^>]+?)<''', 1, True)[0]
              printDBG( 'Host phTitle4: '+phTitle )
              if len(phTitle)<4: phTitle = self.cm.ph.getSearchGroups(item, '''text_el">([^>]+?)<''', 1, True)[0]
              printDBG( 'Host phTitle5: '+phTitle )
              if len(phTitle)<4: phTitle = 'No Title'
              phRuntime = self.cm.ph.getSearchGroups(item, '''>(\d\d:\d\d)<''', 1, True)[0] 
              if not phRuntime: phRuntime = self.cm.ph.getSearchGroups(item, '''>(\d\d:\d\d:\d\d)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              phTitle = phTitle.replace('\n','')
              Title = phTitle[:95].split('#')[0]
              if len(Title)<4: Title = phTitle[:95].split('#')[1]
              printDBG( 'Host phTitle6: '+phTitle )
              printDBG( 'Host phUrl: '+phUrl )
              printDBG( 'Host phImage: '+phImage )
              if phRuntime:
                 valTab.append(CDisplayListItem(decodeHtml(Title),'['+phRuntime+']  '+decodeHtml(phTitle[:95]),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'freeomovie' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.freeomovie.com/'
           COOKIEFILE = os_path.join(GetCookieDir(), 'freeomovie.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage4k(url, 'freeomovie.cookie', 'freeomovie.com', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'Categories<', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'freeomovie-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['http://www.freeomovie.com'],             'freeomovie-clips',    '',None))
           self.SEARCH_proc='freeomovie-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'freeomovie-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.freeomovie.com/?s=%s' % url.replace(' ','+'), 'freeomovie-clips')
           return valTab              
        if 'freeomovie-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.freeomovie.com/'
           COOKIEFILE = os_path.join(GetCookieDir(), 'freeomovie.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage4k(url, 'freeomovie.cookie', 'freeomovie.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           next_page = self.cm.ph.getSearchGroups(data, '''<link rel='next' href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="boxtitle">', 'class="metargt">')
           for item in data:
              #printDBG( 'Host listsItems item: '+str(item) )
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              phImage = urlparser.decorateUrl(phImage, {'Referer': url})
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [ phUrl], 'freeomovie-serwer', phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'freeomovie-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'freeomovie.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage4k(url, 'freeomovie.cookie', 'freeomovie.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getDataBeetwenMarkers(data, '<div id="videocont"', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''(http[^"^']+?)['"&]''', 1, True)[0] 
              phTitle = phUrl.split('/')[2]
              if phTitle=='': phTitle=phUrl
              if not 'filecrypt' in phTitle:
                 valTab.append(CDisplayListItem(phTitle,phUrl,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, '', None)) 

        if 'KATESTUBE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.katestube.com'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           #data = self.cm.ph.getDataBeetwenMarkers(data, 'class="thumbs-list">', 'footer', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="thumb">', '</div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'KATESTUBE-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,['https://www.katestube.com/most-popular/'],             'KATESTUBE-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['https://www.katestube.com/top-rated/'],             'KATESTUBE-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Latest ---","Latest",     CDisplayListItem.TYPE_CATEGORY,['https://www.katestube.com/latest-updates/'],             'KATESTUBE-clips',    '',None))
           self.SEARCH_proc='KATESTUBE-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'KATESTUBE-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.katestube.com/search/?q=%s' % url.replace(' ','+'), 'KATESTUBE-clips')
           return valTab              
        if 'KATESTUBE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, '<li><span>', 'class="next"', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="thumb"', '</div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''<img\ssrc=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''duration" class="length">([^"^']+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(phTitle,'['+phTime+']  '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              next = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if next.startswith('/'): next = 'https://www.katestube.com' + next
              valTab.append(CDisplayListItem('Next', next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'ZBIORNIKMINI' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://mini.zbiornik.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'zbiornikmini.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data2 = self.cm.ph.getDataBeetwenMarkers(data, '<div class="collapse navbar-collapse" id="photos-menu">', '</div>', False)[1]
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data2, '<a href=', '</a>')
           for item in data2:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              if phUrl.startswith('/'): phUrl = 'https://mini.zbiornik.com' + phUrl
              printDBG( 'Host phTitle: '+phTitle )
              printDBG( 'Host phUrl: '+phUrl )
              if len(phUrl)>3:
                 if phTitle<>'2004' and phTitle<>'2005' and phTitle<>'2006':
                    valTab.append(CDisplayListItem(phTitle,phUrl.split('/')[-1],     CDisplayListItem.TYPE_CATEGORY,[phUrl],'ZBIORNIKMINI-filmy','https://static.zbiornik.com/upimg/0160d9c44a354d20e81f0e6df5fe832e.jpg',None))
           valTab.insert(0,CDisplayListItem("--- Ranking ---","Ranking",     CDisplayListItem.TYPE_CATEGORY,['https://mini.zbiornik.com/ludzie/ranking'],             'ZBIORNIKMINI-ranking',    '',None))
           valTab.insert(0,CDisplayListItem("--- Wyświetl profile ---","Wyświetl profile",     CDisplayListItem.TYPE_CATEGORY,['https://mini.zbiornik.com/ludzie/szukaj/0,1,1,1,0,1:0:0:0:18:50:2:0:0:1:0'],             'ZBIORNIKMINI-szukaj',    '',None))
           data2 = None
           return valTab    
        if 'ZBIORNIKMINI-szukaj' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'zbiornikmini.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="pager">', '</ul>', False)[1]
           if next_page:
              next_page = re.compile('href="(.*?)"').findall(next_page)
              if next_page[-1].startswith('/'): next_page = 'https://mini.zbiornik.com' + next_page[-1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="search-profile-box">', '</h5>')
           for item in data:
              phImage = self.cm.ph.getSearchGroups(item, '''url\(['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?filmy)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              if phUrl.startswith('/'): phUrl = 'https://mini.zbiornik.com' + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl], 'ZBIORNIKMINI-filmy', phImage, None)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))  
           return valTab
        if 'ZBIORNIKMINI-ranking' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'zbiornikmini.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="pager">', '</ul>', False)[1]
           if next_page:
              next_page = re.compile('href="(.*?)"').findall(next_page)
              if next_page[-1].startswith('/'): next_page = 'https://mini.zbiornik.com' + next_page[-1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="panel-body">', '</h3>')
           for item in data:
              phImage = self.cm.ph.getSearchGroups(item, '''url\(['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              if phUrl.startswith('/'): phUrl = 'https://mini.zbiornik.com' + phUrl +'/filmy'
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl], 'ZBIORNIKMINI-filmy', phImage, None)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))  
           return valTab
        if 'ZBIORNIKMINI-filmy' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'zbiornikmini.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="pager">', '</ul>', False)[1]
           if next_page:
              next_page = re.compile('href="(.*?)"').findall(next_page)
              if next_page[-1].startswith('/'): next_page = 'https://mini.zbiornik.com' + next_page[-1]
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href="/film/', '</a></div>    </div>')
           if not data2: data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a href="/film/', '</a>')
           for item in data2:
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)\n''', 1, True)[0]  
              exTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)Widoczne''', 1, True)[0]  
              Name = re.compile('cropped-info"><a href="/(.*?)"').findall(item)
              if Name: 
                 Name = Name[-1]
              else:
                 Name = ''
              if phUrl.startswith('/'): phUrl = 'https://mini.zbiornik.com' + phUrl
              if phTitle<>'#01':
                 valTab.append(CDisplayListItem(Name+' - '+decodeHtml(phTitle),Name+' - '+decodeHtml(exTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
                 if Name != '' and config.plugins.iptvplayer.xxxzbiornik.value:
                    valTab.append(CDisplayListItem(Name, Name, CDisplayListItem.TYPE_CATEGORY, ['https://mini.zbiornik.com/' +Name+'/filmy'], name, '', None))  
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))  
           data2 = None
           return valTab

        if 'vporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.vporn.com'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="cats-all categories-list">', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'vporn-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest",     CDisplayListItem.TYPE_CATEGORY,['http://www.vporn.com/longest/'],             'vporn-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Votes ---","Most Votes",     CDisplayListItem.TYPE_CATEGORY,['http://www.vporn.com/votes/'],             'vporn-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Comments ---","Most Comments",     CDisplayListItem.TYPE_CATEGORY,['http://www.vporn.com/comments/'],             'vporn-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Favorited ---","Most Favorited",     CDisplayListItem.TYPE_CATEGORY,['http://www.vporn.com/favorites/'],             'vporn-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---","Most Viewed",     CDisplayListItem.TYPE_CATEGORY,['http://www.vporn.com/views/'],             'vporn-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['http://www.vporn.com/rating/'],             'vporn-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['http://www.vporn.com/newest/'],             'vporn-clips',    '',None))
           self.SEARCH_proc='vporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'vporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.vporn.com/search?q=%s' % url.replace(' ','+'), 'vporn-clips')
           return valTab              
        if 'vporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, '<link rel="next"', '>', False)[1]
           #data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="thumb"', '</div>')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video"', 'Rating')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''<img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"time">([^"^']+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = 'https://www.vporn.com' + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              next = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if next.startswith('/'): next = 'https://www.vporn.com' + next
              valTab.append(CDisplayListItem('Next', next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'hotmovs' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://hotmovs.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'hotmovs.cookie')
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           #data = self.cm.ph.getDataBeetwenMarkers(data, 'class="cats-all categories-list">', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'hotmovs-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest",     CDisplayListItem.TYPE_CATEGORY,['http://hotmovs.com/longest/'],             'hotmovs-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,['http://hotmovs.com/most-popular/'],             'hotmovs-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['http://hotmovs.com/top-rated/'],             'hotmovs-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['http://hotmovs.com/latest-updates/'],             'hotmovs-clips',    '',None))
           self.SEARCH_proc='hotmovs-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'hotmovs-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://hotmovs.com/search/?q=%s' % url.replace(' ','+'), 'hotmovs-clips')
           return valTab              
        if 'hotmovs-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'hotmovs.cookie')
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           header = {'Origin': 'http://hotmovs.com', 'Referer':url, 'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return valTab
           printDBG( 'Host getResolvedURL data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'class="next"', '</a>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-video-id=', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''class="thumbnail__info__right">([^"^']+?)<''', 1, True)[0].strip()
              if phUrl.startswith('/'): phUrl = 'http://hotmovs.com' + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(phTitle,'['+phTime+']  '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              next = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if next.startswith('/'): next = 'http://hotmovs.com' + next
              if '/categories/' in next: next = next+'?mode=async&function=get_block&block_id=sphinx_list_cat_videos_videos_list'
              if next <> '#search':
                 valTab.append(CDisplayListItem('Next', next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'pornoxo' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.pornoxo.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornoxo.cookie')
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'title="Main Page"', 'Top Users</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].replace('Tube','') 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phTitle.startswith('+'): phTitle = ''
              if phTitle<>'':
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'pornoxo-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest",     CDisplayListItem.TYPE_CATEGORY,['https://www.pornoxo.com/videos/longest/'],             'pornoxo-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,['https://www.pornoxo.com/videos/most-popular/today/'],             'pornoxo-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['https://www.pornoxo.com/videos/top-rated/'],             'pornoxo-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['https://www.pornoxo.com/videos/newest/'],             'pornoxo-clips',    '',None))
           self.SEARCH_proc='pornoxo-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornoxo-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.pornoxo.com/search/%s/?sort=mw&so=y' % url.replace(' ','+'), 'pornoxo-clips')
           return valTab              
        if 'pornoxo-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornoxo.cookie')
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           header = {'Referer':url, 'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'vidItem', 'class="clear"')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''([\d]?\d\d:\d\d)''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = 'https://www.pornoxo.com' + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(phTitle,'['+phTime+']  '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              if next.startswith('/'): next = 'https://www.pornoxo.com' + next
              valTab.append(CDisplayListItem('Next', next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'pornfree' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://pornfree.tv'
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornfree.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornfree.cookie', 'pornfree.tv', self.defaultParams)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'text">Categories', 'fa fa-times', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'id="menu-item', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''text">([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phTitle<>'Categories':
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'pornfree-clips', '', None)) 
           #valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Liked ---","Liked",     CDisplayListItem.TYPE_CATEGORY,['http://pornfree.tv/?order_post=liked'],             'pornfree-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Viewed ---","Viewed",     CDisplayListItem.TYPE_CATEGORY,['http://pornfree.tv/?order_post=viewed'],             'pornfree-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Latest ---","Latest",     CDisplayListItem.TYPE_CATEGORY,['http://pornfree.tv/?order_post=latest'],             'pornfree-clips',    '',None))
           self.SEARCH_proc='pornfree-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornfree-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://pornfree.tv/?s=%s' % url.replace(' ','+'), 'pornfree-clips')
           return valTab              
        if 'pornfree-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornfree.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornfree.cookie', 'pornfree.tv', self.defaultParams)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+str(data) )
           next_page = self.cm.ph.getSearchGroups(data, '''<link rel='next' href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="item-img">', '</h3>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item) 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [ phUrl], 'pornfree-serwer', phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'pornfree-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornfree.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'pornfree.cookie', 'pornfree.tv', self.defaultParams)
           if not sts: return valTab
           #printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="col-sm-3">', '</div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              valTab.append(CDisplayListItem(phTitle,phUrl,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, '', None)) 
           return valTab

        if 'pinflix' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.pinflix.com'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="pfx-cat">', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'pinflix-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Pornstars ---","Pornstars", CDisplayListItem.TYPE_CATEGORY,['http://www.pinflix.com/pornstars'], 'pinflix-pornstars', '',None))
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest", CDisplayListItem.TYPE_CATEGORY,['http://www.pinflix.com/?order=longest'], 'pinflix-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Featured ---","Featured", CDisplayListItem.TYPE_CATEGORY,['http://www.pinflix.com/?order=featured'], 'pinflix-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated", CDisplayListItem.TYPE_CATEGORY,['http://www.pinflix.com/?order=top-rated'], 'pinflix-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular", CDisplayListItem.TYPE_CATEGORY,['http://www.pinflix.com/?order=most-popular'], 'pinflix-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest", CDisplayListItem.TYPE_CATEGORY,['http://www.pinflix.com/?order=newest'], 'pinflix-clips', '',None))
           self.SEARCH_proc='pinflix-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pinflix-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.pinflix.com/search?search=%s' % url.replace(' ','+'), 'pinflix-clips')
           return valTab              
        if 'pinflix-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''data-next-page=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-thumbindexes', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''img alt="([^"]+?)"''', 1, True)[0]  
              phTime = self.cm.ph.getSearchGroups(item, '''<time>([^>]+?)<''', 1, True)[0]  
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              url = re.sub('&page.+', '', url)
              url = re.sub('\?page.+', '', url)
              if '?order' in url:
                 next_page = url+'&page='+next_page
              else:
                 next_page = url+'?page='+next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'pinflix-pornstars' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, '<li class="next ">', '</li>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="pfx-pornstar">', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = 'https://www.pinflix.com' + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'pinflix-clips', phImage, None)) 
           if next_page:
              next_page = self.cm.ph.getSearchGroups(next_page, '''data-query-value=['"]([^"^']+?)['"]''', 1, True)[0] 
              url = re.sub('\?page.+', '', url)
              next_page = url+'?page='+next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab  

        if 'OKLIVETV' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://oklivetv.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'oklivetv.cookie')
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           header = {'Referer':url, 'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="nag cf">', '</footer>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-id=', '>Likes')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = 'http://oklivetv.com' + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              if next.startswith('/'): next = 'http://oklivetv.com' + next
              next = next + '?orderby=title'
              valTab.append(CDisplayListItem('Next', next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           return valTab

        if 'upornia' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.upornia.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'upornia.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'upornia-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest",     CDisplayListItem.TYPE_CATEGORY,['http://www.upornia.com/longest/'],             'upornia-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,['http://www.upornia.com/most-popular/'],             'upornia-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['http://www.upornia.com/top-rated/'],             'upornia-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['http://www.upornia.com/latest-updates/'],             'upornia-clips',    '',None))
           self.SEARCH_proc='upornia-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'upornia-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://upornia.com/search/?q=%s' % url.replace(' ','+'), 'upornia-clips')
           return valTab              
        if 'upornia-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'upornia.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''<li class="next">[^>]+?href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt="([^"]+?)"''', 1, True)[0]  
              phTime = self.cm.ph.getSearchGroups(item, '''right">([^>]+?)<''', 1, True)[0]  
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'https://upornia.com' + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'txxx' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.txxx.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'txxx.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="c-thumb">', '</div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''title">([^>]+?)<''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'txxx-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest",     CDisplayListItem.TYPE_CATEGORY,['http://www.txxx.com/longest/'],             'txxx-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,['http://www.txxx.com/most-popular/'],             'txxx-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['http://www.txxx.com/top-rated/'],             'txxx-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['http://www.txxx.com/latest-updates/'],             'txxx-clips',    '',None))
           self.SEARCH_proc='txxx-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'txxx-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.txxx.com/search/?s=%s' % url.replace(' ','+'), 'txxx-clips')
           return valTab              
        if 'txxx-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'txxx.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''btn--next"\shref=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-video-id', '</div></div></div><div')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt="([^"]+?)"''', 1, True)[0]  
              phTime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0]  
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'https://www.txxx.com' + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'sunporno' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.sunporno.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'sunporno.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<em>', '</em>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item).strip()[:55]
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'sunporno-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---","Longest",     CDisplayListItem.TYPE_CATEGORY,['https://www.sunporno.com/long-movies/date-last-week/'],             'sunporno-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Most viewed ---","Most viewed",     CDisplayListItem.TYPE_CATEGORY,['https://www.sunporno.com/most-viewed/date-last-week/'],             'sunporno-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- HD Porn ---","HD Porn",     CDisplayListItem.TYPE_CATEGORY,['https://www.sunporno.com/high-definition/date-last-week/'],             'sunporno-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,['https://www.sunporno.com/top-rated/date-last-week/'],             'sunporno-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Recent videos ---","Recent videos",     CDisplayListItem.TYPE_CATEGORY,['https://www.sunporno.com/most-recent/date-last-week/'],             'sunporno-clips',    '',None))
           self.SEARCH_proc='sunporno-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'sunporno-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.sunporno.com/search/%s/' % url.replace(' ','+'), 'sunporno-clips')
           return valTab              
        if 'sunporno-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'sunporno.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getSearchGroups(data, '''pag-next"\shref=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-id=', '</div>	<div')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title="([^"]+?)"''', 1, True)[0]  
              phTime = self.cm.ph.getSearchGroups(item, '''"btime">([^>]+?)<''', 1, True)[0]  
              if phUrl.startswith('/'): phUrl = 'https://www.sunporno.com' + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'https://www.sunporno.com' + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'sexu' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://sexu.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'sexu.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/tag[^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item).strip() 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl 
              if phUrl:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'sexu-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Trending ---","Trending",     CDisplayListItem.TYPE_CATEGORY,['http://sexu.com/trending/1'],             'sexu-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Hall of Fame ---","Hall of Fame",     CDisplayListItem.TYPE_CATEGORY,['http://sexu.com/all/1'],             'sexu-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,['http://sexu.com/1'],             'sexu-clips',    '',None))
           self.SEARCH_proc='sexu-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'sexu-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://sexu.com/search?q=%s' % url.replace(' ','+'), 'sexu-clips')
           return valTab              
        if 'sexu-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'sexu.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'rel="self">', 'rel="next">', False)[1]
           next_page = re.compile('href="(.*?)"').findall(next_page)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="thumb', '</div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt="([^"]+?)"''', 1, True)[0]  
              phTime = self.cm.ph.getSearchGroups(item, '''timeVideo">([^>]+?)<''', 1, True)[0]  
              if phUrl.startswith('/'): phUrl = 'http://sexu.com' + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              next_page = next_page[-1]
              if next_page.startswith('/'): next_page = 'http://sexu.com' + next_page
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'movie4k' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://movie4k.org'
           COOKIEFILE = os_path.join(GetCookieDir(), 'movie4k.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage4k(url, 'movie4k.cookie', 'movie4k.org', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data2: '+str(data) )
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div id="divnotinuse">', '</tbody>')
           for item in data2:
              #printDBG( 'Host item: '+str(item) )
              desc = ''
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]\.([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl 
              if phUrl.startswith('/'): phUrl = 'http://movie4k.org//' + phUrl 
              if phImage.startswith('/'): phImage = 'http://movie4k.org/' + phImage
              desc = self._cleanHtmlStr(item).strip().replace ('Download','')
              valTab.append(CDisplayListItem(decodeHtml(phTitle),desc,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           valTab.insert(0,CDisplayListItem("--- All movies ---","All movies",     CDisplayListItem.TYPE_CATEGORY,['http://movie4k.org//xxx-all.html'],             'movie4k-all',    '',None))
           valTab.insert(0,CDisplayListItem("--- Latest updates ---","Latest updates",     CDisplayListItem.TYPE_CATEGORY,['http://movie4k.org//xxx-updates.html'],             'movie4k-clips',    '',None))
           return valTab              
        if 'movie4k-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'movie4k.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage4k(url, 'movie4k.cookie', 'movie4k.org', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+str(data) )
           next_page = re.compile('<div id="boxwhite".*?href="(.*?)"').findall(data)
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<TR id="cover', '</TR>')
           if not data2: data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<TD id="tdmovies"', '</TR>')
           for item in data2:
              #printDBG( 'Host item: '+str(item) )
              desc = ''
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item).strip() 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phImage: 
                 phImage = 'http://movie4k.org/' + phImage 
              if '/img/' in phImage:
                 if '-watch' in phUrl: 
                    iconid = self.cm.ph.getSearchGroups(phUrl, '''watch-movie-([0-9]+?)\.''')[0]
                    title = re.sub('-watch.+', '', phUrl)
                    phImage = 'http://movie4k.io/thumbs/cover-'+iconid+'-'+title+'-movie4k-film.jpg'
                 if '-online' in phUrl: 
                    iconid = self.cm.ph.getSearchGroups(phUrl, '''online-film-([0-9]+?)\.''')[0]
                    title = re.sub('-online.+', '', phUrl)
                    phImage = 'http://movie4k.io/thumbs/cover-'+iconid+'-'+title+'-movie4k-film.jpg'
              phUrl = 'http://movie4k.org//' + phUrl 
              if 'flashPlayer2' in item: desc = 'FlashPlayer'
              if 'hoster' in item: desc = 'Hoster'
              if 'divx' in item: desc = 'divx'
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle)+'\n'+desc,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              next_page = next_page[-1] 
              num = next_page.split('-')[-1]
              next_page = 'http://movie4k.org/' + next_page 
              valTab.append(CDisplayListItem('Next', 'Page: '+num, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'movie4k-all' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'movie4k.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage4k(url, 'movie4k.cookie', 'movie4k.org', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+str(data) )
           data2 = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div id="box', '</div>')
           for item in data2:
              #printDBG( 'Host item: '+str(item) )
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]\.([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item).strip() 
              if phUrl: phUrl = 'http://movie4k.org//' + phUrl 
              if phUrl and phTitle:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle), decodeHtml(phTitle), CDisplayListItem.TYPE_CATEGORY, [phUrl], 'movie4k-clips', '', None))
           valTab.insert(0,CDisplayListItem("#","#", CDisplayListItem.TYPE_CATEGORY,['http://movie4k.org//xxx-all.html'],'movie4k-clips','',None))
           return valTab

        if 'tubewolf' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = url #'http://www.tubewolf.com'
           url = url + '/categories/'
           COOKIEFILE = os_path.join(GetCookieDir(), 'tubewolf.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           if url.startswith('http://crocotube.com'): 
              data = self.cm.ph.getDataBeetwenMarkers(data, 'categories</h2>', 'Footer', False)[1]
              data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="thumb">', '</li>')
           else:
              data = self.cm.ph.getDataBeetwenMarkers(data, 'Categories<', 'Categories<', False)[1]
              data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = url + phUrl 
              if phUrl:
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'tubewolf-clips', phImage, url)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/top-rated'],             'tubewolf-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/most-popular'],             'tubewolf-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/latest-updates'],             'tubewolf-clips',    '',self.MAIN_URL))
           self.SEARCH_proc='tubewolf-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'tubewolf-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search/?q=%s' % url.replace(' ','+'), 'tubewolf-clips')
           return valTab              
        if 'tubewolf-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'tubewolf.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0] 
           if url.startswith('https://www.alphaporno.com'): data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a itemprop="url"', '</li>')
           if url.startswith('https://crocotube.com'): data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="thumb">', '</li>')
           if url.startswith('https://www.tubewolf.com'): data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a itemprop="url"', '</div>')
           if url.startswith('https://zedporn.com'): data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="thumb', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              if not phImage: phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title="([^"]+?)"''', 1, True)[0]  
              if not phTitle: phTitle = self.cm.ph.getSearchGroups(item, '''alt="([^"]+?)"''', 1, True)[0]  
              phTime = self.cm.ph.getSearchGroups(item, '''duration">([^>]+?)<''', 1, True)[0]  
              if phUrl.startswith('/'): phUrl = catUrl + phUrl
              if phImage.startswith('/'): phImage = 'http:' + phImage
              if not 'Sponsored' in item:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'PORNTUBE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.porntube.com'
           url = url + '/tags'
           COOKIEFILE = os_path.join(GetCookieDir(), 'PORNTUBE.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getSearchGroups(data, '''window.INITIALSTATE = ['"]([^"^']+?)['"]''', 1, True)[0] 
           data = urllib.unquote(base64.b64decode(data))
           result = byteify(simplejson.loads(data))
           for item in result["page"]["embedded"]["topTags"]:
              phUrl = self.MAIN_URL + "/tags/" + str(item["slug"])
              phTitle = str(item["name"]).title()
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNTUBE-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=rating&time=month'],             'PORNTUBE-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=views&time=month'],             'PORNTUBE-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=date'],             'PORNTUBE-clips',    '',self.MAIN_URL))
           self.SEARCH_proc='PORNTUBE-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'PORNTUBE-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search/?q=%s' % url.replace(' ','+'), 'PORNTUBE-clips')
           return valTab              
        if 'PORNTUBE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'PORNTUBE.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getSearchGroups(data, '''window.INITIALSTATE = ['"]([^"^']+?)['"]''', 1, True)[0] 
           data = urllib.unquote(base64.b64decode(data))
           printDBG( 'Host listsItems data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              if result["page"]["embedded"].has_key('videos'):
                 node = result["page"]["embedded"]
              else:
                 node = result["page"]
              for item in node["videos"]["_embedded"]["items"]:
                 phUrl = self.MAIN_URL + "/api/videos/" + str(item["uuid"]) + "?ssr=false&slug=" + str(item["slug"]) + "&orientation="
                 phTitle = str(item["title"])
                 m, s = divmod(item['durationInSeconds'], 60)
                 phTime = "%02d:%02d" % (m, s)
                 phImage = str(item["thumbnailsList"][0])
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           except Exception:
              printExc()
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'ASHEMALETUBE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.ashemaletube.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'ASHEMALETUBE.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="thumb">', '</div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://www.ashemaletube.com' + phUrl 
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'ASHEMALETUBE-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='ASHEMALETUBE-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'ASHEMALETUBE-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.ashemaletube.com/search/%s/' % url.replace(' ','+'), 'ASHEMALETUBE-clips')
           return valTab              
        if 'ASHEMALETUBE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'ASHEMALETUBE.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="thumb-item videospot', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''([\d]?\d\d:\d\d)''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://www.ashemaletube.com' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'https://www.ashemaletube.com' + next_page 
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'MULEMAX' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://mulemax.com'
           COOKIEFILE = os_path.join(GetCookieDir(), 'MULEMAX.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="col-sm-6', '</div> </a> </div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://mulemax.com' + phUrl 
              if phImage.startswith('/'): phImage = 'https://mulemax.com' + phImage 
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'MULEMAX-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='MULEMAX-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'MULEMAX-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://mulemax.com/search/videos?search_query=%s' % url.replace(' ','+'), 'MULEMAX-clips')
           return valTab              
        if 'MULEMAX-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'MULEMAX.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''</a></li><li><a href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="col-sm-6', '</div> </div>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://mulemax.com' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'https://mulemax.com' + next_page 
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'streamporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://streamporn.pw'
           COOKIEFILE = os_path.join(GetCookieDir(), 'streamporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li id="menu-item', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phTitle = self._cleanHtmlStr(item).strip() 
              if phTitle=='Studios': phTitle='.:'+phTitle+':.'
              if phTitle=='Years': phTitle='.:'+phTitle+':.'
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://streamporn.pw' + phUrl 
              if phImage.startswith('/'): phImage = 'https://streamporn.pw' + phImage 
              if phTitle<>'Hollywood Movies' and phTitle<>'Tvshows':
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'streamporn-clips', phImage, None)) 
           #valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='streamporn-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'streamporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://streamporn.pw/?s=%s' % url.replace(' ','+'), 'streamporn-clips')
           return valTab              
        if 'streamporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'streamporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           if next_page =='': next_page = self.cm.ph.getSearchGroups(data, '''class='active'>.*?class='page larger' href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div data-movie-id', '<div class="jtip-bottom">')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://streamporn.pw' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'streamporn-serwer', phImage, phImage)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'https://streamporn.pw' + next_page 
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'streamporn-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'streamporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           catUrl = self.currList[Index].possibleTypesOfSearch
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="hosts', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://streamporn.pw' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, catUrl, None)) 
           return valTab

        if 'onlinepornfree' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://onlinepornfree.xyz'
           COOKIEFILE = os_path.join(GetCookieDir(), 'onlinepornfree.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li id="menu-item', '</a>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phTitle = self._cleanHtmlStr(item).strip() 
              #if phTitle=='Studios': phTitle='.:'+phTitle+':.'
              #if phTitle=='Years': phTitle='.:'+phTitle+':.'
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://onlinepornfree.xyz' + phUrl 
              if phImage.startswith('/'): phImage = 'https://onlinepornfree.xyz' + phImage 
              if phTitle<>'Studios' and phTitle<>'Sitemap'  and phTitle<>'Contact'  and phTitle<>'Movies TV Series':
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'onlinepornfree-clips', phImage, None)) 
           #valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc='onlinepornfree-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'onlinepornfree-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://onlinepornfree.xyz/?s=%s' % url.replace(' ','+'), 'onlinepornfree-clips')
           return valTab              
        if 'onlinepornfree-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'onlinepornfree.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''<link rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           if next_page =='': next_page = self.cm.ph.getSearchGroups(data, '''class='active'>.*?class='page larger' href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''<img src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://onlinepornfree.xyz' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'onlinepornfree-serwer', phImage, phImage)) 
           if next_page:
              if next_page.startswith('/'): next_page = 'https://onlinepornfree.xyz' + next_page 
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab
        if 'onlinepornfree-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'onlinepornfree.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )
           catUrl = self.currList[Index].possibleTypesOfSearch
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="hosts', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''"duration">([^>]+?)<''', 1, True)[0].strip()
              if phTime=='': phTime = self.cm.ph.getSearchGroups(item, '''>HD </span>([^>]+?)<''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://onlinepornfree.xyz' + phUrl 
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, catUrl, None)) 
           return valTab

        if 'fux' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.fux.com'
           url = url + '/tags'
           COOKIEFILE = os_path.join(GetCookieDir(), 'fux.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getSearchGroups(data, '''window.INITIALSTATE = ['"]([^"^']+?)['"]''', 1, True)[0] 
           data = urllib.unquote(base64.b64decode(data))
           result = byteify(simplejson.loads(data))
           for item in result["page"]["embedded"]["topTags"]:
              phUrl = self.MAIN_URL + "/tags/" + str(item["slug"])
              phTitle = str(item["name"]).title()
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'fux-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=rating&time=month'],             'fux-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=views&time=month'],             'fux-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=date'],             'fux-clips',    '',self.MAIN_URL))
           self.SEARCH_proc='fux-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'fux-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search/?q=%s' % url.replace(' ','+'), 'fux-clips')
           return valTab              
        if 'fux-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'fux.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getSearchGroups(data, '''window.INITIALSTATE = ['"]([^"^']+?)['"]''', 1, True)[0] 
           data = urllib.unquote(base64.b64decode(data))
           printDBG( 'Host listsItems data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              if result["page"]["embedded"].has_key('videos'):
                 node = result["page"]["embedded"]
              else:
                 node = result["page"]
              for item in node["videos"]["_embedded"]["items"]:
                 phUrl = self.MAIN_URL + "/api/videos/" + str(item["uuid"]) + "?ssr=false&slug=" + str(item["slug"]) + "&orientation="
                 phTitle = str(item["title"])
                 m, s = divmod(item['durationInSeconds'], 60)
                 phTime = "%02d:%02d" % (m, s)
                 phImage = str(item["thumbnailsList"][0])
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           except Exception:
              printExc()
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab

        if 'MIAMI' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://miamitvhd.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'miami.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'miami.cookie', 'miamitvhd.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li><a class="dropdown-item"', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item).strip() 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://miamitvhd.com' + phUrl 
              if phTitle=='Promos': break
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'MIAMI-clips', '', None)) 
           valTab.insert(0,CDisplayListItem("--- MIAMI TV Espania ---","MIAMI TV Espania",     CDisplayListItem.TYPE_VIDEO,[CUrlItem('', self.MAIN_URL+'/?channel=miamitv4', 1)],0,    'https://miamitvhd.com/assets/miamitvespana-eec799e28bb876387f572458461375127e49c28c27e71e7363293db36b803039.png',None))
           valTab.insert(0,CDisplayListItem("--- MIAMI TV Colombia ---","MIAMI TV Colombia",     CDisplayListItem.TYPE_VIDEO,[CUrlItem('', self.MAIN_URL+'/?channel=miamitv3', 1)],0,    'https://miamitvhd.com/assets/miamitvcolombia-16791a2f575f8932b66528b7340353f82d242346d117345eb82a3876612b4789.png',None))
           valTab.insert(0,CDisplayListItem("--- MIAMI TV Latino ---","MIAMI TV Latino",     CDisplayListItem.TYPE_VIDEO,[CUrlItem('', self.MAIN_URL+'/?channel=miamitv2', 1)],0,    'https://miamitvhd.com/assets/miamitvlatino-a0a662e0cef788009ad389105e7263d585707570b055e46e3b9b7eb5329775aa.png',None))
           valTab.insert(0,CDisplayListItem("--- MIAMI TV ---","MIAMI TV",     CDisplayListItem.TYPE_VIDEO,[CUrlItem('', self.MAIN_URL+'/?channel=miamitv', 1)], 0,    'https://miamitvhd.com/assets/miamitv-8fcf2efe186508c88b6ebd5441452254a32c410d1d18ea7f82ffbb0d26b35271.png',None))
           return valTab
        if 'MIAMI-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://miamitvhd.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'miami.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'miami.cookie', 'miamitvhd.com', self.defaultParams)
           if not sts: return valTab
           printDBG( 'Host listsItems data: '+str(data) )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="card-video', '</li>')
           for item in data:
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTitle = self._cleanHtmlStr(item)
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('//'): phUrl = 'http:' + phUrl + '/' 
              if phUrl.startswith('/'): phUrl = 'https://miamitvhd.com' + phUrl 
              valTab.append(CDisplayListItem(phTitle.split('\n')[0],phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           return valTab

        if 'pornerbros' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.pornerbros.com'
           url = url + '/tags'
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornerbros.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except Exception as e:
              printExc()
              msg = _("Last error:\n%s" % str(e))
              GetIPTVNotify().push('%s' % msg, 'error', 20)
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getSearchGroups(data, '''window.INITIALSTATE = ['"]([^"^']+?)['"]''', 1, True)[0] 
           data = urllib.unquote(base64.b64decode(data))
           result = byteify(simplejson.loads(data))
           for item in result["page"]["embedded"]["topTags"]:
              phUrl = self.MAIN_URL + "/tags/" + str(item["slug"])
              phTitle = str(item["name"]).title()
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'pornerbros-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=rating&time=month'],             'pornerbros-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=views&time=month'],             'pornerbros-clips',    '',self.MAIN_URL))
           valTab.insert(0,CDisplayListItem("--- Newest ---","Newest",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos?sort=date'],             'pornerbros-clips',    '',self.MAIN_URL))
           self.SEARCH_proc='pornerbros-search'
           valTab.insert(0,CDisplayListItem(_('Search history'), _('Search history'), CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem(_('Search'),  _('Search'),                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           return valTab
        if 'pornerbros-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, self.MAIN_URL+'/search/?q=%s' % url.replace(' ','+'), 'pornerbros-clips')
           return valTab              
        if 'pornerbros-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornerbros.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           catUrl = self.currList[Index].possibleTypesOfSearch
           next_page = self.cm.ph.getSearchGroups(data, '''rel="next" href=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&')
           data = self.cm.ph.getSearchGroups(data, '''window.INITIALSTATE = ['"]([^"^']+?)['"]''', 1, True)[0] 
           data = urllib.unquote(base64.b64decode(data))
           printDBG( 'Host listsItems data: '+data )
           try:
              result = byteify(simplejson.loads(data))
              if result["page"]["embedded"].has_key('videos'):
                 node = result["page"]["embedded"]
              else:
                 node = result["page"]
              for item in node["videos"]["_embedded"]["items"]:
                 phUrl = self.MAIN_URL + "/api/videos/" + str(item["uuid"]) + "?ssr=false&slug=" + str(item["slug"]) + "&orientation="
                 phTitle = str(item["title"])
                 m, s = divmod(item['durationInSeconds'], 60)
                 phTime = "%02d:%02d" % (m, s)
                 phImage = str(item["thumbnailsList"][0])
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phTime+']  '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           except Exception:
              printExc()
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))                
           return valTab


        return valTab

    def getLinksForVideo(self, url):
        printDBG("Urllist.getLinksForVideo url[%s]" % url)
        videoUrls = []
        uri, params   = DMHelper.getDownloaderParamFromUrl(url)
        printDBG(params)
        uri = urlparser.decorateUrl(uri, params)
       
        urlSupport = self.up.checkHostSupport( uri )
        if 1 == urlSupport:
            retTab = self.up.getVideoLinkExt( uri )
            videoUrls.extend(retTab)
            printDBG("Video url[%s]" % videoUrls)
            return videoUrls

    def getParser(self, url):
        printDBG( 'Host getParser begin' )
        printDBG( 'Host getParser mainurl: '+self.MAIN_URL )
        printDBG( 'Host getParser url    : '+url )
        if url.startswith('http://www.4tube.com'):                    return 'http://www.4tube.com'
        if url.startswith('https://www.4tube.com'):                   return 'http://www.4tube.com'
        if url.startswith('https://www.fux.com'):                     return 'http://www.4tube.com'
        if url.startswith('http://www.pornerbros.com'):               return 'http://www.4tube.com'
        if url.startswith('https://www.pornerbros.com'):              return 'http://www.4tube.com'
        if url.startswith('https://www.porntube.com'):                return 'http://www.4tube.com'
        if url.startswith('https://www.ah-me.com'):                   return 'http://www.ah-me.com'
        if url.startswith('http://befuck.com'):                       return 'http://befuck.com'
        if url.startswith('http://www.befuck.com'):                   return 'http://befuck.com'
        if url.startswith('http://www.cliphunter.com'):               return 'http://www.cliphunter.com'
        if url.startswith('http://www.dachix.com'):                   return 'http://www.dachix.com'
        if url.startswith('http://www.drtuber.com'):                  return 'http://www.drtuber.com'
        if url.startswith('http://www.empflix.com'):                  return "video_url: '"
        if url.startswith('http://www.eporner.com'):                  return 'http://www.eporner.com'
        if url.startswith('https://faapy.com'):                       return 'http://faapy.com'
        if url.startswith('https://www.hclips.com'):                  return 'http://www.hclips.com'
        if url.startswith('http://www.hdporn.net'):                   return 'http://www.hdporn.net'
        if url.startswith('http://www.hdzog.com'):                    return 'http://www.hdzog.com'
        if url.startswith('http://hentaigasm.com'):                   return 'http://hentaigasm.com'
        if url.startswith('http://www.homemoviestube.com'):           return 'http://www.homemoviestube.com'
        if url.startswith('http://hotmovs.com'):                      return 'http://www.hclips.com'
        if url.startswith('http://www.hotshame.com'):                 return 'http://www.updatetube.com'
        if url.startswith('http://hotshame.com'):                     return 'http://www.updatetube.com'
        if url.startswith('https://hotshame.com'):                    return 'http://www.updatetube.com'
        if url.startswith('https://www.katestube.com'):               return 'https://www.katestube.com'
        if url.startswith('http://www.katestube.com'):                return 'https://www.katestube.com'
        if url.startswith('https://www.koloporno.com'):               return 'https://www.koloporno.com'
        if url.startswith('https://www.pinflix.com'):                 return 'https://www.pinflix.com'
        if url.startswith('http://www.pinkrod.com'):                  return 'http://www.updatetube.com'
        if url.startswith('http://pinkrod.com'):                      return 'http://www.updatetube.com'
        if url.startswith('https://pinkrod.com'):                     return 'http://www.updatetube.com'
        if url.startswith('https://videos.porndig.com'):              return 'https://porndig.com'
        if url.startswith('http://porndoe.com'):                      return 'http://porndoe.com'
        if url.startswith('https://porndoe.com'):                     return 'http://porndoe.com'
        if url.startswith('https://www.porndoe.com'):                 return 'http://porndoe.com'
        if url.startswith('http://www.pornhd.com'):                   return 'http://www.pornhd.com'
        if url.startswith('http://www.pornhub.com/embed/'):           return 'http://www.pornhub.com/embed/'
        if url.startswith('http://pl.pornhub.com/embed/'):            return 'http://www.pornhub.com/embed/'
        if url.startswith('http://pl.pornhub.com'):                   return 'http://www.pornhub.com'
        if url.startswith('http://www.pornhub.com'):                  return 'http://www.pornhub.com'
        if url.startswith('http://m.pornhub.com'):                    return 'http://m.pornhub.com'
        if url.startswith('http://pornicom.com'):                     return 'http://pornicom.com'
        if url.startswith('https://pornicom.com'):                    return 'http://pornicom.com'
        if url.startswith('http://www.pornicom.com'):                 return 'http://pornicom.com'
        if url.startswith('https://pornohub.su'):                     return 'http://pornohub.su'
        if url.startswith('https://www.pornoxo.com'):                 return 'https://www.pornoxo.com'
        if url.startswith('http://www.pornrabbit.com'):               return 'http://www.pornrabbit.com'
        if url.startswith('https://www.realgfporn.com'):              return 'https://www.realgfporn.com'
        if url.startswith('http://embed.redtube.com'):                return 'http://embed.redtube.com'
        if url.startswith('http://www.redtube.com'):                  return 'http://www.redtube.com'
        if url.startswith('http://thenewporn.com'):                   return 'http://www.updatetube.com'
        if url.startswith('https://thenewporn.com'):                  return 'http://www.updatetube.com'
        if url.startswith('http://www.thenewporn.com'):               return 'http://www.updatetube.com'
        if url.startswith('http://www.thumbzilla.com'):               return 'http://www.thumbzilla.com'
        if url.startswith('http://www.tnaflix.com'):                  return 'https://www.tnaflix.com'
        if url.startswith('https://alpha.tnaflix.com'):               return 'https://alpha.tnaflix.com'
        if url.startswith('http://www.tube8.com/embed/'):             return 'http://www.tube8.com/embed/'
        if url.startswith('http://www.tube8.com'):                    return 'http://www.tube8.com'
        if url.startswith('http://m.tube8.com'):                      return 'http://m.tube8.com'
        if url.startswith('https://www.tube8.com'):                   return 'http://www.tube8.com'
        if url.startswith('http://www.updatetube.com'):               return 'http://www.updatetube.com'
        if url.startswith('https://www.vporn.com'):                   return 'https://www.vporn.com'
        if url.startswith('http://xhamster.com'):                     return 'http://xhamster.com'
        if url.startswith('https://xhamster.com'):                    return 'http://xhamster.com'
        if url.startswith('http://www.xnxx.com'):                     return 'http://www.xnxx.com'
        if url.startswith('http://www.xvideos.com'):                  return 'http://www.xvideos.com'
        if url.startswith('http://www.youjizz.com'):                  return 'http://www.youjizz.com'
        if url.startswith('http://www.youporn.com/embed/'):           return 'http://www.youporn.com/embed/'
        if url.startswith('http://www.youporn.com'):                  return 'http://www.youporn.com'
        if url.startswith('https://www.youporn.com'):                 return 'http://www.youporn.com'
        if url.startswith('https://yourporn.sexy'):                   return 'https://yourporn.sexy'
        if url.startswith('https://mini.zbiornik.com'):               return 'https://mini.zbiornik.com'
        if url.startswith('http://sexkino.to'):                       return 'http://sexkino.to'
        if url.startswith('http://www.plashporn.com'):                return 'http://sexkino.to'
        if url.startswith('http://www.alphaporno.com'):               return 'http://www.tubewolf.com'
        if url.startswith('http://crocotube.com'):                    return 'http://www.tubewolf.com'
        if url.startswith('http://www.tubewolf.com'):                 return 'http://www.tubewolf.com'
        if url.startswith('http://zedporn.com'):                      return 'http://www.tubewolf.com'
        if url.startswith('https://www.alphaporno.com'):               return 'http://www.tubewolf.com'
        if url.startswith('https://crocotube.com'):                    return 'http://www.tubewolf.com'
        if url.startswith('https://www.tubewolf.com'):                 return 'http://www.tubewolf.com'
        if url.startswith('https://zedporn.com'):                      return 'http://www.tubewolf.com'
        if url.startswith('https://www.ashemaletube.com'):            return 'https://www.ashemaletube.com'

# URLPARSER
        if url.startswith('https://openload.co'):                     return 'xxxlist.txt'
        if url.startswith('http://openload.co'):                      return 'xxxlist.txt'
        if url.startswith('https://oload.tv'):                        return 'xxxlist.txt'
        if url.startswith('http://www.cda.pl'):                       return 'xxxlist.txt'
        if url.startswith('http://hqq.tv'):                           return 'xxxlist.txt'
        if url.startswith('https://hqq.tv'):                          return 'xxxlist.txt'
        if url.startswith('https://www.rapidvideo.com'):              return 'xxxlist.txt'
        if url.startswith('http://videomega.tv'):                     return 'xxxlist.txt'
        if url.startswith('http://www.flashx.tv'):                    return 'xxxlist.txt'
        if url.startswith('http://streamcloud.eu'):                   return 'xxxlist.txt'
        if url.startswith('http://thevideo.me'):                      return 'xxxlist.txt'
        if url.startswith('http://dato.porn'):                        return 'http://dato.porn'
        if url.startswith('https://dato.porn'):                       return 'http://dato.porn'
        if url.startswith('http://datoporn.co'):                      return 'http://dato.porn'
        if url.startswith('https://datoporn.co'):                     return 'http://dato.porn'
        if url.startswith('http://datoporn.com'):                     return 'http://dato.porn'
        if url.startswith('https://datoporn.com'):                    return 'http://dato.porn'
        if url.startswith('https://vidlox.tv'):                       return 'https://vidlox.tv'
        if self.MAIN_URL == 'http://pornfree.tv':                     return 'xxxlist.txt'
        if self.MAIN_URL == 'http://www.freeomovie.com/':             return 'xxxlist.txt'
        if self.MAIN_URL == 'https://movie4k.org':                    return 'https://movie4k.org'
        if self.MAIN_URL == 'https://streamporn.pw':                  return 'xxxlist.txt' 
        if self.MAIN_URL == 'https://onlinepornfree.xyz':             return 'xxxlist.txt' 

# A TO DO ...
        if url.startswith('http://www.slutsxmovies.com/embed/'): return 'http://www.nuvid.com'
        if url.startswith('http://www.cumyvideos.com/embed/'):   return 'http://www.nuvid.com'
        #if url.startswith('http://www.x3xtube.com'):         return 'file: '
        if url.startswith('http://www.nuvid.com'):           return 'http://www.nuvid.com'
        if url.startswith('http://www.wankoz.com'):          return 'file: '
        if url.startswith('http://hornygorilla.com'):        return 'file: '
        #if url.startswith('http://www.vikiporn.com'):        return '1file: "'
        if url.startswith('http://www.fetishshrine.com'):    return 'file: '
        if url.startswith('http://www.sunporno.com'):        return 'http://www.sunporno.com'
        if url.startswith('http://theclassicporn.com'):      return "video_url: '"
        if url.startswith('http://www.faphub.xxx'):          return 'http://www.faphub.xxx'
        if url.startswith('http://www.sleazyneasy.com'):     return 'file: '
        if url.startswith('http://www.proporn.com'):         return 'http://www.proporn.com'
        if url.startswith('http://www.tryboobs.com'):        return "video_url: '"
        if url.startswith('http://www.viptube.com'):         return 'http://www.nuvid.com'
        if url.startswith('http://pervclips.com'):           return 'http://www.wankoz.com'
        if url.startswith('http://www.jizz.us'):             return 'http://www.x3xtube.com'
        if url.startswith('http://www.pornstep.com'):        return 'videoFile="'
        if url.startswith('http://www.azzzian.com'):         return "video_url: '"
        if url.startswith('http://www.porndreamer.com'):     return 'http://www.x3xtube.com'
        if url.startswith('http://www.tubeon.com'):          return 'http://www.tubeon.com'
        if url.startswith('http://www.finevids.xxx'):        return "video_url: '"
        if url.startswith('http://www.pornwhite.com'):       return 'file: '
        if url.startswith('http://www.xfig.net'):            return 'videoFile="'
        if url.startswith('http://www.pornoid.com'):         return "video_url: '"
        if url.startswith('http://tubeq.xxx'):               return 'http://www.faphub.xxx'
        if url.startswith('http://www.wetplace.com'):        return "video_url: '"
        if url.startswith('http://sexylies.com'):            return 'http://sexylies.com'
        if url.startswith('http://www.eskimotube.com'):      return 'http://www.eskimotube.com'
        if url.startswith('http://www.pornalized.com'):      return "video_url: '"
        if url.startswith('http://www.porn5.com'):           return 'http://www.porn5.com'
        if url.startswith('http://www.pornyeah.com'):        return 'http://www.pornyeah.com'
        if url.startswith('http://www.porn.com'):            return 'http://www.porn5.com'
        if url.startswith('http://www.yeptube.com'):         return 'http://www.yeptube.com'
        if url.startswith('http://www.upornia.com'):         return "video_url: '"
        if url.startswith('http://www.pornpillow.com'):      return 'http://www.pornpillow.com'
        if url.startswith('http://porneo.com'):              return 'http://www.nuvid.com'
        if url.startswith('http://www.5fing.com'):           return 'file: '
        if url.startswith('http://www.pornroxxx.com'):       return "0p'  : '"
        if url.startswith('http://www.hd21.com'):            return "0p'  : '"
        if url.startswith('http://www.pornrox.com'):         return "0p'  : '"
        if url.startswith('http://www.flyflv.com'):          return 'http://www.flyflv.com'
        if url.startswith('http://www.xtube.com'):           return 'https://vidlox.tv'
        if url.startswith('http://xxxkingtube.com'):         return 'http://xxxkingtube.com'
        if url.startswith('http://www.boyfriendtv.com'):     return 'source src="'
        if url.startswith('http://pornxs.com'):              return 'http://pornxs.com'
        if url.startswith('http://pornsharing.com'):         return 'http://pornsharing.com'
        if url.startswith('http://www.xerotica.com'):        return 'http://pornohub.su'
        if url.startswith('http://www.vivatube.com'):        return 'http://vivatube.com'
        if url.startswith('http://www.clipcake.com'):        return 'videoFile="'
        if url.startswith('http://www.cliplips.com'):        return 'videoFile="'
        if url.startswith('http://www.sheshaft.com'):        return 'file: '
        if url.startswith('http://www.vid2c.com'):           return 'videoFile="'
        if url.startswith('http://www.bonertube.com'):       return 'videoFile="'

# Test mjpg
        if url.endswith('.mjpg'):                            return 'mjpg_stream'
        if url.endswith('.cgi'):                             return 'mjpg_stream'
        if self.MAIN_URL == 'http://hotmovs.com':            return 'http://www.hclips.com'
        if self.MAIN_URL == 'https://www.vporn.com':         return self.MAIN_URL
        if self.MAIN_URL == 'https://yourporn.sexy':         return self.MAIN_URL
        if self.MAIN_URL == 'http://www.moviefap.com':       return self.MAIN_URL
        if self.MAIN_URL == 'http://www.updatetube.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://www.homemoviestube.com': return self.MAIN_URL
        if self.MAIN_URL == 'http://www.hdzog.com':          return 'http://www.hclips.com'
        if self.MAIN_URL == 'https://www.4tube.com':         return 'http://www.4tube.com'
        if self.MAIN_URL == 'https://www.fux.com':           return 'http://www.4tube.com'
        if self.MAIN_URL == 'https://www.pornerbros.com':    return 'http://www.4tube.com'
        if self.MAIN_URL == 'https://www.porntube.com':      return 'http://www.4tube.com'
        if self.MAIN_URL == 'http://faapy.com':              return self.MAIN_URL
        if self.MAIN_URL == 'https://www.realgfporn.com':    return self.MAIN_URL
        if self.MAIN_URL == 'http://befuck.com':             return self.MAIN_URL
        if self.MAIN_URL == 'http://smotri.com':             return self.MAIN_URL
        if self.MAIN_URL == 'http://tubepornclassic.com':    return 'http://www.hclips.com' #self.MAIN_URL
        if self.MAIN_URL == 'https://www.koloporno.com':     return self.MAIN_URL
        if self.MAIN_URL == 'https://www.pornomenge.com':    return self.MAIN_URL
        if self.MAIN_URL == 'http://www.yuvutu.com':         return self.MAIN_URL
        if self.MAIN_URL == 'https://www.camsoda.com/':      return self.MAIN_URL
        if self.MAIN_URL == 'http://adult-channels.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://www.thumbzilla.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://pornohub.su':            return self.MAIN_URL
        if self.MAIN_URL == 'http://www.cliphunter.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://www.filmyporno.tv':      return self.MAIN_URL
        if self.MAIN_URL == 'http://porndoe.com':            return self.MAIN_URL
        if self.MAIN_URL == 'http://www.porntrex.com':       return self.MAIN_URL
        if self.MAIN_URL == 'http://porn720.net':            return self.MAIN_URL
        if self.MAIN_URL == 'http://rusporn.tv':             return self.MAIN_URL
        if self.MAIN_URL == 'http://www.extremetube.com':    return self.MAIN_URL
        if self.MAIN_URL == 'http://search.el-ladies.com':   return self.MAIN_URL
        if self.MAIN_URL == 'http://new.livejasmin.com':     return self.MAIN_URL
        if self.MAIN_URL == 'https://pl.bongacams.com':      return self.MAIN_URL
        if self.MAIN_URL == 'https://www.tnaflix.com':       return self.MAIN_URL
        if self.MAIN_URL == 'https://www.empflix.com':       return self.MAIN_URL
        if self.MAIN_URL == 'http://www.myfreecams.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://www.drtuber.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.dachix.com':         return self.MAIN_URL
        if self.MAIN_URL == 'http://www.youjizz.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.cam4.pl':            return self.MAIN_URL
        if self.MAIN_URL == 'http://www.amateurporn.net':    return self.MAIN_URL
        if self.MAIN_URL == 'https://chaturbate.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.ah-me.com':          return self.MAIN_URL
        if self.MAIN_URL == 'http://www.pornhd.com':         return self.MAIN_URL
        if self.MAIN_URL == 'http://www.pornrabbit.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://beeg.com':               return self.MAIN_URL
        if self.MAIN_URL == 'http://www.tube8.com':          return self.MAIN_URL
        if self.MAIN_URL == 'http://www.redtube.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.youporn.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://showup.tv':              return self.MAIN_URL
        if self.MAIN_URL == 'http://www.xnxx.com':           return self.MAIN_URL
        if self.MAIN_URL == 'http://www.xvideos.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://hentaigasm.com':         return self.MAIN_URL
        if self.MAIN_URL == 'http://xhamsterlive.com':       return 'http://xhamster.com/cams'
        if self.MAIN_URL == 'http://xhamster.com':           return self.MAIN_URL
        if self.MAIN_URL == 'http://www.eporner.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.pornhub.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.4tube.com':          return self.MAIN_URL
        if self.MAIN_URL == 'http://www.hdporn.net':         return self.MAIN_URL
        if self.MAIN_URL == 'http://m.tube8.com':            return self.MAIN_URL
        if self.MAIN_URL == 'http://m.pornhub.com':          return self.MAIN_URL
        if self.MAIN_URL == 'https://www.katestube.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://www.hclips.com':         return 'http://www.hclips.com'
        if self.MAIN_URL == 'https://www.pinflix.com':       return self.MAIN_URL
        if self.MAIN_URL == 'http://oklivetv.com':           return self.MAIN_URL
        if self.MAIN_URL == 'http://www.upornia.com':        return 'http://www.hclips.com' #self.MAIN_URL
        if self.MAIN_URL == 'https://www.txxx.com':          return 'http://www.hclips.com'
        if self.MAIN_URL == 'https://www.sunporno.com':      return 'http://www.sunporno.com'
        if self.MAIN_URL == 'http://sexu.com':               return self.MAIN_URL
        if self.MAIN_URL == 'http://www.tubewolf.com':       return self.MAIN_URL
        if self.MAIN_URL == 'https://streamate.com':         return self.MAIN_URL 
        if self.MAIN_URL == 'https://mulemax.com':           return self.MAIN_URL 
        if self.MAIN_URL == 'https://miamitvhd.com':         return self.MAIN_URL 

        return ''

    def getResolvedURL(self, url):
        printDBG( 'Host getResolvedURL begin' )
        printDBG( 'Host getResolvedURL url: '+url )
        videoUrl = ''
        parser = self.getParser(url)
        printDBG( 'Host getResolvedURL parser: '+parser )
        if parser == '': return url

        if parser == 'mjpg_stream':
           try:
              stream=urllib.urlopen(url)
              bytes=''
              while True:
                 bytes+=stream.read(1024)
                 a = bytes.find('\xff\xd8')
                 b = bytes.find('\xff\xd9')
                 if a!=-1 and b!=-1:
                    jpg = bytes[a:b+2]
                    bytes= bytes[b+2:]
                    with open('/tmp/obraz.jpg', 'w') as titleFile:  
                       titleFile.write(jpg) 
                       return 'file:///tmp/obraz.jpg'
           except: pass
           return ''

        if parser == 'http://www.porntrex.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'porntrex.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'porntrex.cookie', 'porntrex.com', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+str(data) )
           if 'video is a private' in data:
              SetIPTVPlayerLastHostError(_(' This video is a private.'))
              return []
           if self.format4k:
              videoPage = self.cm.ph.getSearchGroups(data, '''video_alt_url5: ['"]([^"^']+?)['"]''')[0] 
              if videoPage:
                 printDBG( 'Host videoPage video_alt_url5 4k: '+videoPage )
                 return videoPage
              videoPage = self.cm.ph.getSearchGroups(data, '''video_alt_url4: ['"]([^"^']+?)['"]''')[0] 
              if videoPage:
                 printDBG( 'Host videoPage video_alt_url4 High HD: '+videoPage )
                 return videoPage
              videoPage = self.cm.ph.getSearchGroups(data, '''video_alt_url3: ['"]([^"^']+?)['"]''')[0] 
              if videoPage:
                 printDBG( 'Host videoPage video_alt_url3 Full High: '+videoPage )
                 return videoPage
           videoPage = self.cm.ph.getSearchGroups(data, '''video_alt_url2: ['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              printDBG( 'Host videoPage video_alt_url2 HD: '+videoPage )
              return videoPage
           videoPage = self.cm.ph.getSearchGroups(data, '''video_alt_url: ['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              printDBG( 'Host videoPage video_alt_url Medium: '+videoPage )
              return videoPage
           videoPage = self.cm.ph.getSearchGroups(data, '''video_url: ['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              printDBG( 'Host videoPage video_url Low: '+videoPage )
              return videoPage
           return ''

        if parser == 'http://www.hclips.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'hclips.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host hclips data: '+data )
           videoPage = self.cm.ph.getSearchGroups(data, '''var video_url\s?=\s?['"]([^"^']+?)['"]''')[0] 
           printDBG( 'Host getResolvedURL videoPage: '+videoPage )
           try:
              hash = self.cm.ph.getSearchGroups(data, '''video_url\s?\+=\s?['"]([^"^']+?)['"]''')[0] 
              if hash:
                 printDBG( 'Host hash1: '+hash.split('||')[1])
                 printDBG( 'Host hash2: '+hash.split('||')[2])
                 printDBG( 'Host hash3: '+hash.split('||')[3])
              if videoPage:
                 decoder = "decrypt=function(_0xf4bdx6) {"\
                    "var _0xf4bdx7 = '',"\
                    "    _0xf4bdx8 = 0;"\
                    "/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g ['exec'](_0xf4bdx6) && console['log']('error decoding url');"\
                    "_0xf4bdx6 = _0xf4bdx6['replace'](/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g, '');"\
                    "do {"\
                    "var _0xf4bdx9 = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                    "_0xf4bdxa = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                    "_0xf4bdxb = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                    "_0xf4bdxc = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                    "_0xf4bdx9 = _0xf4bdx9 << 2 | _0xf4bdxa >> 4,"\
                    "_0xf4bdxa = (_0xf4bdxa & 15) << 4 | _0xf4bdxb >> 2,"\
                    "_0xf4bdxd = (_0xf4bdxb & 3) << 6 | _0xf4bdxc,"\
                    "_0xf4bdx7 = _0xf4bdx7 + String['fromCharCode'](_0xf4bdx9);"\
                    "64 != _0xf4bdxb && (_0xf4bdx7 += String['fromCharCode'](_0xf4bdxa));"\
                    "64 != _0xf4bdxc && (_0xf4bdx7 += String['fromCharCode'](_0xf4bdxd))"\
                    "} while (_0xf4bdx8 < _0xf4bdx6['length']);;"\
                    "return unescape(_0xf4bdx7)"\
                    "};" 
                 js = decoder + "\n" + "vidurl = decrypt('"+videoPage+"');"  
                 printDBG( 'Host getResolvedURL js: '+js )
                 urls = js_execute( js+ '\nfor (n in this){print(n+"="+this[n]+";");}')
                 videoUrl = self.cm.ph.getSearchGroups(urls['data'], '''vidurl=([^"^']+?);''')[0]
                 if hash: videoUrl = videoUrl.replace('/'+videoUrl.split('/')[-7]+'/'+videoUrl.split('/')[-6]+'/'+videoUrl.split('/')[-5]+'/',hash.split('||')[1])
                 if videoUrl: return videoUrl+'&lip='+hash.split('||')[2]+'&lt='+hash.split('||')[3]
           except Exception as e:
              printExc()
              if videoPage.startswith('http'): return videoPage
           return ''

        if parser == 'http://www.hdzog.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'hdzog.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           videoPage = self.cm.ph.getSearchGroups(data, '''var video_url=['"]([^"^']+?)['"]''')[0] 
           printDBG( 'Host getResolvedURL videoPage: '+videoPage )
           hash = self.cm.ph.getSearchGroups(data, '''/get_file/(\d/[^"^']+?)/''')[0] 
           printDBG( 'Host hash: '+hash )
           if videoPage:
              decoder = "decrypt=function(_0xf4bdx6) {"\
                 "var _0xf4bdx7 = '',"\
                 "    _0xf4bdx8 = 0;"\
                 "/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g ['exec'](_0xf4bdx6) && console['log']('error decoding url');"\
                 "_0xf4bdx6 = _0xf4bdx6['replace'](/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g, '');"\
                 "do {"\
                 "var _0xf4bdx9 = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdxa = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdxb = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdxc = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdx9 = _0xf4bdx9 << 2 | _0xf4bdxa >> 4,"\
                 "_0xf4bdxa = (_0xf4bdxa & 15) << 4 | _0xf4bdxb >> 2,"\
                 "_0xf4bdxd = (_0xf4bdxb & 3) << 6 | _0xf4bdxc,"\
                 "_0xf4bdx7 = _0xf4bdx7 + String['fromCharCode'](_0xf4bdx9);"\
                 "64 != _0xf4bdxb && (_0xf4bdx7 += String['fromCharCode'](_0xf4bdxa));"\
                 "64 != _0xf4bdxc && (_0xf4bdx7 += String['fromCharCode'](_0xf4bdxd))"\
                 "} while (_0xf4bdx8 < _0xf4bdx6['length']);;"\
                 "return unescape(_0xf4bdx7)"\
                 "};" 
              js = decoder + "\n" + "vidurl = decrypt('"+videoPage+"');"  
              printDBG( 'Host getResolvedURL js: '+js )
              urls = js_execute( js+ '\nfor (n in this){print(n+"="+this[n]+";");}')
              videoUrl = self.cm.ph.getSearchGroups(urls['data'], '''vidurl=([^"^']+?);''')[0] 
              printDBG( 'Host split: '+videoUrl.split('/')[4]+'/'+videoUrl.split('/')[5])
              if hash: videoUrl = videoUrl.replace(videoUrl.split('/')[4]+'/'+videoUrl.split('/')[5],hash)
              if videoUrl: return videoUrl
              if videoPage.startswith('http'): return videoPage
           return ''


        if parser == 'http://www.upornia.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'upornia.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           #printDBG( 'Host getResolvedURL data: '+data )
           try:
              video_url = self.cm.ph.getSearchGroups(data, '''var video_url=['"]([^"^']+?)['"]''')[0]
              hash = self.cm.ph.getSearchGroups(data, '''/get_file/(\d+/[^"^']+?)/''')[0] 
              #printDBG( 'Host video_url: '+video_url )
              decoder = 'Dpww3Dw64=function(b){var c="",d=0;/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g.exec(b)'\
              '&&console.log("error decoding url");b=b.replace(/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g,"");'\
              'do{var f="\u0410\u0412\u0421D\u0415FGHIJKL\u041cNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".'\
              'indexOf(b.charAt(d++)),e="\u0410\u0412\u0421D\u0415FGHIJKL\u041cNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".'\
              'indexOf(b.charAt(d++)),g="\u0410\u0412\u0421D\u0415FGHIJKL\u041cNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".'\
              'indexOf(b.charAt(d++)),h="\u0410\u0412\u0421D\u0415FGHIJKL\u041cNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".'\
              'indexOf(b.charAt(d++)),f=f<<2|e>>4,e=(e&15)<<4|g>>2,k=(g&3)<<6|h,c=c+String.fromCharCode(f);'\
              '64!=g&&(c+=String.fromCharCode(e));64!=h&&(c+=String.fromCharCode(k))}while(d<b.length);return unescape(c)};'
              js = decoder + '\n' + 'var video_url="'+video_url+'";\n'+'vidurl = (Dpww3Dw64(video_url));'  
              #printDBG( 'Host getResolvedURL js: '+js )
              urls = js_execute( js+ '\nfor (n in this){print(n+"="+this[n]+";");}')
              videoUrl = self.cm.ph.getSearchGroups(urls['data'], '''vidurl=([^"^']+?);''')[0]
              if hash: videoUrl = videoUrl.replace(videoUrl.split('/')[-6]+'/'+videoUrl.split('/')[-5],hash)
              if videoUrl: return videoUrl
           except Exception:
              printExc()
           printDBG( 'Host start embed' )
           videoPage = self.cm.ph.getSearchGroups(data, '''(https://upornia.com/embed/[^"^']+?)[&"]''')[0] 
           if not videoPage: videoPage = self.cm.ph.getSearchGroups(data, '''(https://www.txxx.com/embed/[^"^']+?)[&"]''')[0] 
           if videoPage:
              try: data2 = self.cm.getURLRequestData({ 'url': videoPage, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
              except:
                 printDBG( 'Host getResolvedURL query error url: '+videoPage )
                 return ''
              #printDBG( 'Host getResolvedURL data embed: '+data )
              videoUrl = self.cm.ph.getSearchGroups(data2, '''video_url=['"]([^"^']+?)['"]''')[0]
              if 'http' in videoUrl: return videoUrl
           printDBG( 'Host direct link' )
           videoPage = self.cm.ph.getSearchGroups(data, '''(https://upornia.com/get_file/[^"^']+?)['"]''')[0] 
           if videoPage: return videoPage
           videoPage = self.cm.ph.getSearchGroups(data, '''(https://www.txxx.com/get_file/[^"^']+?)['"]''')[0] 
           if videoPage: return videoPage
           return ''

        if parser == 'http://beeg.com':
           host = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              return ''
           printDBG( 'second beeg-clips data: '+data )
           bestUrl = re.findall('0p":"(.*?)"', data, re.S)
           if bestUrl:
              if self.format4k:
                 phUrl = 'http:%s' % bestUrl[-1]
              else:
                 phUrl = 'http:%s' % bestUrl[-1]
                 if '/1080p/' in phUrl: phUrl = 'http:%s' % bestUrl[-2]
              phUrl = phUrl.replace('{DATA_MARKERS}','data=pc.DE')
              key = re.search(r'/key=(.*?)%2Cend=', phUrl, 0) 
              key = key.group(1)
              printDBG( 'key encrypt : '+key )
              key = decrypt_key(key, self.beeg_salt)
              printDBG( 'key decrypt: '+key )
              videoUrl = re.sub(r'/key=(.*?)%2Cend=', '/key='+key+',end=', phUrl)
              return videoUrl
           else: return ''
  
        if parser == 'http://showup.tv':
           COOKIEFILE = os_path.join(GetCookieDir(), 'showup.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           parse = re.search("var srvE = '(.*?)'", data, re.S)
           if parse:
              printDBG( 'Host Url: '+url)
              printDBG( 'Host rtmp: '+ parse.group(1))
              rtmp = parse.group(1)
           startChildBug = re.search("startChildBug\(user\.uid, '', '([\s\S]+?)'", data, re.I);
           if startChildBug:
              s = startChildBug.group(1)
              printDBG( 'Host startChildBug: '+ s)
              ip = ''
              t = re.search(r"(.*?):(.*?)", s, re.I)
              if t.group(1) == 'j12.showup.tv': ip = '94.23.171.122'
              if t.group(1) == 'j13.showup.tv': ip = '94.23.171.121'
              if t.group(1) == 'j11.showup.tv': ip = '94.23.171.115'
              if t.group(1) == 'j14.showup.tv': ip = '94.23.171.120'
              printDBG( 'Host IP: '+ip)
              port = s.replace(t.group(1)+':', '')
              printDBG( 'Host Port: '+port)
              modelName = url.replace('http://showup.tv/','')
              printDBG( 'Host modelName: '+modelName)

              libsPath = GetPluginDir('libs/')
              import sys
              sys.path.insert(1, libsPath)
              import websocket 
              wsURL1 = 'ws://'+s
              wsURL2 = 'ws://'+ip+':'+port
              printDBG( 'Host wsURL1: '+wsURL1)
              printDBG( 'Host wsURL2: '+wsURL2)
              ws = websocket.create_connection(wsURL2)

              zapytanie = '{ "id": 0, "value": ["", ""]}'
              zapytanie = zapytanie.decode("utf-8")
              printDBG( 'Host zapytanie1: '+zapytanie)
              ws.send(zapytanie) 
              result = ws.recv()
              printDBG( 'Host result1: '+result)

              zapytanie = '{ "id": 2, "value": ["%s"]}' % modelName
              zapytanie = zapytanie.decode("utf-8")
              printDBG( 'Host zapytanie2: '+zapytanie)
              ws.send(zapytanie) 
              result = ws.recv()
              printDBG( 'Host result2: '+result)

              playpath = re.search('value":\["(.*?)"', result)

              if playpath:
                 Checksum =  playpath.group(1)  
                 if len(Checksum)<30: 
                    for x in range(1, 10): 
                       ws.send(zapytanie)
                       result = ws.recv()
                       czas = re.search('(\d+)\[:\](\d+)\[', result )
                       if czas:
                          printDBG( 'Host czas.group(1): '+czas.group(1) )
                          printDBG( 'Host czas.group(2): '+czas.group(2) )
                          czas = int(czas.group(1)) - int(czas.group(2))
                          printDBG( 'Host a: '+str(czas) )
                          a = str(czas)
                          if a=='0': a = 'kilka'
                          Checksum = 'PRIVATE - Czekaj '+a+' sekund'
                          break
                    if Checksum=='' or Checksum=='failure': Checksum='OFFLINE'
                    ws.close() 
                    SetIPTVPlayerLastHostError(Checksum)
                    return []
                 videoUrl = 'rtmp://cdn-t0.showup.tv:1935/webrtc/'+Checksum+'_aac' # token=fake'
                 ws.close() 
                 try:
                    import commands
                    for x in range(1, 9): 
                       cmd = '/usr/bin/rtmpdump -B 1 -r "%s"' % videoUrl.replace('cdn-t0','cdn-t0'+str(x))
                       wow = commands.getoutput(cmd)
                       printDBG( 'HostXXX cmd > '+ cmd )
                       #printDBG( 'HostXXX rtmpdump > '+ wow )
                       if not 'StreamNotFound' in wow:
                          return videoUrl.replace('cdn-t0','cdn-t0'+str(x))+' live=1'
                       printDBG( 'HostXXX GUZIK ' )
                 except:
                    printDBG( 'HostXXX error commands.getoutput ' )
                 return videoUrl.replace('cdn-t0','cdn-t01')+' live=1'

           return ''

        if parser == 'http://smotri.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'smotri.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           #printDBG( 'Host listsItems data1: '+data )
           file = self.cm.ph.getSearchGroups(data, '''data-user-file=['"]([^"^']+?)['"]''')[0] 
           sid = self.cm.ph.getSearchGroups(data, ''''data-sid=['"]([^"^']+?)['"]''')[0] 
           swf = self.cm.ph.getSearchGroups(data, '''drawFlash\(['"]([^"^']+?)['"]''')[0] 
           if swf.startswith('//'): swf = 'http:' + swf
           printDBG( 'Host listsItems file: '+file )
           printDBG( 'Host listsItems sid: '+sid )
           printDBG( 'Host listsItems swf: '+swf )
           ticket = 'http://smotri.com/broadcast/view/url/?ticket=%s' % file
           try: data = self.cm.getURLRequestData({ 'url': ticket, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           dane = '['+data+']'
           printDBG( 'Host listsItems json: '+dane )
           result = simplejson.loads(dane)
           if result:
              for item in result:
                 try:
                    _vidURL = str(item["_vidURL"])
                    _server_hls = str(item["_server_hls"])
                 except: 
                    return ''
                 if _server_hls<>'': return 'http://'+_server_hls+'/hls/'+_vidURL+'/index.m3u8'
           return ''

        if parser == 'http://adult-channels.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'adult.cookie')
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           header = {'Referer':'http://adult-channels.com', 'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data1: '+data )
           videoUrl = re.search('<iframe.*?src="(.*?)"', data, re.S)
           if videoUrl:
              link = ''
              if videoUrl.group(1).startswith('/'): link = 'http://adult-channels.com' 
              xml = link+videoUrl.group(1)
              try: data = self.cm.getURLRequestData({ 'url': xml, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
              except:
                 printDBG( 'Host getResolvedURL query error xml: '+xml )
                 return ''
              printDBG( 'Host getResolvedURL data2: '+data )
              videoUrl = self.cm.ph.getSearchGroups(data, '''file:['"]([^"^']+?)['"]''')[0] 
              if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''<source[^>]*?src=['"]([^"^']+?)['"]''')[0] 
              if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''<source[^>]+?src=['"]([^"^']+?)['"]''')[0] 
              if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''file\': ['"]([^"^']+?)['"]''')[0] 
              if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, ''';src=([^"^']+?)['"]''')[0] 
              printDBG( 'Host videoUrl: '+videoUrl )
              if '.mp4' in videoUrl: return videoUrl.replace('\/','/')
              if '.m3u8' in videoUrl:
                 if self.cm.isValidUrl(videoUrl): 
                    tmp = getDirectM3U8Playlist(videoUrl)
                    for item in tmp:
                       printDBG( 'Host listsItems valtab: '  +str(item))
                       return item['url']
              else:
                 videoUrl = self.cm.ph.getSearchGroups(data, '''<iframe[^>]+?src=['"]([^"^']+?)['"]''')[0] 
                 if videoUrl:
                    return self.getResolvedURL(videoUrl)
           return ''

        if parser == 'http://www.myfreecams.com':
           videoUrl = myfreecam_start(url)
           if videoUrl:
              if self.cm.isValidUrl(videoUrl): 
                 tmp = getDirectM3U8Playlist(videoUrl)
                 for item in tmp:
                    printDBG( 'Host listsItems valtab: '  +str(item))
                    if item['with']: return item['url']
           return ''

        def _get_stream_uid(username):
           m = hashlib.md5(username.encode('utf-8') + str(time_time()).encode('utf-8'))
           return m.hexdigest()

        if parser == 'https://pl.bongacams.com':
           printDBG( 'Host url:  '+url )
           username = self.cm.ph.getSearchGroups(url, '''playpath=stream_([^"^']+?)[?]''')[0] 
           printDBG( 'Host username:  '+username )
           COOKIEFILE = os_path.join(GetCookieDir(), 'bongacams.cookie')
           host = 'Mozilla/5.0 (iPad; CPU OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B466 Safari/600.1.4'
           header = {'User-Agent': host, 'Accept':'text/html,application/json','Accept-Language':'en,en-US;q=0.7,en;q=0.3'} 
           query_data = { 'url': 'https://pl.bongacams.com/'+username, 'header': header, 'Referer':'https://pl.bongacams.com/'+username, 'Origin':'https://pl.bongacams.com', 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              return ''
           #printDBG( 'Parser Bonga data: '+data ) 
           amf = self.cm.ph.getSearchGroups(data, '''MobileChatService\(\'\/([^"^']+?)\'\+\$''')[0] 
           if not amf: amf = 'tools/amf.php?x-country=pl&m=1&res='
           url_amf = 'https://pl.bongacams.com/' + amf + str(random.randint(2100000, 3200000))
           printDBG( 'Host url_amf:  '+url_amf )
           postdata = {'method' : 'getRoomData', 'args[]' : username} 
           header = {'User-Agent': host, 'Accept':'text/html,application/xhtml+xml,application/xml,application/json','Accept-Language':'en,en-US;q=0.7,en;q=0.3','X-Requested-With':'XMLHttpRequest'} 
           query_data = { 'url': url_amf, 'header': header, 'Referer':'https://pl.bongacams.com', 'Origin':'https://pl.bongacams.com', 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': True, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data, postdata)
           except:
              printDBG( 'Parser error: '+url_amf ) 
              return ''
           #printDBG( 'Parser Bonga link2: '+data ) 
           serwer = self.cm.ph.getSearchGroups(data, '''"videoServerUrl":['"]([^"^']+?)['"]''', 1, True)[0] 
           printDBG( 'Parser Bonga serwer: '+serwer ) 
           url_m3u8 = 'https:' + serwer.replace('\/','/') + '/hls/stream_' +username + '/chunks.m3u8'
           if self.bongastream == 'm3u8': return urlparser.decorateUrl(url_m3u8, {'User-Agent': host})
           if self.bongastream == 'rtmp': 
              url = url.replace('//dedNUMER_SERWERA-bongacams.com',serwer.replace('\/','/'))
              return url.replace('SKROT_MD5',_get_stream_uid(username)) + 'flashVer=WIN 2024,0,0,186 '
           return ''

        if parser == 'http://new.livejasmin.com':
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           videoPage = re.search('performerid":"(.*?)".*?proxyip":"(.*?)"', data, re.S) 
           if videoPage.group(1) and videoPage.group(2):
              printDBG( 'Host listsItems videoPage.group(2): '+videoPage.group(2) )
              printDBG( 'Host listsItems videoPage.group(1): '+videoPage.group(1) )
              return (videoPage.group(2)+'/'+videoPage.group(1)) 
           kto = re.search('performerid":"(.*?)"', data, re.S) 
           if kto:
              videoUrl = 'http://109.71.162.191/'+kto.group(1)
              videoUrl = urlparser.decorateUrl(videoUrl, {'Referer': url, 'User-Agent':'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.18) Gecko/20110621 Mandriva Linux/1.9.2.18-0.1mdv2010.2 (2010.2) Firefox/3.6.18'}) 
              return videoUrl

        if parser == 'http://www.cam4.pl':
           if '-rtmp-' in url:
              url = url.replace('-rtmp-','')
              stream = 'rtmp'
           if '-m3u8-' in url:
              url = url.replace('-m3u8-','')
              stream = 'm3u8'
           COOKIEFILE = os_path.join(GetCookieDir(), 'cam4.cookie')
           host = "Mozilla/5.0 (iPhone; CPU iPhone OS 8_0_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12A366 Safari/600.1.4"
           header = {'User-Agent': host, 'Accept':'text/html,application/json','Accept-Language':'en,en-US;q=0.7,en;q=0.3'} 
           query_data = { 'url': url, 'header': header, 'Referer':url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           parse = re.search('"playerUrl":"(.*?)"', data, re.S) 
           if parse:
              swfUrl = parse.group(1)
              parse = re.search('"videoPlayUrl":"(.*?)"', data, re.S) 
              if parse:
                 videoPlayUrl = parse.group(1)
                 parse = re.search('"videoAppUrl":"(.*?)"', data, re.S) 
                 if parse:
                    videoAppUrl = parse.group(1)
                    printDBG( 'Host swfUrl: '  +swfUrl )
                    printDBG( 'Host videoPlayUrl: '  +videoPlayUrl )
                    printDBG( 'Host videoAppUrl: '  +videoAppUrl )
                    if len(videoPlayUrl)<20: return ''
                    if len(videoAppUrl)<20: return ''
                    if stream == 'rtmp':
                       Url = '%s playpath=%s?playToken=null swfUrl=%s conn=S:OK live=1 pageUrl=%s' % (videoAppUrl, videoPlayUrl, swfUrl, url)
                       return Url+ ' flashVer=WIN 2024,0,0,186 '
           if stream == 'm3u8':
              Url = self.cm.ph.getSearchGroups(data, '''hlsUrl: ['"]([^"^']+?)['"]''')[0]+'?referer=cam4.com&timestamp='+str(int(time_time()*1000))
              #Url = videoAppUrl.replace('rtmp','https').replace('cam4.com/','cam4.com:443/')+'/'+videoPlayUrl+'_aac/playlist.m3u8?referer=cam4.com&timestamp='+str(int(time_time()*1000))
              Url = urlparser.decorateUrl(Url, {'User-Agent': host})
              if self.cm.isValidUrl(Url): 
                 tmp = getDirectM3U8Playlist(Url)
                 for item in tmp:
                    printDBG( 'Host listsItems valtab: '  +str(item))
                    return urlparser.decorateUrl(item['url'], {'User-Agent': host})
           return ''

        if parser == 'https://www.camsoda.com/':
            if 'rtmp' in url:
                rtmp = 1
            else:
                rtmp = 0
            url = url.replace('rtmp','')
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
            try: data = self.cm.getURLRequestData(query_data)
            except:
                printDBG( 'Host getResolvedURL query error url: '+url )
                return ''
            #printDBG( 'Host getResolvedURL data: '+data )
            dane = '['+data+']'
            #printDBG( 'Host listsItems json: '+dane )
            result = simplejson.loads(dane)
            if result:
                try:
                    for item in result:
                        token = str(item["token"])
                        app = str(item["app"])
                        serwer = str(item["edge_servers"][0])
                        #edge_servers2 = str(item["edge_servers"][1])
                        stream_name = str(item["stream_name"])
                        #printDBG( 'Host listsItems token: '+token )
                        #printDBG( 'Host listsItems app: '+app )
                        #printDBG( 'Host listsItems edge_servers1: '+serwer )
                        #printDBG( 'Host listsItems edge_servers2: '+edge_servers2 )
                        #printDBG( 'Host listsItems stream_name: '+stream_name )
                        name = re.sub('-enc.+', '', stream_name)
                        if rtmp == 0:
                            #Url = 'https://%s/%s/mp4:%s_mjpeg/playlist.m3u8?token=%s' % (serwer, app, stream_name, token )
                            Url = 'https://%s/%s/mp4:%s_aac/playlist.m3u8?token=%s' % (serwer, app, stream_name, token )
                            USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0'
                            Url = urlparser.decorateUrl(Url, {'User-Agent': USER_AGENT})
                            if self.cm.isValidUrl(Url): 
                                tmp = getDirectM3U8Playlist(Url)
                                for item in tmp:
                                    #printDBG( 'Host listsItems valtab: '  +str(item))
                                    if str(item["with"])=='0':
                                        SetIPTVPlayerLastHostError(' OFFLINE')
                                        return []
                                    return item['url']
                            SetIPTVPlayerLastHostError(' OFFLINE')
                            return []
                        else:
                            Url = 'rtmp://%s:1935/%s?token=%s/ playpath=?mp4:%s swfUrl=https://www.camsoda.com/lib/video-js/video-js.swf live=1 pageUrl=https://www.camsoda.com/%s' % (serwer, app, token, stream_name, name)
                            return Url
                except Exception: printExc()
            return ''

        if parser == 'xxxlist.txt':
           videoUrls = self.getLinksForVideo(url)
           if videoUrls:
              for item in videoUrls:
                 Url = item['url']
                 Name = item['name']
                 printDBG( 'Host url:  '+Url )
                 return Url
           return ''

        if parser == 'http://xhamster.com/cams':
           config='http://xhamsterlive.com/api/front/config'
           query_data = { 'url': config, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return ''
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('"sessionHash":"(.*?)"', data, re.S) 
           if not parse: return ''
           sessionHash = parse.group(1) 
           printDBG( 'Host sessionHash: '+sessionHash )

           models='http://xhamsterlive.com/api/front/models'
           query_data = { 'url': models, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error models: '+models )
              return ''
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('"models":(.*?),"ttl":', data, re.S) 
           if not parse: return ''
           result = simplejson.loads(parse.group(1))
           if result:
              for item in result:
                 ID = str(item["id"]) 
                 Name = item["username"]
                 BroadcastServer = item["broadcastServer"]
                 swf_url = 'http://xhamsterlive.com/assets/cams/components/ui/Player/player.swf?bgColor=2829099&isModel=false&version=1.5.892&bufferTime=1&camFPS=30&camKeyframe=15&camQuality=85&camWidth=640&camHeight=480'
                 Url = 'rtmp://b-eu4.stripcdn.com:1935/%s?sessionHash=%s&domain=xhamsterlive.com playpath=%s swfUrl=%s pageUrl=http://xhamsterlive.com/cams/%s live=1 ' % (BroadcastServer, sessionHash, ID, swf_url, Name) 
                 if ID == url: 
                    return Url
           return ''

        if parser == 'http://www.cliphunter.com':
           host = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              return ''
           #printDBG( 'Host listsItems data: '+data )
           url = re.findall('"url":"(.*?)"}', data, re.S)
           if url:
              url = url[-1]
              url = url.replace('\u0026', '.').replace(r"\/",r"/")
              if url.startswith('http'): return url
           url = re.findall('"url":"(.*?)"}', data, re.S)
           if url:
              url = url[-1]
              url = url.replace('\u0026', '.')
              translation_table = {
                 'm': 'a', 'b': 'b', 'c': 'c', 'i': 'd', 'd': 'e', 'g': 'f', 'a': 'h',
                 'z': 'i', 'y': 'l', 'n': 'm', 'l': 'n', 'f': 'o', 'v': 'p', 'x': 'r',
                 'r': 's', 'q': 't', 'p': 'u', 'e': 'v',
                 '$': ':', '&': '.', '(': '=', '^': '&', '=': '/',
              }
              url = ''.join(translation_table.get(c, c) for c in url) 
              return url
           else: return ''

        if parser == 'http://www.redtube.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'redtube.cookie')
           host = 'Mozilla/5.0 (Windows NT 6.1; rv:44.0) Gecko/20100101 Firefox/44.0'
           header = {'User-Agent': host, 'Accept':'application/json', 'Accept-Language':'de,en-US;q=0.7,en;q=0.3', 'X-Requested-With':'XMLHttpRequest', 'Content-Type':'application/x-www-form-urlencoded'} 
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('mediaDefinition: (.*?)],', data, re.S) 
           if not parse: return ''
           result = simplejson.loads(parse.group(1)+']')
           if result:
              for item in result:
                 videoUrl = str(item["videoUrl"]) 
                 quality = item["quality"]
                 printDBG( 'Host quality'+quality )
                 printDBG( 'Host videoUrl'+videoUrl )
                 if videoUrl: return videoUrl
           return ''

        if parser == 'http://www.tube8.com/embed/':
           return self.getResolvedURL(url.replace(r"embed/",r""))
        
        if parser == 'http://www.pornhub.com/embed/':
           return self.getResolvedURL(url.replace(r"embed/",r"view_video.php?viewkey="))

        if parser == 'http://www.tube8.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'tube8.cookie')
           host = 'Mozilla/5.0 (Windows NT 6.1; rv:44.0) Gecko/20100101 Firefox/44.0'
           header = {'User-Agent': host, 'Accept':'application/json', 'Accept-Language':'de,en-US;q=0.7,en;q=0.3', 'X-Requested-With':'XMLHttpRequest', 'Content-Type':'application/json'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              printDBG( 'Host listsItems query error url:'+url )
              return ''
           #printDBG( 'Host getResolvedURL data: '+data )
           videoUrl = self.cm.ph.getSearchGroups(data, '''quality_720p['"]:['"]([^"^']+?)['"]''')[0] 
           if not videoUrl: videoUrl = self.cm.ph.getSearchGroups(data, '''quality_480p['"]:['"]([^"^']+?)['"]''')[0] 
           return videoUrl.replace('\/','/') 

        if parser == 'http://www.4tube.com':
           host = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
           header = {'Origin': 'http://www.4tube.com', 'Referer': url, 'User-Agent': host, 'Accept':'application/json', 'Accept-Language':'de,en-US;q=0.7,en;q=0.3', 'X-Requested-With':'XMLHttpRequest', 'Content-Type':'application/x-www-form-urlencoded'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              return ''
           printDBG( 'Host listsItems data: '+str(data) )

           videoID = re.findall('data-id="(\d+)".*?data-quality="(\d+)"', data, re.S)
           try:
              result = byteify(simplejson.loads(data))
              videoID = result["video"]["mediaId"]
              info = {}
              res = ''
              for item in result["video"]["encodings"]:
                 res += str(item["height"]) + "+"
              res.strip('+')
              posturl = "https://tkn.kodicdn.com/%s/desktop/%s" % (videoID, res)
              printDBG( 'Host getResolvedURL posturl: '+posturl )
              query_data = { 'url': posturl, 'header': header, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
              try:
                 data = self.cm.getURLRequestData(query_data)
              except:
                 return ''
              printDBG( 'Host getResolvedURL posturl data: '+data )
              videoUrl = re.findall('token":"(.*?)"', data, re.S)
              if videoUrl: return videoUrl[-1]     
           except Exception:
              printExc()
           if videoID:
              res = ''
              for x in videoID:
                  res += x[1] + "+"
              res.strip('+')
              posturl = "https://tkn.kodicdn.com/%s/embeds/%s" % (videoID[-1][0], res)
              printDBG( 'Host getResolvedURL posturl: '+posturl )
              query_data = { 'url': posturl, 'header': header, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
              try:
                 data = self.cm.getURLRequestData(query_data)
              except:
                 return ''
              printDBG( 'Host getResolvedURL posturl data: '+data )
              videoUrl = re.findall('token":"(.*?)"', data, re.S)
              if videoUrl: return videoUrl[-1]                 
              else: return ''
           else: return ''

        if parser == 'http://hotmovs.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'hotmovs.cookie')
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           videoPage = self.cm.ph.getSearchGroups(data, '''var video_url=['"]([^"^']+?)['"]''')[0] 
           hash = self.cm.ph.getSearchGroups(data, '''/get_file/(\d+/[^"^']+?)/''')[0] 
           printDBG( 'Host getResolvedURL videoPage: '+videoPage )
           if videoPage:
              decoder = "decrypt=function(_0xf4bdx6) {"\
                 "var _0xf4bdx7 = '',"\
                 "    _0xf4bdx8 = 0;"\
                 "/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g ['exec'](_0xf4bdx6) && console['log']('error decoding url');"\
                 "_0xf4bdx6 = _0xf4bdx6['replace'](/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g, '');"\
                 "do {"\
                 "var _0xf4bdx9 = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdxa = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdxb = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdxc = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdx9 = _0xf4bdx9 << 2 | _0xf4bdxa >> 4,"\
                 "_0xf4bdxa = (_0xf4bdxa & 15) << 4 | _0xf4bdxb >> 2,"\
                 "_0xf4bdxd = (_0xf4bdxb & 3) << 6 | _0xf4bdxc,"\
                 "_0xf4bdx7 = _0xf4bdx7 + String['fromCharCode'](_0xf4bdx9);"\
                 "64 != _0xf4bdxb && (_0xf4bdx7 += String['fromCharCode'](_0xf4bdxa));"\
                 "64 != _0xf4bdxc && (_0xf4bdx7 += String['fromCharCode'](_0xf4bdxd))"\
                 "} while (_0xf4bdx8 < _0xf4bdx6['length']);;"\
                 "return unescape(_0xf4bdx7)"\
                 "};" 
              js = decoder + "\n" + "vidurl = decrypt('"+videoPage+"');"  
              printDBG( 'Host getResolvedURL js: '+js )
              urls = js_execute( js+ '\nfor (n in this){print(n+"="+this[n]+";");}')
              videoUrl = self.cm.ph.getSearchGroups(urls['data'], '''vidurl=([^"^']+?);''')[0] 
              printDBG( 'Host hash: '+hash )
              printDBG( 'Host videoUrl.split4: '+videoUrl.split('/')[-6] )
              printDBG( 'Host videoUrl.split5: '+videoUrl.split('/')[-5] )

              if hash: videoUrl = videoUrl.replace(videoUrl.split('/')[-6]+'/'+videoUrl.split('/')[-5],hash)
              if videoUrl: return videoUrl
              if videoPage.startswith('http'): return videoPage

           videoUrl = self.cm.ph.getSearchGroups(data, '''file\':\s['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urllib2.unquote(videoUrl)

        if parser == 'https://www.txxx.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'txxx.cookie')
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           videoPage = self.cm.ph.getSearchGroups(data, '''var video_url=['"]([^"^']+?)['"]''')[0] 
           hash = self.cm.ph.getSearchGroups(data, '''/get_file/(\d+/[^"^']+?)/''')[0] 
           printDBG( 'Host getResolvedURL videoPage: '+videoPage )
           if videoPage:
              decoder = "decrypt=function(_0xf4bdx6) {"\
                 "var _0xf4bdx7 = '',"\
                 "    _0xf4bdx8 = 0;"\
                 "/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g ['exec'](_0xf4bdx6) && console['log']('error decoding url');"\
                 "_0xf4bdx6 = _0xf4bdx6['replace'](/[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9\.\,\~]/g, '');"\
                 "do {"\
                 "var _0xf4bdx9 = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdxa = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdxb = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdxc = '\u0410\u0412\u0421D\u0415FGHIJKL\u041CNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~' ['indexOf'](_0xf4bdx6['charAt'](_0xf4bdx8++)),"\
                 "_0xf4bdx9 = _0xf4bdx9 << 2 | _0xf4bdxa >> 4,"\
                 "_0xf4bdxa = (_0xf4bdxa & 15) << 4 | _0xf4bdxb >> 2,"\
                 "_0xf4bdxd = (_0xf4bdxb & 3) << 6 | _0xf4bdxc,"\
                 "_0xf4bdx7 = _0xf4bdx7 + String['fromCharCode'](_0xf4bdx9);"\
                 "64 != _0xf4bdxb && (_0xf4bdx7 += String['fromCharCode'](_0xf4bdxa));"\
                 "64 != _0xf4bdxc && (_0xf4bdx7 += String['fromCharCode'](_0xf4bdxd))"\
                 "} while (_0xf4bdx8 < _0xf4bdx6['length']);;"\
                 "return unescape(_0xf4bdx7)"\
                 "};" 
              js = decoder + "\n" + "vidurl = decrypt('"+videoPage+"');"  
              printDBG( 'Host getResolvedURL js: '+js )
              urls = js_execute( js+ '\nfor (n in this){print(n+"="+this[n]+";");}')
              videoUrl = self.cm.ph.getSearchGroups(urls['data'], '''vidurl=([^"^']+?);''')[0] 
              printDBG( 'Host hash: '+hash )
              printDBG( 'Host videoUrl.split4: '+videoUrl.split('/')[-6] )
              printDBG( 'Host videoUrl.split5: '+videoUrl.split('/')[-5] )

              if hash: videoUrl = videoUrl.replace(videoUrl.split('/')[-6]+'/'+videoUrl.split('/')[-5],hash)
              if videoUrl: return videoUrl
              if videoPage.startswith('http'): return videoPage

           videoUrl = self.cm.ph.getSearchGroups(data, '''file\':\s['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urllib2.unquote(videoUrl)

        if parser == 'http://www.youporn.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'youporn.cookie')
           host = 'SmartTV'
           header = {'Cookie': 'age_verified=1', 'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'X-Requested-With':'XMLHttpRequest'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           match = re.findall(r'encryptedQuality720URL\s=\s\'([a-zA-Z0-9+/]+={0,2})\',', data)
           if match:
              fetchurl = urllib2.unquote(match[0])
              printDBG( 'Host getResolvedURL fetchurl: '+fetchurl )
              match = re.compile("video_title = '(.*?)'").findall(data)
              if match:
                 title = urllib.unquote_plus(match[0])
                 #title = '%s_720p' % title
                 printDBG( 'Host getResolvedURL title: '+title )
                 printDBG( 'Host getResolvedURL decrypt begin ' )
                 phStream = decrypt(fetchurl, title, 32)
                 if phStream: 
                    printDBG( 'Host getResolvedURL decrypted url: '+phStream )
                    return phStream
           videoUrl = self.cm.ph.getSearchGroups(data, '''1080:[ ]['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&')
           videoUrl = self.cm.ph.getSearchGroups(data, '''720:[ ]['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&')
           videoUrl = self.cm.ph.getSearchGroups(data, '''480:[ ]['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&')
           videoUrl = self.cm.ph.getSearchGroups(data, '''240:[ ]['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&')
           videoUrl = self.cm.ph.getSearchGroups(data, '''"videoUrl":['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&').replace(r"\/",r"/")
           return ''

        if parser == 'https://yourporn.sexy':
           COOKIEFILE = os_path.join(GetCookieDir(), 'yourporn.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self._getPage(url, self.defaultParams)
           if not sts: return 
           printDBG( 'Host listsItems data: '+str(data) )

           videoUrl = self.cm.ph.getSearchGroups(data, '''data-vnfo=['"].*?:['"]([^"^']+?)['"]''')[0].replace(r"\/",r"/")
           if videoUrl:
               printDBG( 'Host listsItems videoUrl: '+videoUrl )
               if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
               if videoUrl.startswith('/'): videoUrl = 'https://yourporn.sexy' + videoUrl
               if '/cdn/' in videoUrl: videoUrl = videoUrl.replace('/cdn/','/cdn2/')
               return videoUrl

           videoUrl = self.cm.ph.getSearchGroups(data, '''<video\sid='player_el'\ssrc=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           if videoUrl: return videoUrl


        if parser == 'http://oklivetv.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'oklivetv.cookie')
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, '<iframe', '</iframe>', False)[1]
           Url = self.cm.ph.getSearchGroups(data, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
           if Url.startswith('//'): Url = 'http:' + Url
           try: data = self.cm.getURLRequestData({ 'url': Url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host listsItems data2: '+data )
           if "eval(function(p,a,c,k,e,d)" in data:
              printDBG( 'Host resolveUrl packed' )
              packed = re.compile('>eval\(function\(p,a,c,k,e,d\)(.+?)</script>', re.DOTALL).findall(data)
              if packed:
                 data2 = packed[-1]
              else:
                 return ''
              printDBG( 'Host data4: '+str(data) )
              try:
                 videoUrl = unpackJSPlayerParams(data2, TEAMCASTPL_decryptPlayerParams, 0, True, True) 
                 printDBG( 'OK4: ')
              except Exception: pass 
              printDBG( 'Host videoUrl: '+str(videoUrl) )
              videoUrl = self.cm.ph.getSearchGroups(videoUrl, '''x-mpegURL","src":['"]([^"^']+?)['"]''', 1, True)[0] 
              if videoUrl: return videoUrl
           videoUrl1 = self.cm.ph.getSearchGroups(data, '''id="tab1.*?href=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           videoUrl2 = self.cm.ph.getSearchGroups(data, '''id="tab2.*?href=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if len(videoUrl1)>len(videoUrl2): 
              videoUrl=videoUrl1
           else:
              videoUrl=videoUrl2
           if videoUrl.startswith('tabs'): videoUrl = 'http://oklivetv.com/xplay/' + videoUrl
           printDBG( 'Host videoUrl tabs: '+str(videoUrl) )
           try: data = self.cm.getURLRequestData({ 'url': videoUrl, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              videoUrl = self.cm.ph.getSearchGroups(data, '''<iframe[^>]+?src=['"]([^"^']+?)['"]''')[0] 
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return self.getResolvedURL(videoUrl)
           printDBG( 'Host listsItems data3: '+data )
           if "eval(function(p,a,c,k,e,d)" in data:
              printDBG( 'Host resolveUrl packed' )
              packed = re.compile('>eval\(function\(p,a,c,k,e,d\)(.+?)</script>', re.DOTALL).findall(data)
              if packed:
                 data = packed[-1]
              else:
                 return ''
              printDBG( 'Host data4: '+str(data) )
              try:
                 videoUrl = unpackJSPlayerParams(data, TEAMCASTPL_decryptPlayerParams, 0, True, True) 
                 printDBG( 'OK4: ')
              except Exception: pass 
              printDBG( 'Host videoUrl: '+str(videoUrl) )
              videoUrl = self.cm.ph.getSearchGroups(videoUrl, '''x-mpegURL","src":['"]([^"^']+?)['"]''', 1, True)[0] 
              return videoUrl

        if parser == 'https://movie4k.org':
           COOKIEFILE = os_path.join(GetCookieDir(), 'movie4k.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage4k(url, 'movie4k.cookie', 'movie4k.org', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+str(data) )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<a\starget="_blank"\shref=['"]([^"^']+?)['"]''', 1, True)[0] 
           if not videoUrl:  videoUrl = self.cm.ph.getSearchGroups(data, '''<iframe[^>]+?src=['"]([^"^']+?)['"]''')[0] 
           if videoUrl:
              printDBG( 'Host videoUrl: '+videoUrl )
              videoUrls = self.getLinksForVideo(videoUrl)
              if videoUrls:
                 for item in videoUrls:
                    Url = item['url']
                    Name = item['name']
                    printDBG( 'Host url:  '+Url )
                    return Url
              else:
                 try:
                    info = 'Brak parsera  %s ' % videoUrl.split('/')[2]
                    GetIPTVNotify().push('%s' % (info), 'info', 3)
                 except: pass 
              #SetIPTVPlayerLastHostError('  Brak parsera  '+videoUrl.split('/')[2])
              #return []
              return self.getResolvedURL(videoUrl)
           return ''

        if parser == 'http://faapy.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'faapy.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'faapy.cookie', 'faapy.com', self.defaultParams)
           if not sts: return ''
           printDBG( 'Host listsItems data: '+str(data) )
           rnd = self.cm.ph.getSearchGroups(data, '''rnd:\s['"]([^"^']+?)['"]''')[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_url:\s['"]([^"^']+?)['"]''')[0].replace('function/0/','')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              videoUrl = videoUrl+'?rnd='+rnd #+'000'
              return videoUrl
              return urlparser.decorateUrl(videoUrl, {'Referer': url, 'Cookie': COOKIEFILE, 'User-Agent':self.USER_AGENT}) 

        if parser == 'http://www.tubewolf.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'tubewolf.cookie')
           host = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/17.0'
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
           for x in range(1, 10): 
              try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
              except:
                 printDBG( 'Host getResolvedURL query error url: '+url )
                 return ''
              printDBG( 'Host getResolvedURL data: '+data )
              data = self.cm.ph.getDataBeetwenMarkers(data, '<video id', '</video>', False)[1]
              videoUrl = re.findall('<source\ssrc="(.*?)"', data, re.S)
              if videoUrl:
                 return videoUrl[-1]

        if parser == 'https://streamate.com':
            COOKIEFILE = os_path.join(GetCookieDir(), 'streamate.cookie')
            url = 'https://streamate.com/blacklabel/hybrid/?name={}&lang=en&manifestUrlRoot=https://sea1c-ls.naiadsystems.com/sea1c-edge-ls/80/live/s:'.format(url)
            query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
            try:
                data = self.cm.getURLRequestData(query_data)
            except Exception as e:
                printExc()
                printDBG( 'Host listsItems query error url:'+url )
                return ''
            printDBG( 'Host listsItems data: '+data )
            url =  self.cm.ph.getSearchGroups(data, '''data-manifesturl=['"]([^"^']+?)['"]''')[0] 
            header = {'Referer': 'https://streamate.com', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
            query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
            try:
                data = self.cm.getURLRequestData(query_data)
            except Exception as e:
                printExc()
                printDBG( 'Host listsItems query error url:'+url )
                return ''
            printDBG( 'Host listsItems data2: '+data )
            try:
                videoinfo = simplejson.loads(data)
                videoUrl = videoinfo['formats']['mp4-hls']['manifest']
                videoUrl = urlparser.decorateUrl(videoUrl, {'Referer': 'https://streamate.com', 'iptv_livestream': True}) 
                if '.m3u8' in videoUrl:
                    if self.cm.isValidUrl(videoUrl): 
                        tmp = getDirectM3U8Playlist(videoUrl)
                        for item in tmp:
                            printDBG( 'Host listsItems valtab: '  +str(item))
                            return item['url']
                return videoUrl
            except Exception as e:
                printExc()
            return ''

        if parser == 'http://www.youjizz.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'youjizz.cookie')
           host = 'iPhone'
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'X-Requested-With':'XMLHttpRequest'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           printDBG( 'Host getResolvedURL data: '+data )
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"1080","filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&")
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"720","filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&")
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"480","filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&")
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"360","filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&") 
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"288","filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&") 
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"270","filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&")
           videoPage = self.cm.ph.getSearchGroups(data, '''"filename":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&")
           videoPage = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return videoPage.replace("&amp;","&")

           error = self.cm.ph.getDataBeetwenMarkers(data, '<p class="text-gray">', '</p>', False)[1]
           if error:
              SetIPTVPlayerLastHostError(_(error))
              return []
           return ''

        if parser == 'https://www.ashemaletube.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'ASHEMALETUBE.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           if 'sources: ' in data:
              try:
                 sources = self.cm.ph.getDataBeetwenMarkers(data, 'sources: ', ']', False)[1]
                 result = byteify(simplejson.loads(sources+']'))
                 for item in result:
                    if str(item["desc"])=='720p' and str(item["active"])=='true': return str(item["src"])
                    if str(item["desc"])=='480p' and str(item["active"])=='true': return str(item["src"])
                    if str(item["desc"])=='360p' and str(item["active"])=='true': return str(item["src"])
              except Exception as e:
                 printExc()
           videoUrl = self.cm.ph.getSearchGroups(data, '''source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return videoUrl 

           if 'To watch this video please' in data:
              SetIPTVPlayerLastHostError(_(' Login Protected.'))
              return []
           return ''

        if parser == 'http://www.pornhub.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'pornhub.cookie')
           host = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
           header = {'User-Agent': host, 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'en,en-US;q=0.7,en;q=0.3','X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except Exception as e:
              printExc()
              return ''
           printDBG( 'Host listsItems data: '+data )
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"720","videoUrl":['"]([^"^']+?)['"]''')[0] 
           if videoPage: return videoPage.replace('\/','/')
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"480","videoUrl":['"]([^"^']+?)['"]''')[0] 
           if videoPage: return videoPage.replace('\/','/')
           videoPage = self.cm.ph.getSearchGroups(data, '''"quality":"240","videoUrl":['"]([^"^']+?)['"]''')[0] 
           if videoPage: return videoPage.replace('\/','/')
           try:
              js = re.findall('(var flashvars_(?:\d+).*?)loadScriptUniqueId', data, re.S)
              #js = self.cm.ph.getDataBeetwenMarkers(data, 'var flashvars_', 'loadScriptUniqueId', False)[1]
              printDBG( 'Host data js: '+js )
              if js:
                 urls = js_execute( js[0]+ '\nfor (n in this){print(n+"="+this[n]+";");}')
                 videoPage = self.cm.ph.getSearchGroups(urls['data'], '''quality_720p=([^"^']+?);''')[0] 
                 if videoPage: return videoPage
                 videoPage = self.cm.ph.getSearchGroups(urls['data'], '''quality_480p=([^"^']+?);''')[0] 
                 if videoPage: return videoPage
                 videoPage = self.cm.ph.getSearchGroups(urls['data'], '''quality_240p=([^"^']+?);''')[0] 
                 if videoPage: return videoPage
           except:
              embed = re.search('"embedCode":"<iframe src=."(.*?)"', data, re.S)
              if embed:
                 url = embed.group(1).replace('\/','/').replace('\\','')
                 printDBG( 'Host data embed: '+url )
                 query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True }

                 try:    data = self.cm.getURLRequestData(query_data)
                 except: 
                    printDBG( 'Host getResolvedURL query error xml' )
                    return ''
                 printDBG( 'Host data embed full: '+data )
                 videoPage = re.findall('quality_720p":"(.*?)"', data, re.S)
                 if videoPage: return videoPage[0].replace('\/','/')
                 videoPage = re.findall('quality_480p":"(.*?)"', data, re.S)
                 if videoPage: return videoPage[0].replace('\/','/')
           return ''

        if parser == 'https://chaturbate.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'chaturbate.cookie')
           self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
           self.defaultParams = {'header':self.HTTP_HEADER}
           sts, data = self.get_Page(url)
           if not sts: return
           printDBG( 'Host listsItems data: '+str(data) )
           host = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.18) Gecko/20110621 Mandriva Linux/1.9.2.18-0.1mdv2010.2 (2010.2) Firefox/3.6.18'
           videoPage = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              item = []
              videoUrl = urllib2.unquote(videoPage.replace('&amp;','&'))
              videoUrl = urlparser.decorateUrl(videoUrl, {'Referer': url, 'User-Agent':host}) 
              if self.cm.isValidUrl(videoUrl): 
                 tmp = getDirectM3U8Playlist(videoUrl)
                 for item in tmp:
                    printDBG( 'Host listsItems valtab: '  +str(item))
                    if item['with']==0: return ''
                    if not self.format4k:
                       if item['with']==1920: return item['url']
                    if item['with']<=500: videoUrl = item['url']
                    if item['with']>=500: videoUrl = item['url']
                    if item['with']>=1000: videoUrl = item['url']
                    if item['with']>=1200: videoUrl = item['url']
                 return videoUrl
           return ''
##########################################################################################################################
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        try:
           data = self.cm.getURLRequestData(query_data)
           printDBG( 'Host getResolvedURL data: '+data )
        except:
           printDBG( 'Host getResolvedURL query error' )
           return videoUrl

        if parser == 'file: ':
           return self.cm.ph.getSearchGroups(data, '''file: ['"]([^"^']+?)['"]''')[0] 

        if parser == "0p'  : '":
           videoPage = re.findall("0p'  : '(http.*?)'", data, re.S)   
           if videoPage:
              return videoPage[-1]
           return ''

        if parser == 'source src="':
           videoPage = re.findall('source src="(http.*?)"', data, re.S)   
           if videoPage:
              return videoPage[-1]
           return ''

        if parser == "video_url: '":
           videoPage = re.findall("video_url: '(.*?).'", data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'videoFile="':
           videoPage = re.findall('videoFile="(.*?)"', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'http://www.pornrabbit.com':
           videoPage = re.findall("file: '(.*?)'", data, re.S)
           if videoPage:
              return videoPage[0]
           return ''

        if parser == 'http://www.pornhd.com':
           videoPage = re.findall("'1080p' : '(.*?)'", data, re.S)
           if videoPage:
              printDBG( 'Host pornhd videoPage:'+videoPage[0])
              if len(videoPage[0])>10: return videoPage[0]
           videoPage = re.findall("'720p' : '(.*?)'", data, re.S)
           if videoPage:
              printDBG( 'Host pornhd videoPage:'+videoPage[0])
              if len(videoPage[0])>10: return videoPage[0]
           videoPage = re.findall("'480p' : '(.*?)'", data, re.S)
           if videoPage:
              printDBG( 'Host pornhd videoPage:'+videoPage[0])
              if len(videoPage[0])>10: return videoPage[0]

           videoPage = self.cm.ph.getSearchGroups(data, '''"1080p":['"]([^"^']+?)['"]''')[0] 
           if videoPage: return videoPage.replace(r"\/",r"/")
           videoPage = self.cm.ph.getSearchGroups(data, '''"720p":['"]([^"^']+?)['"]''')[0] 
           if videoPage: return videoPage.replace(r"\/",r"/")
           videoPage = self.cm.ph.getSearchGroups(data, '''"480p":['"]([^"^']+?)['"]''')[0] 
           if videoPage: return videoPage.replace(r"\/",r"/")
           videoPage = self.cm.ph.getSearchGroups(data, '''"360p":['"]([^"^']+?)['"]''')[0] 
           if videoPage: return videoPage.replace(r"\/",r"/")
           return ''

        if parser == 'http://www.ah-me.com':
           videoPage = re.findall('<video\ssrc="(.*?)"', data, re.S) 
           if videoPage:
              printDBG( 'Host ah-me videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'http://www.amateurporn.net':
           videoPage = re.findall('<param\sname="flashvars"\svalue="file=(.*?)&provider=', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'http://www.nuvid.com':
           videoUrl = re.search("http://www.nuvid.com/video/(.*?)/.+", url, re.S)
           if videoUrl:
              xml = 'http://m.nuvid.com/video/%s' % videoUrl.group(1)
              try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
              except: 
                 printDBG( 'Host getResolvedURL query error xml' )
                 return ''
              #printDBG( 'Host data json: '+data )
              videoPage = re.findall('source src="(.*?)"', data, re.S)   
              if videoPage:
                 return videoPage[0]
           return ''

        if parser == 'http://www.wankoz.com':
           videoPage = re.findall("'video_html5_url']='(.*?).'", data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'http://www.sunporno.com':
           videoPage = re.findall('video src="(.*?)"', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'https://alpha.tnaflix.com':
           videoPage = re.findall('"embedUrl" content="(.*?)"', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return 'http:'+videoPage[0]
           return ''

        if parser == 'http://www.faphub.xxx':
           videoPage = re.findall("url: '(.*?)'", data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''
   
        if parser == 'http://www.proporn.com':
           videoPage = re.findall('source src="(.*?)"', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''
   
        if parser == 'http://www.empflix.com':
           videoPage = re.findall("video_url: '(.*?)'", data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''
   
        if parser == 'http://www.xnxx.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''VideoUrlHigh\(['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''VideoUrlLow\(['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''VideoHLS\(['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = re.search('flv_url=(.*?)&', data, re.S)
           if videoUrl: return decodeUrl(videoUrl.group(1))
           return ''

        if parser == 'http://www.xvideos.com':
           videoUrl = re.search("setVideoUrlHigh\('(.*?)'", data, re.S)
           if videoUrl: return decodeUrl(videoUrl.group(1))
           videoUrl = re.search('flv_url=(.*?)&', data, re.S)
           if videoUrl: return decodeUrl(videoUrl.group(1))
           return ''

        if parser == 'http://embed.redtube.com':
           videoPage = re.findall('sources:.*?":"(.*?)"', data, re.S)
           if videoPage:
              link = videoPage[-1].replace(r"\/",r"/")
              if link.startswith('//'): link = 'http:' + link 
              return link
           return ''

        if parser == 'http://xhamster.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''720p['"]:['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&').replace(r"\/",r"/")
           videoUrl = self.cm.ph.getSearchGroups(data, '''480p['"]:['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&').replace(r"\/",r"/")
           videoUrl = self.cm.ph.getSearchGroups(data, '''240p['"]:['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&').replace(r"\/",r"/")
           xhFile = re.findall('"file":"(.*?)"', data)
           if xhFile: return xhFile[0].replace(r"\/",r"/")
           else: 
              xhFile = re.findall("file: '(.*?)'", data)
              if xhFile: return xhFile[0].replace(r"\/",r"/")
           return ''
        
        if parser == 'http://www.eporner.com':
           videoID = re.search("http://www.eporner.com/hd-porn/(.*?)/.+", url)
           if not videoID: return ''
           parse = re.findall("hash: '(.*?)'", data, re.S)
           hash =  urllib.unquote_plus(parse[0]).decode("utf-8")
           x = calc_hash(hash)
           printDBG( 'Host getResolvedURL hash: '+parse[0]+' calc_hash:'+x)
           xml = 'http://www.eporner.com/xhr/video/%s?device=generic&domain=www.eporner.com&hash=%s&fallback=false' % (videoID.group(1), x)
           try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
           except: 
                   printDBG( 'Host getResolvedURL query error xml' )
                   return ''
           #printDBG( 'Host data json: '+data )
           videoPage = re.findall('src": "(.*?)"', data, re.S)
           if videoPage: return videoPage[0]
           return ''

        if parser == 'http://www.pornhub.com/embed/':
           match = re.findall("container.*?src.*?'(.*?)'", data, re.S)
           if match: return match[0]
           return ''
        
        if parser == 'http://www.hdporn.net':
           match = re.findall('source src="(.*?)"', data, re.S)
           if match: return match[0]
           else: return ''

        if parser == 'http://m.tube8.com':
           match = re.compile('<div class="play_video.+?<a href="(.+?)"', re.DOTALL).findall(data)
           return match[0]

        if parser == 'http://m.pornhub.com':
           match = re.compile('<div class="play_video.+?<a href="(.+?)"', re.DOTALL).findall(data)
           return match[0]

        if parser == 'http://www.dachix.com':
           videoPage = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              return urllib2.unquote(videoPage) 
           return ''

        if parser == 'http://www.drtuber.com':
           params = re.findall('params\s\+=\s\'h=(.*?)\'.*?params\s\+=\s\'%26t=(.*?)\'.*?params\s\+=\s\'%26vkey=\'\s\+\s\'(.*?)\'', data, re.S)
           if params:
              for (param1, param2, param3) in params:
                 hash = hashlib.md5(param3 + base64.b64decode('UFQ2bDEzdW1xVjhLODI3')).hexdigest()
                 url = '%s/player_config/?h=%s&t=%s&vkey=%s&pkey=%s&aid=' % ("http://www.drtuber.com", param1, param2, param3, hash)
                 query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
                 try:
                    data = self.cm.getURLRequestData(query_data)
                 except:
                    printDBG( 'Host listsItems query error' )
                    printDBG( 'Host listsItems query error url: '+url )
                 #printDBG( 'Host listsItems data: '+data )
                 url = re.findall('video_file>.*?(http.*?)\]\]><\/video_file>', data, re.S)
                 if url:
                    url = str(url[0])
                    url = url.replace("&amp;","&")
                    printDBG( 'Host listsItems url: '+url )
                    return url
           return ''

        if parser == 'https://www.tnaflix.com':
           link = re.search("data-vid='(.*?)'\sdata-nk='(.*?)'\sdata-vk='(.*?)'", data, re.S) 
           if link:
              vid = link.group(1)
              nk =  link.group(2)
              vk =  link.group(3)
              xml = 'https://cdn-fck.tnaflix.com/tnaflix/%s.fid?key=%s&VID=%s&nomp4=1&catID=0&rollover=1&startThumb=31&embed=0&utm_source=0&multiview=0&premium=1&country=0user=0&vip=1&cd=0&ref=0&alpha' % (vk, nk, vid) 
           try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
           except: 
                   printDBG( 'Host getResolvedURL query error xml' )
                   return videoUrl
           videoPage = re.findall('<videoLink>.*?//(.*?)(?:]]>|</videoLink>)', data, re.S)
           if videoPage: return 'http://' + videoPage[-1]
           return ''

        if parser == 'https://www.empflix.com':
           videoPage = re.search('"contentUrl" content="(.*?)"', data, re.S)  
           if videoPage:
              return videoPage.group(1)
           return ''

        if parser == 'http://search.el-ladies.com':
           videoPage = re.findall(',file:\'(.*?)\'', data, re.S)  
           if videoPage:
              return videoPage[0]
           return ''

        if parser == 'http://www.extremetube.com':
           videoPage = re.findall('"quality_\d+p":"(.*?)"', data, re.S) 
           if videoPage:
              url = videoPage[-1] 
              url = url.replace('\/','/') 
              if url.startswith('//'): url = 'http:' + url
              return url
           return ''

        if parser == 'http://pornicom.com':
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'var flashvars', '}', False)[1]
           if data2: return self.cm.ph.getSearchGroups(data2, '''['"](https://pornicom.com/get_file/[^"^']+?)['"]''')[0].replace('&amp;','&')
           videoPage = self.cm.ph.getSearchGroups(data, '''file: ['"]([^"^']+?)['"]''')[0] 
           if videoPage: return videoPage
           videoPage = self.cm.ph.getSearchGroups(data, '''['"](https://pornicom.com/get_file/[^"^']+?)['"]''')[0] 
           if videoPage: return urllib2.unquote(videoPage)

        if parser == 'http://sexylies.com':
           videoPage = re.search('source\stype="video/mp4"\ssrc="(.*?)"', data, re.S) 
           if videoPage:
              return videoPage.group(1)
           return ''

        if parser == 'http://www.eskimotube.com':
           videoPage = re.search('color=black.*?href=(.*?)>', data, re.S) 
           if videoPage:
              return videoPage.group(1)
           return ''

        if parser == 'http://www.porn5.com':
           videoPage = re.findall('p",url:"(.*?)"', data, re.S) 
           if videoPage:
              return videoPage[-1]
           return ''

        if parser == 'http://www.pornyeah.com':
           videoPage = re.findall('settings=(.*?)"', data, re.S)
           if not videoPage: return ''
           xml = videoPage[0]
           printDBG( 'Host getResolvedURL xml: '+xml )
           try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
           except: 
                   printDBG( 'Host getResolvedURL query error xml' )
                   return videoUrl
           videoPage = re.findall('defaultVideo:(.*?);', data, re.S)
           if videoPage: return videoPage[0]
           return ''

        if parser == 'http://rusporn.tv':
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_alt_url: ['"]([^"^']+?)['"]''')[0] 
           if videoUrl: return videoUrl
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_url: ['"]([^"^']+?)['"]''')[0] 
           if videoUrl: return videoUrl
           return ''

        if parser == 'http://porn720.net':
           videoUrl = self.cm.ph.getSearchGroups(data, '''720p['"]:['"]([^"^']+?)['"]''')[0] 
           if videoUrl:
              return urlparser.decorateUrl(videoUrl, {'Referer': url}) 
           videoUrl = self.cm.ph.getSearchGroups(data, '''480p['"]:['"]([^"^']+?)['"]''')[0] 
           if videoUrl:
              return urlparser.decorateUrl(videoUrl, {'Referer': url}) 
           return ''

        if parser == 'http://porndoe.com':
           host = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '      <source', '>')
           for item in data:
              printDBG( 'Host item: '+str(item) )

              label1 = self.cm.ph.getSearchGroups(item, '''label=['"](720[^"^']+?)['"]''', 1, True)[0] 
              if label1: videoUrl = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              label2 = self.cm.ph.getSearchGroups(item, '''label=['"](480[^"^']+?)['"]''', 1, True)[0] 
              if label2: videoUrl = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              label3 = self.cm.ph.getSearchGroups(item, '''label=['"](240[^"^']+?)['"]''', 1, True)[0] 
              if label3: videoUrl = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0]
              printDBG( 'Host label1: '+label1 )
              printDBG( 'Host label2: '+label2 )
              printDBG( 'Host label3: '+label3 )

           if label1: return urlparser.decorateUrl(videoUrl, {'Referer': url, 'User-Agent': host}) 
           if label2: return urlparser.decorateUrl(videoUrl, {'Referer': url, 'User-Agent': host}) 
           if label3: return urlparser.decorateUrl(videoUrl, {'Referer': url, 'User-Agent': host}) 
           return ''

        if parser == 'http://www.pornpillow.com':
           videoPage = re.findall("'file': '(.*?)'", data, re.S)   
           if videoPage:
              return videoPage[0]
           return ''

        if parser == 'http://www.filmyporno.tv':
           match = re.findall('source src="(.*?)"', data, re.S)
           if match: return match[0]
           else: return ''

        if parser == 'http://pornohub.su':
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''')[0] 
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urlparser.decorateUrl(videoUrl, {'Referer': url})

        if parser == 'http://www.thumbzilla.com':
           match = re.findall('data-quality="(.*?)"', data)
           if match:
              fetchurl = urllib2.unquote(match[-1])
              fetchurl = fetchurl.replace(r"\/",r"/")
              if fetchurl.startswith('//'): fetchurl = 'http:' + fetchurl
              return fetchurl 
           return ''

        if parser == 'https://vidlox.tv':
           parse = re.search('sources.*?"(http.*?)"', data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://xxxkingtube.com':
           parse = re.search("File = '(http.*?)'", data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://pornsharing.com':
           parse = re.search('btoa\("(http.*?)"', data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://pornxs.com':
           parse = re.search('config-final-url="(http.*?)"', data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://www.flyflv.com':
           parse = re.search('fileUrl="(http.*?)"', data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://www.yeptube.com':
           videoUrl = re.search('video_id = "(.*?)"', data, re.S)
           if videoUrl:
              xml = 'http://www.yeptube.com/player_config_json/?vid=%s&aid=0&domain_id=0&embed=0&ref=&check_speed=0' % videoUrl.group(1)
              try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
              except: 
                 printDBG( 'Host getResolvedURL query error xml' )
                 return ''
              #printDBG( 'Host data json: '+data )
              videoPage = re.search('"hq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
              videoPage = re.search('"lq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
           return ''

        if parser == 'http://vivatube.com':
           videoUrl = re.search('video_id = "(.*?)"', data, re.S)
           if videoUrl:
              xml = 'http://vivatube.com/player_config_json/?vid=%s&aid=0&domain_id=0&embed=0&ref=&check_speed=0' % videoUrl.group(1)
              try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
              except: 
                 printDBG( 'Host getResolvedURL query error xml' )
                 return ''
              #printDBG( 'Host data json: '+data )
              videoPage = re.search('"hq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
              videoPage = re.search('"lq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
           return ''

        if parser == 'http://www.tubeon.com':
           videoUrl = re.search('video_id = "(.*?)"', data, re.S)
           if videoUrl:
              xml = 'http://www.tubeon.com/player_config_json/?vid=%s&aid=0&domain_id=0&embed=0&ref=&check_speed=0' % videoUrl.group(1)
              try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
              except: 
                 printDBG( 'Host getResolvedURL query error xml' )
                 return ''
              #printDBG( 'Host data json: '+data )
              videoPage = re.search('"hq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
              videoPage = re.search('"lq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
           return ''

        if parser == 'http://www.yuvutu.com':
           match = re.findall('iframe src="(.*?)"', data, re.S)
           if match: 
              url = 'http://www.yuvutu.com'+match[0]
              query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
              try:
                 data = self.cm.getURLRequestData(query_data)
              except:
                 printDBG( 'Host listsItems query error url: '+url )
              #printDBG( 'Host listsItems data: '+data )
              url = re.findall('file: "(.*?)"', data, re.S)
              if url: 
                 videoUrl = url[-1]
                 return videoUrl
           return ''

        if parser == 'https://www.pornomenge.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''')[0] 
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return videoUrl

        if parser == 'https://www.koloporno.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''')[0] 
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return videoUrl
  
        if parser == 'http://befuck.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urllib2.unquote(videoUrl)

        if parser == 'https://www.realgfporn.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return videoUrl
           videoUrl = self.cm.ph.getSearchGroups(data, '''file: ['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return videoUrl

        if parser == 'http://www.homemoviestube.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''value="settings=([^"^']+?)['"]''')[0]
           if videoUrl:
              query_data = { 'url': videoUrl, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
              try:
                 data = self.cm.getURLRequestData(query_data)
              except:
                 printDBG( 'Host listsItems query error url: '+url )
              #printDBG( 'Host listsItems data: '+data )
              return self.cm.ph.getSearchGroups(data, '''flvMask:([^"^']+?);''')[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return videoUrl
           return ''

        if parser == 'http://www.moviefap.com':
           xml = re.findall('flashvars.config.*?//(.*?)"', data, re.S)
           if not xml:
              xml = re.findall('name="config".*?//(.*?)"', data, re.S)
           if xml:
              videoUrl = "http://" + xml[0] 
              query_data = { 'url': videoUrl, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
              try:
                 data = self.cm.getURLRequestData(query_data)
              except:
                 printDBG( 'Host listsItems query error url: '+url )
              #printDBG( 'Host listsItems data: '+data )
              url = re.findall('<videoLink>.*?//(.*?)(?:]]>|</videoLink>)', data, re.S)
              if url:
                 return "http://" + url[-1] 
           return ''

        if parser == 'http://dato.porn':
           if "eval(function(p,a,c,k,e,d)" in data:
              printDBG( 'Host resolveUrl packed' )
              packed = re.compile('>eval\(function\(p,a,c,k,e,d\)(.+?)</script>', re.DOTALL).findall(data)
              if packed:
                 data = packed[-1]
              else:
                 return ''
              printDBG( 'Host data4: '+str(data) )
              try:
                 videoUrl = unpackJSPlayerParams(data, TEAMCASTPL_decryptPlayerParams, 0, True, True) 
                 printDBG( 'OK4: ')
              except Exception: pass 
              printDBG( 'Host videoUrl: '+str(videoUrl) )
              videoUrl = re.compile('file:"(.*?)"', re.DOTALL).findall(videoUrl)
              if videoUrl: 
                 USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.120 Chrome/37.0.2062.120 Safari/537.36'
                 Url = urlparser.decorateUrl(videoUrl[-1], {'User-Agent': USER_AGENT, 'Referer': url})
                 return Url
           videoUrl = self.cm.ph.getSearchGroups(data, '''src: ['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl: return videoUrl
           if 'File Not Found' in data: 
              SetIPTVPlayerLastHostError(_(' File Not Found.'))
              return []
           return ''

        if parser == 'https://porndig.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           if '.m3u8' in videoUrl:
              if self.cm.isValidUrl(videoUrl): 
                 tmp = getDirectM3U8Playlist(videoUrl)
                 for item in tmp:
                    printDBG( 'Host listsItems valtab: '  +str(item))
                 return item['url']
           return videoUrl

        if parser == 'http://hentaigasm.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''file: ['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urllib2.unquote(videoUrl)

        if parser == 'https://www.katestube.com':
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'var flashvars', '}', False)[1]
           if data2: return self.cm.ph.getSearchGroups(data2, '''['"](https://www.katestube.com/get_file[^"^']+?)['"]''')[0].replace('&amp;','&')
           data2 = self.cm.ph.getDataBeetwenMarkers(data, 'sources:', ']', False)[1]
           if data2: return self.cm.ph.getSearchGroups(data, '''src:\s['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           videoUrl = self.cm.ph.getSearchGroups(data, '''file: ['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''['"](https://www.katestube.com/get_file[^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              return urllib2.unquote(videoUrl)
           return ''

        if parser == 'https://mini.zbiornik.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return urllib2.unquote(videoUrl)

        if parser == 'https://www.vporn.com':
           for video in re.findall(r'flashvars\.videoUrl([^=]+?)\s*=\s*"(https?://[^"]+)"', data):
              videoUrl = urllib2.unquote(video[1].replace('https://','http://'))
              printDBG( 'Host videoUrl '+videoUrl )
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)

        if parser == 'http://www.updatetube.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''video_url:\s['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)

        if parser == 'https://www.pornoxo.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''"file":['"]([^"^']+?)['"]''')[0].replace('\/','/')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''file\':\s['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''filefallback\':\s['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)
           videoUrl = self.cm.ph.getSearchGroups(data, '''file:\s['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urllib2.unquote(videoUrl)

        if parser == 'https://www.pinflix.com':
           videoUrl = re.findall('\d+p"."(.*?)"', data, re.S)
           if videoUrl:
              return videoUrl[-1].replace('\/','/')

        if parser == 'http://sexu.com':
           videoUrl = re.findall('"file":"(.*?\.mp4)"', data, re.S)
           if videoUrl:
              return urlparser.decorateUrl(videoUrl[-1], {'Referer': 'http://sexu.com/'}) 
           videoUrl = self.cm.ph.getSearchGroups(data, '''"src":['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return urlparser.decorateUrl(videoUrl, {'Referer': 'http://sexu.com/'}) 

        if parser == 'http://sexkino.to':
           videoUrl = re.findall('<iframe.*?src="(.*?)"', data, re.S)
           if videoUrl:
              return self.getResolvedURL(videoUrl[-1])

        if parser == 'https://mulemax.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return videoUrl

        if parser == 'https://miamitvhd.com':
           if '.m3u8' in data:
              return self.cm.ph.getSearchGroups(data, '''source src=['"]([^"^']+?)['"]''', 1, True)[0]
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0].replace('&amp;','&')
           if videoUrl:
              if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
              return videoUrl
 

        printDBG( 'Host getResolvedURL end' )
        return videoUrl





############################################
# functions for host
############################################
def decodeUrl(text):
	text = text.replace('%20',' ')
	text = text.replace('%21','!')
	text = text.replace('%22','"')
	text = text.replace('%23','&')
	text = text.replace('%24','$')
	text = text.replace('%25','%')
	text = text.replace('%26','&')
	text = text.replace('%2B','+')
	text = text.replace('%2F','/')

	text = text.replace('%3A',':')
	text = text.replace('%3B',';')
	text = text.replace('%3D','=')
	text = text.replace('%3F','?')
	text = text.replace('%40','@')
	return text

def decodeHtml(text):
	text = text.replace('&auml;','ä')
	text = text.replace('\u00e4','ä')
	text = text.replace('&#228;','ä')
	text = text.replace('&oacute;','ó')
	text = text.replace('&eacute;','e')
	text = text.replace('&aacute;','a')
	text = text.replace('&ntilde;','n')

	text = text.replace('&Auml;','Ä')
	text = text.replace('\u00c4','Ä')
	text = text.replace('&#196;','Ä')
	
	text = text.replace('&ouml;','ö')
	text = text.replace('\u00f6','ö')
	text = text.replace('&#246;','ö')
	
	text = text.replace('&ouml;','Ö')
	text = text.replace('\u00d6','Ö')
	text = text.replace('&#214;','Ö')
	
	text = text.replace('&uuml;','ü')
	text = text.replace('\u00fc','ü')
	text = text.replace('&#252;','ü')
	
	text = text.replace('&Uuml;','Ü')
	text = text.replace('\u00dc','Ü')
	text = text.replace('&#220;','Ü')
	
	text = text.replace('&szlig;','ß')
	text = text.replace('\u00df','ß')
	text = text.replace('&#223;','ß')
	
	text = text.replace('&amp;','&')
	text = text.replace('&quot;','\"')
	text = text.replace('&gt;','>')
	text = text.replace('&apos;',"'")
	text = text.replace('&acute;','\'')
	text = text.replace('&ndash;','-')
	text = text.replace('&bdquo;','"')
	text = text.replace('&rdquo;','"')
	text = text.replace('&ldquo;','"')
	text = text.replace('&lsquo;','\'')
	text = text.replace('&rsquo;','\'')
	text = text.replace('&#034;','\'')
	text = text.replace('&#038;','&')
	text = text.replace('&#039;','\'')
	text = text.replace('&#39;','\'')
	text = text.replace('&#160;',' ')
	text = text.replace('\u00a0',' ')
	text = text.replace('&#174;','')
	text = text.replace('&#225;','a')
	text = text.replace('&#233;','e')
	text = text.replace('&#243;','o')
	text = text.replace('&#8211;',"-")
	text = text.replace('\u2013',"-")
	text = text.replace('&#8216;',"'")
	text = text.replace('&#8217;',"'")
	text = text.replace('#8217;',"'")
	text = text.replace('&#8220;',"'")
	text = text.replace('&#8221;','"')
	text = text.replace('&#8222;',',')
	text = text.replace('&#x27;',"'")
	text = text.replace('&#8230;','...')
	text = text.replace('\u2026','...')
	text = text.replace('&#41;',')')
	text = text.replace('&lowbar;','_')
	text = text.replace('&rsquo;','\'')
	text = text.replace('&lpar;','(')
	text = text.replace('&rpar;',')')
	text = text.replace('&comma;',',')
	text = text.replace('&period;','.')
	text = text.replace('&plus;','+')
	text = text.replace('&num;','#')
	text = text.replace('&excl;','!')
	text = text.replace('&#039','\'')
	text = text.replace('&semi;','')
	text = text.replace('&lbrack;','[')
	text = text.replace('&rsqb;',']')

	return text	

############################################
# functions for pornhub
############################################
def decrypt(ciphertext, password, nBits):
    printDBG( 'decrypt begin ' )
    blockSize = 16
    if not nBits in (128, 192, 256): return ""
    ciphertext = base64.b64decode(ciphertext)
#    password = password.encode("utf-8")

    nBytes = nBits//8
    pwBytes = [0] * nBytes
    for i in range(nBytes): pwBytes[i] = 0 if i>=len(password) else ord(password[i])
    key = Cipher(pwBytes, KeyExpansion(pwBytes))
    key += key[:nBytes-16]

    counterBlock = [0] * blockSize
    ctrTxt = ciphertext[:8]
    for i in range(8): counterBlock[i] = ord(ctrTxt[i])

    keySchedule = KeyExpansion(key)

    nBlocks = int( math.ceil( float(len(ciphertext)-8) / float(blockSize) ) )
    ct = [0] * nBlocks
    for b in range(nBlocks):
        ct[b] = ciphertext[8+b*blockSize : 8+b*blockSize+blockSize]
    ciphertext = ct

    plaintxt = [0] * len(ciphertext)

    for b in range(nBlocks):
        for c in range(4): counterBlock[15-c] = urs(b, c*8) & 0xff
        for c in range(4): counterBlock[15-c-4] = urs( int( float(b+1)/0x100000000-1 ), c*8) & 0xff

        cipherCntr = Cipher(counterBlock, keySchedule)

        plaintxtByte = [0] * len(ciphertext[b])
        for i in range(len(ciphertext[b])):
            plaintxtByte[i] = cipherCntr[i] ^ ord(ciphertext[b][i])
            plaintxtByte[i] = chr(plaintxtByte[i])
        plaintxt[b] = "".join(plaintxtByte)

    plaintext = "".join(plaintxt)
 #   plaintext = plaintext.decode("utf-8")
    return plaintext

Sbox = [
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
]

Rcon = [
    [0x00, 0x00, 0x00, 0x00],
    [0x01, 0x00, 0x00, 0x00],
    [0x02, 0x00, 0x00, 0x00],
    [0x04, 0x00, 0x00, 0x00],
    [0x08, 0x00, 0x00, 0x00],
    [0x10, 0x00, 0x00, 0x00],
    [0x20, 0x00, 0x00, 0x00],
    [0x40, 0x00, 0x00, 0x00],
    [0x80, 0x00, 0x00, 0x00],
    [0x1b, 0x00, 0x00, 0x00],
    [0x36, 0x00, 0x00, 0x00]
]

def Cipher(input, w):
    printDBG( 'cipher begin ' )
    Nb = 4
    Nr = len(w)/Nb - 1

    state = [ [0] * Nb, [0] * Nb, [0] * Nb, [0] * Nb ]
    for i in range(0, 4*Nb): state[i%4][i//4] = input[i]

    state = AddRoundKey(state, w, 0, Nb)

    for round in range(1, Nr):
        state = SubBytes(state, Nb)
        state = ShiftRows(state, Nb)
        state = MixColumns(state, Nb)
        state = AddRoundKey(state, w, round, Nb)

    state = SubBytes(state, Nb)
    state = ShiftRows(state, Nb)
    state = AddRoundKey(state, w, Nr, Nb)

    output = [0] * 4*Nb
    for i in range(4*Nb): output[i] = state[i%4][i//4]
    return output

def SubBytes(s, Nb):
    printDBG( 'subbytes begin ' )
    for r in range(4):
        for c in range(Nb):
            s[r][c] = Sbox[s[r][c]]
    return s

def ShiftRows(s, Nb):
    printDBG( 'shiftrows begin ' )
    t = [0] * 4
    for r in range (1,4):
        for c in range(4): t[c] = s[r][(c+r)%Nb]
        for c in range(4): s[r][c] = t[c]
    return s

def MixColumns(s, Nb):
    printDBG( 'mixcolumns begin ' )
    for c in range(4):
        a = [0] * 4
        b = [0] * 4
        for i in range(4):
            a[i] = s[i][c]
            b[i] = s[i][c]<<1 ^ 0x011b if s[i][c]&0x80 else s[i][c]<<1
        s[0][c] = b[0] ^ a[1] ^ b[1] ^ a[2] ^ a[3]
        s[1][c] = a[0] ^ b[1] ^ a[2] ^ b[2] ^ a[3]
        s[2][c] = a[0] ^ a[1] ^ b[2] ^ a[3] ^ b[3]
        s[3][c] = a[0] ^ b[0] ^ a[1] ^ a[2] ^ b[3]
    return s

def AddRoundKey(state, w, rnd, Nb):
    printDBG( 'addroundkey begin ' )
    for r in range(4):
        for c in range(Nb):
            state[r][c] ^= w[rnd*4+c][r]
    return state

def KeyExpansion(key):
    printDBG( 'keyexpansion begin ' )
    Nb = 4
    Nk = len(key)/4
    Nr = Nk + 6

    w = [0] * Nb*(Nr+1)
    temp = [0] * 4

    for i in range(Nk):
        r = [key[4*i], key[4*i+1], key[4*i+2], key[4*i+3]]
        w[i] = r

    for i in range(Nk, Nb*(Nr+1)):
        w[i] = [0] * 4
        for t in range(4): temp[t] = w[i-1][t]
        if i%Nk == 0:
            temp = SubWord(RotWord(temp))
            for t in range(4): temp[t] ^= Rcon[i/Nk][t]
        elif Nk>6 and i%Nk == 4:
            temp = SubWord(temp)
        for t in range(4): w[i][t] = w[i-Nk][t] ^ temp[t]
    return w

def SubWord(w):
    printDBG( 'subword begin ' )
    for i in range(4): w[i] = Sbox[w[i]]
    return w

def RotWord(w):
    printDBG( 'rotword begin ' )
    tmp = w[0]
    for i in range(3): w[i] = w[i+1]
    w[3] = tmp
    return w

def encrypt(plaintext, password, nBits):
    printDBG( 'encrypt begin ' )
    blockSize = 16
    if not nBits in (128, 192, 256): return ""
#    plaintext = plaintext.encode("utf-8")
#    password  = password.encode("utf-8")
    nBytes = nBits//8
    pwBytes = [0] * nBytes
    for i in range(nBytes): pwBytes[i] = 0 if i>=len(password) else ord(password[i])
    key = Cipher(pwBytes, KeyExpansion(pwBytes))
    key += key[:nBytes-16]

    counterBlock = [0] * blockSize
    now = datetime.datetime.now()
    nonce = time.mktime( now.timetuple() )*1000 + now.microsecond//1000
    nonceSec = int(nonce // 1000)
    nonceMs  = int(nonce % 1000)

    for i in range(4): counterBlock[i] = urs(nonceSec, i*8) & 0xff
    for i in range(4): counterBlock[i+4] = nonceMs & 0xff

    ctrTxt = ""
    for i in range(8): ctrTxt += chr(counterBlock[i])

    keySchedule = KeyExpansion(key)

    blockCount = int(math.ceil(float(len(plaintext))/float(blockSize)))
    ciphertxt = [0] * blockCount

    for b in range(blockCount):
        for c in range(4): counterBlock[15-c] = urs(b, c*8) & 0xff
        for c in range(4): counterBlock[15-c-4] = urs(b/0x100000000, c*8)

        cipherCntr = Cipher(counterBlock, keySchedule)

        blockLength = blockSize if b<blockCount-1 else (len(plaintext)-1)%blockSize+1
        cipherChar = [0] * blockLength

        for i in range(blockLength):
            cipherChar[i] = cipherCntr[i] ^ ord(plaintext[b*blockSize+i])
            cipherChar[i] = chr( cipherChar[i] )
        ciphertxt[b] = ''.join(cipherChar)

    ciphertext = ctrTxt + ''.join(ciphertxt)
    ciphertext = base64.b64encode(ciphertext)

    return ciphertext

def urs(a, b):
    printDBG( 'urs begin ' )
    a &= 0xffffffff
    b &= 0x1f
    if a&0x80000000 and b>0:
        a = (a>>1) & 0x7fffffff
        a = a >> (b-1)
    else:
        a = (a >> b)
    return a

############################################
# functions for beeg.com
############################################
def decrypt_key(key, a):
    printDBG( 'beeg_salt= '+a)
    e = urllib.unquote_plus(key).decode("utf-8")
    o = ''.join([
        chr(ord(e[n]) - ord(a[n % len(a)]) % 21)
        for n in range(len(e))])
    return ''.join(split(o, 3)[::-1])
	
def split(o, e):
    def cut(s, x):
        n.append(s[:x])
        return s[x:]
    n = []
    r = len(o) % e
    if r > 0:
        o = cut(o, r)
    while len(o) > e:
        o = cut(o, e)
    n.append(o)
    return n
############################################
# functions for eporner
############################################
def calc_hash(s):
    return ''.join((encode_base_n(int(s[lb:lb + 8], 16), 36) for lb in range(0, 32, 8)))

def encode_base_n(num, n, table=None):
    FULL_TABLE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if not table:
        table = FULL_TABLE[:n]

    if n > len(table):
        raise ValueError('base %d exceeds table length %d' % (n, len(table)))

    if num == 0:
        return table[0]

    ret = ''
    while num:
        ret = table[num % n] + ret
        num = num // n
    return ret
############################################
# functions for myfreecam
############################################
vs_str={}
vs_str[0]="PUBLIC"
vs_str[2]="AWAY"
vs_str[12]="PVT"
vs_str[13]="GROUP"
vs_str[90]="CAM OFF"
vs_str[127]="OFFLINE"
vs_str[128]="TRUEPVT"

def fc_decode_json(m):
	try:
		m = m.replace('\r', '\\r').replace('\n', '\\n')
		return simplejson.loads(m[m.find("{"):].decode("utf-8","ignore"))
	except:
		return simplejson.loads("{\"lv\":0}")

def read_model_data(m):
	global CAMGIRLSERVER
	global CAMGIRLCHANID
	global CAMGIRLUID
	usr = ''
	msg = fc_decode_json(m)
	try:
		sid=msg['sid']
		level  = msg['lv']
	except:
		printDBG ("errr reply ... We're fucked ..")
		return

	vs     = msg['vs']
	usr    = msg['nm']

	if vs == 2:
		printDBG ("%s is %s" % (usr, vs_str[vs]))
		SetIPTVPlayerLastHostError(_(vs_str[vs]))
		return []
	if vs == 12:
		printDBG ("%s is %s" % (usr, vs_str[vs]))
		SetIPTVPlayerLastHostError(_(vs_str[vs]))
		return []
	if vs == 13:
		printDBG ("%s is %s" % (usr, vs_str[vs]))
		SetIPTVPlayerLastHostError(_(vs_str[vs]))
		return []
	if vs == 90:
		printDBG ("%s is %s" % (usr, vs_str[vs]))
		SetIPTVPlayerLastHostError(_(vs_str[vs]))
		return []
	if vs == 127:
		printDBG ("%s is %s" % (usr, vs_str[vs]))
		SetIPTVPlayerLastHostError(_(vs_str[vs]))
		return []
	if vs == 128:
		printDBG ("%s is %s" % (usr, vs_str[vs]))
		SetIPTVPlayerLastHostError(_(vs_str[vs]))
		return []

	CAMGIRLUID    = msg['uid']
	CAMGIRLCHANID = msg['uid'] + 100000000
	camgirlinfo=msg['m']
	flags  = camgirlinfo['flags']
	u_info=msg['u']

	try:
		CAMGIRLSERVER = u_info['camserv']
		printDBG ("Video Server : %d Channel Id : %d  Model id : %d " %(CAMGIRLSERVER, CAMGIRLCHANID, CAMGIRLUID))
		if CAMGIRLSERVER >= 1500:
			CAMGIRLSERVER = CAMGIRLSERVER - 800
		elif CAMGIRLSERVER >= 900:
			CAMGIRLSERVER = CAMGIRLSERVER - 500
		if vs != 0:
			CAMGIRLSERVER = 0
	except KeyError:
		CAMGIRLSERVER=0

	truepvt = ((flags & 8) == 8)

	buf=usr+" =>"
	try:
		if truepvt == 1:
			buf+=" (TRUEPVT)"
		else:
			buf+=" ("+vs_str[vs]+")"
	except KeyError:
		pass
	printDBG ("%s  Video Server : %d Channel Id : %d  Model id : %d " %(buf, CAMGIRLSERVER, CAMGIRLCHANID, CAMGIRLUID))

def myfreecam_start(url):
	global CAMGIRL
	global CAMGIRLSERVER
	global CAMGIRLUID
	global CAMGIRLCHANID
	CAMGIRL= url
	CAMGIRLSERVER = 0
	libsPath = GetPluginDir('libs/')
	import sys
	sys.path.insert(1, libsPath)
	import websocket
	printDBG("Connecting to Chat Server...")
	try:
		xchat = [ 20, 22, 23, 24, 25, 26, 27, 28, 29,
				30, 31, 32, 33, 34, 35, 36, 39,
				40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 
				56, 57, 58, 59, 
				60, 61, 62, 63, 64, 65, 66, 67, 69,
				70, 71, 72, 73, 74, 75,
				90, 92, 93, 94
				]
		host = "ws://xchat"+str(random.choice(xchat))+".myfreecams.com:8080/fcsl"
		printDBG("Chat Server..."+host)
		ws = websocket.create_connection(host)
		ws.send("hello fcserver\n\0")
		ws.send("1 0 0 20071025 0 guest:guest\n\0")
	except:
		printDBG ("We're fucked ...")
		return ''
	rembuf=""
	quitting = 0
	try:
		while quitting == 0:
			sock_buf =  ws.recv()
			sock_buf=rembuf+sock_buf
			rembuf=""
			while True:
				hdr=re.search (r"(\w+) (\w+) (\w+) (\w+) (\w+)", sock_buf)
				if bool(hdr) == 0:
					break
				fc = hdr.group(1)
				mlen   = int(fc[0:4])
				fc_type = int(fc[4:])
				msg=sock_buf[4:4+mlen]
				if len(msg) < mlen:
					rembuf=''.join(sock_buf)
					break
				msg=urllib.unquote(msg)
				if fc_type == 1:
					ws.send("10 0 0 20 0 %s\n\0" % CAMGIRL)
				elif fc_type == 10:
					read_model_data(msg)
					quitting=1
				sock_buf=sock_buf[4+mlen:]
				if len(sock_buf) == 0:
					break
	except:
		printDBG ("WebSocket Error")
		return ''
	ws.close()
	if CAMGIRLSERVER != 0:
		Url="http://video"+str(CAMGIRLSERVER)+".myfreecams.com:1935/NxServer/ngrp:mfc_"+\
			str(CAMGIRLCHANID)+".f4v_mobile/playlist.m3u8" #better resolution
		#Url="http://video"+str(CAMGIRLSERVER)+".myfreecams.com:1935/NxServer/mfc_"+str(CAMGIRLCHANID)+".f4v_aac/playlist.m3u8" #320x240
		printDBG("Camgirl - "+CAMGIRL)
		printDBG("Url  - "+Url)
		return Url
	else:
		printDBG ("No video server ... _|_ ")

