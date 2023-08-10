# !/usr/bin/env python

######################### 
# Author: gw700
# Date: 15.06.2023
#########################


# The script can be used to automatically download all the containers of a certain release of openstack or ceph.
# For the openstack part: it goes on github.com to check all the available containers and subcontainers for each service 
# defined under the "plugins" variable down below. Regarding to that it modifies the strings, so that it can download the 
# corresponding versions from quay.io.
# For the ceph part: as ceph doesn't provide release specific tags and also not a "latest" tag, it's more difficult to 
# find the right versions. Therefore the URLs are hardcoded here in the script and need to be manually adjusted by any change.

# Import all modules needed for the script

import argparse
import json
import sys
import tempfile
import subprocess
import os
import requests
from bs4 import BeautifulSoup
import array

##############################################OPENSTACK##############################################

# This is the url needed to check all the releases and container / subcontainer names of an existing service we want to use
url="https://opendev.org/openstack/kolla/src/branch/master/docker"

# This is needed for the arguments to call the script. Basically it can be used for Openstack and Ceph seperately.
# Valid argument values are: --platform openstack --service all, --platform openstack --service neutron,grafana
# --platform ceph --service all, --platform ceph --service grafana etc.
parser = argparse.ArgumentParser(description="Script to down- and upload docker containers")
parser.add_argument("--platform")
parser.add_argument("--service")

args = parser.parse_args()
platform_value = args.platform
service_value = args.service
single_plugins = []

# Those are the releases and container versions we want to get. release = current or future release we want to upgrade to.
# old_version = the release we want to go away from (currently installed)
# container_os can be ubuntu, centos, rocky, etc.
release = 'yoga'
old_version = 'xena'
container_os = 'ubuntu'
container_name = '-source-'

# Here it's defined what plugins we want to download for the openstack deployment. Just check github and add the needed ones
# local_repository can be adjusted due to the own local repository you want to point to.
plugins = ["ovn", "freezer", "cinder", "nova", "grafana", "neutron", "kolla-toolbox", "cron", "influxdb", "prometheus", "storm", "fluentd", "horizon", "heat", "hacluster", "openvswitch", "placement", "glance", "keystone", "rabbitmq", "memcached", "mariadb", "keepalived", "zookeeper", "haproxy"]
repourl_basic = "quay.io/openstack.kolla/"
repourl = repourl_basic+container_os+container_name
local_repository = "deploy:5000"
old_url = "/openstack/kolla/tree/master/docker/"
doubledot = ":"
slash = "/"

# Here we already do a first search and collect all the wanted css classes and names from github.
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
entries = soup.findAll('a', {"class": "muted"})

#####################################################################################################

################################################CEPH#################################################
# If you need to do upgrades, you can just replace the URLs here.
# The registry for Ceph can also be defined in here. It can be different to the one for openstack.
single_plugins_url = []
ceph="quay.io/ceph/ceph:v17"
cephgrafana="quay.io/ceph/ceph-grafana:8.3.5"
prometheus="quay.io/prometheus/prometheus:v2.33.4"
node_exporter="quay.io/prometheus/node-exporter:v1.3.1"
alertmanager="quay.io/prometheus/alertmanager:v0.23.0"
registry="registry:5000"

CEPHALL=(ceph, cephgrafana, prometheus, node_exporter, alertmanager)
CEPHALLSELECT=("ceph", "cephgrafana", "prometheus", "node_exporter", "alertmanager")
#####################################################################################################

# Here the ceph definition starts. It calls the dockercommands.sh shell script to execute the native docker commands on the os.
# Python didn't handle this so well.
def ceph_def():
	cmd1 = "rmi"
	cmd2 = "pull"
	cmd3 = "push"
	cmd4 = "tag"
	
	for cephsingle in CEPHALL:

		modified_string = cephsingle.replace('quay.io', registry)
		print(str(modified_string))
		output="./dockercommands.sh '%s' '%s'" % (str(cmd2), str(cephsingle))
		os.system(output)

		output="./dockercommands.sh '%s' '%s' '%s'" % (str(cmd4), str(cephsingle), str(modified_string))
		os.system(output)

		output="./dockercommands.sh '%s' '%s'" % (str(cmd3), str(modified_string))
		os.system(output)

		output="./dockercommands.sh '%s' '%s'" % (str(cmd1), str(cephsingle))
		os.system(output)

