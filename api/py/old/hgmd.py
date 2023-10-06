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

def obtenerImagenes(genname,data):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()
  
    try:
        #Leemos los datos de la mutacion
        cursor.execute(f"SELECT id,mutation FROM hgmd_mutation where genid  = '{genname}'") 
        row = cursor.fetchone()
        if row == None:
            print("Dato no encontrado se carga o actualiza para el proceso batch")
            #Si ya existe se consulta la bbdd y se marca para actualizar
            cursor.execute(f"SELECT * FROM gen_to_check where genid = '{genname}' and origin = 'hgmd'; ")
            row = cursor.fetchone()
            ins_stm1 = ''
            #si encuentro un registro lo marco para actualizar
            if row == None:
                #si no exite lo inserto
                #insert item
                ins_stm1 = "insert into gen_to_check (genid, check_for_update,"\
                            " date_insert, date_update,origin) values (%s, 1, now(), now(),'hgmd'); "
                cursor.execute(ins_stm1,(genname,))
            else:
                #Actualiza el registro para que de actualice
                upd_stm1 = "update gen_to_check  set check_for_update = 1, date_update = now()"\
                                " where  genid = %s and origin = 'hgmd'; "
                cursor.execute(upd_stm1,(genname,))
                conn.commit()
            data.append({"genid":genname, "data": "No information found recharge in 24 hours"})
        else:
            strMutation = row[1] 
            IdIntMutation = row[0]
            data.append({"genid":genname, "data":{"Mutation": strMutation,"info":[]}})
            #leemos de la base de datos, buscamos todos los elemantos de la tabla hgmd_mutation_detail
            cursor.execute(f"SELECT Mutation_type, json_info FROM hgmd_mutation_detail where id_mutation = {IdIntMutation} and accession_number <> 'N/A';") 
            rows2 = cursor.fetchall()
            print("Print each row and it's columns values")
            strMutation_type_ref = ''
            iter = -1
            data_local_r= {}
            for row2 in rows2:
                strMutation_type_read = row2[0] 
                if strMutation_type_read != strMutation_type_ref:
                    strMutation_type_ref = row2[0]
                    #data_local_r.append({ "Mutation Type": strMutation_type_ref.strip() ,"mut_type":[]})
                    data[0]["data"]["info"].append({ "Mutation Type": strMutation_type_ref.strip() ,"mut_type":[]})
                    iter = iter +1
                
                #data_local_r[iter]["mut_type"].append(row2[1])
                str_row = str(row2[1])
                str_row = str_row.replace("[","")
                str_row = str_row.replace("]","")
                str_row = str_row.replace("'",'"')
                
                data[0]["data"]["info"][iter]["mut_type"].append(json.loads(str_row))
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)      
    
    cursor.close()
    conn.close()
    data[0]["data"]["info"].append(data_local_r)

def get_hgmd(genid,data):
    obtenerImagenes(genid,data)

    