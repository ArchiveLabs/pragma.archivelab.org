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
from api.pragmas import save, WaybackSnapshot, OpenAnnotation
from configs import WAYBACK_SERVER


class OpenAnnotations(MethodView):
    @rest
    def get(self, oaid=None):
        if oaid:
            return OpenAnnotation.get(oaid).dict()
        return {"annotations": [oa.dict() for oa in OpenAnnotation.query.all()]}

    @rest
    def post(self):
        annotation = request.json
        oa = OpenAnnotation(annotation=annotation)
        return annotation


class WaybackAnnotations(MethodView):
    @rest
    def get(self):
        return {"pragmas": [p.dict() for p in WaybackSnapshot.query.all()]}

    @rest
    def post(self):
        url = request.json.get('url', '')
        annotation = request.json.get('annotation', '')
        wayback = save(url)
        wayback_url = '%s%s' % (WAYBACK_SERVER, wayback['id'])

        if annotation:
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
            oa = OpenAnnotation(annotation=annotation)
            oa.create()
        p = WaybackSnapshot(domain=wayback['domain'],
                   protocol=wayback['protocol'],
                   path=wayback['path'],
                   wayback_id=wayback['id'])
        if annotation:
            p.annotation_id = oa.id
        p.create()
        return p.dict()


class WaybackAnnotation(MethodView):
    @rest
    def get(self, pid):
        return WaybackSnapshot.get(pid).dict()


class Favicon(MethodView):
    def get(self):
        return ''

urls = (
    '/favicon.ico', Favicon,
    '/annotations/<oaid>', OpenAnnotations,
    '/annotations', OpenAnnotations,
    '/<pid>', WaybackAnnotation,
    '/', WaybackAnnotations
)
