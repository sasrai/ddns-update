# coding: utf-8

import sys
import urllib

plugin_name = "ddo.jp"

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
		wget = urllib.FancyURLopener({})
		url = "http://free.ddo.jp/dnsupdate.php?dn=%s&pw=%s" % (id, password)
		f = wget.open("http://free.ddo.jp/dnsupdate.php?dn=%s&pw=%s" % (id, password))
#		f = urllib.urlopen(url)
		gettxt = f.read()
		f.close()
	except:
		return False
	return True
