#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import os, re, sys, argparse, json, datetime, xmltodict, inspect, importlib, uuid, logging

from Classes import *
from .Crown import Crown

import sqlalchemy
import sqlalchemy.orm

from Argumental.Argue import Argue
from Spanners.Squirrel import Squirrel
from Baubles.Logger import Logger

def quiet():
	for name in [
		'boto3.resources.action',
		'boto3.resources.factory',
		'botocore.auth',
		'botocore.client',
		'botocore.configprovider',
		'botocore.credentials',
		'botocore.endpoint',
		'botocore.hooks',
		'botocore.httpsession',
		'botocore.loaders',
		'botocore.parsers',
		'botocore.regions',
		'botocore.retryhandler',
		'botocore.utils',
		'sqlalchemy.engine.Engine',
		'sqlalchemy.engine.base.Engine',
		'sqlalchemy.orm.mapper.Mapper',
		'sqlalchemy.pool.NullPool',
		'sqlalchemy.pool.SingletonThreadPool',
		'sqlalchemy.pool.impl.NullPool',
		'sqlalchemy.pool.impl.QueuePool',
		'sqlalchemy.pool.impl.SingletonThreadPool',
		'urllib3.connectionpool',
	]:
		logging.getLogger(name).setLevel(logging.ERROR)

quiet()

args = Argue()
squirrel = Squirrel()
logger = Logger()

#____________________________________________________________
@args.command(single=True)
class Jester(object):
	'''
	Helper class for Classy types
	'''

	schemaURLs = dict(
		mysql= 'mysql+mysqlconnector://{username}:{password}@{hostname}/{database}',
		sqlite='sqlite:///{database}',
	)

	@args.property(short='v', flag=True, help='verbose logging')
	def verbose(self): return

	@args.property(short='s', choices=list(schemaURLs.keys()), help='database schema type', default='sqlite')
	def schema(self): return

	@args.property(short='m', flag=True, help='make new schema')
	def make(self): return

	@args.property(short='n', help='database host', default='localhost')
	def hostname(self): return

	@args.property(short='u', help='database username', default='root')
	def username(self): return

	@args.property(short='d', help='database name', default=':memory:')
	def database(self): return

	@args.property(short='p', help='database password')
	def password(self): return squirrel.get('%s:%s:%s'%(self.schema,self.hostname,self.username))

	#........................................................
	@logger.info
	def __init__(self, session=None, schema=None, username=None, password=None, hostname=None, database=None):
		self.verbose = False

		if schema: self.schema = schema
		if username: self.username = username
		if password: self.password = password
		if hostname: self.hostname = hostname
		if database: self.database = database

		if not session:
			keys=['username','password','hostname','database']
			schema = dict([(x,getattr(self,x)) for x in keys])
			url = self.schemaURLs[self.schema].format(**schema)

			crown = Crown(url, self.database, verbose=self.verbose)
			engine = crown.connect()
			self.session = crown.session()
		else:
			self.session = session

		self.now = datetime.datetime.now()
		self.dawnOfTime = datetime.datetime(1980,1,1,0,0,0,0)

		root = self.getOrCreateType(Package, name='/', parent=None)
		fundamentals = self.getOrCreateType(Package, name='Fundamentals', parent=root)

		exists = set()

		for name, tipe in inspect.getmembers(sys.modules['sqlalchemy.types']):
			if name[0] == '_': continue
			if not inspect.isclass(tipe): continue
			if len(tipe.__bases__) == 0: continue
			parent = tipe.__bases__[0]

			if parent.__name__[0] == '_' or parent.__name__ == 'object' : continue

			if parent.__name__ in exists: continue

			#print(parent.__name__, tipe)
			exists.add(parent.__name__)
			self.getOrCreateType(Class, name=parent.__name__, package=fundamentals)

		self.session.commit()

	def close(self):
		if self.session: self.session.close()

	def getOrCreateType(self, tipe, **kwargs):
		item = self.session.query(tipe).filter_by(**kwargs).first()
		if not item:
			item = tipe(**kwargs)
			self.session.add(item)
		return item

	def fundamentals(self):
		items = {}
		fundamentals = self.session.query(Package).filter_by(name='Fundamentals').first()
		for item in self.session.query(Class).filter_by(package=fundamentals).all():
			items[item.name] = item
		return items

#____________________________________________________________
if __name__ == '__main__': args.execute()

