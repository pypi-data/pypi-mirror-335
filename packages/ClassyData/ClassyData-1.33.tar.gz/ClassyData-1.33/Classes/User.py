#!/usr/bin/env python3

'''
Created on 12/01/2015

@author: dedson
'''

import os
import sqlalchemy
import sqlalchemy.orm

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.engine import reflection
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import InstrumentedList, InstrumentedDict, InstrumentedSet

from .Base import Base

from .Accessor import Accessor
from .User2Group import User2Group

from jsonweb.encode import to_object
from jsonweb.decode import from_object

from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

@from_object()
@to_object(suppress=['groups'])
class User(Accessor):
	'''
	A User class is an accessor sub class used to define a user access permission.
	'''

	__tablename__ = 'user'

	id         = Column(Integer, ForeignKey('accessor.id'), primary_key=True)
	name	   = Column(String(256))
	password   = Column(EncryptedType(sqlalchemy.Unicode,os.environ.get('ENCRYPTION_KEY','password'),AesEngine,'pkcs5'))
	groups     = relationship('Group', secondary='user2group', back_populates='users')

	__mapper_args__ = {
		'polymorphic_identity':'user'
	}

	def __init__(
		self,
		id=None,
		inherited='user',
		name=None,
		password=None,
		access_id=None,
		groups=[]
	):
		super(Accessor,self).__init__(
			id=id,
			inherited=inherited,
			access_id=access_id
		)
		self.name = name
		self.password = password
		self.groups = groups
		return

	def __dir__(self):
		return Accessor.__dir__(self) + [
			'name',
			'password',
			'groups',
		]

