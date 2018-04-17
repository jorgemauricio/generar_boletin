#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#######################################
# Script que permite la generación de mapas para las variables de
# temperatura (máxima, mínima y promedio),
# Humedad Relativa (máxima, mínima y promedio),
lluvia, y reflectividad de radar.
# Author: Jorge Mauricio
# Email: jorge.ernesto.mauricio@gmail.com
# Date: 2018-02-01
# Version: 1.0
#######################################
Created on Mon Jul 17 16:17:25 2017
@author: jorgemauricio
"""

# librerías
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from scipy.interpolate import griddata as gd
from time import gmtime, strftime
import time
import os
from time import gmtime, strftime
import ftplib
import shutil
import csv
import schedule

# PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import Image

def main():
    """
    Función que genera los mapas de temperatura mínima
    """
    #%% fecha del pronostico
    fechaPronostico = strftime("%Y-%m-%d")
    variables = ["Rain","Tmax","Tmin","Tpro","Hr","Hrmin","Hrmax"]

    LAT_MAX = 33.5791
    LAT_MIN = 12.3782

    LONG_MAX = -86.101
    LONG_MIN = -118.236

    #%% generate arrayFechas
    # Generate Days
    arrayFechas = []
    tanio, tmes, tdia = fechaPronostico.split('-')
    anio = int(tanio)
    mes = int(tmes)
    dia = int(tdia)

    dirAnio = anio
    dirMes = mes
    dirDia = dia

    #%% generate arrayFechas

    for i in range(0,5,1):
        if i == 0:
            newDiaString = '{}'.format(dia)
            if len(newDiaString) == 1:
            	newDiaString = '0' + newDiaString
            newMesString = '{}'.format(mes)
            if len(newMesString) == 1:
            	newMesString = '0' + newMesString
            fecha = '{}'.format(anio)+"-"+newMesString+"-"+newDiaString
            arrayFechas.append(fecha)
        if i > 0:
            dia = dia + 1
            if mes == 2 and anio % 4 == 0:
            	diaEnElMes = 29
            elif mes == 2 and anio % 4 != 0:
            	diaEnElMes = 28
            elif mes == 1 or mes == 3 or mes == 5 or mes == 7 or mes == 8 or mes == 10 or mes == 12:
            	diaEnElMes = 31
            elif mes == 4 or mes == 6 or mes == 9 or mes == 11:
            	diaEnElMes = 30
            if dia > diaEnElMes:
            	mes = mes + 1
            	dia = 1
            if mes > 12:
            	anio = anio + 1
            	mes = 1
            newDiaString = '{}'.format(dia)
            if len(newDiaString) == 1:
            	newDiaString = '0' + newDiaString
            newMesString = '{}'.format(mes)
            if len(newMesString) == 1:
            	newMesString = '0' + newMesString
            fecha = '{}'.format(anio)+"-"+newMesString+"-"+newDiaString
            arrayFechas.append(fecha)

    # path server
    path = "/home/jorge/Documents/Research/generar_boletin"
    # os.chdir("/home/jorge/Documents/work/autoPronosticoSonora")
    os.chdir(path)

    #%% read csvs
    pathFile1 = '{}/data/{}/d1.txt'.format(path, fechaPronostico)
    pathFile2 = '{}/data/{}/d2.txt'.format(path, fechaPronostico)
    pathFile3 = '{}/data/{}/d3.txt'.format(path, fechaPronostico)
    pathFile4 = '{}/data/{}/d4.txt'.format(path, fechaPronostico)
    pathFile5 = '{}/data/{}/d5.txt'.format(path, fechaPronostico)

    data1 = pd.read_table(pathFile1, sep=',')
    data2 = pd.read_table(pathFile2, sep=',')
    data3 = pd.read_table(pathFile3, sep=',')
    data4 = pd.read_table(pathFile4, sep=',')
    data5 = pd.read_table(pathFile5, sep=',')

    # ciclo para generar los mapas de cada una de las variables
    for variable in variables:
        #%% make one dataFrame
        data = data1.filter(items=['Long', 'Lat',variable])
        data['{}1'.format(variable)] = data1[variable]
        data['{}2'.format(variable)] = data2[variable]
        data['{}3'.format(variable)] = data3[variable]
        data['{}4'.format(variable)] = data4[variable]
        data['{}5'.format(variable)] = data5[variable]

        #%% get values from Ags
        data = data.loc[data['Lat'] >= LAT_MIN]
        data = data.loc[data['Lat'] <= LAT_MAX]
        data = data.loc[data['Long'] >= LONG_MIN]
        data = data.loc[data['Long'] <= LONG_MAX]

        print(data.head())

        #%% get x and y values
        lons = np.array(data['Long'])
        lats = np.array(data['Lat'])


        #%% loop diarios
        counterFecha = 0
        for i in range(1,6,1):
            #%% set up plot
            plt.clf()
            #fig = plt.figure(figsize=(48,24))
            m = Basemap(projection='mill',llcrnrlat=LAT_MIN,urcrnrlat=LAT_MAX,llcrnrlon=LONG_MIN,urcrnrlon=LONG_MAX,resolution='h')

            #%% generate lats, lons
            x, y = m(lons,lats)

            #%% number of cols and rows
            numcols = len(x)
            numrows = len(y)

            #%% generate xi, yi
            xi = np.linspace(x.min(), x.max(), 1000)
            yi = np.linspace(y.min(), y.max(), 1000)

            #%% generate meshgrid
            xi, yi = np.meshgrid(xi,yi)

            #%% genate zi
            tempTitleColumn = "{}{}".format(variable,i)
            z = np.array(data[tempTitleColumn])
            zi = gd((x,y), z, (xi,yi), method='cubic')

            #%% generate clevs
            #generate clevs
            step = (z.max() - z.min()) / 15

            if variable == "Rain":
                clevs = [1,5,10,20,30,50,70,100,150,200,250,300,350,400,500]
            else:
                clevs = np.linspace(z.min(), z.max(), 15)

            cmap_variable = colores_por_variable(variable)

            #%% contour plot
            cs = m.contourf(xi,yi,zi, clevs, zorder=4, alpha=0.5, cmap=cmap_variable)
            #%% draw map details
            # m.drawcoastlines()
            # m.drawstates(linewidth=0.7)
            # m.drawcountries()

            #%% read municipios shape file
            m.readshapefile('shapes/Estados', 'Estados')
            #m.drawmapscale(22, -103, 23, -102, 100, units='km', fontsize=14, yoffset=None, barstyle='fancy', labelstyle='simple', fillcolor1='w', fillcolor2='#000000',fontcolor='#000000', zorder=5)

            #%% colorbar
            cbar = m.colorbar(cs, location='right', pad="5%")

            # simbología colorbar
            simbologia = generar_simbologia(variable)
            cbar.set_label(simbologia)
            titulo_mapa = generarTexto(variable, arrayFechas[counterFecha])
            plt.title(titulo_mapa)
            titulo_archivo = "{}/data/{}/{}_{}.png".format(path, fechaPronostico,variable, i)
            plt.annotate('@2018 INIFAP', xy=(-102,22), xycoords='figure fraction', xytext=(0.45,0.45), color='g')
            plt.savefig(titulo_archivo, dpi=600, bbox_inches='tight')
            counterFecha += 1
            print('****** Genereate: {}'.format(titulo_archivo))

def colores_por_variable(v):
    """
    param: v: variable
    return : nombre del cmap a mapear
    """
    if v == "Rain":
        return "gist_ncar"
    if v == "Tmax":
        return "gist_heat_r"
    if v == "Tmin":
        return "Blues_r"
    if v == "Tpro":
        return "gist_earth"
    if v == "Hr" or v == "Hrmin" or v == "Hrmax":
        return "seismic_r"
    else:
        pass

def generar_simbologia(v):
    """
    param: v: variable
    return : simbolo para el colorbar
    """
    if v == "Rain":
        return "mm"
    if v == "Tmax" or v == "Tmin" or v == "Tpro":
        return "°C"
    if v == "Hr" or v == "Hrmin" or v == "Hrmax":
        return "%"

def generarTexto(v, f):
    """
    Función que nos permite generar el texto correspondiente para cada mapa
    param: v: variable
    param: f: fecha
    """
    titulo = ""
    if v == "Rain":
        titulo = "Precipitación acumulada en 24h\n Pronóstico válido para: {}".format(f)
        return titulo
    elif v == "Tmax":
        titulo = "Temperatura máxima en 24h\n Pronóstico válido para: {}".format(f)
        return titulo
    elif v == "Tmin":
        titulo = "Temperatura mínima en 24h\n Pronóstico válido para: {}".format(f)
        return titulo
    elif v == "Tpro":
        titulo = "Temperatura promedio en 24h\n Pronóstico válido para: {}".format(f)
        return titulo
    elif v == "Hr":
        titulo = "Humedar relativa promedio en 24h\n Pronóstico válido para: {}".format(f)
        return titulo
    elif v == "Hrmin":
        titulo = "Humedad relativa mínima en 24h\n Pronóstico válido para: {}".format(f)
        return titulo
    elif v == "Hrmax":
        titulo = "Humedad relativa máxima en 24h\n Pronóstico válido para: {}".format(f)
        return titulo
    else:
        pass


if __name__ == '__main__':
    main()
