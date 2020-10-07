'''
Created on Jan 5, 2010
@author: Robert Breit

Module with classes for parsing service check configurations and handling the service checks
'''

from xml.sax import handler 
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces
from xml.sax import SAXException

import urllib2
import httplib
import socket
import re


# testing_serv = open("../output/testing_efpServ.txt", "w")

class Service:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.link = ''
	self.external = 'false'

    def addConnect(self, url):
        self.connect = url
        
    def addIcon (self, filename):
        self.icon = filename
        
    def addLink (self, url):
        self.link = url
        
    def addExternal (self, webservice):
        testing_serv.write("webservice = %s\n"%(webservice))
	self.external = webservice
    
    def addNoResultRegex (self, pattern):
        self.resultPattern = pattern
        self.patterntype = 'negative'
        
    def addResultRegex (self, pattern):
        self.resultPattern = pattern
        self.patterntype = 'positive'

    def checkService(self, gene):
        # Get sample signals through webservice.
        link = self.connect[:]
        if(link == ''):
            return 'Yes';              # return Yes, if no url defined
        
        link = re.sub("GENE", gene, link)
 
        try:
            # timeout condition
	    timeout = 10
	    socket.setdefaulttimeout(timeout)
	    page = urllib2.urlopen(link)
            result = page.read()
            check = re.search(self.resultPattern, result) 
            if self.patterntype == 'negative':
                if check == None:
                    return 'Yes'        # result doesn't match pattern for NoResult
                else:
                    return None         # result matches pattern for NoResult
            else:
                if check == None:
                    return None         # result doesn't match pattern for Result
                else:
                    return 'Yes'        # result matches pattern for Result
        except (urllib2.HTTPError, urllib2.URLError, httplib.HTTPException):
            return 'error'

        return None
    
    def getExternal(self):
        return self.external
    
    def getLink(self, gene):
        link = self.link[:]
        link = re.sub("GENE", gene, link)
        return link

class ServiceHandler(handler.ContentHandler):
    def __init__(self, info):
        self.info = info
    
    def startElement(self, name, attrs):
        if name == 'service':
            self.currentService = Service(attrs.get('name'), attrs.get('type'))
        
        if name == 'connect':
            self.currentService.addConnect(attrs.get('url'))

        if name == 'icon':
            self.currentService.addIcon(attrs.get('filename'))

        if name == 'link':
            self.currentService.addLink(attrs.get('url'))

        if name == 'noresult_regex':
            self.currentService.addNoResultRegex(attrs.get('pattern'))

        if name == 'result_regex':
            self.currentService.addResultRegex(attrs.get('pattern'))
        
	if name == 'external':
            self.currentService.addExternal(attrs.get('webservice'))
        
 
    def endElement(self, name):
        if name == 'service':
            self.info.addService(self.currentService)
            
        
class Info:
    def __init__(self):
        self.services = {} # Dictionary of views
    
    def addService(self, service):
        self.services[service.name] = service
        
    def getService(self, name):
        return self.services[name]
        
    def getServices(self):
        allServices = []
	externalServices = []
	for name in self.services:
	    service = self.getService(name)
	    testing_serv.write("external for %s = %s\n"%(name, service.getExternal()))
 	    if service.getExternal() == 'true':
	       externalServices.append(name)
	    else:
	       allServices.append(name)
	testing_serv.write("before appending externalServices:\n")
	for serv in allServices:
	    testing_serv.write("%s\n"%serv)
	allServices.extend(externalServices)
	testing_serv.write("\nafter appending externalServices:\n")
	for serv in allServices:
	    testing_serv.write("%s\n"%serv)
        return allServices
    
        
    def load(self, file):
        # Create a parser
        parser = make_parser()
        parser.setFeature(feature_namespaces, 0)
        
        # Create the handler
        handler = ServiceHandler(self)
        parser.setContentHandler(handler)
        
        # Parse the file
        try:
            parser.parse(file)
        except (ValueError, SAXException):
            return 'error'
        
        return None
