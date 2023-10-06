#!/usr/bin/python
# -*- coding: utf-8 -*-

# api.py: REST API for brca
#   - this module is just demonstrating how to handle basic CRUD
#   - GET operations are available for visitors, editing requires login

# Author: José Manuel Aroca

from flask import request, jsonify, g
from playhouse.shortcuts import dict_to_model, update_model_from_dict

from webutil import app, login_required, get_myself

import logging
import brca
log = logging.getLogger("api.brca")


@app.route('/api/brca/genid/', methods = ['GET'])
def brca_query():
    """Returns information of brca for gen id."""

    input = request.args
    genName = input.get("genId")
    data = []
    
    brca.get_brca(genName,data)
    
    #return data
    #print(info)
    return jsonify(data), 200
@app.route('/api/brca/genidPlus/', methods = ['GET'])
def brca_query_plus():
    """Returns information of brca for gen id."""

    input = request.args
    genName = input.get("genId")
    data = []
    
    brca.get_brca(genName,data)
    
    #return data
    #print(info)
    return jsonify(data), 200

@app.route('/api/brca/', methods = ['DELETE'])
@login_required(role='editor')
def brca_delete():
    """Delete  information of brca from DB for  gen id."""
    #m = db.get_brca(genId)
    #m.delete_instance()

    return jsonify({"reply":"brca_delete"}), 200

