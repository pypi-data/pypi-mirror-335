#!/usr/bin/env python3

'''
Created on 12/01/2015

@author: dedson
'''

import sqlalchemy
import sqlalchemy.orm

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.engine import reflection
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import InstrumentedList, InstrumentedDict, InstrumentedSet

from .Base import Base

from .Access import Access
from .Class import Class

from jsonweb.encode import to_object
from jsonweb.decode import from_object

@from_object()
@to_object(suppress=['parent'])
class Package(Access):
	'''
	The Package class defines a list of classes in a namespace or package.
	'''

	__tablename__ = 'package'
	id			= Column(Integer, ForeignKey('access.id'), primary_key=True)
	name		  = Column(String(256))
	url		   = Column(String(256))
	parent_id	 = Column(Integer,ForeignKey('package.id'))
	parent		= relationship("Package", uselist=False, foreign_keys=[parent_id], remote_side=[id])

	__mapper_args__ = {
		'polymorphic_identity' : 'package'
	}

	def __init__(
		self,
		id=None,
		guid=None,
		inherited='package',
		version=None,
		fromDate=None,
		toDate=None,
		modified=None,
		display=None,
		description=None,
		isLabel=None,
		path=None,
		modifiers=None,
		name=None,
		url=None,
		parent=None,
		parent_id=None
	):
		super(Package,self).__init__(
			id=id,
			guid=guid,
			inherited=inherited,
			version=version,
			fromDate=fromDate,
			toDate=toDate,
			modified=modified,
			display=display,
			description=description,
			isLabel=isLabel,
			path=path,
			modifiers=modifiers
		)
		self.name = name
		self.url = url
		if parent: self.parent = parent
		self.parent_id = parent_id
		self
		return

	def __dir__(self):
		return Access.__dir__(self) + [
			'name',
			'url',
			'parent_id',
			'parent'
		]

	def fullname(self):
		name = self.name
		parent = self.parent
		while parent:
			if parent.name and parent.name == '/':
				name = f'/{name}'
			else:
				name = f'{parent.name}/{name}'
			parent = parent.parent
		return name


