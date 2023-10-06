#!/usr/bin/env python
import mechanize

import json # import json library
#Gestión de imagenes
from PIL import Image,  ImageEnhance, ImageFilter
#from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import copy
import os

import pytesseract 

# request url

from selenium import webdriver
import time


try:
    import cookielib
except:
    import http.cookiejar
    cookielib = http.cookiejar

import sys
from io import BytesIO

hgmd_url_base = "http://www.hgmd.cf.ac.uk"
hgmd_login_url = "http://www.hgmd.cf.ac.uk/docs/login.html"
hgmd_gen_url = "http://www.hgmd.cf.ac.uk/ac/gene.php?gene="
hgmd_url_all="http://www.hgmd.cf.ac.uk/ac/all.php"
email_address = "jmafernandez@ubu.es"
password = "HGMD895679"

#modificamos webdriver
chrome_opt = webdriver.ChromeOptions()
chrome_opt.add_argument('--headless')
chrome_opt.add_argument('--no-sandbox')
driver = webdriver.Chrome('./applications/chromedriver', options=chrome_opt)
dict_images={}





def obtenerImagenes(genname,data,dict_images):
    driver.get(hgmd_login_url)
    driver.find_element(By.NAME,'email').send_keys(email_address)
    driver.find_element(By.NAME,'password').send_keys(password)

    driver.find_element(By.XPATH,"//input[@type='submit' and @value='log in']").click()
  
    # wait 2 seconds to not overload the server
    driver.find_element(By.NAME,'input').send_keys(genname)
    driver.find_element(By.XPATH,"//div[@class='search1']/form[@action='search.php']/input[@type='submit' and @value='Go!']").click()
  


    # wait 2 seconds to not overload the server")
    driver.find_element(By.LINK_TEXT,genname).click()
    #copy driver
    driver_img = copy.copy(driver)
    #Comprobamos si hay pagina intermedia
    elements_captcha = driver_img.find_elements(By.XPATH,"//div[@class='content']/form[@class='captcha']/input[contains(@value,'>> Continue to')]")
    if len(elements_captcha) == 1:
        item_captcha = elements_captcha[0]
        time.sleep(1) # Sleep for 3 seconds
        item_captcha.click()
    elements = driver_img.find_elements(By.XPATH,"//div[@class='content']/table[@class='gene']/tbody/tr/td[@class='center']/form[@action='all.php']/input[@type='submit' and @value='Get mutations']")
    num =  len(elements)

    print("Number of items found:" )
    print( num)
    step = 10
    data.append({"genid":genname, "data":[]})
    
    for x in range(0,num-1):
        item = elements[x]
        
        item.click()
        
        try:
            print('Buscando imagenes')
            """
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
            """    
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
            strMutationType = driver.find_element(By.XPATH,"//th[@class='black']").text
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
                    for cellH  in heads:
                        step = 17
                        #print ('Dentro p_p_tbody == th-cell',cellH.text)
                        contenth = cellH.text.strip()
                        step = 18
                        print ("header content [", iterh, "]:",contenth)
                        dh[iterh] = contenth
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
                        data_local_r[0]["info"].append(data_local)
                    data[0]["data"].append(data_local_r)                
        except :
            print("Oops!", sys.exc_info(), "occurred.")
            print('Step:',step)
        
        #driver_img.execute_script("window.history.go(-1)")
        driver_img.back()
        elements = driver_img.find_elements(By.XPATH,"//div[@class='content']/table[@class='gene']/tbody/tr/td[@class='center']/form[@action='all.php']/input[@type='submit' and @value='Get mutations']")
    
    return driver_img


def get_hgmd(genid,data):
    driver_back = obtenerImagenes(genid,data,dict_images)
    #driver.quit()
    #driver_back.quit()
    
#if __name__ == '__main__':
#        br = initialize_browser()
#        obtenerImagenes(driver_back)
    #    resp = browse_dbcline(br, genes = ['GCS1'])
#        br = login_hgmd(br)
#        data = []
#        br = query_gen_info(br,data)
#        print (json.dumps(data))
#        driver.quit()
#        driver_back.quit()


    #if driver_back:
    #    if not driver.window_handles:
    #        print ("Cerrado")
    #    else:
    #        driver_back.close()
   