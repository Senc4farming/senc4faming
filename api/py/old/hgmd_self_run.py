#!/usr/bin/env python
from ast import excepthandler
from stat import FILE_ATTRIBUTE_SPARSE_FILE
import mechanize

import json # import json library
#Gestión de imagenes
from PIL import Image
#from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import copy
import os
import pytesseract 
# import the connect library from psycopg2
import psycopg2
from psycopg2 import connect

from io import BytesIO

# request url

from selenium import webdriver
import time
import json

try:
    import cookielib
except:
    import http.cookiejar
    cookielib = http.cookiejar

import sys
hgmd_url_base = "http://www.hgmd.cf.ac.uk"
hgmd_login_url = "http://www.hgmd.cf.ac.uk/docs/login.html"
hgmd_gen_url = "http://www.hgmd.cf.ac.uk/ac/gene.php?gene="
hgmd_url_all="http://www.hgmd.cf.ac.uk/ac/all.php"
#database =['Missense/nonsense','Splicing','Regulatory']
email_address = "jmafernandez@ubu.es"
password = "HGMD895679*"
#genRef ="BRCA1"
#genRef ="PSEN1"
#genRef ="MUTYH"
#genRef ="POLD1"
list_genref = ['POLD1']

#'ARID1A','ATM','ATRX','APC','BARD1','BRCA1','BRCA2','BRIP1','CD274','CDH1','CDK4','CDK6','CDK12','CDKN2A','CHEK2','EPCAM','ERBB2','MET',
#'MLH1','MSH2','MSH6','MUTYH','NBN','NTRK1','NTRK2','NTRK3','PALB2','PDCD1LG2','PMS2','POLD1','POLE','PTEN','RAD51C','RAD51D','RET','STK11','VHL'
#modificamos webdriver


driver = webdriver.Chrome()
dict_images={}
#cap = DesiredCapabilities.CHROME 
#driver= webdriver.Remote(command_executor='http://localhost:4444/', desired_capabilities=cap)
#driver_back = webdriver.Remote(command_executor='http://localhost:4444/', desired_capabilities=cap)

 



