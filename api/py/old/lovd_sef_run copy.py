#!/usr/bin/env python
"""
"""
import random
import mechanize
import util
import json # import json library
import requests
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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver

import copy
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

api_url_gen = "https://databases.lovd.nl/shared/api/rest.php/genes/*gen*"
url_variant = "https://databases.lovd.nl/shared/variants/*gen*/unique#page_size=10&page=1"
#url_variant = "https://databases.lovd.nl/shared/variants/*gen*/unique#page_size=1000"
#genname = "ATRX"
#list_genref_0 = ['POLD1','ARID1A','ATM','ATRX','APC']

#list_genre_1 = ['BARD1','BRCA1','BRCA2','BRIP1']
#list_genref_2 = ['CD274','CDH1','CDK4','CDK6']
#list_genref_3 = ['CDK12','CDKN2A','CHEK2','EPCAM']
#list_genref_4 = ['ERBB2','MET','MLH1','MSH2']
#list_genref_5 = ['MSH6','MUTYH','NBN','NTRK1']
#list_genref_6 = ['NTRK2','NTRK3','PALB2','PDCD1LG2']
#list_genref_7 = ['PMS2','POLE','PTEN','RAD51C']
#list_genref_8 = ['RET','STK11','VHL']
#list_genref = ['BRCA1','BRCA2','BRIP1']
list_genref = ['POLD1']
#'ARID1A','ATM','ATRX','APC','BARD1','BRCA1','BRCA2','BRIP1','CD274','CDH1','CDK4','CDK6','CDK12','CDKN2A','CHEK2','EPCAM','ERBB2','MET',
#'MLH1','MSH2','MSH6','MUTYH','NBN','NTRK1','NTRK2','NTRK3','PALB2','PDCD1LG2','PMS2','POLD1','POLE','PTEN','RAD51C','RAD51D','RET','STK11','VHL'
email_address = "jmafernanez@ubu.es"
step  = 0
driver = webdriver.Chrome()

def initialize_browser():
    """
    Initialize a Browser object

    thanks to <http://stockrt.github.com/p/emulating-a-browser-in-python-with-mechanize/>
    """

    br = mechanize.Browser()
    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
#    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Want debugging messages?
#    br.set_debug_http(True)
#    br.set_debug_redirects(True)
#    br.set_debug_responses(True)

    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    br.addheaders.append(('email', email_address))

    return br

