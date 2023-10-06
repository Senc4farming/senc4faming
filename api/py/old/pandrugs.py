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
def obtenerDatosBasic(genname,data):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()

    try:
        #Leemos los datos de la mutacion
        cursor.execute(f"SELECT * FROM pandrugs_basic_info where title   = '{genname}'") 
        rowd = cursor.fetchone()
        if rowd == None:
            print("Dato no encontrado se carga o actualiza para el proceso batch")
            #Si ya existe se consulta la bbdd y se marca para actualizar
            cursor.execute(f"SELECT * FROM gen_to_check where genid = '{genname}' and origin = 'pandrugs'; ")
            row = cursor.fetchone()
            #si encuentro un registro lo marco para actualizar
            if row == None:
                #si no exite lo inserto
                #insert item
                ins_stm1 = "insert into gen_to_check (genid, check_for_update,"\
                            " date_insert, date_update,origin) values (%s, 1, now(), now(),'pandrugs'); "
                cursor.execute(ins_stm1,(genname,))
            else:
                #Actualiza el registro para que de actualice
                upd_stm1 = "update gen_to_check  set check_for_update = 1, date_update = now()"\
                                " where  genid = %s and origin = 'pandrugs'; "
                cursor.execute(upd_stm1,(genname,))
                conn.commit()
            data.append({"genid":genname, "data": "No information found recharge in 24 hours"})
        else:
            basic_info_id = rowd[0]
            #write row into a dict
            d_basic  = dict()
            d_basic["title"] = str(rowd[1]).replace(" ","")
            d_basic["date_insert"] = str(rowd[2])
            d_basic["date_update"] = str(rowd[3])
        
            #creamos el bloque inicial
            data.append({"genid":genname, "date_ini": d_basic["date_insert"] , "date_updates":  d_basic["date_update"] })
            
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)      
    
    cursor.close()
    conn.close()

def obtenerDatosgeneInteraction(genname,data):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()

    try:
        #Leemos los datos de la mutacion
        cursor.execute(f"SELECT * FROM pandrugs_basic_info where title   = '{genname}'") 
        rowd = cursor.fetchone()
        if rowd == None:
            print("Dato no encontrado se carga o actualiza para el proceso batch")
            #Si ya existe se consulta la bbdd y se marca para actualizar
            cursor.execute(f"SELECT * FROM gen_to_check where genid = '{genname}' and origin = 'pandrugs'; ")
            row = cursor.fetchone()
            #si encuentro un registro lo marco para actualizar
            if row == None:
                #si no exite lo inserto
                #insert item
                ins_stm1 = "insert into gen_to_check (genid, check_for_update,"\
                            " date_insert, date_update,origin) values (%s, 1, now(), now(),'pandrugs'); "
                cursor.execute(ins_stm1,(genname,))
            else:
                #Actualiza el registro para que de actualice
                upd_stm1 = "update gen_to_check  set check_for_update = 1, date_update = now()"\
                                " where  genid = %s and origin = 'pandrugs'; "
                cursor.execute(upd_stm1,(genname,))
                conn.commit()
            data.append({"genid":genname, "data": "No information found recharge in 24 hours"})
        else:
             
            basic_info_id = rowd[0]
            #write row into a dict
            d_basic  = dict()
            basic_info_id = str(rowd[0])
            d_basic["title"] = str(rowd[1]).replace(" ","")
            d_basic["date_insert"] = str(rowd[2])
            d_basic["date_update"] = str(rowd[3])
            #creamos el bloque inicial
            data.append({"genid":genname, "data":{"basic_info":d_basic,"interaction_info": []}})
            #añadimos datos de variant lovd_variant_info
            cursor.execute(f"select gi.* from pandrugs_gene_interaction_info gi where  gi.basic_info_id  = {basic_info_id};") 
            rows2 = cursor.fetchall()
            print("Print each row and it's columns values")
            for row2 in rows2:
                d_variant = dict()
                d_variant["gene"] = str(row2[2]).replace(" ","")
                d_variant["date_insert"] = str(row2[3])
                d_variant["date_update"] = str(row2[4])
                
                data[0]["data"]["interaction_info"].append(d_variant)
            
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)      
    
    cursor.close()
    conn.close()

def obtenerDatosdrugInteraction(genname,data):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()

    try:
        #Leemos los datos de la mutacion
        cursor.execute(f"SELECT * FROM pandrugs_basic_info where title   = '{genname}'") 
        rowd = cursor.fetchone()
        if rowd == None:
            print("Dato no encontrado se carga o actualiza para el proceso batch")
            #Si ya existe se consulta la bbdd y se marca para actualizar
            cursor.execute(f"SELECT * FROM gen_to_check where genid = '{genname}' and origin = 'pandrugs'; ")
            row = cursor.fetchone()
            #si encuentro un registro lo marco para actualizar
            if row == None:
                #si no exite lo inserto
                #insert item
                ins_stm1 = "insert into gen_to_check (genid, check_for_update,"\
                            " date_insert, date_update,origin) values (%s, 1, now(), now(),'pandrugs'); "
                cursor.execute(ins_stm1,(genname,))
            else:
                #Actualiza el registro para que de actualice
                upd_stm1 = "update gen_to_check  set check_for_update = 1, date_update = now()"\
                                " where  genid = %s and origin = 'pandrugs'; "
                cursor.execute(upd_stm1,(genname,))
                conn.commit()
            data.append({"genid":genname, "data": "No information found recharge in 24 hours"})
        else:
            basic_info_id = rowd[0]
            #write row into a dict
            d_basic  = dict()
            basic_info_id = str(rowd[0])
            d_basic["title"] = str(rowd[1]).replace(" ","")
            d_basic["date_insert"] = str(rowd[2])
            d_basic["date_update"] = str(rowd[3])
            #creamos el bloque inicial
            data.append({"genid":genname, "data":{"basic_info":d_basic,"drugInteraction_info": []}})
            #añadimos datos de variant lovd_variant_info
            cursor.execute(f"select dr.* from pandrugs_drugInteraction_info dr where  dr.basic_info_id = {basic_info_id};") 
            rows2 = cursor.fetchall()
            print("Print each row and it's columns values")
            for row2 in rows2:
                d_variant = dict()
                d_variant["standardDrugName"] = str(row2[2])
                d_variant["showDrugName"] = str(row2[3])
                d_variant["target_value"] = str(row2[4])
                
                data[0]["data"]["drugInteraction_info"].append(d_variant)
            
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)      
    
    cursor.close()
    conn.close()


def get_pandrugs_basic(genid,data):
    obtenerDatosBasic(genid,data)

def get_pandrugs_drugInteraction(genid,data):
    obtenerDatosdrugInteraction(genid,data)

def get_pandrugs_geneInteraction(genid,data):
    obtenerDatosgeneInteraction(genid,data)