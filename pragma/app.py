#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    app.py
    ~~~~~~

    :copyright: (c) 2015 by Mek.
    :license: see LICENSE for more details.
"""

from flask import Flask
from flask_cors import CORS
from flask_routing import router
from views import endpoints
from configs import options, cors


urls = ('', endpoints)
app = router(Flask(__name__, static_folder=None, static_url_path='https://web.archive.org/static'), urls)
cors = CORS(app) if cors else None


if __name__ == "__main__":
    app.run(**options)
