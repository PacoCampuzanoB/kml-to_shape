#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 21:22:09 2020

@author: searCampuzano

"""

import geopandas as gpd
import os
import pandas as pd
import fiona
from shapely.geometry import Point
import subprocess

############################################################################################

diccionario = {'clave': [], 'nombre': [], 'situacion': [], 'entidad': [], 'municipio': [], 'organismo': [],\
                'cuenca': [], 'clim_dia': [], 'estadis': [], 'norm_51_10': [],\
                'norm_71_00': [], 'norm_81_10': [], 'val_extr': [], \
                'val_mens': [], 'geometry': []}
for base, dirs, files in os.walk("geojson/"):
    pass

############################################################################################
# patrones
########################################################################################

pEst ='Estado : </b>'
pMun = 'Municipio : </b>'
pOrg = 'Organismo : </b>'
pCuenca = 'Cuenca : </b>'
pClimDia = '>Climatología diaria'
pEstads = '>Estadística'
pNorm5110 = '>Normales 1951-2010'
pNorm7100 = '>Normales 1971-2000'
pNorm8110 = '>Normales 1981-2010'
pValExtr = '>Valores Extremos'
pValMens = '>Valores Mensuales'

patrones0 = [pEst, pMun, pOrg, pCuenca]
patrones1 = [pClimDia, pEstads, pNorm5110, pNorm7100, pNorm8110, pValExtr, pValMens]

############################################################################################

###########################################################################################

numPatrones0 = len(patrones0)
numPatrones1 = len(patrones1)

for k in range (len(files)):
    
    nombreFile = files[k].split(".")
    nombreFile = nombreFile[0] + ".shp"
    nombreFile = "shapes/" + nombreFile 
    geojsons = "geojson/" + files[k]
    df = gpd.read_file(geojsons)

    for j in range (len(df)):
        
        lista = df.iloc[j, 1]
        listaFinal = []
        numChar = 4    
        char = []
        while (lista[numChar] != '<'):                          #   Nombre y Situación
            char.append(lista[numChar])
            numChar += 1
        info = "".join(char)
        info = info.split(" - ")
        if (info[0] == ''):
            info = '----'
        listaFinal.append(info[0])
        if (info[1] == ''):
            info = '----'
        listaFinal.append(info[1])
        
        for k in range (numPatrones0): # Entidad, municipio, organismo, cuenca
            
            if (lista.count(patrones0[k]) == 1):
                numChar = lista.find(patrones0[k]) + len(patrones0[k])
                char = []
                while (lista[numChar] != '<'):
                    char.append(lista[numChar])
                    numChar += 1
                info = "".join(char)
                if (info == ''):                 # llena algún dato que falte
                    info = '----'
                listaFinal.append(info)
            else:
                listaFinal.append('****')        # En caso de que falte un campo      
                
        for l in range (numPatrones1):           # Climatología diaria, Estadísticas,    
                                        # normales climatológicas 51-10, 71-00, 81-10
            if (lista.count(patrones1[l]) == 1): # Valores extremos, valores mensuales   
                numChar = lista.find(patrones1[l]) - 1 
                char = []
                while (lista[numChar] != '='):
                    char.append(lista[numChar])
                    numChar -= 1
                info = "".join(char)
                info = "".join(reversed(info))
                if (info == ''):                 # llena algún dato que falte
                    info = '----'
                listaFinal.append(info)    
            else:
                listaFinal.append('****')

        diccionario['clave'].append(df.iloc[j, 0])
        diccionario['nombre'].append(listaFinal[0])
        diccionario['situacion'].append(listaFinal[1])
        diccionario['entidad'].append(listaFinal[2])
        diccionario['municipio'].append(listaFinal[3])  
        diccionario['organismo'].append(listaFinal[4])
        diccionario['cuenca'].append(listaFinal[5])
        diccionario['clim_dia'].append(listaFinal[6])
        diccionario['estadis'].append(listaFinal[7])
        diccionario['norm_51_10'].append(listaFinal[8])
        diccionario['norm_71_00'].append(listaFinal[9])
        diccionario['norm_81_10'].append(listaFinal[10])
        diccionario['val_extr'].append(listaFinal[11])
        diccionario['val_mens'].append(listaFinal[12])
        diccionario['geometry'].append(df.iloc[j, -1])

cD = pd.DataFrame(diccionario)

lon=[]; lat=[]; alt=[]

for i in range (len(cD)):    # Se extrae la posición de cada estación
    x = (cD.iloc[i, -1]).x
    y = (cD.iloc[i, -1]).y
    z = (cD.iloc[i, -1]).z
    lon.append(x)
    lat.append(y)
    alt.append(z)

#diccionario2 = {'longitud': lon, 'latitud': lat, 'altitud': alt}

cD['longitud'] = pd.Series(lon) # Se crean tres columnas con los campos longitud, latitud y altitud
cD['latitud'] = pd.Series(lat)
cD['altitud'] = pd.Series(alt)
cD.drop(['geometry'], axis=1, inplace=True) # Se borra la columna geometry

crs = {'init': 'epsg:4326'}
geometry = [Point(xy) for xy in zip(cD.longitud, cD.latitud)]
estacionesNal = gpd.GeoDataFrame(cD, crs=crs, geometry=geometry)
#estacionesNal = gpd.GeoDataFrame(cD, crs=crs, geometry=cD['geometry'])
estacionesNal.to_file("shapes/estClimNal1.shp", driver='ESRI Shapefile')

# ############################################################################################
# Se utliza un script bash para unir los shapes de cada estado
###########################################################################################

os.chdir('/home/sear/Desktop/estacionesClimatologicas/estClimSEGOB/EstacionesClimatologicas.kmz_FILES/shapes')
subprocess.call(['./unirShapes.sh']) # Para ejecutar scripts en python
