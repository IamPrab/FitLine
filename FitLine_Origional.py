import json
import numpy as np
from numpy.polynomial.polynomial import polyfit
import matplotlib.pyplot as plt
import os
import scipy.stats as scipystats
from pyod.utils.data import get_outliers_inliers
from sklearn.metrics import mean_squared_error
import math
import pandas as pd
from pyod.models.abod import ABOD
from pyod.models.knn import KNN

class Results:
    SourceTestName: str
    Intercept: float
    Slope: float
    XParameter: str
    RootMeanSquareError: float
    KillRate: float
    PolulationStatistics: list[float]



IDV="nill"
HeaderVmins=[]

def kill_points(key,x,y,b,m):
    passToKillBucket={}
    passBucketX=[]
    passBucketY=[]
    killBucketX=[]
    killBucketY=[]

    killOffset=0.16

    count=0
    while(count<len(x)):
        kill_line= killOffset + b + m * x[count]
        if y[count] >= kill_line:
            killBucketX.append(x[count])
            killBucketY.append(y[count])
        else:
            passBucketX.append(x[count])
            passBucketY.append(y[count])
        count=count+1
    passToKillBucket[key]=[passBucketX,passBucketY,killBucketX,killBucketY]

    return passToKillBucket

def distributionStatistic(x,y,b,m):
    c=0
    max=0
    distStats={}
    arrStats=[]
    while(c < len(y)):
        sigma=round((y[c]-((m*x[c])+b))/0.02)
        #print(sigma)
        if sigma<0:
            sigma=-1*sigma
        if sigma>max:
            max=sigma
        if sigma>=0:
            if sigma in distStats:
                distStats[sigma]=distStats[sigma]+1
            else:
                distStats[sigma]=1
        c=c+1
    arrStats=np.zeros(max+1)
    for key in distStats:
        arrStats[key]=distStats[key]
    for i in range(len(arrStats)-1):
        arrStats[i+1]=arrStats[i]+arrStats[i+1]
    for i in range(len(arrStats)):
        arrStats[i]=(arrStats[i]/len(y))

    #print(arrStats)
    return arrStats


def getLinePoints(x,y,b,m):
    c=0
    linePoints=[]
    while(c < len(x)):
        z=m*x[c]+b
        linePoints.append(z)
        c=c+1
    return linePoints

def fitLine(pair, file):
    my_path= os.path.dirname(__file__)
    results_dir = my_path + '\\Results_graph'
    for key in pair:
        #plt.figure()
        x = np.array(pair[key][0])
        y = np.array(pair[key][1])
        print(key,len(x),len(y))
        df = pd.DataFrame(zip(y,x))
        df = df[(np.abs(scipystats.zscore(df)) < 3).all(axis=1)]
        x1=np.array(df[1])
        y1= np.array(df[0])
        if x1.size!=0 and y1.size !=0:
            b1, m1 = polyfit(x1, y1, 1)
        b, m =polyfit(x, y, 1)
        #print(b,m,key)



        stats=distributionStatistic(x,y,b,m)
        passToKillBucket = kill_points(key,x,y,b,m)
        passBucketX = passToKillBucket[key][0]
        passBucketY = passToKillBucket[key][1]
        killBucketX = passToKillBucket[key][2]
        killBucketY = passToKillBucket[key][3]
        killToPassRatio = len(killBucketY)/len(y)
        #print(killToPassRatio)

        linePoints=getLinePoints(x,y,b,m)
        MSE = mean_squared_error(y, linePoints)

        RMSE = math.sqrt(MSE)

        result1=Results()
        result1.Slope=m
        result1.Intercept=b
        result1.SourceTestName=key
        result1.XParameter=IDV
        result1.RootMeanSquareError=RMSE
        result1.KillRate=killToPassRatio
        result1.PopulationStatistics=stats.tolist()


        json_string = json.dumps(result1, default=lambda o: o.__dict__, sort_keys=True, indent=2)
        file.write(json_string)
        file.write(',')
        #
        # plt.plot(x,y, 'g.')
        # plt.plot(x1,y1, 'y.')
        #
        # plt.plot(x, b + m * x, 'b-')
        # plt.plot(x, b1 + m1* x, 'r-')
        # kill_offset= 0.16+b
        # plt.plot(x, kill_offset + m * x, 'r-')
        #
        # if "::" in key:
        #     name=key.split("::")
        #     file_name= name[0]+name[1]
        #     plt.savefig(results_dir+file_name)
        # else:
        #     plt.savefig(results_dir+key)
        # plt.close()



def read_data(path):
    IDV_Vmin_Dict={}
    IDV_Vmin_Dict = {}
    with open(path) as data:
        d = json.load(data)
        data.close()

        for i in d:
            key = i['VminName']
            HeaderVmins.append(key)
            IdvValues=[]
            VminVlaues=[]
            CoreVminIdvPair=[]
            for j in i['Data']:
                IdvValues.append(float(j['IDV']))
                VminVlaues.append(float(j['Vmin']))
                listOfGlobals = globals()
                listOfGlobals['IDV'] = j['IdvName']
                core_Vmin_Idv=j['VminName']+"%"+str(j['IDV'])+"%"+str(j['Vmin'])
                if j['VminName']!= key :
                    CoreVminIdvPair.append(core_Vmin_Idv)
            IDV_Vmin_Dict[key] = [IdvValues, VminVlaues]

            for i in CoreVminIdvPair:
                dataStr= i.split("%")
                VminName = dataStr[0]
                IDV = float(dataStr[1])
                Vmin = float(dataStr[2])
                CoreIDV=[]
                CoreVmin=[]

                if VminName not in IDV_Vmin_Dict:
                    CoreIDV.append(IDV)
                    CoreVmin.append(Vmin)
                    IDV_Vmin_Dict[VminName] = [CoreIDV, CoreVmin]

                else:
                    x= np.array(IDV_Vmin_Dict[VminName][0])
                    y= np.array(IDV_Vmin_Dict[VminName][1])
                    xNew = np.append(x,IDV)
                    yNew = np.append(y,Vmin)
                    IDV_Vmin_Dict[VminName] = [xNew,yNew]


    return IDV_Vmin_Dict

# def GetOutpulForAxelParsing(equationsFile):
#     SupersetVmin = {}
#     with open(equationsFile) as data:
#         d = json.load(data)
#         data.close()
#
#         for tests in d:
#             testName= tests['SourceTestName']
#             result1 = Results()
#             result1.Slope = tests['Slope']
#             result1.Intercept = tests['Intercept']
#             result1.SourceTestName = tests['SourceTestName']
#             result1.XParameter = tests['XParameter']
#             result1.RootMeanSquareError = tests['RootMeanSquareError']
#             result1.KillRate = tests['KillRate']
#             result1.PopulationStatistics = tests['PopulationStatistics']


    path = "C:/Users/kaurp/PycharmProjects/FitLine_NewData/idvVminPairs.json"
    outPath = "C:/Users/kaurp/PycharmProjects/FitLine_NewData/results1.json"

    IDV_Vmin_Dict=read_data(path)
    with open(outPath, 'w') as file:
        file.write("[")
        fitLine(IDV_Vmin_Dict, file)
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.write("]")


