#!/usr/bin/python
# -*- coding: utf-8 -*-

# api.py: REST API for hgmd
#   - this module is just demonstrating how to handle basic CRUD
#   - GET operations are available for visitors, editing requires login

# Author: José Manuel Aroca

from flask import request, jsonify, g
from playhouse.shortcuts import dict_to_model, update_model_from_dict

import db
import util
from webutil import app, login_required, get_myself

import logging
import hgmd
log = logging.getLogger("api.hgmd")


@app.route('/api/hgmd/', methods = ['GET'])
def hgmd_query():
    """Returns information of hgmd for gen id."""

    input = request.args
    genName = input.get("genId")
    info = []
    #Query hgmd db
    hgmd.get_hgmd(genName,info)
    #return data
    print(info)
    return jsonify(info), 200


@app.route('/api/hgmd/', methods = ['DELETE'])
@login_required(role='editor')
def hgmd_delete():
    """Delete  information of hgmd from DB for  gen id."""
    #m = db.get_hgmd(genId)
    #m.delete_instance()

    return jsonify({"reply":"hgmd_delete"}), 200

