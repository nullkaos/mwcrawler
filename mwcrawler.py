#!/usr/bin/python
# Copyright (C) 2012 Ricardo Dias
#
# Malware Crawler Module v0.4
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Requirements:
# - BeautifulSoup 3.0.8

from BeautifulSoup import BeautifulSoup as bs
import sys
import hashlib
import re
import urllib2
import magic
import os 
import socket
import datetime

# By default thug analyis is disabled
isthug	= False

# variable for date value manipulation
now		= datetime.datetime.now()
str(now)

# maximum wait time of http gets
timeout	= 15
socket.setdefaulttimeout(timeout)

# load thug function, also checks if thug is installed
def loadthug():
	try:
		sys.path.append('/opt/thug/src')
		import thug
		isthug = True
		print "- Thug module loaded for html analysis"
	except ImportError:
		print "- No Thug module found, html code inspection won't be available"

# determine file type for correct archival
def gettype(file):
	ms = magic.open(magic.MAGIC_NONE)
	ms.load()
	return ms.buffer(file)

# beautifulsoup parser
def parse(url):
	request = urllib2.Request(url)
	request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1)')
	try:
		http = bs(urllib2.urlopen(request))
	except:
		print "- Error parsing %s" % (url)
		return
	return http

def decisor(url):
	if not re.match('http',url):
		url = 'http://'+url

	try:
		url_dl = urllib2.urlopen(url).read()
	except Exception, e:
		#print "-- Error: %s" % e
		return

	filetype = gettype(url_dl).split(' ')[0]
	md5      = hashlib.md5(url_dl).hexdigest()

	if (filetype == 'HTML'):
		if isthug:
			print "-- Thug candidate: HTML code in %s" % url

			try:
				thug.Thug([url])()
			except Exception, e:
				print "- Thug error: %s" % e
				return

	else:
		dest = '/opt/malware/unsorted/'+filetype
		fpath = dest+'/'+str(md5)

		if not os.path.exists(dest):
			os.makedirs(dest)

		if not os.path.exists(fpath):
			file = open(fpath, 'wb')
			file.write(url_dl)
			file.close
			print "-- Saved file type %s with md5: %s" % (filetype,md5)

def malwaredl(soup):
	print "- Fetching from Malware Domain List"
	mdl=[]
	for row in soup('description'):
		mdl.append(row)
	del mdl[0]
	mdl_sites=[]
	for row in mdl:
		site = re.sub('&amp;','&',str(row).split()[1]).replace(',','')
		if site == '-':
			mdl_sites.append(re.sub('&amp;','&',str(row).split()[4]).replace(',',''))
		else:
			mdl_sites.append(site)
	print "-- Found %s urls" % len(mdl)
	for row in mdl_sites:
		decisor(row)

def vxvault(soup):
	print "- Fetching from VXVault"
	vxv=[]
	for row in soup('pre'):
		vxv = row.string.split('\r\n')
	del vxv[:4]
	del vxv[-1]
	print "-- Found %s urls" % len(vxv)
	for row in vxv:
		decisor(row)

def malc0de(soup):
	print "- Fetching from Malc0de"
	mlc=[]
	for row in soup('description'):
		mlc.append(row)
	del mlc[0]
	mlc_sites=[]
	for row in mlc:
		site = re.sub('&amp;','&',str(row).split()[1]).replace(',','')
		mlc_sites.append(site)
	print "-- Found %s urls" % len(mlc_sites)
	for row in mlc_sites:
		decisor(row)





if __name__ == "__main__":
	print "Malware Parser v0.4"

	try:
		if sys.argv[1] == '-t':
			loadthug()
	except:
		print "- Thug analysis not enabled (use -t to enable thug)"

	#source list

	malwaredl(parse('http://www.malwaredomainlist.com/hostslist/mdl.xml'))
	vxvault(parse('http://vxvault.siri-urz.net/URL_List.php'))
	malc0de(parse('http://malc0de.com/rss'))
	
