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
https://brcaexchange.org/backend/data/
?format=json
&filter=Pathogenicity_expert
&filterValue=Pathogenic
&filter=Gene_Symbol
&filterValue=*gen*&order_by=Gene_Symbol
&direction=ascending&page_size=100
&page_num=0&search_term=
&include=Variant_in_ENIGMA&include=Variant_in_ClinVar
&include=Variant_in_1000_Genomes&include=Variant_in_ExAC
&include=Variant_in_LOVD&include=Variant_in_BIC
&include=Variant_in_ESP&include=Variant_in_exLOVD
&include=Variant_in_ENIGMA_BRCA12_Functional_Assays&include=Variant_in_GnomAD
"""


list_genref = ['BRCA1','BRCA2']

email_address = "jmafernanez@ubu.es"
step  = 0

def get_initial_info(conn, cursor, gen_name ):
    
    step = 40
    try:
        #Si ya existe se consulta la bbdd y se marca para actualizar
        s_stm1 = "SELECT * FROM brca_basic_info where title = %s; "
        cursor.execute(s_stm1,(gen_name,))
        rows = cursor.fetchone()
        stm1 = ''
        step = 50
        #si encuentro un registro lo marco para actualizar
        if rows == None:
            print("Dato no encontrado se carga o actualiza para el proceso batch")
            #Si ya existe se consulta la bbdd y se marca para actualizar
            cursor.execute(f"SELECT * FROM gen_to_check where genid = '{gen_name}' and origin = 'brca'; ")
            row_1 = cursor.fetchone()
            #si encuentro un registro lo marco para actualizar
            if row_1 == None:
                #si no exite lo inserto
                #insert item
                ins_stm1 = "insert into gen_to_check (genid, check_for_update,"\
                            " date_insert, date_update,origin) values (%s, 1, now(), now(),'brca'); "
                cursor.execute(ins_stm1,(gen_name,))
            else:
                #Actualiza el registro para que de actualice
                upd_stm1 = "update gen_to_check  set check_for_update = 1, date_update = now()"\
                                " where  genid = %s and origin = 'brca'; "
                cursor.execute(upd_stm1,(gen_name,))
            step = 60
            #insert item
            stm1 = "insert into brca_basic_info ( title ,date_insert,date_update) values (\
                        %s,now(),now()) RETURNING id; "
            cursor.execute(stm1,(gen_name ,  ))
            conn.commit()
            basic_info_id =  cursor.fetchone()[0]
        else:
            # we got rows!
            basic_info_id =  rows[0]
            step = 70
            #insert item
            stm1 = "update  lovd_basic_info set date_update = now() where title = %s ; "
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
    #print(results)
    update_db_info(results,cursor,conn,basic_info_id  )
    
    number_of_items = results['count']
    print("Number of pathogenic variants: %d"% results['count'])
    #print(results)
    number_of_pages = int(number_of_items/100)
    num_page = 1
    query_next = query_ini
    while num_page <= number_of_pages:
        str_num_page_next = 'page_num=' + str(num_page)
        str_num_page_prev = 'page_num=' + str(num_page -1)
        query_next = query_next.replace(str_num_page_prev, str_num_page_next)
        print (query_next)
        results = rq.get(query_next).json()
        print("Number of pathogenic variants: %d"% results['count'])
        update_db_info(results,cursor,conn,basic_info_id  )
        num_page = num_page+1
def update_db_info(results,cursor,conn,basic_info_id ):
    #read info from json and update db
    #Load JSON string into a dictionary
    for item in results["data"]:
        #print (item["id"])
        str_id_brca = item["id"]
        str_Gene_Symbol =item["Gene_Symbol"][:100]
        str_Reference_Sequence =item["Reference_Sequence"][:100]
        str_HGVS_cDNA =item["HGVS_cDNA"][:100]
        str_BIC_Nomenclature =item["BIC_Nomenclature"][:100]
        str_HGVS_Protein =item["HGVS_Protein"][:100]
        str_HGVS_RNA =item["HGVS_RNA"][:100]
        str_Protein_Change =item["Protein_Change"][:100]
        str_Allele_Frequency =item["Allele_Frequency"][:100]
        str_Max_Allele_Frequency =item["Max_Allele_Frequency"][:100]
        str_Genomic_Coordinate_hg38 =item["Genomic_Coordinate_hg38"][:100]
        str_Hg38_Start =item["Hg38_Start"]
        str_Hg38_End =item["Hg38_End"]
        str_Hg37_Start =item["Hg37_Start"]
        str_Hg37_End =item["Hg37_End"]
        str_Genomic_Coordinate_hg37 =item["Genomic_Coordinate_hg37"][:100]
        str_Genomic_HGVS_38 =item["Genomic_HGVS_38"][:100]
        str_Genomic_HGVS_37 =item["Genomic_HGVS_37"][:100]
        str_Source_URL =item["Source_URL"][:2000]
        str_Discordant =item["Discordant"][:100]
        str_Synonyms =item["Synonyms"][:2000]
        str_Pathogenicity_expert =item["Pathogenicity_expert"][:100]
        str_Pathogenicity_all =item["Pathogenicity_all"][:100]
        str_Chr =item["Chr"][:100]
        str_Pos =item["Pos"][:100]
        str_Ref =item["Ref"][:100]
        str_Alt =item["Alt"][:100]
        str_Polyphen_Prediction =item["Polyphen_Prediction"][:100]
        str_Polyphen_Score =item["Polyphen_Score"][:100]
        str_Sift_Score =item["Sift_Score"][:100]
        str_Sift_Prediction =item["Sift_Prediction"][:100]
        str_BX_ID_ENIGMA_BRCA12_Functional_Assays =item["BX_ID_ENIGMA_BRCA12_Functional_Assays"]
        str_BX_ID_ENIGMA =item["BX_ID_ENIGMA"][:100]
        str_BX_ID_LOVD =item["BX_ID_LOVD"][:1000]
        str_BX_ID_ESP =item["BX_ID_ESP"][:100]
        str_BX_ID_BIC =item["BX_ID_BIC"][:1000]
        str_BX_ID_ClinVar =item["BX_ID_ClinVar"][:1000]
        str_BX_ID_1000_Genomes =item["BX_ID_1000_Genomes"][:100]
        str_BX_ID_ExAC =item["BX_ID_ExAC"][:100]
        str_BX_ID_exLOVD =item["BX_ID_exLOVD"][:100]
        str_BX_ID_GnomAD =item["BX_ID_GnomAD"][:100]
        str_BX_ID_Findlay_BRCA1_Ring_Function_Scores =item["BX_ID_Findlay_BRCA1_Ring_Function_Scores"][:100]
        str_BX_ID_GnomADv3 =item["BX_ID_GnomADv3"]
        str_VR_ID =item["VR_ID"][:100]
        str_Mupit_Structure_id =item["Mupit_Structure_id"]
        str_CA_ID =item["CA_ID"][:100]
        str_BayesDel_nsfp33a_noAF =item["BayesDel_nsfp33a_noAF"]
        str_Data_Release_id =item["Data_Release_id"]
        str_Variant_in_ENIGMA =item["Variant_in_ENIGMA"]
        str_Variant_in_ClinVar =item["Variant_in_ClinVar"]
        str_Variant_in_1000_Genomes =item["Variant_in_1000_Genomes"]
        str_Variant_in_ExAC =item["Variant_in_ExAC"]
        str_Variant_in_LOVD =item["Variant_in_LOVD"]
        str_Variant_in_BIC =item["Variant_in_BIC"]
        str_Variant_in_ESP =item["Variant_in_ESP"]
        str_Variant_in_exLOVD =item["Variant_in_exLOVD"]
        str_Variant_in_Findlay_BRCA1_Ring_Function_Scores = item["Variant_in_Findlay_BRCA1_Ring_Function_Scores"]
        str_Variant_in_ENIGMA_BRCA12_Functional_Assays =item["Variant_in_ENIGMA_BRCA12_Functional_Assays"]
        str_Variant_in_GnomAD =item["Variant_in_GnomAD"]
        str_Variant_in_GnomADv3 =item["Variant_in_GnomADv3"]
        str_Source =item["Source"][:100]
        str_URL_ENIGMA =item["URL_ENIGMA"][:100]
        str_Condition_ID_type_ENIGMA =item["Condition_ID_type_ENIGMA"][:100]
        str_Condition_ID_value_ENIGMA =item["Condition_ID_value_ENIGMA"][:100]
        str_Condition_category_ENIGMA =item["Condition_category_ENIGMA"][:100]
        str_Clinical_significance_ENIGMA =item["Clinical_significance_ENIGMA"][:100]
        str_Date_last_evaluated_ENIGMA =item["Date_last_evaluated_ENIGMA"][:100]
        str_Assertion_method_ENIGMA =item["Assertion_method_ENIGMA"][:100]
        str_Assertion_method_citation_ENIGMA =item["Assertion_method_citation_ENIGMA"][:100]
        str_Clinical_significance_citations_ENIGMA =item["Clinical_significance_citations_ENIGMA"][:100]
        str_Comment_on_clinical_significance_ENIGMA =item["Comment_on_clinical_significance_ENIGMA"][:100]
        str_Collection_method_ENIGMA =item["Collection_method_ENIGMA"][:100]
        str_Allele_origin_ENIGMA =item["Allele_origin_ENIGMA"][:100]
        str_ClinVarAccession_ENIGMA =item["ClinVarAccession_ENIGMA"][:100]
        str_Clinical_Significance_ClinVar =item["Clinical_Significance_ClinVar"][:100]
        str_Date_Last_Updated_ClinVar =item["Date_Last_Updated_ClinVar"][:100]
        str_Submitter_ClinVar =item["Submitter_ClinVar"][:2000]
        str_SCV_ClinVar =item["SCV_ClinVar"][:100]
        str_Allele_Origin_ClinVar =item["Allele_Origin_ClinVar"][:100]
        str_Method_ClinVar =item["Method_ClinVar"][:100]
        str_Functional_analysis_technique_LOVD =item["Functional_analysis_technique_LOVD"][:100]
        str_Functional_analysis_result_LOVD =item["Functional_analysis_result_LOVD"][:100]
        str_Variant_frequency_LOVD =item["Variant_frequency_LOVD"][:100]
        str_Variant_haplotype_LOVD =item["Variant_haplotype_LOVD"][:100]
        str_HGVS_cDNA_LOVD =item["HGVS_cDNA_LOVD"][:100]
        str_HGVS_protein_LOVD =item["HGVS_protein_LOVD"][:100]
        str_Individuals_LOVD =item["Individuals_LOVD"][:100]
        str_Variant_effect_LOVD =item["Variant_effect_LOVD"][:100]
        str_Genetic_origin_LOVD =item["Genetic_origin_LOVD"][:100]
        str_RNA_LOVD =item["RNA_LOVD"] 	[:100]
        str_Submitters_LOVD =item["Submitters_LOVD"][:2000]
        str_Created_date_LOVD =item["Created_date_LOVD"][:100]
        str_Edited_date_LOVD =item["Edited_date_LOVD"][:100]
        str_DBID_LOVD =item["DBID_LOVD"][:100]
        str_Remarks_LOVD =item["Remarks_LOVD"][:100]
        str_Classification_LOVD =item["Classification_LOVD"][:100]
        step = 40
        try:
            #Si ya existe se consulta la bbdd y se marca para actualizar
            s_stm1 = "SELECT * FROM brca_main_info where  basic_info_id = %s and id_brca = %s ; "
            cursor.execute(s_stm1,(basic_info_id,str_id_brca))
            rows = cursor.fetchone()
            stm1 = ''
            step = 50
            #si encuentro un registro lo marco para actualizar
            if rows == None:
                try:
                    step = 60
                    #print("el elemento no existe:", basic_info_id,str_id_brca)
                    #insert item
                    stm1 = ''
                    stm1 = "insert into brca_main_info (basic_info_id,id_brca ,Gene_Symbol ,Reference_Sequence ,\
                        HGVS_cDNA ,BIC_Nomenclature ,HGVS_Protein ,\
                        HGVS_RNA ,Protein_Change ,Allele_Frequency ,\
                        Max_Allele_Frequency ,Genomic_Coordinate_hg38 ,Hg38_Start ,\
                        Hg38_End ,Hg37_Start ,Hg37_End ,\
                        Genomic_Coordinate_hg37 ,Genomic_HGVS_38 ,Genomic_HGVS_37 ,\
                        Source_URL ,Discordant ,Synonyms ,\
                        Pathogenicity_expert ,Pathogenicity_all ,Chr ,\
                        Pos ,Ref ,Alt ,\
                        Polyphen_Prediction ,Polyphen_Score ,\
                        Sift_Score ,Sift_Prediction ,BX_ID_ENIGMA_BRCA12_Functional_Assays ,\
                        BX_ID_ENIGMA ,BX_ID_LOVD ,BX_ID_ESP ,\
                        BX_ID_BIC ,BX_ID_ClinVar ,BX_ID_1000_Genomes ,\
                        BX_ID_ExAC ,BX_ID_exLOVD ,BX_ID_GnomAD ,\
                        BX_ID_Findlay_BRCA1_Ring_Function_Scores ,BX_ID_GnomADv3 ,VR_ID ,\
                        Mupit_Structure_id ,CA_ID ,BayesDel_nsfp33a_noAF ,\
                        Data_Release_id ,Variant_in_ENIGMA ,Variant_in_ClinVar ,\
                        Variant_in_1000_Genomes ,Variant_in_ExAC ,Variant_in_LOVD ,\
                        Variant_in_BIC ,Variant_in_ESP ,Variant_in_exLOVD ,\
                        Variant_in_Findlay_BRCA1_Ring_Function_Scores,Variant_in_ENIGMA_BRCA12_Functional_Assays ,Variant_in_GnomAD ,\
                        Variant_in_GnomADv3 ,Source ,URL_ENIGMA ,\
                        Condition_ID_type_ENIGMA ,Condition_ID_value_ENIGMA ,Condition_category_ENIGMA ,\
                        Clinical_significance_ENIGMA ,Date_last_evaluated_ENIGMA ,Assertion_method_ENIGMA ,\
                        Assertion_method_citation_ENIGMA ,Clinical_significance_citations_ENIGMA ,Comment_on_clinical_significance_ENIGMA ,\
                        Collection_method_ENIGMA ,Allele_origin_ENIGMA ,ClinVarAccession_ENIGMA ,\
                        Clinical_Significance_ClinVar ,Date_Last_Updated_ClinVar ,Submitter_ClinVar ,\
                        SCV_ClinVar ,Allele_Origin_ClinVar ,Method_ClinVar ,\
                        Functional_analysis_technique_LOVD ,Functional_analysis_result_LOVD ,Variant_frequency_LOVD ,\
                        Variant_haplotype_LOVD ,HGVS_cDNA_LOVD ,HGVS_protein_LOVD ,\
                        Individuals_LOVD ,Variant_effect_LOVD ,Genetic_origin_LOVD ,\
                        RNA_LOVD ,Submitters_LOVD ,Created_date_LOVD ,\
                        Edited_date_LOVD ,DBID_LOVD ,Remarks_LOVD ,\
                        Classification_LOVD,date_insert,date_update) values (\
                                %s,%s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                %s,%s,%s,%s,%s,%s,\
                                now(),now()) RETURNING id; "
                    cursor.execute(stm1,(basic_info_id,str_id_brca ,str_Gene_Symbol ,str_Reference_Sequence ,
                        str_HGVS_cDNA ,str_BIC_Nomenclature ,str_HGVS_Protein ,
                        str_HGVS_RNA ,str_Protein_Change ,str_Allele_Frequency ,
                        str_Max_Allele_Frequency ,str_Genomic_Coordinate_hg38 ,str_Hg38_Start ,
                        str_Hg38_End ,str_Hg37_Start ,str_Hg37_End ,
                        str_Genomic_Coordinate_hg37 ,str_Genomic_HGVS_38 ,str_Genomic_HGVS_37 ,
                        str_Source_URL ,str_Discordant ,str_Synonyms ,
                        str_Pathogenicity_expert ,str_Pathogenicity_all ,str_Chr ,
                        str_Pos ,str_Ref ,str_Alt ,
                        str_Polyphen_Prediction ,str_Polyphen_Score,
                        str_Sift_Score ,str_Sift_Prediction ,str_BX_ID_ENIGMA_BRCA12_Functional_Assays ,
                        str_BX_ID_ENIGMA ,str_BX_ID_LOVD ,str_BX_ID_ESP ,
                        str_BX_ID_BIC ,str_BX_ID_ClinVar ,str_BX_ID_1000_Genomes ,
                        str_BX_ID_ExAC ,str_BX_ID_exLOVD ,str_BX_ID_GnomAD ,
                        str_BX_ID_Findlay_BRCA1_Ring_Function_Scores ,str_BX_ID_GnomADv3 ,str_VR_ID ,
                        str_Mupit_Structure_id ,str_CA_ID ,str_BayesDel_nsfp33a_noAF ,
                        str_Data_Release_id ,str_Variant_in_ENIGMA ,str_Variant_in_ClinVar ,
                        str_Variant_in_1000_Genomes ,str_Variant_in_ExAC ,str_Variant_in_LOVD ,
                        str_Variant_in_BIC ,str_Variant_in_ESP ,str_Variant_in_exLOVD ,
                        str_Variant_in_Findlay_BRCA1_Ring_Function_Scores,str_Variant_in_ENIGMA_BRCA12_Functional_Assays ,str_Variant_in_GnomAD ,
                        str_Variant_in_GnomADv3 ,str_Source ,str_URL_ENIGMA ,
                        str_Condition_ID_type_ENIGMA ,str_Condition_ID_value_ENIGMA ,str_Condition_category_ENIGMA ,
                        str_Clinical_significance_ENIGMA ,str_Date_last_evaluated_ENIGMA ,str_Assertion_method_ENIGMA ,
                        str_Assertion_method_citation_ENIGMA ,str_Clinical_significance_citations_ENIGMA ,str_Comment_on_clinical_significance_ENIGMA ,
                        str_Collection_method_ENIGMA ,str_Allele_origin_ENIGMA ,str_ClinVarAccession_ENIGMA ,
                        str_Clinical_Significance_ClinVar ,str_Date_Last_Updated_ClinVar ,str_Submitter_ClinVar ,
                        str_SCV_ClinVar ,str_Allele_Origin_ClinVar ,str_Method_ClinVar ,
                        str_Functional_analysis_technique_LOVD ,str_Functional_analysis_result_LOVD ,str_Variant_frequency_LOVD ,
                        str_Variant_haplotype_LOVD ,str_HGVS_cDNA_LOVD ,str_HGVS_protein_LOVD ,
                        str_Individuals_LOVD ,str_Variant_effect_LOVD ,str_Genetic_origin_LOVD ,
                        str_RNA_LOVD ,str_Submitters_LOVD ,str_Created_date_LOVD ,
                        str_Edited_date_LOVD ,str_DBID_LOVD ,str_Remarks_LOVD ,
                        str_Classification_LOVD			        ))
                    conn.commit()
                except Exception as err:
                    print ("Oops! An exception has occured:", error)
                    print ("Exception TYPE:", type(error))
            else:
                # we got rows!
                step = 70
                #print("el elemento  existe:", basic_info_id,str_id_brca)
                #insert item
                stm2 = ''
                stm2 = "update  brca_main_info set Gene_Symbol = %s,Reference_Sequence = %s,\
                    HGVS_cDNA = %s,BIC_Nomenclature = %s,HGVS_Protein = %s,\
                    HGVS_RNA = %s,Protein_Change = %s,Allele_Frequency = %s,\
                    Max_Allele_Frequency = %s,Genomic_Coordinate_hg38 = %s,Hg38_Start = %s,\
                    Hg38_End = %s,Hg37_Start = %s,Hg37_End = %s,\
                    Genomic_Coordinate_hg37 = %s,Genomic_HGVS_38 = %s,Genomic_HGVS_37 = %s,\
                    Source_URL = %s,Discordant = %s,Synonyms = %s,\
                    Pathogenicity_expert = %s,Pathogenicity_all = %s,Chr = %s,\
                    Pos = %s,Ref = %s,Alt = %s,\
                    Polyphen_Prediction = %s,Polyphen_Score = %s,\
                    Sift_Score = %s,Sift_Prediction = %s,BX_ID_ENIGMA_BRCA12_Functional_Assays = %s,\
                    BX_ID_ENIGMA = %s,BX_ID_LOVD = %s,BX_ID_ESP = %s,\
                    BX_ID_BIC = %s,BX_ID_ClinVar = %s,BX_ID_1000_Genomes = %s,\
                    BX_ID_ExAC = %s,BX_ID_exLOVD = %s,BX_ID_GnomAD = %s,\
                    BX_ID_Findlay_BRCA1_Ring_Function_Scores = %s,BX_ID_GnomADv3 = %s,VR_ID = %s,\
                    Mupit_Structure_id = %s,CA_ID = %s,BayesDel_nsfp33a_noAF = %s,\
                    Data_Release_id = %s,Variant_in_ENIGMA = %s,Variant_in_ClinVar = %s,\
                    Variant_in_1000_Genomes = %s,Variant_in_ExAC = %s,Variant_in_LOVD = %s,\
                    Variant_in_BIC = %s,Variant_in_ESP = %s,Variant_in_exLOVD = %s,\
                    Variant_in_Findlay_BRCA1_Ring_Function_Scores= %s,Variant_in_ENIGMA_BRCA12_Functional_Assays = %s,Variant_in_GnomAD = %s,\
                    Variant_in_GnomADv3 = %s,Source = %s,URL_ENIGMA = %s,\
                    Condition_ID_type_ENIGMA = %s,Condition_ID_value_ENIGMA = %s,Condition_category_ENIGMA = %s,\
                    Clinical_significance_ENIGMA = %s,Date_last_evaluated_ENIGMA = %s,Assertion_method_ENIGMA = %s,\
                    Assertion_method_citation_ENIGMA = %s,Clinical_significance_citations_ENIGMA = %s,Comment_on_clinical_significance_ENIGMA = %s,\
                    Collection_method_ENIGMA = %s,Allele_origin_ENIGMA = %s,ClinVarAccession_ENIGMA = %s,\
                    Clinical_Significance_ClinVar = %s,Date_Last_Updated_ClinVar = %s,Submitter_ClinVar = %s,\
                    SCV_ClinVar = %s,Allele_Origin_ClinVar = %s,Method_ClinVar = %s,\
                    Functional_analysis_technique_LOVD = %s,Functional_analysis_result_LOVD = %s,Variant_frequency_LOVD = %s,\
                    Variant_haplotype_LOVD = %s,HGVS_cDNA_LOVD = %s,HGVS_protein_LOVD = %s,\
                    Individuals_LOVD = %s,Variant_effect_LOVD = %s,Genetic_origin_LOVD = %s,\
                    RNA_LOVD = %s,Submitters_LOVD = %s,Created_date_LOVD = %s,\
                    Edited_date_LOVD = %s,DBID_LOVD = %s,Remarks_LOVD = %s,\
                    Classification_LOVD = %s  ,date_update = now() where  basic_info_id = %s  and id_brca = %s  ; "
                cursor.execute(stm2,( str_Gene_Symbol ,str_Reference_Sequence ,
                    str_HGVS_cDNA ,str_BIC_Nomenclature ,str_HGVS_Protein ,
                    str_HGVS_RNA ,str_Protein_Change ,str_Allele_Frequency ,
                    str_Max_Allele_Frequency ,str_Genomic_Coordinate_hg38 ,str_Hg38_Start ,
                    str_Hg38_End ,str_Hg37_Start ,str_Hg37_End ,
                    str_Genomic_Coordinate_hg37 ,str_Genomic_HGVS_38 ,str_Genomic_HGVS_37 ,
                    str_Source_URL ,str_Discordant ,str_Synonyms ,
                    str_Pathogenicity_expert ,str_Pathogenicity_all ,str_Chr ,
                    str_Pos ,str_Ref ,str_Alt ,
                    str_Polyphen_Prediction ,str_Polyphen_Score,
                    str_Sift_Score ,str_Sift_Prediction ,str_BX_ID_ENIGMA_BRCA12_Functional_Assays ,
                    str_BX_ID_ENIGMA ,str_BX_ID_LOVD ,str_BX_ID_ESP ,
                    str_BX_ID_BIC ,str_BX_ID_ClinVar ,str_BX_ID_1000_Genomes ,
                    str_BX_ID_ExAC ,str_BX_ID_exLOVD ,str_BX_ID_GnomAD ,
                    str_BX_ID_Findlay_BRCA1_Ring_Function_Scores ,str_BX_ID_GnomADv3 ,str_VR_ID ,
                    str_Mupit_Structure_id ,str_CA_ID ,str_BayesDel_nsfp33a_noAF ,
                    str_Data_Release_id ,str_Variant_in_ENIGMA ,str_Variant_in_ClinVar ,
                    str_Variant_in_1000_Genomes ,str_Variant_in_ExAC ,str_Variant_in_LOVD ,
                    str_Variant_in_BIC ,str_Variant_in_ESP ,str_Variant_in_exLOVD ,
                    str_Variant_in_Findlay_BRCA1_Ring_Function_Scores,str_Variant_in_ENIGMA_BRCA12_Functional_Assays ,str_Variant_in_GnomAD ,
                    str_Variant_in_GnomADv3 ,str_Source ,str_URL_ENIGMA ,
                    str_Condition_ID_type_ENIGMA ,str_Condition_ID_value_ENIGMA ,str_Condition_category_ENIGMA ,
                    str_Clinical_significance_ENIGMA ,str_Date_last_evaluated_ENIGMA ,str_Assertion_method_ENIGMA ,
                    str_Assertion_method_citation_ENIGMA ,str_Clinical_significance_citations_ENIGMA ,str_Comment_on_clinical_significance_ENIGMA ,
                    str_Collection_method_ENIGMA ,str_Allele_origin_ENIGMA ,str_ClinVarAccession_ENIGMA ,
                    str_Clinical_Significance_ClinVar ,str_Date_Last_Updated_ClinVar ,str_Submitter_ClinVar ,
                    str_SCV_ClinVar ,str_Allele_Origin_ClinVar ,str_Method_ClinVar ,
                    str_Functional_analysis_technique_LOVD ,str_Functional_analysis_result_LOVD ,str_Variant_frequency_LOVD ,
                    str_Variant_haplotype_LOVD ,str_HGVS_cDNA_LOVD ,str_HGVS_protein_LOVD ,
                    str_Individuals_LOVD ,str_Variant_effect_LOVD ,str_Genetic_origin_LOVD ,
                    str_RNA_LOVD ,str_Submitters_LOVD ,str_Created_date_LOVD ,
                    str_Edited_date_LOVD ,str_DBID_LOVD ,str_Remarks_LOVD ,
                    str_Classification_LOVD			   ,basic_info_id ,str_id_brca))
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
        
    
