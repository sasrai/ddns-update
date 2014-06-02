# coding: utf-8

import urllib

plugin_name = "dip.jp"

############################################################
def get_name():
	return plugin_name

############################################################
def conf(i, p, o):
	global id, password, other
	id = i
	password = p
	other = o
	return True

############################################################
def ddns_update():
	try:
		url = 'http://ieserver.net/cgi-bin/dip.cgi'
		params = urllib.urlencode({'username':id, 'password':password, 'domain':"dip.jp", 'updatehost':u"実行".encode('euc-jp')})
		f = urllib.urlopen(url, params)
		gettxt = f.read()
		f.close()
	except:
		return False
	return True
