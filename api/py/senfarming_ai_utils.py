import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import r2_score
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
from scipy import stats
import psycopg2
from psycopg2 import connect
import json
import os
import psycopg2.extras as extras

#select csv item
#elem = 11
elem_corr = [5]

filestitlearray = [
                    '0:22/07/2024 v1',
                    '1:22/07/2024 v1 ndvi_02_04 ',
                    '2:22/07/2024 v1 msavi_menos1_02 ',
                    '3:22/07/2024 v1 msavi_menos1_02_v1 ',
                    '4: 5 days ',
                    '5: 10 days ',
                    '6: 20 days ',
                    '7: v3 30 days ',
                    '8: v6 days ',
                    '9: v8 45 days ',  
                    '10: v9 60 days ',
                    '11: v2 full range dates '
                   ]
#literal for scatter plot
str_occ_max = ' 0.07'
str_gen = "Results using one reflectance vector for each point with minimum NDVI and cc less than "+ str_occ_max
#Bands to use 1 all 2 rgb
opt_band = 1
#darw scatter ranges
scatter_min_x=40
scatter_min_y=40
#select band_set
#pendiente
#select set values
band_array  = ['02','03','04','05','06','07','08','09','11','12','8A']
band_array_20m  = ['06','07','11','12','8A']
band_array_02  = ['02']
band_array_03  = ['03']
band_array_04  = ['04']
band_array_05  = ['05']
band_array_06  = ['06']
band_array_07  = ['07']
band_array_08  = ['08']
band_array_09  = ['09']
band_array_11  = ['11']
band_array_12  = ['12']
band_array_8A  = ['8A']
band_array_dia_a  = ['05','06','07','08','08A','11','12']
band_array_red_nir_swnir  = ['04','05','06','07','08','08A','11','12']
band_array_msavi_red_nir_swnir  = ['03','04','05','06','07','08','08A','11','12','MSAVI']
band_array_msavi_red_nir_swnir_p  = ['NDVI','s2wi']

band_array_titulo  = ' todas las bandas'
band_array_02_titulo  = ' banda 02'
band_array_03_titulo  = ' banda 03'
band_array_04_titulo  = ' banda 04'
band_array_05_titulo  = 'banda 05'
band_array_06_titulo  =' banda 06'
band_array_07_titulo  = ' banda 07'
band_array_08_titulo  = ' banda 08'
band_array_09_titulo  =' banda 09'
band_array_11_titulo  = ' banda 11'
band_array_12_titulo  = ' banda 12'
band_array_8A_titulo  = ' banda 8A'
band_array_20m_titulo = ' bandas 20m'
band_array_10m_titulo = ' bandas 10m'
band_array_dia_titulo =  'Bandas 4,8'
band_array_red_nir_swnir_titulo =  'Bandas red_nir_swnir_titulo'
band_array_msavi_red_nir_swnir_titulo =  'Bandas msavi red_nir_swnir_titulo'
band_array_msavi_red_nir_swnir_p_titulo = 'Todas las bandas menos la 1'


band_array_min_ndiv_30d = ['04','07','08','08A','NDVI']
band_array_min_ndiv_30d_titulo = 'Bandas min ndvi 30 dias'

band_array_min_ndiv_45d = ['NDVI']
band_array_min_ndiv_45d_titulo = 'Bandas min ndvi 45 dias'


band_array_min_ndiv_60d = ['08','12','NDVI']
band_array_min_ndiv_60d_titulo = 'Bandas min ndvi 45 dias'

band_array_min_ndiv_todosd = ['01','02','03','04','05','06','07','08','09','11','12','8A','NDVI']
band_array_min_ndiv_todosd_titulo = 'Bands min ndvi and cc less than ' + str_occ_max

band_array_min_ndiv_rgb_d = ['02','03','04']
band_array_min_ndiv_rgb_d_titulo = 'Bands RGB b2,b3,b4 min ndvi and cc less than ' + str_occ_max

band_array_min_ndiv_grp1d = ['02','03','04','NDVI']
band_array_min_ndiv_grp1d_titulo = 'Bands grp 1 min ndvi and cc less than ' + str_occ_max


if opt_band == 1:
    band_array_usar = band_array_min_ndiv_todosd 
    band_array_usar_titulo = band_array_min_ndiv_todosd_titulo
elif opt_band == 2:
    band_array_usar = band_array_min_ndiv_rgb_d 
    band_array_usar_titulo = band_array_min_ndiv_rgb_d_titulo
elif opt_band == 3:
    band_array_usar = band_array_min_ndiv_grp1d 
    band_array_usar_titulo = band_array_min_ndiv_grp1d_titulo
    
