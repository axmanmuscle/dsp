import numpy as np

class emitter():
  def __init__(self):
    self.pos = 0
    self.vel = 0


class stat_emitter(emitter):
  """
  stationary emitter class
  """
  
  def __init__(self, pos):
    self.pos = pos
    self.vel = 0