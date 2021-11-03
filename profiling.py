# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 11:51:13 2014

@author: cmurray
"""

import cProfile

def func_to_profile():
    import Heat_Model

cProfile.run('func_to_profile()')