def obtenerImagenes(data,dict_images):
    driver.get(hgmd_login_url)
    driver.find_element(By.NAME,'email').send_keys(email_address)
    driver.find_element(By.NAME,'password').send_keys(password)

    driver.find_element(By.XPATH,"//input[@type='submit' and @value='log in']").click()
    time.sleep(2)
    # wait 2 seconds to not overload the server
    for genname in list_genref:
        driver.find_element(By.NAME,'input').send_keys(genname)
        driver.find_element(By.XPATH,"//div[@class='search1']/form[@action='search.php']/input[@type='submit' and @value='Go!']").click()
        time.sleep(2)

        #conexion a la bbdd
        conn = psycopg2.connect(user="tm",
                                        password="eneas",
                                        host="127.0.0.1",
                                        port="5432",
                                        database="hgmd")
        
        cursor = conn.cursor()
        # wait 2 seconds to not overload the server")
        time.sleep(2)
        driver.find_element(By.LINK_TEXT,genname).click()
        #copy driver
        driver_img = copy.copy(driver)

        elements = driver_img.find_elements(By.XPATH,"//div[@class='content']/table[@class='gene']/tbody/tr/td[@class='center']/form[@action='all.php']/input[@type='submit' and @value='Get mutations']")
        num =  len(elements)

        print("Number of items found:" )
        print( num)
        step = 10
        data.append({"genid":genname, "data":[]})

        for x in range(0,num-1):
            print ("Elemanto:",x)
            item = elements[x]
            
            item.click()
            #Comprobamos si hay pagina intermedia
            elements_captcha = driver_img.find_elements(By.XPATH,"//div[@class='content']/form[@class='captcha']/input[contains(@value,'>> Continue to')]")
            print('Buscando captcha')
            if len(elements_captcha) == 1:
                item_captcha = elements_captcha[0]
                print('captcha')
                item_captcha.click()
            try:
                #preparo las cabeceras del json
                #get mutation name
                step = 11
                strMutationType = ''
                strMutation = ''
                form_inputs = driver.find_elements(By.XPATH,"//form[@action='cdna_new.php']//input")
                for form_itm in form_inputs:
                    step = 12
                    if form_itm.get_attribute("type") == 'submit':
                                strMutation = form_itm.get_attribute("value")
                #get mutation type
                strMutationType = driver.find_element(By.XPATH,"//th[@class='black']").text.strip()
                getGenInfo = 0
                IdIntMutation = -1
                try:
                    #Si ya existe se consulta la bbdd y se marca para actualizar
                    cursor.execute(f"SELECT * FROM hgmd_gen_to_check where genid = '{genname}'; ")
                    rows = cursor.fetchone()
                    ins_stm1 = ''
                    #si encuentro un registro lo marco para actualizar
                    if rows == None:
                        #si no exite lo inserto
                        #insert item
                        ins_stm1 = "insert into hgmd_gen_to_check (genid, check_for_update,"\
                                    " date_insert, date_update) values (%s, 1, now(), now()); "
                        cursor.execute(ins_stm1,(genname,))
                        getGenInfo = 1
                        # execute an SQL statement using the psycopg2 cursor object
                        cursor.execute(f"SELECT * FROM hgmd_mutation where genid = '{genname}' and  Mutation = '{strMutation}';")
                        #si no existe se llama carga desde la página
                        row1 = cursor.fetchone()
                        if row1 == None:
                            print("Inserto 1:")
                            #buscamos en la web
                            getGenInfo = 1
                            #insert item
                            ins_stm2 = "insert into hgmd_mutation (genid, Mutation, json_info,date_insert,"\
                                            "date_update) values (%s,%s, null, now(), now()) RETURNING id; "
                            cursor.execute(ins_stm2,(genname,strMutation))
                            conn.commit()
                            #get id for mutation
                            IdIntMutation = cursor.fetchone()[0]
                        else:
                            getGenInfo = 0
                            #Obtengo el id para consultar las mutaciones
                            IdIntMutation = row1[0]
                    else:
                        # we got rows!
                        #Actualiza el registro para que de actualice
                        upd_stm1 = "update hgmd_gen_to_check  set check_for_update = 1, date_update = now()"\
                                        " where  genid = %s; "
                        cursor.execute(upd_stm1,(genname,))
                        # execute an SQL statement using the psycopg2 cursor object
                        cursor.execute(f"SELECT * FROM hgmd_mutation where genid = '{genname}' and  Mutation = '{strMutation}';")
                        #si no existe se llama carga desde la página
                        row1 = cursor.fetchone()
                        if row1 == None:
                            #buscamos en la web
                            #insert item
                            ins_stm2 = "insert into hgmd_mutation (genid, Mutation, json_info,date_insert,"\
                                            "date_update) values (%s,%s, null, now(), now()); "
                            cursor.execute(ins_stm2,(genname,strMutation))
                            conn.commit()
                            #get id for mutation
                            IdIntMutation = cursor.fetchone()[0]
                            getGenInfo = 1
                        else:
                            getGenInfo = 1
                            #Obtengo el id para consultar las mutaciones
                            IdIntMutation = row1[0]
                        #print("El id de la mutación a leer es:" + str(IdIntMutation) )
                except (Exception, psycopg2.Error) as error:
                        print("Error while fetching data from PostgreSQL", error) 
                
                if getGenInfo == 1:
                    print('Buscando imagenes')
                    images =driver_img.find_elements(By.XPATH,"//img[contains(@src,'incs/image-create-mutation.php')]")
                    for img in images:
                        desired_y = (img.size['height'] / 2) + img.location['y']
                        window_h = driver_img.execute_script('return window.innerHeight')
                        window_y = driver_img.execute_script('return window.pageYOffset')
                        current_y = (window_h / 2) + window_y
                        scroll_y_by = desired_y - current_y
                    
                        driver_img.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)
                        scroll = driver_img.execute_script("return window.scrollY;")

                        #print('Imagen encontrada')
                        #print(img.get_attribute('src'))
                        filename = img.get_attribute('src').strip().split('/')[-1].strip()

                        str_filename = str(filename).replace('.php?id=','_')
                        str_filename = str_filename.replace('&type=','_')
                        str_filename = './img/' + str_filename + '.png'
                        #if os.path.exists(str_filename):
                        #    os.remove(str_filename)

                        #print ('Getting: ' + str_filename)
                        location = img.location
                        #print ('location' ) 
                        #print ( location ) 
                        size = img.size
                        #print ('size:'  ) 
                        #print ( size )
                        
                        # crop image
                        x = location['x']
                        y = location['y'] - scroll
                        width = location['x']+size['width']
                        height = location['y']+size['height'] - scroll
                        
                        png = driver.get_screenshot_as_png() # saves screenshot of entire page
                        im = Image.open(BytesIO(png)) # uses PIL library to open image in memory
                        im = im.crop((int(x), int(y), int(width), int(height)))
                        #convert img to text
                        text = pytesseract.image_to_string(im)
                        text = text.replace("\n","")
                        text = text.replace("\f","")
                        #print('Imagen:' + str_filename + ",texto:" + text)
                        dict_images[str_filename] = text
                        
                    
                    #header
                    
                    data_local_r= []
                    data_local_r.append({"Mutation": strMutation, "Mutation Type": strMutationType ,"info":[]}) 
                    #recorro todas las tablas
                    for tb in driver_img.find_elements(By.XPATH,"//*[@class= 'gene']"):
                        #si la tabla contiene imagenes sigo
                        step = 15
                        if 'incs/image-create-mutation.php' in tb.get_attribute("innerHTML"):
                            #leemos la cabecera
                            step = 16
                            heads = tb.find_elements(By.CSS_SELECTOR,"th")
                            dh = dict()
                            iterh = 0
                            Accession_Number = ''
                            Codon_change = ''
                            Codon_number = ''
                            Phenotype = ''
                            if strMutationType == 'Splicing':
                                dh[0] =  'Accession Number'
                                dh[1] =  'HGMD Splicing mutation'
                                dh[2] =  'Genomic coordinates & HGVS nomenclature'
                                dh[3] =  'Phenotype'
                                dh[4] =  'Reference'
                                dh[5] =  'Comments'
                                Phenotype = dh[3] 
                            else:
                                for cellH  in heads:
                                    
                                    step = 17
                                    #print ('Dentro p_p_tbody == th-cell',cellH.text)
                                    contenth = cellH.text.strip()
                                    step = 18
                                    print ("header content [", iterh, "]:",contenth)
                                    dh[iterh] = contenth
                                    if contenth == "Accession Number" and Accession_Number == '':
                                        Accession_Number = contenth
                                    if contenth  == "Codon change" and Codon_change == '':
                                        Codon_change = contenth
                                    if contenth == "Codon number" and Codon_number == '':
                                        Codon_number = contenth
                                    if contenth == "Phenotype" and Phenotype == '':
                                        Phenotype = contenth      
                                    iterh = iterh +1
                            
                            #recorremos la tabla
                            #print(tb.get_attribute("innerHTML"))
                            step = 20
                            for row in tb.find_elements(By.CSS_SELECTOR,"tr"):
                                #recorremos las filas de datos
                                data_local=[]
                                d = dict()
                                iterd = 0
                                step = 25
                                #print(row.get_attribute("innerHTML"))
                                dh[iterd]
                                for  celld  in row.find_elements(By.CSS_SELECTOR,"td"):
                                    step = 30
                                    content = str(celld.text).replace('\n','')
                                
                                    
                                    #print (celld.get_attribute("innerHTML"))
                                    if ("img" in celld.get_attribute("innerHTML") and '.php' in celld.get_attribute("innerHTML")):
                                        step = 40
                                        
                                        img_src = celld.get_attribute("innerHTML").replace('<img src="','')
                                        img_src = img_src.replace('">','')
                                        #print('Antes',img_src)
                                        img_src = img_src.strip().split('/')[-1].strip()

                                        img_src = str(img_src).replace('.php?id=','_')
                                        img_src = img_src.replace('&amp;type=','_')
                                        img_src = './img/' + img_src + '.png'
                                        #print('Despues',img_src)
                                        #find image on dict
                                        if img_src in dict_images:
                                            text = dict_images[img_src]
                                        else:
                                            text = "Not Found"
                                        step = 90
                                        if (iterd in dh):
                                            d[dh[iterd]] = text
                                        else:
                                            d[iterd] = text
                                    else:
                                        content = content.replace('Additional phenotype report available to subscribers','')
                                        content = content.replace('Functional characterisation report available to subscribers','')
                                        content = content.replace('Additional report available to subscribers','')
                                        print(content)
                                        if (iterd in dh):
                                            #print ("content [", dh[iterd], "]:",content)
                                            d[dh[iterd]] = content
                                                                                
                                        else:
                                            #print ("content [", iterd, "]:",content)
                                            d[iterd] = content
                                    iterd = iterd +1
                                step = 100
                                data_local.append( {"inputs":d})
                                #CHECK if item exists
                                txtAccession_Number = ''
                                if Accession_Number in d:
                                    txtAccession_Number = d[Accession_Number]
                                else:
                                    txtAccession_Number = 'N/A'
                                #Getting search_id
                                txtCodon_change = ''
                                txtCodon_number = ''
                                txtCodon_number_change = ''
                                if Codon_change in d and Codon_number in d:
                                    txtCodon_change = d[Codon_change]
                                    txtCodon_number = d[Codon_number]
                                    strRepl = txtCodon_number + '-'
                                    txtCodon_number_change = str(txtCodon_change).replace('-',strRepl)
                                else:
                                    txtCodon_number_change = 'N/A'
                                #getting Phenotype
                                txtPhenotype = ''
                                if Phenotype in d:
                                    txtPhenotype =  d[Phenotype]
                                else:
                                    txtPhenotype = 'N/A'


                                query = f"SELECT * FROM hgmd_mutation_detail where id_mutation = {IdIntMutation} and  accession_number = '{txtAccession_Number}';"
                                cursor.execute(query)
                                #si no existe se llama carga desde la página
                                row2 = cursor.fetchone()
                                if row2 == None:
                                    step = 110
                                    #insert item
                                    ins_stm = "insert into hgmd_mutation_detail (id_mutation, accession_number,mutation_type,"\
                                                "search_id,Phenotype,json_info,date_insert, date_update) "\
                                                "values (%s,%s,%s,%s,%s,%s, now(), now()); "
                                    print(ins_stm)
    
                                    cursor.execute(ins_stm,(IdIntMutation,txtAccession_Number, strMutationType, txtCodon_number_change,txtPhenotype, json.dumps(data_local, indent=4)))
                                else:
                                    #update item
                                    step = 120
                                    upd_stm = "update  hgmd_mutation_detail set  json_info  = %s , search_id = %s , Phenotype = %s "\
                                                "where id_mutation = %s and  accession_number = %s"\
                                                " and mutation_type = %s  ;"
                                    cursor.execute(upd_stm,( json.dumps(data_local, indent=4),txtCodon_number_change,txtPhenotype,IdIntMutation,txtAccession_Number,strMutationType))
                                step = 130
                                conn.commit()
                                
                                data_local_r[0]["info"].append(data_local)
                                
                            data[0]["data"].append(data_local_r)
                else:
                    try:
                        #leemos de la base de datos, buscamos todos los elemantos de la tabla hgmd_mutation_detail
                        cursor.execute(f"SELECT Mutation_type, json_info FROM hgmd_mutation_detail where id_mutation = {IdIntMutation} and accession_number <> 'N/A';") 
                        rows2 = cursor.fetchall()
                        print("Print each row and it's columns values")
                        strMutation_type_ref = ''
                        FirstItem = 0
                        iter = -1
                        data_local_r= []
                        for row2 in rows2:
                            strMutation_type_read = row2[0] 
                            if strMutation_type_read != strMutation_type_ref:
                                strMutation_type_ref = row2[0]
                                data_local_r.append({"Mutation": strMutation, "Mutation Type": strMutation_type_ref.strip() ,"info":[]})
                                iter = iter +1
                            data_local_r[iter]["info"].append(row2[1])
                        

                    except (Exception, psycopg2.Error) as error:
                        print("Error while fetching data from PostgreSQL", error)       
            except :
                print("Oops!", sys.exc_info(), "occurred.")
                print('Step:',step)
            
            conn.commit()
            
            #driver_img.execute_script("window.history.go(-1)")
            time.sleep(5)
            driver_img.back()
            time.sleep(5)
            elements = driver_img.find_elements(By.XPATH,"//div[@class='content']/table[@class='gene']/tbody/tr/td[@class='center']/form[@action='all.php']/input[@type='submit' and @value='Get mutations']")
        data[0]["data"].append(data_local_r)  
        cursor.close()
        conn.close()
    return driver_img


def get_hgmd(genid):
    data = []
    driver_back = obtenerImagenes(genid,data,dict_images)
    driver.quit()
    driver_back.quit()
    return data
    
if __name__ == '__main__':
    data = []
    driver_back = obtenerImagenes(data,dict_images)
    #print (data)
    driver.quit()
    driver_back.quit()


   
   