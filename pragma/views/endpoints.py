#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    endpoints.py
    ~~~~~~~~~~~~

    :copyright: (c) 2015 by Mek.
    :license: see LICENSE for more details.
"""

from flask import render_template, request
from flask.views import MethodView
from views import rest, paginate
from datetime import datetime
from api.pragmas import save, Pragma
from configs import WAYBACK_SERVER


class Annotations(MethodView):
    @rest
    def get(self):
        return {"pragmas": [p.dict() for p in Pragma.query.all()]}

    @rest
    def post(self):
        url = request.json.get('url', '')
        annotation = request.json.get('annotation', '')        
        wayback = save(url)
        wayback_url = '%s%s' % (WAYBACK_SERVER, wayback['id'])
        if not annotation:
            raise Exception("Page archived as %s but no annotation detected" \
                            % wayback_url)
        annotation['hasTarget']= {
            'hasSource': {
                '@id': wayback_url,
                'originalUrl': '%s://%s%s' % (
                    wayback['protocol'],
                    wayback['domain'],
                    wayback['path']
                )
            }
        }
        annotation['annotatedAt'] = datetime.utcnow().ctime()
        p = Pragma(domain=wayback['domain'],
                   protocol=wayback['protocol'],
                   path=wayback['path'],
                   wayback_id=wayback['id'],
                   annotation=annotation)
        p.create()
        return p.dict()


class Annotation(MethodView):
    @rest
    def get(self, pid):
        return Pragma.get(pid).dict()


class Favicon(MethodView):
    def get(self):
        return ''

urls = (
    '/favicon.ico', Favicon,
    '/<pid>', Annotation,
    '/', Annotations
)
