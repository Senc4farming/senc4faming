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
from os import listdir
from os.path import isfile, join
import pytesseract 

# request url

from selenium import webdriver
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup


from urllib.request import urlopen
from urllib.parse import urlparse
from mimetypes import guess_extension

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
email_address = "jmafernandez@ubu.es"
password = "HGMD895679"

#modificamos webdriver
chrome_opt = webdriver.ChromeOptions()
chrome_opt.add_argument('--headless')
chrome_opt.add_argument('--no-sandbox')
driver = webdriver.Chrome('./applications/chromedriver', options=chrome_opt)
dict_images={}



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


def login_hgmd(br):
    """
    login to HGMD

    After calling this function, you will be able to search in HGMD programmatically
    """
    response = br.open(hgmd_login_url)
    html = response.read()

    # print response to STDOUT for debugging purposes
    # the html2text library is used for formatting the output in a more readable form
    #print(html)

    # print all the forms in the current page
    # for f in br.forms:
    # print (f)
    
    # select login form
    #print("login_hgmd: select_form(nr=0)")
    br.select_form(nr=0)
    #print (br.form)

    # print all controls in the current form, for debugging purposes

    # set username and password
    br.form['email'] = email_address
    br.form['password'] = password
    print("login_hgmd: login frm con valores")
    print (br.form)
    # submit form
    response_form = br.submit()

    # Now, you should have successfully logged in. The contents of the page will be changed. Check the contents of br.read()
    html_response = response_form.read()

    #pasamos al index
    response = br.open(hgmd_url_base)
    html = response.read()


    # wait 2 seconds to not overload the server
    time.sleep(1)

    return br
def obtenerImagenes(genname,dict_images):
    driver.get(hgmd_login_url)
    driver.find_element(By.NAME,'email').send_keys(email_address)
    driver.find_element(By.NAME,'password').send_keys(password)

    driver.find_element(By.XPATH,"//input[@type='submit' and @value='log in']").click()
  
    # wait 2 seconds to not overload the server
    time.sleep(1)
    driver.find_element(By.NAME,'input').send_keys(genname)
    driver.find_element(By.XPATH,"//div[@class='search1']/form[@action='search.php']/input[@type='submit' and @value='Go!']").click()
  


    # wait 2 seconds to not overload the server")
    driver.find_element(By.LINK_TEXT,genname).click()
    #copy driver
    driver_img = copy.copy(driver)
    elements = driver_img.find_elements(By.XPATH,"//input[@type='submit' and @value='Get mutations']")
    num =  len(driver_img.find_elements(By.XPATH,"//input[@type='submit' and @value='Get mutations']"))

    print("Number of items found:" )
    print( num)
    iter = 0
    for x in range(0,num-1):
        item = elements[x]
        
        item.click()
        try:
            print('Buscando imagenes')
            scroll_old = -1
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
                if os.path.exists(str_filename):
                    os.remove(str_filename)

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
                if scroll_old != scroll:
                    if os.path.exists("./img/pageImage.png"):
                        os.remove("./img/pageImage.png")
                    driver.save_screenshot("./img/pageImage.png");
                    #print ('Buscando características de la imagen principal:')
                    #print(os.path.getsize("./img/pageImage.png") )
                    im = Image.open("./img/pageImage.png")
                #print ('Abriendo  la imagen principal:')
                #print(os.path.getsize("./img/pageImage.png") )
                
                im = im.crop((int(x), int(y), int(width), int(height)))
                #convert img to text
                text = pytesseract.image_to_string(im)
                text = text.strip("\n")
                text = text.rstrip("\f")
                dict_images[str_filename] = text
                scroll_old = scroll
                #arr = os.listdir("./img")
                #print(arr)
    
        except :
            print('Imagen no encontrada')
        driver_img.execute_script("window.history.go(-1)")
        elements = driver_img.find_elements(By.XPATH,"//input[@type='submit' and @value='Get mutations']")
    return driver_img


