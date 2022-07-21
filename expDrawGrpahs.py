import json
import math

import numpy as np
from numpy.polynomial.polynomial import polyfit
import matplotlib.pyplot as plt
import os
import gc

from sklearn.metrics import mean_squared_error


def getLinePoints(x, y, b, m):
    c = 0
    linePoints = []
    while (c < len(x)):
        z = m * x[c] + b
        linePoints.append(z)
        c = c + 1
    return linePoints

def GetGraphs(MasterData,outPath,sigma):
    results_dir = os.path.join(outPath + '/GraphData')
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
        print(results_dir+"...Result directory")

    for key in MasterData:
        x = np.array(MasterData[key][0])
        y = np.array(MasterData[key][1])
        if (len(x)>0 and key =="FUN_GT::LLCSBFT_GT_SEARCH_K_END_X_VCCR_XTFM_4300_X_CSE"):
            b, m = polyfit(x, y, 1)
            if m > 0:
                m = 0
                b = np.mean(y)
            plt.figure()

            plt.plot(x,y, 'g.')

            plt.plot(x, b + m * x, 'b-')

            linePoints = getLinePoints(x, y, b, m)
            MSE = mean_squared_error(y, linePoints)
            RMSE = math.sqrt(MSE)
            if (RMSE >= 0.02):
                sigma_Val = RMSE * float(sigma)
            else:
                sigma_Val = (0.02) * float(sigma)
            kill_offset= sigma_Val + b
            plt.plot(x, kill_offset + m * x, 'r-')
            m=-0.0000346
            b=1.642721
            plt.plot(x, b + m * x, 'm-')
            plt.title(key)
            plt.show()

def ReadData(path):
    with open(path) as data:
        d = json.load(data)
        data.close()
    MasterData={}
    for tests in d:
        fullName= tests['YName']
        x=[]
        y=[]
        for val in tests['Data']:
            if (float(val['YValue'])>0):
                x.append(float(val['XValue']))
                y.append(float(val['YValue']))

        MasterData[fullName]=[x,y]
    return MasterData



if __name__ == '__main__':
    path = "C:/temp/axel_temp/vminData.json"
    out_Path = "C:/temp/axel_temp"
    sigma = 8
    MasterData=ReadData(path)
    GetGraphs(MasterData,out_Path,sigma)
