# -*- coding: utf-8 -*-

import sys
import cv
import os
import math
import numpy as np

from opencv import highgui
from dis import dis

# imagens de entada
width = 320 
height = 240

# Video de saida: 9 imagens em cada quadro.
multiplicadorTamanho = 3
nw = int(320*multiplicadorTamanho)
nh = int(240*multiplicadorTamanho)

fps = 20

# http://www.koders.com/cpp/fid1791D327A443F07957F42F94831CD7B6FA6A712B.aspx
# retirado do teste do trabalho prático... que funciona
fourcc = 1196444237

fourcc = cv.CV_FOURCC('P','I','M','1')

print 'Dimensoes do video de saida: %dx%d' % (nw,nh)
print 'Taxa de quadros: %d fps' % (fps)






# informacoes para escrever texto sobre o video
line_type = cv.CV_NORMAL
fontMaior = cv.InitFont (cv.CV_FONT_VECTOR0,0.7, 0.7, 0.0, 1, line_type)
fontMenor = cv.InitFont (cv.CV_FONT_HERSHEY_COMPLEX,0.5, 0.5, 0.0, 1, line_type)
fontGigante = cv.InitFont (cv.CV_FONT_VECTOR0,0.9, 0.7, 0.0, 1, line_type)

if len(sys.argv) < 2:
    print 'O primeiro parametro é o diretorio com os videos de entrada:'
    print 'Os vídeos serão alinhados por ordem alfabética, até 9 vídeos com extensão .avi.'
    print 'O arquivo de saída ficará no mesmo diretório de entrada!'
    sys.exit()

dirVideos = sys.argv[1] + '/'

print
print 'Diretório de entdada e saída dos vídeos: ' +  dirVideos
print

ARQ_SAIDA = 'VIDEOx9.avi'

try:
    os.remove(dirVideos + ARQ_SAIDA)
except:
    pass










#carrega as imagens originais na memória...
def carregaArquivosDiretorio(diretorio,extensoes):   
    
    
    arquivos = os.listdir(diretorio)
    if not arquivos:
        print '  Sem arquivos de imagens originais neste diretorio.'
        return []
    
    arquivosSaida = []
            
    for arq in arquivos:
        for ext in extensoes:
            if ext in arq:                
                arqPath = r"%s%s"  % (diretorio,arq)
                arquivosSaida.append(arq)                
                            
    return arquivosSaida
              













# carrega os videos de entrada.
arquivos = carregaArquivosDiretorio(dirVideos, ['.avi'])

if not arquivos:
    print 'Não há arquivos de vídeo no diretório informado!'
    exit()

print 'Arquivos de vídeo encontrados: %d' % len(arquivos)
print arquivos
print






# cria o escritores para os videos de saida
writer_saida = cv.CreateVideoWriter('%s/%s' % (dirVideos,ARQ_SAIDA),int(fourcc),fps,(int(nw),int(nh)),1)


# usa o primeiro vídeo como tamanho de todos


captures = []
for i in range(len(arquivos)):
    capture = cv.CaptureFromFile(dirVideos + arquivos[i])
    captures.append(capture)
    
totalFrames = int(cv.GetCaptureProperty(captures[0], cv.CV_CAP_PROP_FRAME_COUNT)) 

print 'Total de frames do video 0: %d' % totalFrames



# verifica cada frame do video
for iframe in xrange(totalFrames):
    
    print 'Processando frame %d de %d' % (iframe,totalFrames)
    
        
    # cria a imagem de saida
    imgSaida = cv.CreateImage((nw,nh), cv.IPL_DEPTH_8U, 3)
    
    #cria o array de imagens de entrada e textos.
    imagens = []
    textos = []    
    # carrega as imagens... um frame de cada arquivo de entrada
    for i in range(len(arquivos)):
        # captura o frame
        imagens.append(cv.QueryFrame(captures[i]))
        # coloca o texto de cada um
        textos.append('')
        

    # copia as imagens nas posicoes especificas do frame final
    for k in range(len(imagens)):
        img = imagens[k]       
          
          
        if k < len(textos):
            texto = '  ' + textos[k] 
          
          
        xi = (k % multiplicadorTamanho) * width
        yi = ((k/3) % multiplicadorTamanho) * height        
        
                
        cor = (255,255,255)
        #escreve preto no ultimo video.
        if k==len(imagens)-1:
            cor = (0,0,0)
        cv.PutText (img, texto, (0,height-20), fontMaior, cor)
        
        for x in range(width):
            for y in range(height):
                imgSaida[y+yi,x+xi] = img[y,x]      
       

    
    
    
    
    
    
    
    # coloca a imagem do gráfico sobre a imagem...   
        
        

   
    if i == 1000:
        exit()
        
        
        
    
    # grava o frame mais de uma vez para deixar o video mais lento.
    # o codec nao suporta diminuir o framerate.
    for slow in range(4):
        cv.WriteFrame(writer_saida, imgSaida)       
    
    
    
