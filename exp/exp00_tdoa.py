import numpy as np

c = 299e6

def calc_range(x, y):
  return np.linalg.norm(x - y)

def calc_toa(tot, transmit_pos, receive_pos):
  """
  calculate time of arrival to a static receiver
  """
  r = calc_range(transmit_pos, receive_pos)
  return tot + r / c

def main():
  transmitter = np.array([[1, 1, 0]])

  rec1 = np.array([[50, 50, 25]])
  rec2 = np.array([[3, 100, 75]])

  toa1 = calc_toa(0, transmitter, rec1)
  toa2 = calc_toa(0, transmitter, rec2)

  tdoa = toa2 - toa1
  # uhh
  return 0

if __name__ == "__main__":
  main()