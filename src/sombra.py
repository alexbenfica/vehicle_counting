# -*- coding: utf-8 -*-

import sys
import os
import math
import time
import numpy as np
from pprint import pprint

import cv
from opencv import highgui
from util import *







'''
Detecta a sombra em uma imagem recebendo a imagem e o backgroud.
Retorna mascara com as regiões de sombra.

http://dali.mty.itesm.mx/~autonomos/Navdyn/node11.html

'''
def DetectaSombra(frame,bg):
    
    dbg = 1
    
    if dbg:
        t1 = time.time()    
 
    
    print 'Detectando sombras na imagem...'
    
    # gera as imagens de cada canal RGB
    imgCinza = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U,1)
    imgHSV = cv.CloneImage(frame) 
            
    imgH = cv.CloneImage(imgCinza)
    imgS = cv.CloneImage(imgCinza)
    imgV = cv.CloneImage(imgCinza)
    
    imgR = cv.CloneImage(imgCinza)
    imgG = cv.CloneImage(imgCinza)
    imgB = cv.CloneImage(imgCinza)
    

    bgCinza = cv.CreateImage(cv.GetSize(bg), cv.IPL_DEPTH_8U,1)
    bgHSV = cv.CloneImage(bg) 
            
    bgH = cv.CloneImage(bgCinza)
    bgS = cv.CloneImage(bgCinza)
    bgV = cv.CloneImage(bgCinza)
    
    bgR = cv.CloneImage(bgCinza)
    bgG = cv.CloneImage(bgCinza)
    bgB = cv.CloneImage(bgCinza)
    
    
    
    # gera as imagens de cada frame e backgroun nos canais de HSV e RGB
    cv.CvtColor(frame, imgHSV, cv.CV_BGR2HSV)            
    cv.Split(imgHSV, imgH, imgS, imgV, None)    
    cv.Split(frame, imgR, imgG, imgB, None)    
    
    cv.CvtColor(bg, bgHSV, cv.CV_BGR2HSV)            
    cv.Split(bgHSV, bgH, bgS, bgV, None)    
    cv.Split(bg, bgR, bgG, bgB, None)


    # inicio de calculos para descobrir sombras.    
    ivbv = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U,1)
    cv.Div(imgV, bgV, ivbv,255)    

    isbs = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U,1)
    cv.Sub(imgS, bgS, isbs)

    ihbh = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U,1)
    cv.AbsDiff(imgH, bgH, ihbh)

    # parametros de deteccao de sombra
    alfa = 190
    beta = 210
        
    thrSat = 20    
    thrHue = 50



    alfa = 220
    beta = 240
        
    thrSat = 90    
    thrHue = 90




    
    nErode = 0
    nDilate = 0
    
    # trata ivbv
    imgThr_ivbv = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U,1)
    # deixa apenas os menores que beta
    cv.Threshold(ivbv, imgThr_ivbv, beta, 255, cv.CV_THRESH_TRUNC)       
    # deixa apenas os maiores que alfa
    cv.Threshold(imgThr_ivbv, imgThr_ivbv, alfa, 255, cv.CV_THRESH_TOZERO)
    # binariza    
    cv.Threshold(imgThr_ivbv, imgThr_ivbv, alfa, 255, cv.CV_THRESH_BINARY)    


    # trata isbs
    imgThr_isbs = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U,1)
    # deixa apenas os menores que thrSat
    cv.Threshold(isbs, imgThr_isbs, thrSat, 255, cv.CV_THRESH_BINARY)       


    # trata isbs
    imgThr_ihbh = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U,1)
    # deixa apenas os menores que thrSat
    cv.Threshold(ihbh, imgThr_ihbh, thrHue, 255, cv.CV_THRESH_BINARY_INV)       


    
    # onde é preto em todas as imagens, é sombra
    imgSombra = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U,1)
    
    
    cv.Not(imgThr_ivbv,imgThr_ivbv)
    cv.Not(imgThr_isbs,imgThr_isbs)
    
    cv.And(imgThr_ivbv,imgThr_isbs,imgSombra)
    
    cv.Not(imgThr_ihbh,imgThr_ihbh)
        
    cv.And(imgSombra,imgThr_ihbh,imgSombra)

    for i in range(nErode):
        cv.Erode(imgSombra,imgSombra)
    
    for i in range(nDilate):
        cv.Dilate(imgSombra,imgSombra)


    


    if dbg:
        print 'Tempo para detectar sombras: %.5f' % (time.time() - t1)    
    #exibe frames de saida
    
    
    
    #destaca de verde a sombra sobre o frame
    frameDestacado = cv.CloneImage(frame)
    
    cv.Or(imgG,imgSombra,imgG)    
    
    cv.Merge(imgR, imgG, imgB,None, frameDestacado)
    

    '''    
    cv.ShowImage('frameDestacado',frameDestacado)
    cv.WaitKey()
    '''
    
    
    retorno = {}
    retorno['sombra'] = imgSombra
    retorno['sombraDestacada'] = frameDestacado
    
    
    
    
    return retorno
    

    cv.ShowImage('ivbv', ivbv)    
    cv.ShowImage('isbs', isbs)    
    cv.ShowImage('ihbh', ihbh)

    cv.ShowImage('imgThr_isbs', imgThr_isbs)
    cv.ShowImage('imgThr_ivbv', imgThr_ivbv)    
    cv.ShowImage('imgThr_ihbh', imgThr_ihbh)
    
    cv.ShowImage('imgSombra', imgSombra)

    
    
    cv.WaitKey()
    
    sys.exit()


    frameMerge = cv.CloneImage(frame)    
    cv.Merge(imgR, imgR, imgR,None, frameMerge)


       
    cv.ShowImage('frame', frame)
    cv.ShowImage('frameMerge', frameMerge)
    
    
    cv.ShowImage('imgR', imgR)
    cv.ShowImage('imgG', imgG)
    cv.ShowImage('imgB', imgB)
    
    cv.ShowImage('imgH', imgH)
    cv.ShowImage('imgS', imgS)
    cv.ShowImage('imgV', imgV)
    
    cv.WaitKey()

    
    
    
    
    
    
    
    
    
    
    
    
    
    return 0
    




# se chamar diretamente, executa
if 'sombra.py' in sys.argv[0]:
    imgFrame = cv.LoadImage(sys.argv[1])
    imgBack = cv.LoadImage(sys.argv[2])
    sombras = DetectaSombra(imgFrame, imgBack)
    
    