def get_initial_info_br(gen_name, br,strMutationMain):
    #change genname in url
    requestURL = api_url_gen.replace('*gen*',gen_name) 
    response1 = br.open(  requestURL)
    html = response1.read()
    step = 10
    res_dict = parse(html)
    step = 20
    d_content = dict()
    for line in str(res_dict['entry']['content']['#text']).split('\n'):
        (key,val) = line.split(':',1)
        d_content[str(key).replace(' ','')] = val
    step = 30
    #print(d_content)
    #insertamos valores para lo que recorremos el xml
    str_title = str(res_dict['entry']['title'])
    str_link_href = str(res_dict['entry']['link']['@href'])
    str_lovd_id  = str(res_dict['entry']['id'])
    str_author = str(res_dict['entry']['author']['name'])
    str_contributor = str(res_dict['entry']['contributor']['name'])
    str_date_published   = str(res_dict['entry']['published'])
    str_date_updated_lovd = str(res_dict['entry']['updated'])
    str_content_gene_id = d_content['id']
    str_content_entrez_id = d_content['entrez_id']
    str_content_symbol = d_content['symbol']
    str_content_name = d_content['name']
    str_content_chromosome_location = d_content['chromosome_location']
    str_content_position_start = d_content['position_start']
    str_content_position_end = d_content['position_end']
    str_content_refseq_genomic = d_content['refseq_genomic']
    str_content_refseq_mrna = d_content['refseq_mrna']
    str_content_refseq_build =  d_content['refseq_build']

    #conexion a la bbdd
    conn = psycopg2.connect(user="tm",
                                    password="eneas",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="hgmd")

    cursor = conn.cursor()
    step = 40
    try:
        #Si ya existe se consulta la bbdd y se marca para actualizar
        s_stm1 = "SELECT * FROM lovd_basic_info where title = %s; "
        cursor.execute(s_stm1,(gen_name,))
        rows = cursor.fetchone()
        stm1 = ''
        step = 50
        #si encuentro un registro lo marco para actualizar
        if rows == None:
            print("Dato no encontrado se carga o actualiza para el proceso batch")
            #Si ya existe se consulta la bbdd y se marca para actualizar
            cursor.execute(f"SELECT * FROM gen_to_check where genid = '{gen_name}' and origin = 'lovd'; ")
            row_1 = cursor.fetchone()
            #si encuentro un registro lo marco para actualizar
            if row_1 == None:
                #si no exite lo inserto
                #insert item
                ins_stm1 = "insert into gen_to_check (genid, check_for_update,"\
                            " date_insert, date_update,origin) values (%s, 1, now(), now(),'lovd'); "
                cursor.execute(ins_stm1,(gen_name,))
            else:
                #Actualiza el registro para que de actualice
                upd_stm1 = "update gen_to_check  set check_for_update = 1, date_update = now()"\
                                " where  genid = %s and origin = 'lovd'; "
                cursor.execute(upd_stm1,(gen_name,))
            step = 60
            #insert item
            stm1 = "insert into lovd_basic_info ( title ,link_href ,lovd_id , \
                        author,contributor ,date_published ,date_updated_lovd , \
                        content_gene_id ,content_entrez_id ,content_symbol ,content_name , \
                        content_chromosome_location ,content_position_start ,content_position_end \
                        ,content_refseq_genomic ,content_refseq_mrna ,content_refseq_build,date_insert,date_update) values (\
                        %s,%s, %s,\
                        %s,%s,%s,%s,\
                        %s,%s,%s,%s,\
                        %s,%s,%s,\
                        %s,%s,%s,now(),now()) RETURNING id; "
            cursor.execute(stm1,(str_title , str_link_href , str_lovd_id ,
            str_author,str_contributor ,str_date_published ,str_date_updated_lovd ,
            str_content_gene_id ,str_content_entrez_id ,str_content_symbol ,str_content_name ,
            str_content_chromosome_location ,str_content_position_start ,str_content_position_end ,
            str_content_refseq_genomic ,str_content_refseq_mrna ,str_content_refseq_build ))
            conn.commit()
            basic_info_id =  cursor.fetchone()[0]
        else:
            # we got rows!
            basic_info_id =  rows[0]
            step = 70
            #insert item
            stm1 = "update  lovd_basic_info set link_href = %s ,lovd_id = %s , \
                        author = %s,contributor = %s ,date_published  = %s,date_updated_lovd = %s , \
                        content_gene_id= %s ,content_entrez_id = %s,content_symbol= %s ,content_name = %s, \
                        content_chromosome_location = %s ,content_position_start = %s ,content_position_end = %s \
                        ,content_refseq_genomic = %s ,content_refseq_mrna = %s ,content_refseq_build = %s,date_update = now() where title = %s ; "
            cursor.execute(stm1,(str_link_href , str_lovd_id ,
            str_author,str_contributor ,str_date_published ,str_date_updated_lovd ,
            str_content_gene_id ,str_content_entrez_id ,str_content_symbol ,str_content_name ,
            str_content_chromosome_location ,str_content_position_start ,str_content_position_end ,
            str_content_refseq_genomic ,str_content_refseq_mrna ,str_content_refseq_build ,str_title))
            conn.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error,": Step:", step )
        return -1
    strMutationMain = str_content_refseq_mrna
    print ("strMutationMain = str_content_refseq_mrna: ", strMutationMain )
    return basic_info_id

