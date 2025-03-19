#!/usr/bin/env python3

'''
Created on 11/02/2025

@author: dedson
'''


import sqlalchemy
import sqlalchemy.orm

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.engine import reflection
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import InstrumentedList, InstrumentedDict, InstrumentedSet

from .Base import Base

from jsonweb.encode import to_object
from jsonweb.decode import from_object

@from_object()
@to_object()
class Constant(Base):
	'''
	a single value for an enumeration
	'''

	__tablename__ = 'constant'

	id			 = Column(Integer, primary_key=True)
	enum_id	     = Column(Integer, ForeignKey('enum.id'))
	name		 = Column(String(256))

	def __init__(
		self,
		id=None,
   		enum_id=None,
		name=None
	):
		self.id = id
		self.enum_id = enum_id
		self.name=name
		return

	def __dir__(self):
		return [
			'id',
			'name',
			'enum_id'
		]