# This is the openstack definition.
def openstack_def():

	# We go through all the defined plugins to download them.
	for i in plugins:
		url="https://opendev.org/openstack/kolla/src/branch/master/docker/"
		url = url+i
		response = requests.get(url)
		soup = BeautifulSoup(response.text, 'html.parser')
		entries = soup.findAll('a', {"class": "muted"})
		
		# For each plugin we go through all the entries provided from BeautifulSoup, from our webscrapting of github.
		for entry in entries:
			title = entry.get('title')
			try:
				if title is not None and i in title:
					deeper_link = url+title

					if ".sh" not  in deeper_link or "Dockerfile" not in deeper_link or "grafana_sudoers" not in deeper_link or ".yml" not in deeper_link or ".yaml" not in deeper_link:
						deeper_link = url
						str(deeper_link)
						url = "https://opendev.org/openstack/kolla/src/branch/master/docker/"
						url = url+i
					   
					    # The URLs are sticked, converted and merged together for the corresponding usage.
						converted = deeper_link.replace(url, repourl+title)
						converted_local = converted.replace('quay.io', local_repository)
						converted = converted+doubledot+release
						converted_local = converted_local+doubledot+release
						
						# Those are just the native docker commands declared as variables to execute it via shell.
						cmd1 = "rmi"
						cmd2 = "pull"
						cmd3 = "push"
						cmd4 = "tag"
						arg1 = converted
						arg2 = converted_local

						##########
						# The commands below always execute the shell script with arguments.
						#Delete the image
						output="./dockercommands.sh '%s' '%s'" % (str(cmd1), str(arg1))
						output2="./dockercommands.sh '%s' '%s'" % (str(cmd1), str(arg2))
						os.system(output)
						os.system(output2)

						#Download the image
						output="./dockercommands.sh '%s' '%s'" % (str(cmd2), str(arg1))
						os.system(output)

						#Tag the image
						output="./dockercommands.sh '%s' '%s' '%s'" % (str(cmd4), str(arg1), str(arg2))
						os.system(output)

						#Push the image
						output="./dockercommands.sh '%s' '%s'" % (str(cmd3), str(arg2))
						os.system(output)
						
						#Delete downloaded one
						output="./dockercommands.sh '%s' '%s'" % (str(cmd1), str(arg1))
						os.system(output)
						
						#Delete old release if it's a major upgrade
						if release != old_release:
							converted_local_oldrelease = converted_local.replace(release, old_release)
							arg3 = converted_local_oldrelease
							output="./dockercommands.sh '%s' '%s'" % (str(cmd1), str(arg3))
							os.system(output)

			except:
				print('')

# We check if the script has been called with arguments or not. If the script has been run with: python3 script.py --platform openstack
# then, this is going to be executed.
if "openstack" in platform_value:
	# if the script is called with --platform openstack --service all ... it just executes the whole openstack definition with all its plugins.
	if "all" in service_value:
		openstack_def()

# if we want to download specific services for openstack, then this part will be executed instead of the above one.
	if "all" not in service_value:
		# This for loop goes just through the defined services with --service [service1 service2]
		for allarguments in plugins:
			if allarguments in service_value:
				single_plugins.append(allarguments)
		plugins = single_plugins
		for entry in plugins:
			openstack_def()

# If the script has been called with --platform ceph ... this part will be executed.			
if "ceph" in platform_value:
	# If we want everything from ceph to be updates, this will be executed.
	if "all" in service_value:
		ceph_def()
	
	# if we provided specific services such as --platform ceph --service grafana ... then just grafana will be updated.
	if "all" not in service_value:
		for allarguments in CEPHALLSELECT:
			if allarguments in service_value:
				single_plugins.append(allarguments)
		
		CEPHALLSELECT = single_plugins
		for allentries in CEPHALLSELECT:
			search_term = allentries
			found = False
			for matchingitem in CEPHALL:
				if search_term in matchingitem:
					found = True
					result = matchingitem
					break
					
			if found:
				single_plugins_url.append(result)
				
			else:
				print("Search term not found")		
			
		CEPHALL = single_plugins_url
		ceph_def()

