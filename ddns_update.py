#!/usr/bin/python
# coding: UTF-8

import ConfigParser
import syslog
import sys
from random import randint
import urllib
import re
import os
import datetime
import imp

# configファイルパス
config_path = '/etc/ddns.cfg'

# syslog関連リネーム
slog = syslog.syslog
LOG = {'EMERG' : syslog.LOG_EMERG,
		'ALERT'   : syslog.LOG_ALERT,
		'CRIT'    : syslog.LOG_CRIT,
		'ERR'     : syslog.LOG_ERR,
		'WARNING' : syslog.LOG_WARNING,
		'NOTICE'  : syslog.LOG_NOTICE,
		'INFO'    : syslog.LOG_INFO,
		'DEBUG'   : syslog.LOG_DEBUG}

############################################################
def __exit__():
	slog(LOG['DEBUG'], "exit")
	syslog.closelog()

############################################################
def __init__():
	# syslogを初期化
	syslog.openlog('ddns_update', syslog.LOG_PID, syslog.LOG_USER)
	slog(LOG['NOTICE'], "DDNS Checker")
	# コンフィグファイル読み込みエラー時の処理
	if not loadconfig():
		slog(LOG['ERR'], "don't load config.")
		exit(-1)
	# プラグインロード
	load_plugins()

############################################################
def loadconfig():
	config = ConfigParser.RawConfigParser()
	try:
		config.read(config_path)
		# syslogマスク設定
		loglevel = config.get('Global', 'LogLevel')
		syslog.setlogmask(syslog.LOG_UPTO(LOG[loglevel]))
		slog(LOG['DEBUG'], "LogLevel: " + loglevel)
		# その他設定の読み込み
		global interval, cache, plugindir
		interval = 24
		cache = '/var/cache/ddns'
		plugindir = os.path.join(os.getcwd(), 'plugin')
		interval = config.getint('Global', 'UpdateInterval')
		cache = os.path.normpath(config.get('Global', 'CacheDir'))
		pdir = config.get('Global', 'PluginDir')
		if "/" == pdir[0]:
			plugindir = os.path.normpath(pdir)
		else:
			plugindir = os.path.normpath(os.path.join(os.getcwd(), pdir))
		slog(LOG['DEBUG'], "UpdateInterval: " + str(interval))
		slog(LOG['DEBUG'], "CacheDir: " + cache)
		slog(LOG['DEBUG'], "PluginDir: " + plugindir)
		if not os.path.exists(cache):
			os.makedirs(cache)
		# IPアドレスチェックサービスリストの読み込み
		servers = config.items('IPAddrChecker')
		global ip_checker
		ip_checker = []
		for key,url in servers:
			ip_checker.append(url)
			slog(LOG['DEBUG'], "IPChecker: " + url)
	except ConfigParser.MissingSectionHeaderError:
		slog(LOG['WARNING'], "MissingSectionHeader")
		return False
	except ConfigParser.NoSectionError:
		slog(LOG['WARNING'], "NoSectionError")
		return False
	except ConfigParser.NoOptionError:
		slog(LOG['WARNING'], "NoOptionError")
		return False
	except:
		slog(LOG['ERR'], "Unexpected error: " + str(sys.exc_info()[:2]))
		return False
	return True

############################################################
def load_module(module_name, basepath):
	f,n,d = imp.find_module(module_name, [basepath])
	return imp.load_module(module_name, f, n, d)