def get_variant_br(data,gen_name,basic_info_id,strMutation):
    data.append({"genid":gen_name, "data":{"Mutation": strMutation,"info":[]}})
    step = 10
    #table_id
    table_id = "viewlistTable_CustomVL_VOTunique_VOG_" + gen_name
    #conexion a la bbdd
    conn = psycopg2.connect(user="tm",
                                password="eneas",
                                host="127.0.0.1",
                                port="5432",
                                database="hgmd")

    cursor = conn.cursor()
    #change genname in url
    requestURL = url_variant.replace('*gen*',gen_name) 
    print (requestURL)
    #prepare mechanize

    driver.get(requestURL)
    WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[./span[text()='Close']]"))).click()
    time.sleep(1)
    #obtenemos las cabeceras
    print("Buscando table_id:",table_id)
    tb =  driver.find_element(By.ID,table_id)
    #print (tb)

    #leemos la cabecera
    step = 14
    dh = dict()
    print("Buscando table_id:",step)
    heads = tb.find_elements(By.CSS_SELECTOR,"th")
    #print(heads)
    iterh = 0
    for cellH  in heads:
        step = 47
        contenth = cellH.text.strip()
        #print ("header content [", iterh, "]:",contenth)
        dh[iterh] = contenth
        iterh = iterh +1
    read_table_data(data, tb,table_id,dh,step)
    #look for number of pages
    itm_num_pages = driver.find_element(By.XPATH,"//span[contains( text( ), 'entries on')]")
    
    #find position for ON
    str_on_position = itm_num_pages.text.index('on') + len("on")
    str_pages_position = itm_num_pages.text.index('page')
    num_pages = int(str(itm_num_pages.text[str_on_position:str_pages_position]))
    step = 20
    #look for page numbers
    num_page = 2
    print ("Pages:", str(num_pages))

    #last_page = 1
    while num_page <= num_pages:
        try:
            step = 30
            print ("PPS antes:")
            pps  = driver.find_elements(By.XPATH,'//td[@class="num"]')
            for itm in pps:
                print ( "itm: ", itm.get_attribute('outerHTML'))
                print (itm.text)
                if itm.text == str(num_page):
                    print ( "itm encontrado: ")
                    itm.click()
                    break
            print ("PPS despues:")
            driver.execute_script("document.body.style.zoom='25%'")
            print("Buscando table_id:",table_id)
            WebDriverWait(driver, 20).until( EC.presence_of_element_located((By.ID, table_id)))
            tb =  driver.find_element(By.ID,table_id)
            print ("On page forward:", str(num_page))
            step = 40
            #read_table_data(data, tb,table_id,dh,step)
            #leemos la cabecera
            step = 46
            for row in tb.find_elements(By.CLASS_NAME ,"data"):
                #recorremos las filas de datos
                d = dict()
                iterd = 0
                step = 48
                for  celld  in row.find_elements(By.CSS_SELECTOR,"td"):
                    step = 49
                    print ("Step,iterd:",step,":",str(iterd))
                    content = str(celld.text).replace('\n','')
                    if (iterd in dh):
                        #print ("content [", dh[iterd], "]:",content)
                        d[dh[iterd]] = content
                                                            
                    else:
                        #print ("content [", iterd, "]:",content)
                        d[iterd] = content
                    iterd = iterd +1
                    step = 50
                data[0]["data"]["info"].append({"inputs":d})
            """ 
                if num_page <= num_pages:
                print ("Before elements On page:", str(num_page))
                driver_p = webdriver.Chrome()
                driver_p.set_window_size(1366, 600)
                driver_p.get(requestURL)
                WebDriverWait(driver_p,10).until(EC.element_to_be_clickable((By.XPATH,"//button[./span[text()='Close']]"))).click()
                time.sleep(2)
                print ("Open browser  On page:", str(num_page))
                while num_page > last_page:
                    print ("On page forward:", str(last_page))
                    item = WebDriverWait(driver_p, 20).until(EC.element_to_be_clickable((By.XPATH,"//th[contains( text( ), 'Next ›')]")))
                    print ("On page forward:", str(last_page))
                    item.click()
                    last_page = last_page + 1
                    print ("On page forward:", str(last_page))
                print ("On page:", str(num_page))                
                read_table_data(data, driver_p,table_id,step)
                driver.quit()
                last_page = num_page
                else:
                    break"""
            num_page = num_page +1
            print ("On page forward next page:", str(num_page))
        except:
            print("No page found for :", str(num_page),";step:",step )
            raise
    #print(data)
    update_db_info(data,cursor,conn,basic_info_id )

    cursor.close()
    conn.close()

def read_table_data(data_aux, tb, table_id,dh,step):
    #print (tb)

    #leemos la cabecera
    step = 46
    for row in tb.find_elements(By.CLASS_NAME ,"data"):
        #recorremos las filas de datos
        d = dict()
        iterd = 0
        step = 48
        for  celld  in row.find_elements(By.CSS_SELECTOR,"td"):
            step = 49
            content = str(celld.text).replace('\n','')
            if (iterd in dh):
                #print ("content [", dh[iterd], "]:",content)
                d[dh[iterd]] = content
                                                    
            else:
                #print ("content [", iterd, "]:",content)
                d[iterd] = content
            iterd = iterd +1
            step = 50
        data_aux[0]["data"]["info"].append({"inputs":d})
     

