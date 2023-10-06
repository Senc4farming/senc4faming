#!/usr/bin/env python
import psycopg2
from psycopg2 import connect

# request url
import time
try:
    import cookielib
except:
    import http.cookiejar
    cookielib = http.cookiejar

import sys
from io import BytesIO
import json
import os



#modificamos webdriver
# first load config from a json file,
srvconf = json.load(open(os.environ["PYSRV_CONFIG_PATH"]))



def obtenerDatosGene(genname,data):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()

    try:
        #Leemos los datos de la mutacion
        my_query = query_db(cursor,"select  a.*\
            from pharmgkb_genes a \
            where t.Symbol   = %s limit 10", (genname,))
        print(my_query)
  
        data.append({"genid":genname, "data":{"variant_info": my_query }})
            
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)      
    
    cursor.close()
    conn.close()


def obtenerDatosVariant(genname,data):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()

    try:
        #Leemos los datos de la mutacion
        my_query = query_db(cursor,"select * from \
            (\
            select  a.*, c.*, b.* \
            from pharmgkb_genes a \
            join pharmgkb_relationships b on b.Entity1_id = a.PharmGKBAccessionId and \
                                            b.Entity1_type = 'Gene' and \
                                            b.Entity2_type = 'Variant' \
            join pharmgkb_variant c on c.VariantID = b.Entity2_id  \
            union\
            select  a.*, c.*, b.* from pharmgkb_genes a \
            join pharmgkb_relationships b on b.Entity2_id = a.PharmGKBAccessionId and \
                                            b.Entity2_type = 'Gene' and \
                                            b.Entity1_type = 'Variant' \
            join pharmgkb_variant c on c.VariantID = b.Entity1_id \
            ) t \
            where t.Symbol   = %s limit 10", (genname,))
        print(my_query)
  
        data.append({"genid":genname, "data":{"variant_info": my_query }})
            
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)      
    
    cursor.close()
    conn.close()

def obtenerDatosChemicals(genname,data):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()

    try:
        #Leemos los datos de la mutacion
        my_query = query_db(cursor,"select * from \
            (\
            select  a.*, c.*, b.* \
            from pharmgkb_genes a \
            join pharmgkb_relationships b on b.Entity1_id = a.PharmGKBAccessionId and \
                                            b.Entity1_type = 'Gene' and \
                                            b.Entity2_type = 'Chemical' \
            join pharmgkb_chemicals c on c.PharmGKBAccessionId = b.Entity2_id  \
            union\
            select  a.*, c.*, b.* from pharmgkb_genes a \
            join pharmgkb_relationships b on b.Entity2_id = a.PharmGKBAccessionId and \
                                            b.Entity2_type = 'Gene' and \
                                            b.Entity1_type = 'Chemical' \
            join pharmgkb_chemicals c on c.PharmGKBAccessionId = b.Entity1_id \
            ) t \
            where t.Symbol   = %s limit 10", (genname,))
        print(my_query)
  
        data.append({"genid":genname, "data":{"chemicals_info": my_query }})
            
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)      
    
    cursor.close()
    conn.close()


def obtenerDatosDrugs(genname,data):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()

    try:
        #Leemos los datos de la mutacion
        my_query = query_db(cursor,"select * from \
            (\
            select  a.*, c.*, b.* \
            from pharmgkb_genes a \
            join pharmgkb_relationships b on b.Entity1_id = a.PharmGKBAccessionId and \
                                            b.Entity1_type = 'Gene' and \
                                            b.Entity2_type = 'Disease' \
            join pharmgkb_drugs c on c.PharmGKBAccessionId = b.Entity2_id  \
            union\
            select  a.*, c.*, b.* from pharmgkb_genes a \
            join pharmgkb_relationships b on b.Entity2_id = a.PharmGKBAccessionId and \
                                            b.Entity2_type = 'Gene' and \
                                            b.Entity1_type = 'Disease' \
            join pharmgkb_drugs c on c.PharmGKBAccessionId = b.Entity1_id \
            ) t \
            where t.Symbol   = %s limit 10", (genname,))
        print(my_query)
  
        data.append({"genid":genname, "data":{"variant_info": my_query }})
            
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)      
    
    cursor.close()
    conn.close()


def obtenerDatosPhenotypes(genname,data):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()

    try:
        #Leemos los datos de la mutacion
        my_query = query_db(cursor,"select * from \
            (\
            select  a.*, c.*, b.* \
            from pharmgkb_genes a \
            join pharmgkb_relationships b on b.Entity1_id = a.PharmGKBAccessionId and \
                                            b.Entity1_type = 'Gene' and \
                                            b.Entity2_type = 'Haplotype' \
            join pharmgkb_phenotypes c on c.PharmGKBAccessionId = b.Entity2_id  \
            union\
            select  a.*, c.*, b.* from pharmgkb_genes a \
            join pharmgkb_relationships b on b.Entity2_id = a.PharmGKBAccessionId and \
                                            b.Entity2_type = 'Gene' and \
                                            b.Entity1_type = 'Haplotype' \
            join pharmgkb_phenotypes c on c.PharmGKBAccessionId = b.Entity1_id \
            ) t \
            where t.Symbol   = %s limit 10", (genname,))
        print(my_query)
  
        data.append({"genid":genname, "data":{"phenotypes_info": my_query }})
            
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)      
    
    cursor.close()
    conn.close()


def query_db(cursor,query, args=(), one=False):
    cursor.execute(query, args)
    r = [dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    cursor.connection.close()
    return (r[0] if r else None) if one else r

def get_variant(genid,data):
    obtenerDatosVariant(genid,data)
    
def get_chemicals(genid,data):
    obtenerDatosChemicals(genid,data)

def get_drugs(genid,data):
    obtenerDatosDrugs(genid,data)

def get_phenotypes(genid,data):
    obtenerDatosPhenotypes(genid,data)

def get_gene(genid,data):
    obtenerDatosGene(genid,data)