############################################################
def load_plugins():
	plugin_list = []
	config = ConfigParser.RawConfigParser()
	try:
		config.read(config_path)
	except:
		return []
	for fdn in os.listdir(plugindir):
		try:
			if fdn.startswith(".") or fdn.endswith(".pyc"):
				continue
			elif fdn.endswith(".py"):
				m = load_module(fdn.replace(".py",""), plugindir)
				plugin_list.append(m)
			elif os.path.isdir(fdn):
				m = load_module(fdn)
				plugin_list.append(m)
			slog(LOG['INFO'], "Load Plugins: " + m.get_name())
			plugin_cfg = config.items(m.get_name())
			id = ""
			pw = ""
			opt = ""
			for key,value in plugin_cfg:
				if "id" == key:
					id = value
				elif "pw" == key:
					pw = value
				elif "option" == key:
					opt = value
			m.conf(id, pw, opt)
		except ImportError:
			slog(LOG['ERR'], "Load Plugin error: " + fdn)
			pass
	global plugins
	plugins = plugin_list

############################################################
def ipaddr_check():
	slog(LOG['DEBUG'], "IP Address Checker")
	# 最低更新間隔チェック
	update_check = os.path.join(cache, "upcheck")
	if os.path.exists(update_check):
		cf = open(update_check, "r")
		latest = datetime.datetime.strptime(cf.read(), "%Y%m%d%H%M%S")
		latest2 = latest + datetime.timedelta(0,0,0,0,2)
		if datetime.datetime.now() < latest2:
			slog(LOG['NOTICE'], "Time interval is too short.")
			return False
	 	cf = open(update_check, "w")
		cf.write(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
		cf.close()
	else:
	 	cf = open(update_check, "w")
		cf.write(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
		cf.close()
	r = randint(0, len(ip_checker) - 1)
	slog(LOG['INFO'], "IPAddr from : " + ip_checker[r])
	wget = urllib.FancyURLopener({})
	f = wget.open(ip_checker[r])
	gettxt = f.read()
	m = re.search("(?:\D|^)(\d|[01]?\d\d|2[0-4]\d|25[0-5])\.(\d|[01]?\d\d|2[0-4]\d|25[0-5])\.(\d|[01]?\d\d|2[0-4]\d|25[0-5])\.(\d|[01]?\d\d|2[0-4]\d|25[0-5])(?:\D|$)", gettxt)
	if None == m:
		print gettxt
		return False
	addr = m.group(1) + "." + m.group(2) + "." + m.group(3) + "." + m.group(4)
	slog(LOG['INFO'], "GetIPAddr: " + addr)
	addr_cache = os.path.join(cache, "ip")
	addr_old = "0.0.0.0"
	global new_addr
	new_addr = ""
	if os.path.exists(addr_cache):
		cf = open(addr_cache, "r")
		addr_old = cf.read()
		cf.close()
	if addr_old != addr:
		slog(LOG['NOTICE'], "Update IP Address [" + addr_old + " => " + addr + "]")
		new_addr = addr
		return True
	# 定期更新間隔チェック
	interval_check = os.path.join(cache, "lastupdate")
	if os.path.exists(interval_check):
		cf = open(interval_check, "r")
		latest = datetime.datetime.strptime(cf.read(), "%Y%m%d%H%M%S")
		latest2 = latest + datetime.timedelta(0,0,0,0,0,interval)
		cf.close()
		if datetime.datetime.now() > latest2:
			return True
	else:
		return True
	return False

############################################################
def ddns_update():
	status = True
	slog(LOG['DEBUG'], "DDNS Update.")
	print "New Address :: " + new_addr
	for p in plugins:
		try:
			slog(LOG['NOTICE'], "DDNS Access: " + p.get_name())
			p.ddns_update()
			slog(LOG['DEBUG'], "DDNS Updated: " + p.get_name())
		except:
			slog(LOG['ERR'], "DDNS Update error: " + str(sys.exc_info()[:2]))
			status = False
			pass
	if status:
		addr_cache = os.path.join(cache, "ip")
		interval_check = os.path.join(cache, "lastupdate")
		cf = open(addr_cache, "w")
		cf.write(new_addr)
		cf.close()
		cf = open(interval_check, "w")
		cf.write(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
		cf.close()
	return status

############################################################
__init__()
if ipaddr_check():
	ddns_update()
else:
	print "Don't update."

syslog.closelog()
