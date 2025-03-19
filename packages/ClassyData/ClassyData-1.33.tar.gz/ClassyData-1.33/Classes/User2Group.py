#!/usr/bin/env python3

'''
Created on 12/01/2015

@author: dedson
'''

import sqlalchemy
import sqlalchemy.orm

from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.engine import reflection
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import InstrumentedList, InstrumentedDict, InstrumentedSet

from .Base import Base

User2Group = Table(
   	'user2group',
	Base.metadata,
	Column('user_id', ForeignKey('user.id'), primary_key=True),
	Column('group_id', ForeignKey('group.id'), primary_key=True)
)