def query_gen_info(br,data,genname,dict_images):
    """
    login to HGMD

    After calling this function, you will be able to search in HGMD programmatically
    """
    response = br.open(hgmd_gen_url +  genname)
    html = response.read()

    # print response to STDOUT for debugging purposes
    # the html2text library is used for formatting the output in a more readable form
    print("query_gen_info: respuesta del gen  :" , genname)
    #print  (html)
    #jresponse = xmltojson.parse(html)
    # write to file as pretty print
    #with open('asdaresp.json', 'w') as outfile:
    #    json.dump(jresponse, outfile, sort_keys=True, indent=4)
    #print("query_gen_info fin de html")

    # print all the forms in the current page
    # string to be found in f
    strAll = "all"
    strGm = "Get mutations"
    bEncontrado = False
    count = 0
    esPrimeraLLamada = True
    data.append({"genid":genname, "data":[]})
    
    for f in br.forms():
        if strAll in f.action and strGm in str(f):
            print("id",count)

            #f.set_all_readonly(False)
            #print("Descripción formulario tras el cambio")
            #print (f)
            #control = f.find_control("database")
            #print (control.name)
            #print( control.value)
            #print ( control.type )
            if esPrimeraLLamada:
                print ("en navigate_item_first")
                bEncontrado = navigate_item_first(count,br,data,dict_images)
                if bEncontrado == False:
                    print ("en navigate_item con primera llamada")
                    navigate_item(count,br,data,dict_images)
                esPrimeraLLamada = False
            else:
                print ("en navigate_item")
                navigate_item(count,br,data,dict_images)
            
            #time.sleep(1)
        count +=1
     # wait 2 seconds to not overload the server
    #time.sleep(1)

    return br
def navigate_item_first(count,br,data,dict_images):
    bEncontrado = False
     #se ejecuta el formulario
    br.select_form(nr=count)
    # submit form
    response_form = br.submit()
    # Now, you should have successfully logged in. The contents of the page will be changed. Check the contents of br.read()
    html_response = response_form.read()
    print("Now, you should have successfully logged in. The contents of the page will be changed. Check the contents of br.read()")
    #print (html_response)
    # wait 2 seconds to not overload the server
    #time.sleep(2)
    # string to be found in f
    strAll = "all"
    strCt = "Continue to"
    
    #looking for form
    count = 0

    for f in br.forms():
        if strAll in f.action and strCt in str(f):
            bEncontrado = True
            br.select_form(nr=count)
            # submit form
            response_form = br.submit()
            parent = count
            # Now, you should have successfully logged in. The contents of the page will be changed. Check the contents of br.read()
            html_response = response_form.read()
            print("estamos en el grid de los datos, buscando gene")
            #print (html_response)
            soup = BeautifulSoup(html_response ,"html.parser")
            #get mutation name
            strMutationType = parent
            strMutation = parent
            forms = soup.find_all("form")
            for i, form in enumerate(forms, start=1):
                if form.attrs.get("action").lower() == 'cdna_new.php':
                    for input_tag in form.find_all("input"):
                        if input_tag.attrs.get("type", "text") == 'submit':
                            strMutation = input_tag.attrs.get("value", "")
            #get mutation type
            strMutationType = soup.find('th', {'class' :'black'}).text
            #header
            data_local = []
            data_local_r= []
            data_local_r.append({"Mutation": strMutation, "Mutation Type": strMutationType ,"info":[]}) 
            rowH = soup.select_one('.gene:-soup-contains("Accession Number")')("th")
            dh = dict()
            iterh = 0
            for cell in rowH:
                content = cell.text.strip()
                print ("header content [", iterh, "]:",content)
                dh[iterh] = content
                iterh += 1
            rows = soup.select_one('.gene:-soup-contains("Accession Number")')("tr")
            
            for row in rows:
                #print (row)
                iter = 0
                d = dict()
                for cell in row("td"):
                    #print(cell)
                    
                    content = cell.text.strip()
                    if ("img" in str(cell) and '.php' in str(cell)):
                        content = cell.img['src']
                        filename = content.strip().split('/')[-1].strip()
                        str_filename = str(filename).replace('.php?id=','_')
                        str_filename = str_filename.replace('&type=','_')
                        str_filename = './img/' + str_filename + '.png'
                        #find image on dict
                        if str_filename in dict_images:
                            text = dict_images[str_filename]
                        else:
                            text = "Not Found"

                        if (iter in dh):
                            d[dh[iter]] = text
                        else:
                            d[iter] = text
                    else:
                        if (iter in dh):
                            #print ("content [", dh[iter], "]:",content)
                            d[dh[iter]] = content
                        else:
                            #print ("content [", iter, "]:",content)
                            d[iter] = content

                    iter += 1
                data_local.append( {"inputs":d}) 
            data_local_r[0]['info'].append(data_local)
            data[0]['data'].append(data_local_r)       

            # wait 2 seconds to not overload the server
            #time.sleep(1)
        count +=1
        
    br.back()
    return bEncontrado
