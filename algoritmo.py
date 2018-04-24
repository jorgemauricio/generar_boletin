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
from reportlab.lib.pagesizes import portrait
from reportlab.platypus import Image

def main():
    """
    Función que genera los mapas de temperatura mínima
    """
    #%% fecha del pronostico
    # fechaPronostico = strftime("%Y-%m-%d")
    fechaPronostico = "2018-04-17"
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

    cols = ["Long","Lat","Graupel","Hail","Rain","Tmax","Tmin","Tpro","Dpoint","Hr","Windpro","WindDir","Hrmin","Hrmax","TprSoil0_10","TprSoil10_40","WprSoil0_10","WprSoil10_40"]

    data1.columns = cols
    data2.columns = cols
    data3.columns = cols
    data4.columns = cols
    data5.columns = cols

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
            # simbologia = generar_simbologia(variable)
            # cbar.set_label(simbologia)
            titulo_mapa = generarTexto(variable, arrayFechas[counterFecha])
            plt.title(titulo_mapa)
            titulo_archivo = "{}/data/{}/{}_{}.png".format(path, fechaPronostico,variable, i)
            plt.annotate('@2018 INIFAP', xy=(-102,22), xycoords='figure fraction', xytext=(0.45,0.45), color='g')
            plt.savefig(titulo_archivo, dpi=600, bbox_inches='tight')
            counterFecha += 1
            print('****** Genereate: {}'.format(titulo_archivo))

        # generar pdf

        """
        GENERAR GRÁFICA

        y1 = []
        y2 = []

        for k in range(1,6):
            y1.append(data["{}{}".format(variable, k)].max())
            y2.append(data["{}{}".format(variable, k)].min())

        ind = np.arange(5)

        fig, ax = plt.subplots()
        width = 0.35
        rects1 = ax.bar(ind, y1, width, color='darkred')
        rects2 = ax.bar(ind + width, y2, width, color='darkblue')

        # add some text for labels, title and axes ticks
        # ax.set_ylabel(simbologia)
        # ax.set_title(variable)
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(arrayFechas)

        # ax.legend((rects1[0], rects2[0]), ('Máximo', 'Mínimo'), loc=3)

        def autolabel(rects):
            # Attach a text label above each bar displaying its height
            for rect in rects:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                        '%d' % int(height),
                        ha='center', va='bottom')

        autolabel(rects1)
        autolabel(rects2)

        titulo_grafica = "{}/data/{}/{}_grafica.png".format(path, fechaPronostico, variable)

        plt.savefig(titulo_grafica, dpi=600, bbox_inches='tight' )
        """


        nombre_archivo_pdf = "{}/data/{}/{}.pdf".format(path, fechaPronostico, variable)
        c = canvas.Canvas(nombre_archivo_pdf, pagesize=portrait(letter))

        # logo inifap
        logo_inifap = "{}/images/inifap.jpg".format(path)
        c.drawImage(logo_inifap, 20, 700, width=100, height=100)

        # encabezado
        c.setFont("Helvetica", 20, leading=None)
        titulo_pdf = generar_titulo_pdf(variable)
        c.drawCentredString(350, 750, titulo_pdf)

        # imagen anuales
        imagen_1 = "{}/data/{}/{}_1.png".format(path, fechaPronostico, variable)
        imagen_2 = "{}/data/{}/{}_2.png".format(path, fechaPronostico, variable)
        imagen_3 = "{}/data/{}/{}_3.png".format(path, fechaPronostico, variable)
        imagen_4 = "{}/data/{}/{}_4.png".format(path, fechaPronostico, variable)
        imagen_5 = "{}/data/{}/{}_5.png".format(path, fechaPronostico, variable)
        imagen_6 = "{}/images/info_wrf.png".format(path)

        # draw images
        c.drawImage(imagen_1, 20, 475, width=260, height=172)
        c.drawImage(imagen_2, 325, 475, width=260, height=172)
        c.drawImage(imagen_3, 20, 250, width=260, height=172)
        c.drawImage(imagen_4, 325, 250, width=260, height=172)
        c.drawImage(imagen_5, 20, 25, width=260, height=172)
        c.drawImage(imagen_6, 325, 25, width=260, height=172)

        c.showPage()
        c.save()

        print(titulo_pdf)

def colores_por_variable(v):
    """
    param: v: variable
    return : nombre del cmap a mapear
    """
    if v == "Rain":
        return "gist_ncar"
    if v == "Tmax" or v == "Tmin" or v == "Tpro":
        return "jet"
    if v == "Hr" or v == "Hrmin" or v == "Hrmax":
        return "YlGnBu"
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

def generar_titulo_pdf(v):
    titulo = ""
    if v == "Rain":
        titulo = "Precipitación (mm) acumulada en 24h"
        return titulo
    elif v == "Tmax":
        titulo = "Temperatura (°C) máxima en 24h"
        return titulo
    elif v == "Tmin":
        titulo = "Temperatura (°C) mínima en 24h"
        return titulo
    elif v == "Tpro":
        titulo = "Temperatura (°C) promedio en 24h"
        return titulo
    elif v == "Hr":
        titulo = "Humedad relativa (%) promedio en 24h"
        return titulo
    elif v == "Hrmin":
        titulo = "Humedad relativa (%) mínima en 24h"
        return titulo
    elif v == "Hrmax":
        titulo = "Humedad relativa (%) máxima en 24h"
        return titulo
    else:
        pass


def generarTexto(v, f):
    """
    Función que nos permite generar el texto correspondiente para cada mapa
    param: v: variable
    param: f: fecha
    """
    anio_t, mes_t, dia_t = f.split("-")
    titulo = "{} de {} de {}".format(dia_t, generar_mes_en_string(int(mes_t)), anio_t)
    return titulo

def generar_mes_en_string(m):
    """

    """
    if m == 1:
        return "Enero"
    elif m == 2:
        return "Febrero"
    elif m == 3:
        return "Marzo"
    elif m == 4:
        return "Abril"
    elif m == 5:
        return "Mayo"
    elif m == 6:
        return "Junio"
    elif m == 7:
        return "Julio"
    elif m == 8:
        return "Agosto"
    elif m == 9:
        return "Septiembre"
    elif m == 10:
        return "Octubre"
    elif m == 11:
        return "Noviembre"
    elif m == 12:
        return "Diciembre"
    else:
        pass


if __name__ == '__main__':
    main()
