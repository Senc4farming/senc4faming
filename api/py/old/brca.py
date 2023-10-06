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
    step = 10
    try:
        #Leemos los datos de la mutacion
        cursor.execute(f"select distinct ba.id, ba.title, mi.reference_sequence  from brca_basic_info ba \
                        join brca_main_info mi on mi.basic_info_id = ba.id where ba.title = '{genname}'") 
        rowd = cursor.fetchone()
        step = 20
        if rowd == None:
            step = 30
            print("Dato no encontrado se carga o actualiza para el proceso batch")
            #Si ya existe se consulta la bbdd y se marca para actualizar
            cursor.execute(f"SELECT * FROM gen_to_check where genid = '{genname}' and origin = 'brca'; ")
            row = cursor.fetchone()
            #si encuentro un registro lo marco para actualizar
            if row == None:
                #si no exite lo inserto
                #insert item
                print("insert")
                ins_stm1 = "insert into gen_to_check (genid, check_for_update,"\
                            " date_insert, date_update,origin) values (%s, 1, now(), now(),'brca'); "
                cursor.execute(ins_stm1,(genname,))
                print("despues insert")
            else:
                #Actualiza el registro para que de actualice
                print("update")
                upd_stm1 = "update gen_to_check  set check_for_update = 1, date_update = now()"\
                                " where  genid = %s and origin = 'brca'; "
                cursor.execute(upd_stm1,(genname,))
                conn.commit()
            data.append({"genid":genname, "data": "No information found recharge in 24 hours"})
        else:
            step = 40
            strMutation = str(rowd[2]).replace(" ","") 
            basic_info_id = rowd[0]
            #write row into a dict
            d_basic  = dict()
            
            
            strMutation = str(rowd[2]).replace(" ","")
            
            #creamos el bloque inicial
            data.append({"genid":genname, "data":{"Mutation": strMutation,"info": []}})
            #añadimos datos de variant lovd_variant_info
            step = 45
            cursor.execute(f"SELECT id_brca ,Gene_Symbol ,Reference_Sequence ,\
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
                        Classification_LOVD,date_insert,date_update  FROM brca_main_info  where basic_info_id = {basic_info_id};") 
            step = 48
            rows2 = cursor.fetchall()
            step = 50
            print("Print each row and it's columns values")
            for row2 in rows2:
                d_info = dict()
                d_info["id_brca"] = str(row2[1])
                d_info["Gene_Symbol"] = str(row2[2])
                d_info["Reference_Sequence"] = str(row2[3])
                d_info["HGVS_cDNA"] = str(row2[4])
                d_info["BIC_Nomenclature"] = str(row2[5])
                d_info["HGVS_Protein"] = str(row2[6])
                d_info["HGVS_RNA"] = str(row2[7])
                d_info["Protein_Change"] = str(row2[8])
                d_info["Allele_Frequency"] = str(row2[9])
                d_info["Max_Allele_Frequency"] = str(row2[10])
                d_info["Genomic_Coordinate_hg38"] = str(row2[11])
                d_info["Hg38_Start"] = str(row2[12])
                d_info["Hg38_End"] = str(row2[13])
                d_info["Hg37_Start"] = str(row2[14])
                d_info["Hg37_End"] = str(row2[15])
                d_info["Genomic_Coordinate_hg37"] = str(row2[16])
                d_info["Genomic_HGVS_38"] = str(row2[17])
                d_info["Genomic_HGVS_37"] = str(row2[18])
                d_info["Source_URL"] = str(row2[19])
                d_info["Discordant"] = str(row2[20])
                d_info["Synonyms"] = str(row2[21])
                d_info["Pathogenicity_expert"] = str(row2[22])
                d_info["Pathogenicity_all"] = str(row2[23])
                d_info["Chr"] = str(row2[24])
                d_info["Pos"] = str(row2[25])
                d_info["Ref"] = str(row2[26])
                d_info["Alt"] = str(row2[27])
                d_info["Polyphen_Prediction"] = str(row2[28])
                d_info["Polyphen_Score"] = str(row2[29])
                d_info["Sift_Score"] = str(row2[30])
                d_info["Sift_Prediction"] = str(row2[31])
                d_info["BX_ID_ENIGMA_BRCA12_Functional_Assays"] = str(row2[32])
                d_info["BX_ID_ENIGMA"] = str(row2[33])
                d_info["BX_ID_LOVD"] = str(row2[34])
                d_info["BX_ID_ESP"] = str(row2[35])
                d_info["BX_ID_BIC"] = str(row2[36])
                d_info["BX_ID_ClinVar"] = str(row2[37])
                d_info["BX_ID_1000_Genomes"] = str(row2[38])
                d_info["BX_ID_ExAC"] = str(row2[39])
                d_info["BX_ID_exLOVD"] = str(row2[40])
                d_info["BX_ID_GnomAD"] = str(row2[41])
                d_info["BX_ID_Findlay_BRCA1_Ring_Function_Scores"] = str(row2[42])
                d_info["BX_ID_GnomADv3"] = str(row2[43])
                d_info["VR_ID"] = str(row2[44])
                d_info["Mupit_Structure_id"] = str(row2[45])
                d_info["CA_ID"] = str(row2[46])
                d_info["BayesDel_nsfp33a_noAF"] = str(row2[47])
                d_info["Data_Release_id"] = str(row2[48])
                d_info["Variant_in_ENIGMA"] = str(row2[49])
                d_info["Variant_in_ClinVar"] = str(row2[50])
                d_info["Variant_in_1000_Genomes"] = str(row2[51])
                d_info["Variant_in_ExAC"] = str(row2[52])
                d_info["Variant_in_LOVD"] = str(row2[53])
                d_info["Variant_in_BIC"] = str(row2[54])
                d_info["Variant_in_ESP"] = str(row2[55])
                d_info["Variant_in_exLOVD"] = str(row2[56])
                d_info["Variant_in_Findlay_BRCA1_Ring_Function_Scores"] = str(row2[57])
                d_info["Variant_in_ENIGMA_BRCA12_Functional_Assays"] = str(row2[58])
                d_info["Variant_in_GnomAD"] = str(row2[59])
                d_info["Variant_in_GnomADv3"] = str(row2[60])
                d_info["Source"] = str(row2[61])
                d_info["URL_ENIGMA"] = str(row2[62])
                d_info["Condition_ID_type_ENIGMA"] = str(row2[63])
                d_info["Condition_ID_value_ENIGMA"] = str(row2[64])
                d_info["Condition_category_ENIGMA"] = str(row2[65])
                d_info["Clinical_significance_ENIGMA"] = str(row2[66])
                d_info["Date_last_evaluated_ENIGMA"] = str(row2[67])
                d_info["Assertion_method_ENIGMA"] = str(row2[68])
                d_info["Assertion_method_citation_ENIGMA"] = str(row2[69])
                d_info["Clinical_significance_citations_ENIGMA"] = str(row2[70])
                d_info["Comment_on_clinical_significance_ENIGMA"] = str(row2[71])
                d_info["Collection_method_ENIGMA"] = str(row2[72])
                d_info["Allele_origin_ENIGMA"] = str(row2[73])
                d_info["ClinVarAccession_ENIGMA"] = str(row2[74])
                d_info["Clinical_Significance_ClinVar"] = str(row2[75])
                d_info["Date_Last_Updated_ClinVar"] = str(row2[76])
                d_info["Submitter_ClinVar"] = str(row2[77])
                d_info["SCV_ClinVar"] = str(row2[78])
                d_info["Allele_Origin_ClinVar"] = str(row2[79])
                d_info["Method_ClinVar"] = str(row2[80])
                d_info["Functional_analysis_technique_LOVD"] = str(row2[81])
                d_info["Functional_analysis_result_LOVD"] = str(row2[82])
                d_info["Variant_frequency_LOVD"] = str(row2[83])
                d_info["Variant_haplotype_LOVD"] = str(row2[84])
                d_info["HGVS_cDNA_LOVD"] = str(row2[85])
                d_info["HGVS_protein_LOVD"] = str(row2[86])
                d_info["Individuals_LOVD"] = str(row2[87])
                d_info["Variant_effect_LOVD"] = str(row2[88])
                d_info["Genetic_origin_LOVD"] = str(row2[89])
                d_info["RNA_LOVD"] = str(row2[90])
                d_info["Submitters_LOVD"] = str(row2[91])
                d_info["Created_date_LOVD"] = str(row2[92])
                d_info["Edited_date_LOVD"] = str(row2[93])
                d_info["DBID_LOVD"] = str(row2[94])
                d_info["Remarks_LOVD"] = str(row2[95])
                d_info["Classification_LOVD"] = str(row2[96])
                data[0]["data"]["info"].append(d_info)
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error,"; step :", step)      
    
    cursor.close()
    conn.close()

def get_brca(genid,data):
    obtenerDatos(genid,data)

    