font1 = {'family':'serif','color':'blue','size':15}
font2 = {'family':'serif','color':'darkred','size':15}
font3 = {'family':'serif','color':'blue','size':12}
font4 = {'family':'serif','color':'darkred','size':12}
display_level = 0

# first load config from a json file,
srvconf = json.load(open(os.environ["PYSRV_CONFIG_PATH"]))

def display_func(level,text):   
    if level <= display_level:
        print(text)
def display_func_val(level,text,val):  
    if level <= display_level:
        print(text,val)
def normalizeOC(df):   
    """Takes in a value, min and max of the data| returns the normalized value between 0 and 1.
    """
    df_orig = df
    df_oc = df.filter(['readvalue'], axis=1)
    normalized_df_oc=(df_oc-df_oc.min())/(df_oc.max()-df_oc.min())
    display_func(1,normalized_df_oc.head(10))
    #elimino la columna
    df_orig = df_orig.drop('readvalue', axis=1)
    display_func(1,df_orig.head(10))
    df_orig = pd.concat([df_orig, normalized_df_oc], axis=1)
    display_func(1,df_orig.head(10))
    return df_orig
def normalizeOCCorr(df):   
    """Takes in a value, min and max of the data| returns the normalized value between 0 and 1.
    """
    df_orig = df
    df_oc = df.filter(['oc'], axis=1)
    normalized_df_oc=(df_oc-df_oc.min())/(df_oc.max()-df_oc.min())
    #display_func(1,normalized_df_oc.head(10))
    #elimino la columna
    df_orig = df_orig.drop('oc', axis=1)
    #display_func(1,df_orig.head(10))
    df_orig = pd.concat([df_orig, normalized_df_oc], axis=1)
    #display_func(1,df_orig.head(14))
    return df_orig

def clean_outliers(min_value, max_value, df):
    df_orig = df
    display_func(1,"clean_outliers: Initial number of rows:")
    display_func(1,df.shape[0])
    df_new_max = df.loc[(df['readvalue'] < max_value)]
    display_func(1,"clean_outliers: after max:")
    display_func(1,df_new_max.shape[0])
    df_new_min = df_new_max.loc[(df_new_max['readvalue'] > min_value)]
    display_func(1,"clean_outliers: after min:")
    display_func(1,df_new_min.shape[0])
    return df_new_min

def procesamiento_basico_pivot_sin_fechas(df,band_array_in):
    """
    Función que realiza un procesamiento básico (pivotar caracteristicas).
    
    Si lo queremos hacer feten, esto no sería una función sino un Transformer
    https://sklearn-template.readthedocs.io/en/latest/user_guide.html#transformer
    
    Devuelve 
        X: variable independientes
        y: variable dependiente
    
    """
    df = df.loc[df['band'].isin(band_array_in)]
    df["coords"]=list(zip(df["longitude"], df["latitude"]))
    X_df = df.pivot_table(index="coords",
               columns="band",
               values = "reflectance").values
    
    Y = df.groupby("coords").mean()["readvalue"].values
    display_func(1,X_df.head())
    return X_df,Y
def data_scaling(X_train, Y_train):
    '''
        Standardization is a common preprocessing technique used in machine learning to transform data 
        into a standard scale. The scikit-learn library provides a StandardScaler class that performs
        standardization on numerical data.
        Standardization involves subtracting the mean and dividing by the standard deviation for each 
        feature. This process ensures that all features have a mean of zero and a standard deviation of 
        one. Standardizing the data can be beneficial for certain machine learning models and algorithms 
        as it helps to bring the features to a comparable scale and prevents any single feature from
        dominating the learning process.
    '''
    sc_x = StandardScaler()
    sc_y = StandardScaler()
    X_train_sc = sc_x.fit_transform(X_train)
    y_train_sc_int = sc_y.fit_transform(Y_train.reshape(-1,1))
    y_train_sc = y_train_sc_int[:,0]
    display_func_val(1,'data_scalingy_train shape:' , Y_train.shape)
    display_func_val(1,'data_scaling y_train_sc_int shape:' , y_train_sc_int.shape)
    display_func_val(1,'data_scaling y_train_sc shape:' , y_train_sc.shape)
    return  X_train_sc,sc_x,y_train_sc,sc_y
