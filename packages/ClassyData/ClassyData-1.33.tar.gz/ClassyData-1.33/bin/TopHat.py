#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import os, re, sys, argparse, json, datetime, xmltodict, uuid, logging

import inspect

if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec

if os.path.dirname(sys.argv[0]) == '.':
	sys.path.append('..')

from Classes import *
from Handlers import Jester, args

from io import StringIO

import sqlalchemy
import sqlalchemy.orm

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.engine import reflection
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import InstrumentedList, InstrumentedDict, InstrumentedSet

from Baubles.Logger import Logger
from Perdy.pretty import prettyPrintLn, Style

from jsonweb.encode import dumper
from jsonweb.decode import loader

logger = Logger()

#____________________________________________________________
@args.command(single=True)
class TopHat(Jester):

	def __init__(self, schema=None, username=None, password=None, hostname=None, database=None):
		super().__init__(schema=schema, username=username, password=password, hostname=hostname, database=database)

	#........................................................
	@logger.info
	@args.operation
	@args.parameter(name='query', help='package:class')
	def query(self,query,output=sys.stdout):
		(pname,cname) = query.split(':')
		package = self._locatePackage(pname)
		clasz = self._locateClass(cname,package)
		return clasz

	#........................................................
	@logger.info
	@args.operation
	@args.parameter(name='id', help='id of class')
	def get(self, id):
		clasz = self._locatePackageClass(id, create=False)
		return clasz

	#........................................................
	@args.operation(name='packages')
	@args.parameter(name='query', help='name for children, *=root')
	def getPackages(self, query):
		if query == '*':
			parent = None
		else:
			parent = self._locatePackage(query)
		names = []
		for pkg in self.packages(parent):
			names.append(self.packageName(pkg))
		return names

	#........................................................
	@args.operation(name='classes')
	@args.parameter(name='query', help='package name')
	def getClasses(self, query):
		package = self._locatePackage(query)
		names = [x.name for x in self.classes(package)]
		return names

	#........................................................
	@args.operation(name='list')
	def getList(self):
		return self.names()

if __name__ == '__main__':
	result = args.execute()
	if result:
		if isinstance(result, Base):
			result = json.loads(dumper(result))
		prettyPrintLn(result, ignore=True)



