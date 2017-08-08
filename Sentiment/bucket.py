#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging, os, sys
import numpy as np
import tensorflow as tf

from configurable import Configurable

#-------------- Logging  ----------------#
program = os.path.basename(sys.argv[0])
L = logging.getLogger(program)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)

#***************************************************************
class Bucket(Configurable):
  """"""
  
  #=============================================================
  def __init__(self, *args, **kwargs):
    """"""
    
    super(Bucket, self).__init__(*args, **kwargs)
    self._size = None
    self._data = None
    self._sents = None
    self._smod = None    
    return
  
  #=============================================================
  def reset(self, size):
    """"""
    
    self._size = size
    self._data = []
    self._sents = []
    self._smod = []
    return
  
  #=============================================================
  def add(self, sent):
    """"""
    
    if isinstance(self._data, np.ndarray):
      raise TypeError("The buckets have already been finalized, you can't add more")
    if len(sent) > self.size and self.size != -1:
      raise ValueError('Bucket of size %d received sequence of len %d' % (self.size, len(sent)))
    
    words = [word[0] for word in sent]#[1:] # remove root
    idxs = [word[1:] for word in sent]
    sentmod=[]
    modval = max([word[9] for word in sent])
    if modval==2:
      sentmod=[1,0,0]#positive
    elif modval==4:
      sentmod=[0,1,0]#negative
    else:
      sentmod=[0,0,1]#neutral
    self._smod.append(sentmod)
    self._sents.append(words)
    self._data.append(idxs)
    return len(self._data)-1
  
  #=============================================================
  def _finalize(self):
    """"""
    
    if self._data is None:
      raise ValueError('You need to reset the Buckets before finalizing them')
    
    if len(self._data) > 0:
      shape = (len(self._data), self.size, len(self._data[-1][-1]))
      data = np.zeros(shape, dtype=np.int32)
      for i, datum in enumerate(self._data):
        datum = np.array(datum)
        data[i, 0:len(datum)] = datum

      self._data = data
      self._sents = np.array(self._sents)
      self._smod = np.array(self._smod)
    else:
      self._data = np.zeros((0,1), dtype=np.float32)
      self._sents = np.zeros((0,1), dtype=str)
      self._smod = np.zeros((0,1),dtype=np.float32)
    L.info('Bucket %s is %d x %d' % ((self._name,) + self._data.shape[0:2]))
    return
  
  #=============================================================
  def __len__(self):
    return len(self._data)
  
  #=============================================================
  @property
  def size(self):
    return self._size
  @property
  def data(self):
    return self._data
  @property
  def sents(self):
    return self._sents
  @property
  def smod(self):
    return self._smod
