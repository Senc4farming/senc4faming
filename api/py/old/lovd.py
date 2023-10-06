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





def obtenerDatos(genname,data):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()

    try:
        #Leemos los datos de la mutacion
        cursor.execute(f"SELECT id,title,link_href,lovd_id ,\
            author,contributor,date_published,\
            date_updated_lovd,content_gene_id,content_entrez_id,\
            content_symbol,content_name,content_chromosome_location,\
            content_position_start,content_position_end,content_refseq_genomic,\
            content_refseq_mrna,content_refseq_build FROM lovd_basic_info where title   = '{genname}'") 
        rowd = cursor.fetchone()
        if rowd == None:
            print("Dato no encontrado se carga o actualiza para el proceso batch")
            #Si ya existe se consulta la bbdd y se marca para actualizar
            cursor.execute(f"SELECT * FROM gen_to_check where genid = '{genname}' and origin = 'lovd'; ")
            row = cursor.fetchone()
            #si encuentro un registro lo marco para actualizar
            if row == None:
                #si no exite lo inserto
                #insert item
                ins_stm1 = "insert into gen_to_check (genid, check_for_update,"\
                            " date_insert, date_update,origin) values (%s, 1, now(), now(),'lovd'); "
                cursor.execute(ins_stm1,(genname,))
            else:
                #Actualiza el registro para que de actualice
                upd_stm1 = "update gen_to_check  set check_for_update = 1, date_update = now()"\
                                " where  genid = %s and origin = 'lovd'; "
                cursor.execute(upd_stm1,(genname,))
                conn.commit()
            data.append({"genid":genname, "data": "No information found recharge in 24 hours"})
        else:
            strMutation = str(rowd[16]).replace(" ","") 
            basic_info_id = rowd[0]
            #write row into a dict
            d_basic  = dict()
            d_basic["title"] = str(rowd[1]).replace(" ","") 
            d_basic["link_href"] = str(rowd[2]).replace(" ","")
            d_basic["lovd_id"] = str(rowd[3]).replace(" ","")
            d_basic["author"] = str(rowd[4]).replace(" ","")
            d_basic["contributor"] = str(rowd[5]).replace(" ","")
            d_basic["date_published"] = str(rowd[6]).replace(" ","")
            d_basic["date_updated_lovd"] = str(rowd[7]).replace(" ","")
            d_basic["content_gene_id"] = str(rowd[8]).replace(" ","")
            d_basic["content_entrez_id"] = str(rowd[9]).replace(" ","")
            d_basic["content_symbol"] = str(rowd[10]).replace(" ","")
            d_basic["content_name"] = str(rowd[11]).replace(" ","")
            d_basic["content_chromosome_location"] = str(rowd[12]).replace(" ","")
            d_basic["content_position_start"] = str(rowd[13]).replace(" ","")
            d_basic["content_position_end"] = str(rowd[14]).replace(" ","")
            d_basic["content_refseq_genomic"] = str(rowd[15]).replace(" ","")
            d_basic["content_refseq_mrna"] = str(rowd[16]).replace(" ","")
            d_basic["content_refseq_build"] = str(rowd[17]).replace(" ","")
            #creamos el bloque inicial
            data.append({"genid":genname, "data":{"Mutation": strMutation,"basic_info":d_basic,"variant_info": []}})
            #añadimos datos de variant lovd_variant_info
            cursor.execute(f"SELECT id ,Effect ,Reported ,Exon , \
                            cDNA,RNA_change ,Protein ,Classification_method , \
                            Clinical_classification,DNA_change_hg19,DNA_change_hg38 ,Published_as ,\
                            ISCN ,DB_ID,Variant_remarks ,Reference ,\
                            ClinVar_ID ,dbSNP_ID ,Origin ,Segregation ,\
                            Frequency ,Re_site ,VIP ,Methylation ,data_Owner   FROM lovd_variant_info  where basic_info_id = {basic_info_id};") 
            rows2 = cursor.fetchall()
            print("Print each row and it's columns values")
            for row2 in rows2:
                d_variant = dict()
                d_variant["Effect"] = str(row2[1]).replace(" ","")
                d_variant["Reported"] = str(row2[2]).replace(" ","")
                d_variant["Exon"] = str(row2[3]).replace(" ","")
                d_variant["cDNA"] = str(row2[4]).replace(" ","")
                d_variant["RNA_change"] = str(row2[5]).replace(" ","")
                d_variant["Protein"] = str(row2[6]).replace(" ","")
                d_variant["Classification_method"] = str(row2[7]).replace(" ","")
                d_variant["Clinical_classification"] = str(row2[8]).replace(" ","")
                d_variant["DNA_change_hg19"] = str(row2[9]).replace(" ","")
                d_variant["DNA_change_hg38"] = str(row2[10]).replace(" ","")
                d_variant["Published_as"] = str(row2[11]).replace(" ","")
                d_variant["ISCN"] = str(row2[12]).replace(" ","")
                d_variant["DB_ID"] = str(row2[13]).replace(" ","")
                d_variant["Variant_remarks"] = str(row2[14]).replace(" ","")
                d_variant["Reference"] = str(row2[15]).replace(" ","")
                d_variant["ClinVar_ID"] = str(row2[16]).replace(" ","")
                d_variant["dbSNP_ID"] = str(row2[17]).replace(" ","")
                d_variant["Origin"] = str(row2[18]).replace(" ","")
                d_variant["Segregation"] = str(row2[19]).replace(" ","")
                d_variant["Frequency"] = str(row2[20]).replace(" ","")
                d_variant["Re_site"] = str(row2[21]).replace(" ","")
                d_variant["VIP"] = str(row2[22]).replace(" ","")
                d_variant["Methylation"] = str(row2[23]).replace(" ","")
                d_variant["data_Owner"] = str(row2[24]).replace(" ","")
                data[0]["data"]["variant_info"].append(d_variant)
            
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)      
    
    cursor.close()
    conn.close()

