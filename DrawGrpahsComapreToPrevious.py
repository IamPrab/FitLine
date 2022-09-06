import json
import math
import numpy as np
from numpy.polynomial.polynomial import polyfit
import matplotlib.pyplot as plt
import os
import gc



def getLinePoints(x, y, b, m):
    c = 0
    linePoints = []
    while (c < len(x)):
        z = m * x[c] + b
        linePoints.append(z)
        c = c + 1
    return linePoints

def GetGraphs(MasterData,outPath,sigma,preEquations):
    results_dir = os.path.join(outPath + '/GraphData')
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
        print(results_dir+"...Result directory")

    for key in MasterData:
        x = np.array(MasterData[key][0])
        y = np.array(MasterData[key][1])
        if (len(x)>10):

            b, m = polyfit(x, y, 1)
            if m > 0:
                m = 0
                b = np.mean(y)
            plt.figure()

            plt.plot(x,y, 'g.')

            plt.plot(x, b + m * x, 'b-')

            if key in preEquations:
                plt.plot(x, preEquations[key][1]+preEquations[key][0]*x, 'm-', label="Previous KillLine")

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
            plt.title(key)
            legend = plt.legend()

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
        for val in tests['Data']:
            if (float(val['YValue'])>0):
                x.append(float(val['XValue']))
                y.append(float(val['YValue']))

        MasterData[fullName]=[x,y]
    return MasterData

def GetPreviousEquations(previousEquations):
    with open(previousEquations) as data:
        d = json.load(data)
        data.close()
        # print(d)

    preEquations={}

    for i in d:
        SourceTestName = i['SourceTestName']

        if SourceTestName not in preEquations:
            preEquations[SourceTestName] = [i["Slope"], i["Intercept"]]
        else:
            print("repeat stuff in json")

    return preEquations



if __name__ == '__main__':
    path = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\RPL_8PQG_RPL682\\80M\\JsonVminData"
    out_Path = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\RPL_8PQG_RPL682\\80M"
    sigma = 10
    previousEquations= "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\RPL_8PQG_RPL682\\80J\\ADTL_Equations.adtl.json"

    preEquations = GetPreviousEquations(previousEquations)

    datafiles = os.listdir(path)
    for datafile in datafiles:
       if "SCN" in datafile:
            print(datafile)
            filepath = os.path.join(path, datafile)
            MasterData=ReadData(filepath)
            GetGraphs(MasterData,out_Path,sigma,preEquations)
