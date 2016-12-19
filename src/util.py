# -*- coding: utf-8 -*-

import sys
import os



def criaDir(diretorio):
    if not os.path.exists(diretorio):
        try:
            os.makedirs(diretorio)
        except:
            pass