def navigate_item(count,br,data,dict_images):
     #se ejecuta el formulario
    br.select_form(nr=count)
    # submit form
    response_form = br.submit()
    # Now, you should have successfully logged in. The contents of the page will be changed. Check the contents of br.read()
    html_response = response_form.read()
    #print("Now, you should have successfully logged in. The contents of the page will be changed. Check the contents of br.read()")
    #print (html_response)
    print("estamos en el grid de los datos segunda llamada, buscando gene")
    #print (html_response)
    soup = BeautifulSoup(html_response ,"html.parser")

    #header
    data_local= []
    data_local_r= []
    parent = count
    #get mutation name
    strMutation = parent
    strMutationType = parent
    forms = soup.find_all("form")
    for i, form in enumerate(forms, start=1):
        if form.attrs.get("action").lower() == 'cdna_new.php':
            for input_tag in form.find_all("input"):
                if input_tag.attrs.get("type", "text") == 'submit':
                    strMutation = input_tag.attrs.get("value", "")
    #get mutation type
    strMutationType = soup.find('th', {'class' :'black'}).text
    data_local_r.append({"Mutation": strMutation , "Mutation Type": strMutationType ,"info":[]}) 
    rowH = soup.select_one('.gene:-soup-contains("Accession Number")')("th")
    print (rowH)
    dh = dict()
    iterh = 0
    for cell in rowH:
        content = cell.text.strip()
        print ("header content [", iterh, "]:",content)
        dh[iterh] = content
        iterh += 1
    rows = soup.select_one('.gene:-soup-contains("Accession Number")')("tr")
    
    
    for row in rows:
        #print (row)
        iter = 0
        d = dict()
        for cell in row("td"):
            #print(cell)
            content = cell.text.strip()
            if ("img" in str(cell) and '.php' in str(cell)):
                content = cell.img['src']
                filename = content.strip().split('/')[-1].strip()
                str_filename = str(filename).replace('.php?id=','_')
                str_filename = str_filename.replace('&type=','_')
                str_filename = './img/' + str_filename + '.png'
                #find image on dict
                if str_filename in dict_images:
                    text = dict_images[str_filename]
                else:
                    text = "Not Found"

                if (iter in dh):
                    d[dh[iter]] = text
                else:
                    d[iter] = text
            else:
                if (iter in dh):
                    #print ("content [", dh[iter], "]:",content)
                    d[dh[iter]] = content
                else:
                    #print ("content [", iter, "]:",content)
                    d[iter] = content

            iter += 1
        data_local.append( {"inputs":d}) 
    data_local_r[0]['info'].append(data_local)
    data[0]['data'].append(data_local_r)      
    # wait 2 seconds to not overload the server
    #time.sleep(1)
    count +=1
    
    br.back()
def get_hgmd(genid):
    
    br = initialize_browser()
    driver_back = obtenerImagenes(genid,dict_images)

    br = login_hgmd(br)
    data = []
    br = query_gen_info(br,data,genid,dict_images)

    driver.quit()
    driver_back.quit()
    #print(data)
    return data
    
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
   