def procesamiento_basico_pivot_valores_medios_sin_fechas(df,band_array_in):
    """
    Función que realiza un procesamiento básico (pivotar caracteristicas).
    
    Si lo queremos hacer feten, esto no sería una función sino un Transformer
    https://sklearn-template.readthedocs.io/en/latest/user_guide.html#transformer
    
    Devuelve 
        X: variable independientes
        y: variable dependiente
    
    """
    df = df.loc[df['band'].isin(band_array_in)]
    df["coords"]=list(zip(df["longitude"], df["latitude"]))
    X_df = df.pivot_table(index="coords",
               columns="band",
               values = "reflectance",aggfunc=np.mean).values
    Y = df.groupby("coords").mean()["readvalue"].values
    
    return X_df,Y
def obtener_valores_X_normnalizados(X):
    X_norm = (X-np.min(X))/(np.max(X)-np.min(X))
    return X_norm
def mostrar_reflectancias_por_bandas(df):
    str_array = ['01','02','03','04','05','06','07','08','09','11','12','8A']
    df=pd.DataFrame(X,columns=[strval  for strval in str_array])
    df.head()

def particiona_datos(x,y,size,random_state):
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=size, random_state=random_state)
    
    return X_train, X_test, y_train, y_test;

def perform_cross_validation(method, X, y, cv):
    output = []
    
    kf = KFold(n_splits=cv, random_state=None, shuffle=False)
    for i, (train_index, test_index) in enumerate(kf.split(X)):
        X_train, y_train = X[train_index], y[train_index]
        X_test, y_test = X[test_index], y[test_index]
        
        method_i = clone(method)
        method_i.fit(X_train,y_train)
        preds = method_i.predict(X_test)
        output.append((y_test,preds))
        
    return output

def eval_r2(xval_output):
    scores = []
    for real,preds in xval_output:
        scores.append(r2_score(real,preds))
        
    return np.array(scores)


def draw_scatter(xval_output, titulo_metodo,titulo_df_values,reference,fullimagefilename,fullmodelfilename,elem  ):
    #ver como pintar comparativas de 3 scatter plots
    #https://pieriantraining.com/adding-subtitles-to-plots-in-python-a-complete-guide/
    #The P-value is the probability that you would have found the current result if 
    #the correlation coefficient were in fact zero (null hypothesis). If this probability
    #is lower than the conventional 5% (P<0.05) the correlation coefficient is called 
    #statistically significant.
    real_preds = np.concatenate(xval_output, axis=1)
    preds = real_preds[1,:]
    real = real_preds[0,:]
    #......RMSE
    display_func(0,'RMSE')
    display_func(0,np.sqrt(np.mean((preds-real)**2)))
    #MAE
    display_func(0,'MAE')
    display_func(0,mean_absolute_error(real,preds))
    mean_absolute_error
    #r2 score
    display_func(0,'R2')
    display_func(0,r2_score(real, preds) )

    
    
    valor_pearson = stats.pearsonr(real, preds)
    display_func(0,'pearson')
    display_func(0,valor_pearson)
    

    ax = plt.gca()
    ax.set_xlim([0, scatter_min_x])
    ax.set_ylim([0, scatter_min_y])
    plt.suptitle('Scatter p.'+ titulo_metodo + ' : ' + titulo_df_values)
    plt.title(  filestitlearray[elem] + ':' + band_array_usar_titulo, fontdict = font1)
    plt.xlabel("Real" , fontdict = font2)
    plt.ylabel("Preds", fontdict = font2)
    plt.figtext(0.5, -0.05, str_gen, ha="center", fontsize=9, bbox={"facecolor":"orange", "alpha":0.5, "pad":5})
    plt.scatter(real, preds)
    plt.savefig(fullimagefilename)

    rmse = np.sqrt(np.mean((preds-real)**2))
    if titulo_metodo == 'knn':
        url = '/api/ai/pred/knn'
    elif titulo_metodo == 'svr':
        url = '/api/ai/pred/svr'

    #Save data into bbdd
    new_row = pd.DataFrame({ 'name':reference, 'elem':elem, 'modelnamepath':fullmodelfilename, 'modelimagepath':fullimagefilename, 
                            'rmse':rmse, 'mae':mean_absolute_error(real,preds), 'r2':r2_score(real, preds) , 'pearson':str(valor_pearson),
                                'url':url
                                }, index=[0])
    result = guardardatosmodelo(new_row,'tbl_ai_model')

