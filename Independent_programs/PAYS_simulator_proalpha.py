from my_funcs import *
import warnings
import pandas as pd
import numpy as np
from scipy.stats import skewnorm

def create_pdf(sd, mean, alfa):
    #invertire il segno di alfa
    x = skewnorm.rvs(alfa, size=1000000)
    def calc(k, sd, mean):
      return (k*sd)+mean

    x = calc(x, sd, mean) #standard distribution

if __name__ == '__main__':

    size_frame=np.zeros(1000*50)

    size_frame.reshape(1000,50)


    return_frame=pd.DataFrame()