def obtenerDatosDna(genname,dnaChange,data):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()

    try:
        #Leemos los datos de la mutacion
        cursor.execute(f"select a.id,a.title,a.link_href,a.lovd_id ,\
                a.author,a.contributor,a.date_published,\
                a.date_updated_lovd,a.content_gene_id,a.content_entrez_id,\
                a.content_symbol,a.content_name,a.content_chromosome_location,\
                a.content_position_start,a.content_position_end,a.content_refseq_genomic,\
                a.content_refseq_mrna,a.content_refseq_build \
            FROM lovd_basic_info a \
            join lovd_variant_info b on  b.basic_info_id = a.id \
            where title   = '{genname}' and  \
                ( dna_change_hg19 = '{dnaChange}' or DNA_change_hg38 =  '{dnaChange}' )") 
        rowd = cursor.fetchone()
        if rowd == None:
            print("Dato no encontrado se carga o actualiza para el proceso batch")
            #Si ya existe se consulta la bbdd y se marca para actualizar
            cursor.execute(f"SELECT * FROM gen_to_check where genid = '{genname}' and origin = 'lovd'; ")
            row = cursor.fetchone()
            #si encuentro un registro lo marco para actualizar
            if row == None:
                #si no exite lo inserto
                #insert item
                ins_stm1 = "insert into gen_to_check (genid, check_for_update,"\
                            " date_insert, date_update,origin) values (%s, 1, now(), now(),'lovd'); "
                cursor.execute(ins_stm1,(genname,))
            else:
                #Actualiza el registro para que de actualice
                upd_stm1 = "update gen_to_check  set check_for_update = 1, date_update = now()"\
                                " where  genid = %s and origin = 'lovd'; "
                cursor.execute(upd_stm1,(genname,))
                conn.commit()
            data.append({"genid":genname, "data": "No information found recharge in 24 hours"})
        else:
            strMutation = str(rowd[16]).replace(" ","") 
            basic_info_id = rowd[0]
            #write row into a dict
            d_basic  = dict()
            d_basic["title"] = str(rowd[1]).replace(" ","") 
            d_basic["link_href"] = str(rowd[2]).replace(" ","")
            d_basic["lovd_id"] = str(rowd[3]).replace(" ","")
            d_basic["author"] = str(rowd[4]).replace(" ","")
            d_basic["contributor"] = str(rowd[5]).replace(" ","")
            d_basic["date_published"] = str(rowd[6]).replace(" ","")
            d_basic["date_updated_lovd"] = str(rowd[7]).replace(" ","")
            d_basic["content_gene_id"] = str(rowd[8]).replace(" ","")
            d_basic["content_entrez_id"] = str(rowd[9]).replace(" ","")
            d_basic["content_symbol"] = str(rowd[10]).replace(" ","")
            d_basic["content_name"] = str(rowd[11]).replace(" ","")
            d_basic["content_chromosome_location"] = str(rowd[12]).replace(" ","")
            d_basic["content_position_start"] = str(rowd[13]).replace(" ","")
            d_basic["content_position_end"] = str(rowd[14]).replace(" ","")
            d_basic["content_refseq_genomic"] = str(rowd[15]).replace(" ","")
            d_basic["content_refseq_mrna"] = str(rowd[16]).replace(" ","")
            d_basic["content_refseq_build"] = str(rowd[17]).replace(" ","")
            
            #creamos el bloque inicial
            data.append({"genid":genname, "data":{"Mutation": strMutation,"basic_info":d_basic,"variant_info": []}})
            #añadimos datos de variant lovd_variant_info
            cursor.execute(f"SELECT Clinical_classification ,DB_ID ,Origin ,Frequency \
                            FROM lovd_variant_info  where basic_info_id = {basic_info_id} and  \
                            ( dna_change_hg19 = '{dnaChange}' or DNA_change_hg38 =  '{dnaChange}' )") 
            rows2 = cursor.fetchall()

 
            print("Print each row and it's columns values")
            for row2 in rows2:
                d_variant = dict()
                d_variant["Clinical_classification"] = str(row2[0]).replace(" ","")
                d_variant["DB_ID"] = str(row2[1]).replace(" ","")
                d_variant["Origin"] = str(row2[2]).replace(" ","")
                d_variant["Frequency"] = str(row2[3]).replace(" ","")
                data[0]["data"]["variant_info"].append(d_variant)
            
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)      
    
    cursor.close()
    conn.close()

def get_lovd(genid,data):
    obtenerDatos(genid,data)

def get_lovd_dna(genid,dnaChange,data):
    obtenerDatosDna(genid,dnaChange,data)
    