# -*- coding: utf-8 -*-

import sys
import os
import math
import numpy as np
from pprint import pprint

import cv
from opencv import highgui
from util import *




'''
Recebe uma listagem de frames e retorna uma imagem que é uma estimativa do fundo da imagem.
'''
def estimaBG(frames):           
    
    npixels = cv.GetSize(frames[0])[1] * cv.GetSize(frames[0])[0]
    
    gray = cv.CreateImage(cv.GetSize(frames[0]), cv.IPL_DEPTH_8U,1)
    frAbsDif = cv.CloneImage(gray)    
    frThrDif = cv.CloneImage(gray)
    frAnt = cv.CloneImage(gray)
        
    # converte cada quadro para cinza     
    cinzas = []       
    for fr in frames:    
        gray = cv.CreateImage(cv.GetSize(frames[0]), cv.IPL_DEPTH_8U,1)        
        cv.CvtColor(fr, gray, cv.CV_RGB2GRAY)
        cinzas.append(gray)
        
        
    iframe = 1    
    fundos = []
    for fr in cinzas[1:]:        
        frAnt = cinzas[iframe - 1]
        cv.AbsDiff(frAnt,fr,frAbsDif)
        
        pixelsDiferentesAbs =  cv.CountNonZero(frAbsDif)
        
        # limiariza para evitar diferencas muito pequenas.             
        cv.Threshold(frAbsDif, frThrDif, 45, 255,cv.CV_THRESH_TOZERO)        
        # se a direrença for zero, considera a imagem para a mediana dos fundos        
        pixelsDiferentesThr =  cv.CountNonZero(frThrDif)
                
        if not pixelsDiferentesThr:        
            #print 'Imagem adicionada para determinacao do background...'
            fundos.append((frames[iframe],cv.CloneImage(frThrDif),cv.CloneImage(frThrDif),pixelsDiferentesAbs,pixelsDiferentesThr))
        iframe += 1

        
    if not fundos:
        print 'Não foi possivel determinar o fundo usando os primeiros %d frames da imagem' % len(frames)
        sys.exit()

    # pega o menor threshold absoluto, ordenando e pegando o primeiro.
    def porThr(a,b):
        return cmp(a[3],b[3])    
    fundos.sort(porThr)
    
    # retorna o que apresentou melhor diferença com relação ao anterior     
    return fundos[0][0]
    

    
    
    
    
        
    return fr
        
    
    
    
    
    