#!/usr/bin/env python
"""
"""
import random
import mechanize
import util
import json # import json library
from pprint import pprint  # for pretty-printing results
import requests as rq  # for issuing HTTP(S) queries
import shutil # save img locally

# request url

import requests
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# import the connect library from psycopg2
import psycopg2
from psycopg2 import connect

from io import BytesIO
import os
from urllib.parse import urlparse
from mimetypes import guess_extension

try:
    import cookielib
except:
    import http.cookiejar
    cookielib = http.cookiejar
from bs4 import BeautifulSoup
#from seleniumwire import webdriver  # Import from seleniumwire



from xmltoDict import parse, ParsingInterrupted
import collections
import unittest

try:
    from io import BytesIO as StringIO
except ImportError:
    from xmltoDict import StringIO

from xml.parsers.expat import ParserCreate
from xml.parsers import expat
from xml.etree import ElementTree as ET

query = """
https://www.pandrugs.org/pandrugs-backend/api/gene/interactions/
?gene=*gen*
"""


list_genref = ['POLD1','ARID1A','ATM','ATRX','APC','BARD1','BRCA1','BRCA2','BRIP1','CD274','CDH1','CDK4','CDK6','CDK12','CDKN2A','CHEK2','EPCAM','ERBB2','MET',
'MLH1','MSH2','MSH6','MUTYH','NBN','NTRK1','NTRK2','NTRK3','PALB2','PDCD1LG2','PMS2','POLD1','POLE','PTEN','RAD51C','RAD51D','RET','STK11','VHL']



email_address = "jmafernanez@ubu.es"
step  = 0

def get_initial_info(conn, cursor, gen_name ):
    
    step = 40
    try:
        #Si ya existe se consulta la bbdd y se marca para actualizar
        s_stm1 = "SELECT * FROM pandrugs_basic_info where title = %s; "
        cursor.execute(s_stm1,(gen_name,))
        rows = cursor.fetchone()
        stm1 = ''
        step = 50
        #si encuentro un registro lo marco para actualizar
        if rows == None:
            print("Dato no encontrado se carga o actualiza para el proceso batch")
            #Si ya existe se consulta la bbdd y se marca para actualizar
            cursor.execute(f"SELECT * FROM gen_to_check where genid = '{gen_name}' and origin = 'pandrugs'; ")
            row_1 = cursor.fetchone()
            #si encuentro un registro lo marco para actualizar
            if row_1 == None:
                #si no exite lo inserto
                #insert item
                ins_stm1 = "insert into gen_to_check (genid, check_for_update,"\
                            " date_insert, date_update,origin) values (%s, 1, now(), now(),'pandrugs'); "
                cursor.execute(ins_stm1,(gen_name,))
            else:
                #Actualiza el registro para que de actualice
                upd_stm1 = "update gen_to_check  set check_for_update = 1, date_update = now()"\
                                " where  genid = %s and origin = 'pandrugs'; "
                cursor.execute(upd_stm1,(gen_name,))
            step = 60
            #insert item
            stm1 = "insert into pandrugs_basic_info ( title ,date_insert,date_update) values (\
                        %s,now(),now()) RETURNING id; "
            cursor.execute(stm1,(gen_name ,  ))
            conn.commit()
            basic_info_id =  cursor.fetchone()[0]
        else:
            # we got rows!
            basic_info_id =  rows[0]
            step = 70
            #insert item
            stm1 = "update  pandrugs_basic_info set date_update = now() where title = %s ; "
            cursor.execute(stm1,(gen_name ,  ))
            conn.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error,": Step:", step )
        return -1
    return basic_info_id
def get_info(conn, cursor, gen_name,basic_info_id ):
    print(query)
    query_ini = query.replace('*gen*',gen_name)
    query_ini = query_ini.replace('\n', '')
    print(query_ini)
    results = rq.get(query_ini).json()
    print(results[0]["geneInteraction"])
    #print(results)
    update_db_info(results,cursor,conn,basic_info_id ,gen_name )
    
    