def update_db_info(data,cursor,conn,basic_info_id ):
    #read info from json and update db
    #Load JSON string into a dictionary
    
    for item in data[0]["data"]["info"]:
        #print (item["inputs"]["DNA change (hg38)"])
        #update/insert into db
        strEffect = item["inputs"]["Effect"] 
        strReported = item["inputs"]["Reported"]
        strExon = item["inputs"]["Exon"]
        strcDNA = item["inputs"]["DNA change (cDNA)"]
        strRNA_change = item["inputs"]["RNA change"]
        strProtein = item["inputs"]["Protein"]
        strClassification_method = item["inputs"]["Classification method"]
        strClinical_classification = item["inputs"]["Clinical classification"]
        strDNA_change_hg19 = item["inputs"]["DNA change (genomic) (hg19)"]
        strDNA_change_hg38 = item["inputs"]["DNA change (hg38)"]
        strPublished_as = item["inputs"]["Published as"]
        strISCN = item["inputs"]["ISCN"]
        strDB_ID = item["inputs"]["DB-ID"]
        strVariant_remarks = item["inputs"]["Variant remarks"]
        strReference = item["inputs"]["Reference"]
        strClinVar_ID = item["inputs"]["ClinVar ID"]
        strdbSNP_ID = item["inputs"]["dbSNP ID"]
        strOrigin = item["inputs"]["Origin"]
        strSegregation = item["inputs"]["Segregation"]
        strFrequency = item["inputs"]["Frequency"]
        strRe_site = item["inputs"]["Re-site"]
        strVIP = item["inputs"]["VIP"]
        strMethylation = item["inputs"]["Methylation"]
        strdata_Owner = item["inputs"]["Owner"]

        step = 40
        try:
            #Si ya existe se consulta la bbdd y se marca para actualizar
            s_stm1 = "SELECT * FROM lovd_variant_info where cDNA = %s and basic_info_id = %s; "
            cursor.execute(s_stm1,(strcDNA,basic_info_id))
            rows = cursor.fetchone()
            stm1 = ''
            step = 50
            #si encuentro un registro lo marco para actualizar
            if rows == None:
                step = 60
                #insert item
                stm1 = "insert into lovd_variant_info (basic_info_id, Effect  ,Reported  ,Exon   ,\
                            cDNA,RNA_change  ,Protein  ,Classification_method  ,\
                            Clinical_classification  ,DNA_change_hg19 ,DNA_change_hg38  ,\
                            Published_as  ,ISCN  ,DB_ID ,\
                            Variant_remarks  ,Reference  ,ClinVar_ID  ,\
                            dbSNP_ID  ,Origin  ,Segregation  ,\
                            Frequency  ,Re_site  ,VIP  ,\
                            Methylation  ,data_Owner  ,date_insert,date_update ) values (\
                            %s,%s,%s,%s,\
                            %s,%s,%s,%s,\
                            %s,%s,%s,\
                            %s,%s,%s,\
                            %s,%s,%s,\
                            %s,%s,%s,\
                            %s,%s,%s,\
                            %s,%s, now(),now()) RETURNING id; "
                cursor.execute(stm1,(basic_info_id,strEffect  ,strReported  ,strExon  ,
                strcDNA ,strRNA_change  ,strProtein  ,strClassification_method,
                strClinical_classification  ,strDNA_change_hg19 ,strDNA_change_hg38  ,
                strPublished_as  ,strISCN  ,strDB_ID ,
                strVariant_remarks  ,strReference  ,strClinVar_ID  ,
                strdbSNP_ID  ,strOrigin  ,strSegregation  ,
                strFrequency  ,strRe_site  ,strVIP  ,
                strMethylation  ,strdata_Owner   ))
                conn.commit()
            else:
                # we got rows!
                step = 70
                #insert item
                stm1 = "update  lovd_variant_info set  Effect  = %s ,Reported  = %s  ,Exon  = %s   ,\
                            RNA_change  = %s  ,Protein  = %s  ,Classification_method  = %s  ,\
                            Clinical_classification  = %s  ,DNA_change_hg19  = %s ,DNA_change_hg38  = %s  ,\
                            Published_as = %s   ,ISCN   = %s ,DB_ID = %s  ,\
                            Variant_remarks  = %s  ,Reference  = %s  ,ClinVar_ID   = %s ,\
                            dbSNP_ID  = %s  ,Origin   = %s ,Segregation  = %s  ,\
                            Frequency  = %s  ,Re_site = %s   ,VIP  = %s  ,\
                            Methylation   = %s ,data_Owner  = %s  ,date_update = now() where cDNA = %s and basic_info_id = %s; "
                cursor.execute(stm1,(strEffect  ,strReported  ,strExon  ,
                strRNA_change  ,strProtein  ,strClassification_method,
                strClinical_classification  ,strDNA_change_hg19 ,strDNA_change_hg38  ,
                strPublished_as  ,strISCN  ,strDB_ID ,
                strVariant_remarks  ,strReference  ,strClinVar_ID  ,
                strdbSNP_ID  ,strOrigin  ,strSegregation  ,
                strFrequency  ,strRe_site  ,strVIP  ,
                strMethylation  ,strdata_Owner  ,strcDNA,basic_info_id ))
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error,": Step:", step )

    
if __name__ == '__main__':
    br = initialize_browser()
    #    resp = browse_dbcline(br, genes = ['GCS1'])
    for gen_l_name in list_genref:
        strMutation = ""
        basic_info_id = get_initial_info_br(gen_l_name,br,strMutation)
        data = []
        get_variant_br(data,gen_l_name,basic_info_id,strMutation)
        time_wait = random.randint(500,1000)
        time.sleep(time_wait)
    driver.quit()
