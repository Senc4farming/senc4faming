#!/usr/bin/python
# -*- coding: utf-8 -*-

# api.py: REST API for lovd
#   - this module is just demonstrating how to handle basic CRUD
#   - GET operations are available for visitors, editing requires login

# Author: José Manuel Aroca

from flask import request, jsonify, g
from playhouse.shortcuts import dict_to_model, update_model_from_dict
from redis import DataError

from webutil import app, login_required, get_myself

import logging
import pharmaGKB
import charge_pharmaGKB

log = logging.getLogger("api.pharmaGKB")


@app.route('/api/pharmaGKB/importdb/', methods = ['POST'])
def charge_data():
    """Restore db content from pharmaGKB files, remember to backup previous files in case rollback needed """
    print("Calling charge_data")
    charge_pharmaGKB.import_pharmaGKB_files()
    return 200
@app.route('/api/pharmaGKB/gene/', methods = ['GET'])
def pharmaGKB_query_gene():
    """Returns information of pharmaGKB for gene"""

    input = request.args
    genName = input.get("genId")
    data = []
    pharmaGKB.get_gene(genName,data)
    
    
    #return data
    #print(info)
    return jsonify(data), 200

@app.route('/api/pharmaGKB/variant/', methods = ['GET'])
def pharmaGKB_query_variant():
    """Returns information of pharmaGKB for variant info  by gen name"""

    input = request.args
    genName = input.get("genId")
    data = []
    pharmaGKB.get_variant(genName,data)
    return jsonify(data), 200

@app.route('/api/pharmaGKB/drugs/', methods = ['GET'])
def pharmaGKB_query_drugs():
    """Returns information of pharmaGKB for drugs info  by gen name"""

    input = request.args
    genName = input.get("genId")
    data = []
    
    pharmaGKB.get_drugs(genName,data)
    
    #return data
    #print(info)
    return jsonify(data), 200

@app.route('/api/pharmaGKB/chemicals/', methods = ['GET'])
def pharmaGKB_query_chemicals():
    """Returns information of pharmaGKB for chemicals info  by gen name"""

    input = request.args
    genName = input.get("genId")
    data = []
    pharmaGKB.get_chemicals(genName,data)
    
    
    #return data
    #print(info)
    return jsonify(data), 200

@app.route('/api/pharmaGKB/phenotypes/', methods = ['GET'])
def pharmaGKB_query_phenotypes():
    """Returns information of pharmaGKB for phenotypes info by gen name"""

    input = request.args
    genName = input.get("genId")
    data = []
    pharmaGKB.get_phenotypes(genName,data)
    
    
    #return data
    #print(info)
    return jsonify(data), 200
