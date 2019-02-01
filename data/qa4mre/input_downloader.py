 #!/usr/bin/python

# (C) Copyright 2013 Philip Arthur, NAIST
# 
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Lesser General Public License
# (LGPL) version 2.1 which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/lgpl-2.1.html
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.

import urllib2
import os
import sys

from configuration import input as input

def download(name, url, force):
	try:
		if not os.path.exists('input'):
			os.makedirs('input')
		file_path =  "input/" + name + ".txt"
		if force or not os.path.exists(file_path):
			print "Downloading ", name,
			response = urllib2.urlopen(url)
			 
			#open the file for writing
			fh = open(file_path, "w")
			 
			# read from request while writing to file
			fh.write(response.read())
			fh.close()
			print ""
	except Exception:
		print "\nCannot Download file in url:", url, " system is now exiting..."
		return False

	return True


def download_all_files(force = False):
	for name, url in input.iteritems():
		if not download(name, url, force):
			break;
	else:
		sys.exit(1)

if __name__ == "__main__":
	download_all_files(True)