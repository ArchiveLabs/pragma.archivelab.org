#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    endpoints.py
    ~~~~~~~~~~~~

    :copyright: (c) 2015 by Mek.
    :license: see LICENSE for more details.
"""

from flask import render_template, request, jsonify, redirect, Response
from flask.views import MethodView
import requests
import json
import time
from sqlalchemy.orm.attributes import flag_modified
from views import rest, paginate
from datetime import datetime
from api.pragmas import db, save, WaybackSnapshot, OpenAnnotation

from configs import WAYBACK_SERVER

## XXX Todo: Edit / update (js) the annotations w/ crosslinks

class OpenAnnotations(MethodView):
    @rest
    def get(self, oaid=None):
        canvas_id = request.args.get('canvas_id', None)
        ocaid = request.args.get('ocaid', None)
        crosslinks = request.args.get('crosslinks', None)
        if ocaid:
            q = db.query(OpenAnnotation)\
                  .filter(OpenAnnotation.canvas_id.like(
                      '%://iiif.archivelab.org/iiif/' + ocaid + '$%/canvas'))
            if crosslinks:
                q = q.filter(OpenAnnotation.is_crosslink == True)
            return {
                "annotations": [annotation.dict() for annotation in q.all()]
            }

        if oaid:
            annotation = OpenAnnotation.get(oaid)
            return annotation.dict()

        results = []
        q = db.query(OpenAnnotation)
        if crosslinks:
            q = q.filter(OpenAnnotation.is_crosslink == True)
        if canvas_id:
            q = q.filter(OpenAnnotation.canvas_id == canvas_id)

        annotations = q.all()

        for i, _ in enumerate(annotations):
            annotations[i].annotation['@id'] = '%s/%s' % (request.base_url, annotations[i].id)
            results.append(annotations[i].dict())
        return {"annotations": results}

    @rest
    def post(self):
        annotation = request.json
        canvas_id = annotation['on']['full'] if 'on' in annotation else None

        try:
            _id = int(annotation['@id'].split('/')[-1])
            oa = OpenAnnotation.get(_id)
        except (KeyError, ValueError):
            annotation.pop('@id', None)
            oa = OpenAnnotation(annotation=annotation, canvas_id=canvas_id)
            oa.create()
        annotation['@id'] = '%s/%s' % (request.base_url, oa.id)
        oa.annotation = annotation
        oa.save()
        return oa.dict()


class WaybackPlayback(MethodView):

    @staticmethod
    def cite(css_id):
        return """
        <script type="text/javascript">
          var id = "%s";
          var e = document.getElementById(id)
          e.style.backgroundColor="yellow";
          e.scrollIntoView();
        </script>
        """ % (css_id)

    def get(self, pid):
        wbs = WaybackSnapshot.get(pid)
        url = 'https://web-beta.archive.org%s#wbaid-%s' % (wbs.wayback_id, pid)
        return redirect(url)

        #r = requests.get('https://web.archive.org%s' % wbs.wayback_id)
        #snapshot = r.content
        #if wbs.annotation_id:
        #    css_id = wbs.annotation.dict().get('annotation').get('id')
        #    snapshot = snapshot.decode('utf-8').strip().replace('</body>', self.cite(css_id) + "</body>")
        #return snapshot

class WaybackResource(MethodView):

    def get(self, resource=None):
        response = requests.get('https://web.archive.org/%s' % resource)
        return Response(response.content, mimetype=response.headers['content-type'])

class WaybackAnnotations(MethodView):

    def get(self, pid=None):
        if pid:
            return jsonify(WaybackSnapshot.get(pid).dict())
        return render_template('spn.html')

    def post(self):
        annotation = ''
        redir = False
        if request.json:
            url = request.json.get('url', '')
            annotation = request.json.get('annotation', '')
        elif request.form:
            url = request.form.get('url', '')
            if request.form.get('annotation'):
                annotation = {"id": "%s" % request.form.get('annotation', '')}
            redir = request.form.get('redirect', False)

        if not url:
            return jsonify({'error': 'url required'})

        wayback = save(url)
        if 'error' in wayback:
            return jsonify(wayback)

        wayback_url = '%s%s' % (WAYBACK_SERVER, wayback['id'])

        if annotation:
            annotation['hasTarget'] = {
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

        response = p.dict()
        if redir:
            time.sleep(10)
            return redirect('/playback/%s' % response['id'])

        return jsonify(response)


class WaybackAnnotation(MethodView):
    @rest
    def get(self, pid=None):
        wbs = WaybackSnapshot.get(pid)
        wbsd = wbs.dict()
        wbsd['annotation'] = wbs.annotation.dict() if wbs.annotation else None
        return wbsd


class Favicon(MethodView):
    def get(self):
        return ''

urls = (
    '/favicon.ico', Favicon,
    '/annotations/<oaid>', OpenAnnotations,
    '/annotations', OpenAnnotations,
    '/playback/<pid>', WaybackPlayback,
    '/wayback-annotations/<pid>', WaybackAnnotation,
    '/create-wayback-citation', WaybackAnnotations,
    '/<path:resource>', WaybackResource,
    '/', WaybackAnnotations
)
