import csv
import json
import os
import ntpath
import sys
# import the connect library from psycopg2
import psycopg2
from psycopg2 import connect
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def findFiles(rootDir):
    tsvFiles = []
    for path, subdirs, files in os.walk(rootDir):
        for x in files:
            if x.endswith(".tsv"):
                tsvFiles.append(os.path.join(path, x))  # create full path!
    return tsvFiles

def cargar_genes():
    query_trunc = "truncate table pharmgkb_genes;"
    query = "INSERT INTO pharmgkb_genes (PharmGKBAccessionId,NCBIGeneID,HGNCID,\
                EnsemblId,Name_val,Symbol,\
                AlternateNames,AlternateSymbols,IsVIP,\
                HasVariantAnnotation,Crossreferences,HasCPICDosingGuideline,\
                Chromosome,ChromosomalStartGRCh37,ChromosomalStopGRCh37,\
                ChromosomalStartGRCh38,ChromosomalStopGRCh38) \
                VALUES (%s, %s, %s, %s, %s, %s, \
                        %s, %s, %s, %s, %s , %s,\
                        %s, %s, %s, %s, %s)"
    return [query,query_trunc]
def cargar_chemicals():
    query_trunc = "truncate table pharmgkb_chemicals;"
    query = "insert into  pharmgkb_chemicals (PharmGKBAccessionId,Name_val,GenericNames,\
                            TradeNames,BrandMixtures,Type_val,\
                            Cross_references,SMILES,InChI,\
                            DosingGuideline,ExternalVocabulary,ClinicalAnnotationCount,\
                            VariantAnnotationCount,PathwayCount,VIPCount,\
                            DosingGuidelineSources,TopClinicalAnnotationLevel,TopFDALabelTestingLevel,\
                            TopAnyDrugLabelTestingLevel,LabelHasDosingInfo,HasRxAnnotation,\
                            RxNormIdentifiers,ATCIdentifiers,PubChemCompoundIdentifiers) \
                            values (%s, %s, %s, %s, %s, %s, \
                                    %s, %s, %s, %s, %s, %s, \
                                    %s, %s, %s, %s, %s, %s, \
                                    %s, %s, %s, %s, %s, %s)"  
    return [query,query_trunc]
def cargar_drugs():
    query_trunc = "truncate table pharmgkb_drugs;"
    query = "insert into  pharmgkb_drugs(PharmGKBAccessionId,Name_val,GenericNames,\
                            TradeNames,BrandMixtures,Type_val,\
                            Cross_references,SMILES,InChI,\
                            DosingGuideline,ExternalVocabulary,ClinicalAnnotationCount,\
                            VariantAnnotationCount,PathwayCount,VIPCount,\
                            DosingGuidelineSources,TopClinicalAnnotationLevel,TopFDALabelTestingLevel,\
                            TopAnyDrugLabelTestingLevel,LabelHasDosingInfo,HasRxAnnotation,\
                            RxNormIdentifiers,ATCIdentifiers,PubChemCompoundIdentifiers)\
                            values (%s, %s, %s, %s, %s, %s, \
                                    %s, %s, %s, %s, %s, %s, \
                                    %s, %s, %s, %s, %s, %s, \
                                    %s, %s, %s, %s, %s, %s)"  
    return [query,query_trunc]
def cargar_phenotypes():
    query_trunc = "truncate table pharmgkb_phenotypes;"
    query = "insert into pharmgkb_phenotypes(PharmGKBAccessionId,Name_val, \
                            AlternateNames,Cross_references,\
                            ExternalVocabulary) \
                            VALUES (%s, %s, %s, %s, %s)"
    return [query,query_trunc]
def cargar_relationships():
    query_trunc = "truncate table pharmgkb_relationships;"
    query = "INSERT INTO pharmgkb_relationships (Entity1_id ,Entity1_name  ,\
                    Entity1_type  ,Entity2_id  ,\
                    Entity2_name  , Entity2_type  ,\
                    Evidence  ,Association  ,\
                    PK  ,PD  ,   PMIDs) \
                VALUES (%s, %s, %s, %s, %s, %s, \
                        %s, %s, %s, %s, %s)"
    return [query,query_trunc]
def cargar_variants():
    query_trunc = "truncate table pharmgkb_variant;"
    query = "INSERT INTO pharmgkb_variant (VariantID,VariantName,GeneIDs,\
                GeneSymbols,Location,VariantAnnotationcount,\
                ClinicalAnnotationcount,Level1_2ClinicalAnnotationcount,GuidelineAnnotationcount,\
                LabelAnnotationcount,Synonyms ) \
                VALUES (%s, %s, %s, %s, %s, %s, \
                        %s, %s, %s, %s, %s)"
    return [query,query_trunc]
switcher = {
        "genes.tsv":  cargar_genes,
        "chemicals.tsv": cargar_chemicals,
        "drugs.tsv": cargar_drugs,
        "phenotypes.tsv":cargar_phenotypes,
        "relationships.tsv":cargar_relationships,
        "variants.tsv":cargar_variants
    }

def etl_query_select(argument):
    # Get the function from switcher dictionary
    print(argument)
    func = switcher.get(argument, "nothing")
    if func == "nothing":
        print("nothing")
        return ""
    else:
        # Execute the function
        return func()
def insert(tsvFilePath):
    #conexion a la bbdd
    conn = psycopg2.connect(user="tm",
                                password="eneas",
                                host="127.0.0.1",
                                port="5432",
                                database="hgmd")
    
    cursor = conn.cursor()
    tsvfilename = path_leaf(tsvFilePath)
    query = etl_query_select(tsvfilename)[0]
    query_trunc = etl_query_select(tsvfilename)[1]
    status = False
    if query == "":
        print(tsvFilePath , ": file for etl not in list" )

    else:
        with open(tsvFilePath,'r') as source:
            csv.field_size_limit(sys.maxsize)
            rdr= csv.reader( source, delimiter='\t', quotechar='"')
            try:
                cursor.execute(query_trunc)
                conn.commit()
                result = cursor.executemany(query, rdr)
                print(result)
                status = True
                conn.commit()
                print(cursor.rowcount, "Record inserted successfully into mobile table")
            except (Exception, psycopg2.Error) as error:
                print("Failed inserting record into mobile table {}".format(error))

            finally:
                # closing database connection.
                if conn:
                    cursor.close()
                    conn.close()
                    print("PostgreSQL connection is closed")
    if conn is not None:
        conn.close()
    return status


    
path = "./tsv"
tsvFiles = findFiles(path)

if not tsvFiles:
    print("No tsv files found!")
print(tsvFiles)
for tsvFile in tsvFiles:
    print("Processing: %s" % tsvFile)
    res = insert(tsvFile)
    # res holds true or false, so you could rename, move or delete the file:
    #if res:
    #   os.remove(fullPath)