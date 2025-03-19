#!/usr/bin/env python3

'''
Created on 12/01/2015

@author: dedson
'''

import sqlalchemy
import sqlalchemy.orm

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.engine import reflection
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import InstrumentedList, InstrumentedDict, InstrumentedSet

from .Base import Base

from jsonweb.encode import to_object
from jsonweb.decode import from_object

from .Class import Class
from .Access import Access
from .Constant import Constant

@from_object()
@to_object(suppress=['parent','package'])
class Enum(Class):
	'''
	An Enum class stores an enumeration in a comma seperated values list. Helper methods exist to add/list enum values.
	'''

	__tablename__ = 'enum'

	id			= Column(Integer, ForeignKey('class.id'), primary_key=True)
	constants	= relationship("Constant", uselist=True, foreign_keys=[Constant.enum_id])

	__mapper_args__ = {
		'polymorphic_identity' : 'enum',
	}

	def __init__(
		self,
		id=None,
		guid=None,
		inherited='enum',
		version=None,
		fromDate=None,
		toDate=None,
		modified=None,
		display=None,
		robes=None,
		description=None,
		isLabel=None,
		path=None,
		modifiers=None,
		package=None,
		name=None,
		abstract=False,
		constants=[]
	):
		super(Enum,self).__init__(
			id=id,
			guid=guid,
			inherited=inherited,
			version=version,
			fromDate=fromDate,
			toDate=toDate,
			modified=modified,
			display=display,
			robes=robes,
			description=description,
			isLabel=isLabel,
			path=path,
			modifiers=modifiers,
			package=package,
			name=name,
			abstract=abstract
		)
		self.id = id
		self.constants = constants
		return

	def __dir__(self):
		''' don't export class attributes, skip over to Accessor ones '''
		return Class.__dir__(self) + [
			'constants',
		]
