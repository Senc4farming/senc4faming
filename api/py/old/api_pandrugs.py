#!/usr/bin/python
# -*- coding: utf-8 -*-

# api.py: REST API for pandrugs
#   - this module is just demonstrating how to handle basic CRUD
#   - GET operations are available for visitors, editing requires login

# Author: José Manuel Aroca

from flask import request, jsonify, g
from playhouse.shortcuts import dict_to_model, update_model_from_dict

from webutil import app, login_required, get_myself

import logging
import pandrugs

log = logging.getLogger("api.pandrugs")


@app.route('/api/pandrugs/geneInteraction/', methods = ['GET'])
def pandrugs_geneInteraction():
    """Returns information of pandrugs for gen id."""

    input = request.args
    genName = input.get("genId")
    data = []
    
    pandrugs.get_pandrugs_geneInteraction(genName,data)
    
    #return data
    #print(info)
    return jsonify(data), 200

@app.route('/api/pandrugs/drugInteraction/', methods = ['GET'])
def pandrugs_drugInteraction():
    """Returns information of pandrugs for gen id."""

    input = request.args
    genName = input.get("genId")
    data = []
    
    pandrugs.get_pandrugs_drugInteraction(genName,data)
    
    #return data
    #print(info)
    return jsonify(data), 200

@app.route('/api/pandrugs/basic/', methods = ['GET'])
def pandrugs_basic_info():
    """Returns information of pandrugs for gen id."""

    input = request.args
    genName = input.get("genId")
    data = []
    
    pandrugs.get_pandrugs_basic(genName,data)
    
    #return data
    #print(info)
    return jsonify(data), 200


@app.route('/api/pandrugs/', methods = ['DELETE'])
@login_required(role='editor')
def pandrugs_delete():
    """Delete  information of pandrugs from DB for  gen id."""
    #m = db.get_pandrugs(genId)
    #m.delete_instance()

    return jsonify({"reply":"pandrugs_delete"}), 200

