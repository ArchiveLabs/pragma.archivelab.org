#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    api/pragma.py
    ~~~~~~~~~~~~~
    Pragma API

    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""

from random import randint
from datetime import datetime
import requests
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Column, Unicode, BigInteger, Integer, \
    Unicode, DateTime, ForeignKey, Table, exists, func
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.orm import relationship
from api import db, engine, core


class OpenAnnotation(core.Base):

    __tablename__ = "annotations"

    id = Column(BigInteger, primary_key=True)
    canvas_id = Column(Unicode, nullable=True)
    annotation = Column(JSON, nullable=False)


class WaybackSnapshot(core.Base):

    __tablename__ = "wayback_snapshots"

    id = Column(BigInteger, primary_key=True)
    annotation_id = Column(BigInteger, ForeignKey('annotations.id'), nullable=True)
    wayback_id = Column(Unicode, nullable=False)
    domain = Column(Unicode, nullable=False)
    path = Column(Unicode, nullable=False)
    protocol = Column(Unicode, nullable=False)

    annotation = relationship('OpenAnnotation', backref='wayback_snapshots')


def save(url):
    r = requests.get('http://web.archive.org/save/%s' % url)
    if 'x-archive-wayback-liveweb-error' in r.headers:
        raise core.HTTPException(r.headers['x-archive-wayback-liveweb-error'],
                                 r.status_code)
    protocol = 'https' if 'https://' in r.headers['content-location'] else 'http'
    uri = r.headers['content-location'].split("://")[1]
    path = uri[uri.index('/'):] if uri.index('/') is not None else '/';
    return {
        'date': r.headers['date'],
        'protocol': protocol,
        'domain': uri.split('/')[0],
        'path': path,
        'id': r.headers['content-location']
    }
