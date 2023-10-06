#!/usr/bin/python
# -*- coding: utf-8 -*-

# api.py: REST API for lovd
#   - this module is just demonstrating how to handle basic CRUD
#   - GET operations are available for visitors, editing requires login

# Author: José Manuel Aroca

from flask import request, jsonify, g
from playhouse.shortcuts import dict_to_model, update_model_from_dict

from webutil import app, login_required, get_myself

import logging
import lovd

log = logging.getLogger("api.lovd")


@app.route('/api/lovd/querygenId/', methods = ['GET'])
def lovd_query():
    """Returns information of lovd for gen id."""

    input = request.args
    genName = input.get("genId")
    data = []
    
    lovd.get_lovd(genName,data)
    
    #return data
    #print(info)
    return jsonify(data), 200

@app.route('/api/lovd/querygenIdDNA/', methods = ['GET'])
def lovd_query_dna():
    """Returns information of lovd for gen id."""

    input = request.args
    genName = input.get("genId")
    dnaChange = input.get("dnaChange")
    data = []
    
    lovd.get_lovd_dna(genName,dnaChange,data)
    
    #return data
    #print(info)
    return jsonify(data), 200

@app.route('/api/lovd/', methods = ['DELETE'])
@login_required(role='editor')
def lovd_delete():
    """Delete  information of lovd from DB for  gen id."""
    #m = db.get_lovd(genId)
    #m.delete_instance()

    return jsonify({"reply":"lovd_delete"}), 200

