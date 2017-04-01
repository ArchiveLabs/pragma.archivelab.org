#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    endpoints.py
    ~~~~~~~~~~~~

    :copyright: (c) 2015 by Mek.
    :license: see LICENSE for more details.
"""

from flask import render_template, request, jsonify
from flask.views import MethodView
import json

from views import rest, paginate
from datetime import datetime
from api.pragmas import db, save, WaybackSnapshot, OpenAnnotation
from configs import WAYBACK_SERVER


class OpenAnnotations(MethodView):
    @rest
    def get(self, oaid=None):
        canvas_id = request.args.get('canvas_id', None)
        if canvas_id:
            return {
                "annotations": [annotation.dict() for annotation in 
                                db.query(OpenAnnotation)\
                                .filter(OpenAnnotation.canvas_id == canvas_id).all()]
            }
        if oaid:
            return OpenAnnotation.get(oaid).dict()
        return {"annotations": [oa.dict() for oa in OpenAnnotation.query.all()]}

    @rest
    def post(self):
        annotation = request.json
        canvas_id = annotation['on']['full'] if 'on' in annotation else None
        oa = OpenAnnotation(annotation=annotation, canvas_id=canvas_id)
        oa.create()
        oa.annotation['@id'] = oa.id
        oa.save()
        return oa.dict()


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