def draw_scatter_tit(xval_output, titulo_metodo,titulo_df_values,reference,fullimagefilename,fullmodelfilename,title  ):
    #ver como pintar comparativas de 3 scatter plots
    #https://pieriantraining.com/adding-subtitles-to-plots-in-python-a-complete-guide/
    #The P-value is the probability that you would have found the current result if 
    #the correlation coefficient were in fact zero (null hypothesis). If this probability
    #is lower than the conventional 5% (P<0.05) the correlation coefficient is called 
    #statistically significant.
    real_preds = np.concatenate(xval_output, axis=1)
    preds = real_preds[1,:]
    real = real_preds[0,:]
    #......RMSE
    display_func(0,'RMSE')
    display_func(0,np.sqrt(np.mean((preds-real)**2)))
    #MAE
    display_func(0,'MAE')
    display_func(0,mean_absolute_error(real,preds))
    mean_absolute_error
    #r2 score
    display_func(0,'R2')
    display_func(0,r2_score(real, preds) )

    
    
    valor_pearson = stats.pearsonr(real, preds)
    display_func(0,'pearson')
    display_func(0,valor_pearson)
    

    ax = plt.gca()
    ax.set_xlim([0, scatter_min_x])
    ax.set_ylim([0, scatter_min_y])
    plt.suptitle('Scatter p.'+ titulo_metodo + ' : ' + titulo_df_values)
    plt.title( title + ':' + band_array_usar_titulo, fontdict = font1)
    plt.xlabel("Real" , fontdict = font2)
    plt.ylabel("Preds", fontdict = font2)
    plt.figtext(0.5, -0.05, str_gen, ha="center", fontsize=9, bbox={"facecolor":"orange", "alpha":0.5, "pad":5})
    plt.scatter(real, preds)
    plt.savefig(fullimagefilename)

    rmse = np.sqrt(np.mean((preds-real)**2))
    if titulo_metodo == 'knn':
        url = '/api/ai/pred/knn'
    elif titulo_metodo == 'svr':
        url = '/api/ai/pred/svr'

    #Save data into bbdd
    new_row = pd.DataFrame({ 'name':reference, 'elem':-1, 'modelnamepath':fullmodelfilename, 'modelimagepath':fullimagefilename, 
                            'rmse':rmse, 'mae':mean_absolute_error(real,preds), 'r2':r2_score(real, preds) , 'pearson':str(valor_pearson),
                                'url':url
                                }, index=[0])
    result = guardardatosmodelo(new_row,'tbl_ai_model')




def guardardatosmodelo(df,table):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    step = 10
    cursor = conn.cursor()

    tuples = [tuple(x) for x in df.to_numpy()]

    cols = ','.join(list(df.columns))
    #delete old items for the same refference
    deletequery = "delete from %s where name = '%s'" % ( table,df.at[0,'name'])
    cursor.execute(deletequery) 
    # SQL query to execute 
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)

    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
        print("the dataframe is inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    cursor.close()
    return 1

def obtenerModelos():
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    #parametros para procesar datos
    table=''
    df = pd.DataFrame()
    cursor = conn.cursor()
    print("leemos los datos de los modelos ejecutados: tbl_ai_model")
    #En este caso las coordenadas se usam tal cual vienen
    step = 100
    try:
        df = pd.DataFrame()
        #Leemos los datos 
        query = ( 'select name as referencia, elem as  elemento , rmse, mae,r2,pearson ' 
                     ' from tbl_ai_model a '
                    )
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            referencia , elemento , rmse, mae,r2,pearson = row
            step = 120
            new_row = pd.DataFrame({ 'referencia':referencia, 'elemento':elemento,'rmse': rmse, 'mae': mae, 
                                    'r2':r2, 'pearson':pearson}, index=[0])
            df = pd.concat([new_row,df.loc[:]]).reset_index(drop=True)
        #print(points)
    except (Exception, psycopg2.Error) as error:
        print("obtenerModelos: Error while fetching data from PostgreSQL", error,"; step :", step)      
    cursor.close()
    return df


def readmodelbyref( ref, table):
    #conexion a la bbdd
    conn = psycopg2.connect(user= srvconf['PYSRV_DATABASE_USER'],
                                    password=srvconf['PYSRV_DATABASE_PASSWORD'],
                                    host= srvconf['PYSRV_DATABASE_HOST_POSTGRESQL'],
                                    port=srvconf['PYSRV_DATABASE_PORT'],
                                    database= srvconf['PYSRV_DATABASE_NAME'])
    
    cursor = conn.cursor()
    step = 10
    try:
        df = pd.DataFrame()
        #Leemos los datos 
        query = "SELECT modelnamepath FROM %s WHERE name = '%s' " % (table,ref)
        cursor.execute(query) 
        rowd = cursor.fetchall() 
        for row in rowd:
            modelnamepath = row
            step = 120
            new_row = pd.DataFrame({ 'modelnamepath':modelnamepath}, index=[0])
            df = pd.concat([new_row,df.loc[:]]).reset_index(drop=True)
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error,"; step :", step)      
    
    cursor.close()
    conn.close()
    return df