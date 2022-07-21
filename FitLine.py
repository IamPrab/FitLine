import json
import numpy as np
from numpy.polynomial.polynomial import polyfit
import matplotlib.pyplot as plt
import os
import scipy.stats as st
from sklearn.metrics import mean_squared_error
import math

class Results:
    SourceTestName: str
    Intercept: float
    Slope: float
    XParameter: str
    RootMeanSquareError: float
    KillRate: float
    PopulationStatistics: list[float]

IDV="nill"

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
            #print(key)
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

def fitLine(pair, file, outpath):
    my_path = os.path.dirname(__file__)
    results_dir = my_path + '\\Result_graphO'
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
        print('DirectoryMadeResult')
    for key in pair:
        #plt.figure()
        x = np.array(pair[key][0])
        y = np.array(pair[key][1])
        b, m = polyfit(x, y, 1)
        #print(b,m,key)

        stats = distributionStatistic(x, y, b, m)
        passToKillBucket = kill_points(key,x,y,b,m)
        passBucketX = passToKillBucket[key][0]
        passBucketY = passToKillBucket[key][1]
        killBucketX = passToKillBucket[key][2]
        killBucketY = passToKillBucket[key][3]
        killToPassRatio = len(killBucketY)/len(y)

        linePoints = getLinePoints(x, y, b, m)
        MSE = mean_squared_error(y, linePoints)

        RMSE = math.sqrt(MSE)
        if (RMSE >= 0.16):
            b=b+(8*RMSE)-0.16

        result1 = Results()
        result1.Slope = m
        result1.Intercept = b
        result1.SourceTestName = key
        result1.XParameter = IDV
        result1.RootMeanSquareError = RMSE
        result1.KillRate = killToPassRatio
        result1.PopulationStatistics=stats.tolist()


        json_string = json.dumps(result1, default=lambda o: o.__dict__, sort_keys=True, indent=2)
        file.write(json_string)
        file.write(',')

        plt.plot(passBucketX, passBucketY, 'g.')

        plt.plot(x, b + m * x, 'b-')
        kill_offset= 0.16+b
        plt.plot(x, kill_offset + m * x, 'r-')

        if "::" in key:
            name=key.split("::")
            file_name= name[0]+name[1]
            plt.savefig(results_dir+"\\"+file_name)
        else:
            plt.savefig(results_dir+"\\"+key)
        plt.close()



def read_data(path):
    IDV_Vmin_Dict={}
    with open (path) as data:
        d= json.load(data)
        data.close()

        for i in d:
            key = i['VminName']
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



def main(args1, args2):
    path = args1
    outPath = args2

    IDV_Vmin_Dict=read_data(path)
    results_dir = outPath + '/equations.json'
    with open(results_dir, 'w') as file:
        file.write("[")
        fitLine(IDV_Vmin_Dict, file, outPath)
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.write("]")

    print('done')
    #
    # - N150118A
    # - N150144A
    # - N150167A
    # - N151469A

    #- N1514690