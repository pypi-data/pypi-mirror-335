 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
 #                                                                                 #
 # ALPS Project: Algorithms and Libraries for Physics Simulations                  #
 #                                                                                 #
 # ALPS Libraries                                                                  #
 #                                                                                 #
 # Copyright (C) 2010 - 2013 by Lukas Gamper <gamperl@gmail.com>                   #
 #                      2012 by Troels F. Roennow <tfr@nanophysics.dk>             #
 #                                                                                 #
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the “Software”),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
 #                                                                                 #
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import sys

if sys.version_info[:2] >= (3, 8):
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping
import types

from .cxx.pyngsparams_c import params
params.__bases__ = (MutableMapping, ) + params.__bases__

from .cxx.pyngsobservable_c import observable
class ObservableOperators:
    def __lshift__(self, other):
        self.append(other)
observable.__bases__ = (ObservableOperators, ) + observable.__bases__

class RealObservable:
    def __init__(self, name, binnum = 0):
        self.name = name
        self.binnum = binnum
    def addToObservables(self, observables): #rename this with new ALEA
        observables.createRealObservable(self.name, self.binnum)

class RealVectorObservable:
    def __init__(self, name, binnum = 0):
        self.name = name
        self.binnum = binnum
    def addToObservables(self, observables): #rename this with new ALEA
        observables.createRealVectorObservable(self.name, self.binnum)

from .cxx.pyngsobservables_c import observables
observables.__bases__ = (MutableMapping, ) + observables.__bases__

from .cxx.pyngsobservable_c import createRealObservable #remove this with new ALEA!
from .cxx.pyngsobservable_c import createRealVectorObservable #remove this with new ALEA!

from .cxx.pyngsresult_c import result
from .cxx.pyngsresult_c import observable2result #remove this with new ALEA!

from .cxx.pyngsresults_c import results
results.__bases__ = (MutableMapping, ) + results.__bases__

from .cxx.pyngsbase_c import mcbase

from .cxx.pyngsapi_c import collectResults, saveResults

from .cxx.pyngsrandom01_c import random01
