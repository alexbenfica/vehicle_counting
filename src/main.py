# -*- coding: utf-8 -*-

import sys
import cv
import os
import math
import numpy as np
import shutil

from opencv import highgui
from util import *
from background import *
from sombra import *


'''
--------------- Parametros ---------------------------------------------------------------
'''





# minima distancia entre as linhas inciais e finais de detecção de veiculos, com histerese
distMinimaExisteVeiculo = 40
distMinimaNaoExisteVeiculo = 30

# quadros por segundo no video de saida
fpsSaida = 12

SalvarVideoMovimento = False
passoLinhas = 1

nFramesBG = 50

TentativaDiferencaQuadros = False
TentativaDiferencaFundo = True


'''
----------------------------------------------------------------------------------------
'''

print 'Contagem de veiculos'

 
videoEntrada = sys.argv[1]
dirSaida = '../Saida/' 
criaDir(dirSaida)
dirSaida = dirSaida + os.path.basename(videoEntrada).replace('.','_')
#apaga tudo que existir no diretorio de saida do video.
shutil.rmtree(dirSaida, True)
# cria novamente o dir de saida
criaDir(dirSaida)
#cria um diretorio para imagens
criaDir('%s/imagens/'% dirSaida);




# abre o video de entrada
capture = cv.CaptureFromFile(videoEntrada)

width = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH)) 
height = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT))
fps = cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FPS)
fourcc = cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FOURCC) 
totalFrames = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_COUNT))

print 'Informacoes do video de entrada: %s' % videoEntrada
print 'Dimensoes do video de entrada: %dx%d' % (width,height)
print 'Taxa de quadros: %d fps' % (fps)
print 'Total de frames do video: %d' % (totalFrames)

print '?: %d' % (fourcc)





# informacoes para escrever texto sobre o video
line_type = cv.CV_NORMAL
fontMaior = cv.InitFont (cv.CV_FONT_VECTOR0,0.7, 0.7, 0.0, 1, line_type)
fontMenor = cv.InitFont (cv.CV_FONT_HERSHEY_COMPLEX,0.5, 0.5, 0.0, 1, line_type)







MARC_PIXEL_I = 128
MARC_PIXEL_F = 255



# sequencias de video onde existem carros 
sequencias = []


sequencias.append((0,totalFrames-1))
 
 
#sequencias = [[400,500]]
#sequencias = [[0,1000]]



