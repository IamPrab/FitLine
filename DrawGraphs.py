import json
import math

import numpy as np
from numpy.polynomial.polynomial import polyfit
import matplotlib.pyplot as plt
import os
import gc
import matplotlib.colors as mcolors


def getLinePoints(x, y, b, m):
    c = 0
    linePoints = []
    while (c < len(x)):
        z = m * x[c] + b
        linePoints.append(z)
        c = c + 1
    return linePoints

def GetGraphs(MasterData,outPath,sigma,oldEquations,eqnsVminPred):
    results_dir = os.path.join(outPath + '/GraphData')
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
        print(results_dir+"...Result directory")

    for key in MasterData:
        x = np.array(MasterData[key][0])
        y = np.array(MasterData[key][1])
        uniqueId= MasterData[key][2]
        if (len(x)>10):

            # be, me = polyfit(x, y, 1)
            # print(be,me)
            m = eqnsVminPred[key][0]
            b= eqnsVminPred[key][1]
            #print(b, m, "----------------------------")
            vminpred =  eqnsVminPred[key][2]
            if m > 0:
                m = 0
                b = np.mean(y)
            plt.figure()
            i=0
            x1,y1,x2,y2,x3,y3,x5,y5,x43,y43,xn,yn = ([] for i in range (12))
            while (i<len(x)):
                if uniqueId[i] == "1":
                    x1.append(x[i])
                    y1.append(y[i])
                elif uniqueId[i] == "2":
                    x2.append(x[i])
                    y2.append(y[i])
                elif uniqueId[i] == "3":
                    x3.append(x[i])
                    y3.append(y[i])
                elif uniqueId[i] == "43":
                    x43.append(x[i])
                    y43.append(y[i])
                elif uniqueId[i] == "5":
                    x5.append(x[i])
                    y5.append(y[i])
                else:
                    xn.append(x[i])
                    yn.append(y[i])
                i=i+1
            plt.scatter(x1,y1,marker = '^', color ='darkgreen', label = "Bin1")
            plt.scatter(x2,y2,marker = '^', color ='tab:green', label = "Bin2")
            plt.scatter(x3, y3, marker = 'v', color = 'tab:purple', label = "Bin3")
            plt.scatter(x5, y5, marker = 'v', color ='deeppink', label = "Bin5")
            plt.scatter(x43, y43, marker = 'v', color = 'orange',label = "Bin43")
            plt.scatter(xn, yn, marker = 'v', color = 'maroon', label = "Other Bin")
            del  x1,y1,x2,y2,x3,y3,x5,y5,x43,y43,xn,yn

            plt.plot(x, b + m * x, 'b-')

            sigma = 10

            linePoints = getLinePoints(x, y, b, m)
            MSE = np.square(np.subtract(y,linePoints)).mean()
            RMSE = math.sqrt(MSE)
            sigma_Val = 0


            if (RMSE <= 0.015):
                sigma_Val = 0.015 * float(sigma)
            elif (RMSE > 0.015 and RMSE <= 0.025):
                sigma_Val = (0.02) * float(sigma)
            elif (RMSE > 0.025):
                sigma_Val = (RMSE) * float(sigma)

            kill_offset = sigma_Val + b
            label1 = 'Sigma '+ str(sigma)
            plt.plot(x, kill_offset + m * x, 'c-', label=label1)


            sigma0 = 8

            if (RMSE <= 0.015):
                sigma_Val = 0.015 * float(sigma0)
            elif (RMSE > 0.015 and RMSE <= 0.025):
                sigma_Val = (0.02) * float(sigma0)
            elif (RMSE > 0.025):
                sigma_Val = (RMSE) * float(sigma0)

            kill_offset = sigma_Val + b
            plt.plot(x, kill_offset + m * x, 'r-', label="Sigma 8")

            sigma1 = 12

            if (RMSE <= 0.015):
                sigma_Val1 = 0.015 * float(sigma1)
            elif (RMSE > 0.015 and RMSE <= 0.025):
                sigma_Val1 = (0.02) * float(sigma1)
            elif (RMSE > 0.025):
                sigma_Val1 = (RMSE) * float(sigma1)

            kill_offset= sigma_Val1 + b
            plt.plot(x, kill_offset + m * x, 'k-', label = "Sigma 12")

            vminpredVal = b - vminpred
            plt.plot(x, vminpredVal + m * x, 'y-', label = "Vmin Predict")

            if key in oldEquations:
                slope = oldEquations[key][0]
                intercept= oldEquations[key][1]
                plt.plot(x, intercept + slope * x, 'm-', label = "Previous Equation")

            plt.title(key)
            legend = plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

            if "::" in key:
                name=key.split("::")
                file_name= results_dir+"/"+name[0]+name[1]+".png"
                plt.savefig(file_name,bbox_inches='tight')
            else:
                file_name=results_dir+"/"+key+".png"
                plt.savefig(file_name,bbox_inches='tight')
            plt.clf()
            plt.close()
            del x, y
            gc.collect()

def ReadData(path):
    with open(path) as data:
        d = json.load(data)
        data.close()
    MasterData={}
    for tests in d:
        fullName= tests['YName']
        x=[]
        y=[]
        uniqueId = []
        for val in tests['Data']:
            if float(val['YValue'])>0:
                if float(val['XValue']) > 2000 and float(val['XValue']) < 18000:
                    x.append(float(val['XValue']))
                    y.append(float(val['YValue']))
                    uniqueId.append(val['UniqueID'].split("%")[4])

        MasterData[fullName]=[x,y,uniqueId]
    return MasterData

def GetOldEquations(goldenJsonFile):
    with open(goldenJsonFile) as data:
        d = json.load(data)
        data.close()

    oldEquations={}

    for i in d:
        testInstance = i["SourceTestName"]

        if testInstance not in oldEquations:
            oldEquations[testInstance] = [i["Slope"], i["Intercept"]]

    return oldEquations

def GetExistingEquationsVals(equationFile):
    with open(equationFile) as data:
        d = json.load(data)
        data.close()

    eqnsVminPred={}

    for i in d:
        testInstance = i["SourceTestName"]

        if testInstance not in eqnsVminPred:
            eqnsVminPred[testInstance] = [i["Slope"], i["Intercept_0"],i["VminPredOffset"]]

    return eqnsVminPred

def main(args1, args2, args3, args4):
    path = args1
    out_Path = args2
    sigma = args3
    goldenJsonFile = args4

    datafiles = os.listdir(path)

    equationsFile = args2 + "\\equations.json"

    if os.path.exists(equationsFile):
        eqnsVminPred = GetExistingEquationsVals(equationsFile)

    if goldenJsonFile == "blank":
        oldEquations = {}
    else:
        oldEquations = GetOldEquations(goldenJsonFile)
    # print(oldEquations)


    for datafile in datafiles:
        print(datafile)
        filepath = os.path.join(path, datafile)
        MasterData=ReadData(filepath)
        GetGraphs(MasterData,out_Path,sigma, oldEquations, eqnsVminPred)