def update_db_info(results,cursor,conn,basic_info_id ,gen_name):
    #read geneInteraction
    # pandrugs_gene_interaction_info

    for item in results[0]["geneInteraction"]:
        step = 75 
        str_Gene_Symbol =item
        try:
            # Si ya existe se consulta la bbdd y se marca para actualizar
            s_stm1 = "SELECT * FROM pandrugs_gene_interaction_info where  basic_info_id = %s and gene = %s ; "
            cursor.execute(s_stm1,(basic_info_id,str_Gene_Symbol))
            rows = cursor.fetchone()
            stm1 = ''
            step = 80
            
            #si encuentro un registro lo marco para actualizar
            if rows == None:
                #Insertamos en  pandrugs_gene_interaction_info
                try:
                    step = 90
                    #print("el elemento no existe:", basic_info_id,str_id_brca)
                    #insert item
                    stm1 = ''
                    stm1 = "insert into pandrugs_gene_interaction_info (basic_info_id,gene ,\
                            date_insert,date_update) values ( %s,%s, now(),now()) RETURNING id; "
                    cursor.execute(stm1,(basic_info_id,str_Gene_Symbol ))
                    conn.commit()
                except (Exception, psycopg2.Error) as error:
                    print( "Insertando en pandrugs_gene_interaction_info")
                    print ("Oops! An exception has occured:", error)
                    print ("Exception TYPE:", type(error))
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error,": Step:", step )
            conn.rollback()

    #read info from json and update/insert in db
    #Load JSON string into a dictionary
    #Save info in pandrugs_drugInteraction_info
    for item in results[0]["drugInteraction"]:
        #print (item["id"])
        standardDrugName =item["standardDrugName"][:200]
        showDrugName =item["showDrugName"][:200]
        target_value =item["target"]
        step = 100
        try:
            #Si ya existe se consulta la bbdd y se marca para actualizar
            s_stm1 = "SELECT * FROM pandrugs_drugInteraction_info where  basic_info_id = %s and standardDrugName = %s \
                    and showDrugName = %s and  target_value = %s ; "
            cursor.execute(s_stm1,(basic_info_id,standardDrugName,showDrugName,target_value  ))
            rows = cursor.fetchone()
            stm1 = ''
            step = 105
            pandrugs_drugInteraction_info_id = -1
            #si encuentro un registro lo marco para actualizar
            if rows == None:
                try:
                    step = 110
                    #print("el elemento no existe:", basic_info_id,str_id_brca)
                    #insert item
                    stm1 = ''
                    stm1 = "insert into pandrugs_drugInteraction_info (basic_info_id,standardDrugName ,showDrugName ,target_value) \
                        values (%s,%s,%s,%s) RETURNING id; "
                    cursor.execute(stm1,(basic_info_id,standardDrugName,showDrugName,target_value ))
                    pandrugs_drugInteraction_info_id =  cursor.fetchone()[0]
                    conn.commit()
                except (Exception, psycopg2.Error) as error:
                    print( "Insertando en pandrugs_drugInteraction_info")
                    print ("Oops! An exception has occured:", error)
                    print ("Exception TYPE:", type(error))
                #Insertamos en el tabla pandrugs_indirectGene_info
                #recorremos el json
                for item_indirectGene in item["indirectGene"]:
                    try:
                        step = 120
                        #print("el elemento no existe:", basic_info_id,str_id_brca)
                        #insert item
                        stm1 = ''
                        stm1 = "insert into pandrugs_indirectGene_info (drugInteraction_id,gene ,date_insert,date_update) \
                                values ( %s,%s, now(),now()) RETURNING id;"
                        cursor.execute(stm1,(pandrugs_drugInteraction_info_id,item_indirectGene))
                        conn.commit()
                    except (Exception, psycopg2.Error) as error:
                        print( "Insertando en pandrugs_indirectGene_info")
                        print ("Oops! An exception has occured:", error)
                        print ("Exception TYPE:", type(error))
            else:
                # we got rows!
                pandrugs_drugInteraction_info_id =  rows[0]
                step = 130
                #recorremos el json
                for item_indirectGene in item["indirectGene"]:
                    #Si exise no insetamos
                    s_stm1 = "SELECT * FROM pandrugs_indirectGene_info where  drugInteraction_id = %s and gene = %s; "
                    cursor.execute(s_stm1,(pandrugs_drugInteraction_info_id,item_indirectGene))
                    rows = cursor.fetchone()
                    stm1 = ''
                    if rows == None:
                        try:
                            step = 140
                            #print("el elemento no existe:", basic_info_id,str_id_brca)
                            #insert item
                            stm1 = ''
                            stm1 = "insert into pandrugs_indirectGene_info (drugInteraction_id,gene ,date_insert,date_update) \
                                    values ( %s,%s, now(),now()) RETURNING id;"
                            cursor.execute(stm1,(pandrugs_drugInteraction_info_id,item_indirectGene))
                            conn.commit()
                        except (Exception, psycopg2.Error) as err:
                            print( "Insertando en pandrugs_indirectGene_info")
                            print ("Oops! An exception has occured:", error)
                            print ("Exception TYPE:", type(error))
                    conn.commit()
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error,": Step:", step )
            conn.rollback()
        
if __name__ == '__main__':
    #conexion a la bbdd
    conn = psycopg2.connect(user="tm",
                                    password="eneas",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="hgmd")

    cursor = conn.cursor()
    #    resp = browse_dbcline(br, genes = ['GCS1'])
    for gen_l_name in list_genref:
        basic_info_id = get_initial_info(conn, cursor, gen_l_name )
        get_info(conn, cursor, gen_l_name,basic_info_id)
        
    