iseq = 0
for frameInicial,frameFinal in sequencias:    
    iseq += 1
    
    if frameInicial % 2:
        print 'Frame inicial deve ser par!'
        exit()


    # cria o escritores para os videos de saida
    writer_original = cv.CreateVideoWriter('%s/0-ORIGINAL-seq-%d(%d a %d).avi' % (dirSaida,iseq,frameInicial,frameFinal),                                       
                                                                                   int(fourcc),fpsSaida,(int(width),int(height)),1)   

    writer_diff_fundo = cv.CreateVideoWriter('%s/1-DIF.FUNDO-seq-%d(%d a %d).avi' % (dirSaida,iseq,frameInicial,frameFinal),                                       
                                                                                   int(fourcc),fpsSaida,(int(width),int(height)),1)
    
    writer_diff_quadro = cv.CreateVideoWriter('%s/2-DIF.QUADRO-seq-%d(%d a %d).avi' % (dirSaida,iseq,frameInicial,frameFinal),                                       
                                                                                   int(fourcc),fpsSaida,(int(width),int(height)),1)
    
    writer_canny = cv.CreateVideoWriter('%s/4-CANNY-seq-%d(%d a %d).avi' % (dirSaida,iseq,frameInicial,frameFinal),                                       
                                                                                   int(fourcc),fpsSaida,(int(width),int(height)),1)

    writer_saida = cv.CreateVideoWriter('%s/5-CONTADOR-seq-%d(%d a %d).avi' % (dirSaida,iseq,frameInicial,frameFinal),                                       
                                                                                   int(fourcc),fpsSaida,(int(width),int(height)),1)

    writer_diff = cv.CreateVideoWriter('%s/6-DIF.CONSIDERADA-seq-%d(%d a %d).avi' % (dirSaida,iseq,frameInicial,frameFinal),                                       
                                                                                   int(fourcc),fpsSaida,(int(width),int(height)),1)

    writer_sombra = cv.CreateVideoWriter('%s/7-SOMBRA-seq-%d(%d a %d).avi' % (dirSaida,iseq,frameInicial,frameFinal),                                       
                                                                                   int(fourcc),fpsSaida,(int(width),int(height)),1)

    writer_indicadores = cv.CreateVideoWriter('%s/8-INDICADORES-seq-%d(%d a %d).avi' % (dirSaida,iseq,frameInicial,frameFinal),                                       
                                                                                   int(fourcc),fpsSaida,(int(width),int(height)),1)

    writer_diff_semsombra = cv.CreateVideoWriter('%s/9-SEM-SOMBRA-BINARIA-seq-%d(%d a %d).avi' % (dirSaida,iseq,frameInicial,frameFinal),                                       
                                                                                    int(fourcc),fpsSaida,(int(width),int(height)),1)                      



    if SalvarVideoMovimento:
        writer_movimento = cv.CreateVideoWriter('%s/video-movimento-seq-%d(%d a %d).avi' % ( dirSaida,iseq,frameInicial,frameFinal),                                       
                                                                                   int(fourcc),fps,(int(width),int(height)),1)


    distanciasLinhas = []
    nVeiculos = 0
    temVeiculo = False
    
    framesBG = []

    
    
    nFramesSaltar = 0
    
    
    # verifica cada frame do video
    for iframe in xrange(frameFinal):
        
        # captura o frame
        frame = cv.QueryFrame(capture)
        
        # salta alguns frames quando necessario
        for sk in range(nFramesSaltar):
            frame = cv.QueryFrame(capture)
            pass
            
        nFramesSaltar = 0
            
        

        if not frame: continue;
        
        if iframe < nFramesBG:
            print 'Usando frame %d para estimacao do fundo...' % iframe            
            framesBG.append(cv.CloneImage(frame))
            if SalvarVideoMovimento:
                cv.WriteFrame(writer_movimento, frame)
                framesAposMovimento = 10
            continue
        
        else:
            if iframe == nFramesBG:                
                background = estimaBG(framesBG)
                print 'Background determinado!'
                # salva uma copia do backgrout do video.
                
                cv.SaveImage('%s/imagens/background.jpg' % ( dirSaida), background)
                
                

        if iframe > frameFinal: continue;
        if iframe < frameInicial: continue;
        
        
        distanciaLinhas = 0
                
        
        print 'Processando frame: %d da seq %d (%.2f %%)' % (iframe,iseq,(iframe * 100.0)/(totalFrames))
        
        
        # crias as imagens copia somente no primeiro frame
        if (iframe == frameInicial + nFramesBG) or (iframe == frameInicial):
            gray = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U,1)
            frameDiff = cv.CloneImage(gray)            
            frameCarro = cv.CloneImage(gray)
            frameAnterior = cv.CloneImage(gray)
            bggray = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U,1) 
            cv.CvtColor(background, bggray, cv.CV_RGB2GRAY)
                

        
        # converte para cinza
        cv.CvtColor(frame, gray, cv.CV_RGB2GRAY)
        frameSaida = cv.CloneImage(frame)

        
            
        # grava o canny na saida
        gravarCanny = True
        if gravarCanny:
            frameCanny = cv.CloneImage(gray)        
            cv.Canny(gray,frameCanny,150,200,3)
            frameSaidaCanny = cv.CloneImage(frame)
            cv.CvtColor(frameCanny, frameSaidaCanny, cv.CV_GRAY2RGB)        
            cv.WriteFrame(writer_canny, frameSaidaCanny)
            
        
        # separa a imageem em H,S,V
        TentativaHSV = False
        if TentativaHSV:
            largura,altura = cv.GetSize(frame)[0],cv.GetSize(frame)[1]     
                            
            Ihsv = cv.CreateMat(altura,largura, cv.CV_8UC3)        
            hue = cv.CreateMat(altura,largura, cv.CV_8UC1)
            sat = cv.CreateMat(altura,largura, cv.CV_8UC1)
            val = cv.CreateMat(altura,largura, cv.CV_8UC1)
                    
            cv.CvtColor(frame, Ihsv, cv.CV_BGR2HSV)        
            cv.Split(Ihsv, hue, sat, val, None)                   
            
            if 0:
                cv.ShowImage('value', val)
                cv.WaitKey()                
                cv.ShowImage('hue', hue)
                cv.WaitKey()
        
                cv.ShowImage('saturation', sat)
                cv.WaitKey()
        
                cv.ShowImage('HSV', Ihsv)
                cv.WaitKey()
                
            
            cv.Threshold(sat, sat, 128, 255,cv.CV_THRESH_BINARY)
            cv.CvtColor(sat, frameSaida, cv.CV_GRAY2RGB)      
            cv.CvtScale( frameDiff, frameDiff)





        
        

        ProcessaImagem = True
        if ProcessaImagem:
            # filtro gaussiano para tirar o ruído
            cv.Smooth(gray, gray, cv.CV_GAUSSIAN,5,3)                        
            

            colunasIniciais = []
            colunasFinais = []

            pixelsIniciais = []
            pixelsFinais = []
            
            # faz a diferenca com o frame anterior
            if iframe != frameInicial:
                
                # Detecta a sombra
                sombras = DetectaSombra(frame,background)
                sombraDestacada =  sombras['sombraDestacada']
                imgSombra = sombras['sombra'] 

                GeraVideoSombra = True
                if GeraVideoSombra:                                        
                    cv.WriteFrame(writer_sombra, sombraDestacada)                    
                    #continue
                
                
                # subtrai do quadro anterior                  
                if TentativaDiferencaQuadros or 1:
                    p_diffThreshold = 40                    
                    cv.Sub(frameAnterior,gray,frameDiff)
                    cv.AbsDiff(frameAnterior,gray,frameDiff)                   
                    
                    frameDiffQuadroSaida = cv.CloneImage(frameDiff)                                        
                    #frameDiffGravacao = cv.CloneImage(frameDiff)                                        
                    cv.Threshold(frameDiff, frameDiff, p_diffThreshold, 255,cv.CV_THRESH_BINARY)
                    frameDiffQuadros = cv.CloneImage(frameDiff)
                
                
                # subtrai do background
                if TentativaDiferencaFundo:
                    p_diffThreshold = 40                    
                    cv.AbsDiff(bggray,gray,frameDiff)                    
                    frameDiffFundoSaida = cv.CloneImage(frameDiff)                    
                    cv.Threshold(frameDiff, frameDiff, p_diffThreshold, 255,cv.CV_THRESH_BINARY)
                    
                    #for i in range(2): cv.Erode(frameDiff,frameDiff)                    
                    #zera diferenca onde ha sombra        
                    frameSemSombra = cv.CloneImage(imgSombra)
                    # dilata sombra para pegar qualquer borada de sombra
                    #for i in range(2): cv.Erode(frameSemSombra,frameSemSombra)
                    for i in range(2): cv.Dilate(frameSemSombra,frameSemSombra)
                    
                    # inverte e faz um AND
                    cv.Not(frameSemSombra,frameSemSombra)
                    
                    
                                                           
                    cv.And(frameSemSombra, frameDiff, frameSemSombra)                    
                    
                    frameDiff = cv.CloneImage(frameSemSombra)
                    
                    
                    frameDiffSemSombra = cv.CloneImage(frameDiff)
                    
                                        


                    '''
                    Faça uma cópia da imagem.
                    
                    Dê um cvSmooth com método CV_MEDIAN para tirar ruídos da cópia.
                    
                    Dê open (erode + dilate) na cópia.
                    
                        O Erode deve eliminar os ruídos restantes. Você pode usar um kernel horizontal e depois um vertical.
                        Faça os dilates terem 1 grau a mais que o erode (na imagem final o branco que restará é maior que na original)
                    
                    Faça um AND da imagem original com a imagem do Open.
                    '''
                    
                    frameDiff2 = cv.CloneImage(frameDiff)
                    cv.Smooth(frameDiff2,frameDiff2,cv.CV_MEDIAN)
                    cv.Erode(frameDiff2,frameDiff2)
                    cv.Erode(frameDiff2,frameDiff2)                    
                    cv.Dilate(frameDiff2,frameDiff2)
                    cv.Dilate(frameDiff2,frameDiff2)
                    cv.Dilate(frameDiff2,frameDiff2)                    
                    cv.And(frameDiff2,frameDiff, frameDiff2)

                    cv.Dilate(frameDiffQuadros,frameDiffQuadros);                    
                    cv.Dilate(frameDiffQuadros,frameDiffQuadros);                       
                    cv.And(frameDiffQuadros,frameDiff2,frameDiff)
                    
                    frameDiffGravacao = cv.CloneImage(frameDiff)
                                    
                                    
                
                gravarDiff = 1
                if gravarDiff:                     
                    frameSaidaDiff = cv.CloneImage(frame)
                    cv.CvtColor(frameDiffGravacao, frameSaidaDiff, cv.CV_GRAY2RGB)        
                    cv.WriteFrame(writer_diff, frameSaidaDiff)
                    
                    cv.CvtColor(frameDiffQuadroSaida, frameSaidaDiff, cv.CV_GRAY2RGB)        
                    cv.WriteFrame(writer_diff_quadro, frameSaidaDiff)
                    
                    cv.CvtColor(frameDiffFundoSaida, frameSaidaDiff, cv.CV_GRAY2RGB)        
                    cv.WriteFrame(writer_diff_fundo, frameSaidaDiff)

                    cv.CvtColor(frameDiffSemSombra, frameSaidaDiff, cv.CV_GRAY2RGB)        
                    cv.WriteFrame(writer_diff_semsombra, frameSaidaDiff)
                    
                    
                    
                    
                
                     
                
                cv.Zero(frameCarro)
                
                
                
                
                
                
                                                
                
                # detecta o inicio do carro...                
                for y in range(0,height,passoLinhas):                    
                    for x in range(1,width-1):
                        pixel_ant = cv.Get2D(frameDiff,y, x-1)[0]
                        pixel = cv.Get2D(frameDiff, y, x)[0]                            
                        if pixel_ant < pixel:
                            cv.Set2D(frameCarro, y, x, MARC_PIXEL_I)
                            colunasIniciais.append(x)
                            pixelsIniciais.append((x,y))      
                            break
                        

                # detecta o fim do carro...                                
                for y in range(0,height,passoLinhas):                    
                    for x in range(1,width-1):
                        pixel_ant = cv.Get2D(frameDiff,y,(width-x)-1)[0]
                        pixel = cv.Get2D(frameDiff, y, (width-x))[0]                            
                        if pixel_ant < pixel:
                            cv.Set2D(frameCarro, y, width-x, MARC_PIXEL_F)
                            colunasFinais.append(width-x)
                            pixelsFinais.append((width-x,y))
                            break
        
                
                
                
                if colunasIniciais and colunasFinais:
                    
                    mediaI = int(np.mean(colunasIniciais))
                    mediaF = int(np.mean(colunasFinais))
                    
                    mediaI = int(np.median(colunasIniciais))
                    mediaF = int(np.median(colunasFinais))
                    
                    stdI = int(np.std(colunasIniciais))
                    stdF = int(np.std(colunasFinais))
                    
                    
                    minI = int(np.min(colunasIniciais))
                    minF = int(np.min(colunasFinais))

                    maxI = int(np.max(colunasIniciais))
                    maxF = int(np.max(colunasFinais))
                    
                    mediaI += minI
                    mediaF += minF

                    
                    #xlinhaInicial = minI
                    #xlinhaFinal = maxF



                    def porX(a,b):
                        return cmp(a[0],b[0])
                    
                    def porX_Reverso(a,b):
                        return cmp(b[0],a[0])                  

                    
                    #pega a media dos elementos menores na linha inicial
                    pixelsIniciais.sort(porX)
                    xs = []                    
                    for (x,y) in pixelsIniciais:
                        xs.append(x)
                    nx = len(pixelsIniciais)
                    xsm = []                        
                    nconsiderar = len(xs)
                    if len(xs) > 1:
                        nconsiderar = nx/2                            
                    for x in range(0,nconsiderar):
                       xsm.append(xs[x]) 
                    xlinhaInicial = int(np.mean(xsm))
                    
                    #print xs
                    #print xlinhaInicial


                    #pega a media dos elementos maiores na linha final
                    pixelsFinais.sort(porX_Reverso)
                    xs = []                    
                    for (x,y) in pixelsFinais:
                        xs.append(x)
                    nx = len(pixelsFinais)
                    xsm = []                        
                    nconsiderar = len(xs)
                    if len(xs) > 1:
                        nconsiderar = nx/2                            
                    for x in range(0,nconsiderar):
                       xsm.append(xs[x]) 
                    xlinhaFinal = int(np.mean(xsm))

                    #print xs
                    #print xlinhaFinal

                                        
                    # mostra uma linha na imagem de saida com a media do inicio e fim e o desvio padrão
                    cv.Line(frameSaida,(xlinhaInicial,0),(xlinhaInicial,height),(0,255,0),1)
                    cv.Line(frameSaida,(xlinhaFinal,0),(xlinhaFinal,height),(0,0,200),1)

                    distanciaLinhas = abs( xlinhaFinal - xlinhaInicial )
                    
                    
                    #minI = xlinhaInicial
                    #maxF = xlinhaFinal
                    
                    # marca a distâncias entre as linhas...                
                    distanciasLinhas.append(distanciaLinhas)
                    if (distanciaLinhas > distMinimaExisteVeiculo
                          and  ((minI > 20) and (maxF < 300)) 
                        ):                  
                        
                        if temVeiculo == False:
                            nVeiculos += 1
                            #salva imagem de cada veiculo detectado.
                            cv.SaveImage(dirSaida + '/imagens/veiculo_%03d - frame_%d.jpg' % (nVeiculos,iframe), frame)                            
                            # coloca a imagem preto e branca para mostrar a deteccao!
                            frameSaida = cv.CloneImage(frameSaidaDiff)
                            for i in range(0):
                                cv.WriteFrame(writer_saida, frameSaida)
                            
                        temVeiculo = True                    
                    else:
                        if (
                            (distanciaLinhas < distMinimaNaoExisteVeiculo)
                            or
                             ((minI < 80) and (maxF < 80))
                            or 
                             ((minI > 240) and (maxF > 240))
                             
                            or distanciaLinhas > 280 
                            
                            ):                       
                            temVeiculo = False
                
                




                # marca os pixels na imagem de saida
                for y in range(0,height,passoLinhas):                    
                    for x in range(1,width-1):
                        pixel = cv.Get2D(frameCarro, y, x)[0]
                        if pixel == MARC_PIXEL_F:
                            cv.Set2D(frameSaida, y, x, (255,0,0))
                        else:
                            if pixel == MARC_PIXEL_I:
                                cv.Set2D(frameSaida, y, x, (0,255,0))



            # copia o frama cinza para comparacao na proxima iteracao.    
            frameAnterior = cv.CloneImage(gray)            

            if SalvarVideoMovimento:
                                    
                if (colunasIniciais and colunasFinais) and framesAposMovimento == 0:
                    framesAposMovimento = 10                    
                    cv.WriteFrame(writer_movimento, frame)
                    
                if framesAposMovimento:
                    framesAposMovimento -= 1
                    cv.WriteFrame(writer_movimento, frame)
                    

        # mostra o numero de quadros sobreo video
        if ProcessaImagem:
            if colunasIniciais and colunasFinais:
                cv.PutText (frameSaida, "iMin=%d   fMax=%d" % (minI,maxF), (0 ,30), fontMenor, (200,255,255))
                cv.PutText (frameSaida, "#fr=%d    dist=%d" % (iframe,distanciaLinhas), (0 ,50), fontMenor, (0,255,255))            
            cv.PutText (frameSaida, "%d fps   #VEICULOS: %d" % (fpsSaida,nVeiculos), ((width-300) ,int(height-5)), fontMaior, (0,0,255))
                                   
        #salva o video de saida
        cv.WriteFrame(writer_saida, frameSaida)
        
        # salva o video com os indicadores de inicio e fim do carro
        frameCarroSaida = cv.CloneImage(frame)
        cv.Not(frameCarro,frameCarro)
        cv.CvtColor(frameCarro, frameCarroSaida, cv.CV_GRAY2RGB)
        cv.WriteFrame(writer_indicadores, frameCarroSaida)
        
        
        cv.WriteFrame(writer_original, frame)
        
        
        
        
        










                

