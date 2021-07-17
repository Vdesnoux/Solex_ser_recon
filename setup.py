# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 12:15:11 2020

@author: valerie DESNOUX
"""

import sys
from cx_Freeze import setup, Executable

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = None

  
setup(name = "Inti_ser_recon" , 
      version = "0.0" , 
      description = "traitement automatique INTI local pour Spectroheliographe Sol'EX" , 
      executables = [Executable("inti_ser_recon.py")]) 