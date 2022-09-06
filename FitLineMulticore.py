import gc
import xlsxwriter
import json
import numpy as np
from numpy.polynomial.polynomial import polyfit
import os
import math
import os.path
from os import path
import matplotlib.pyplot as plt


def distributionStatistic(x, y, b, m):
    c = 0
    max = 0
    distStats = {}
    while (c < len(y)):
        sigma = round((y[c] - ((m * x[c]) + b)) / 0.02)
        # print(sigma)
        if sigma < 0:
            sigma = -1 * sigma
        if sigma > max:
            max = sigma
        if sigma >= 0:
            if sigma in distStats:
                distStats[sigma] = distStats[sigma] + 1
            else:
                distStats[sigma] = 1
        c = c + 1
    arrStats = np.zeros(max + 1)
    for key in distStats:
        arrStats[key] = distStats[key]
    for i in range(len(arrStats) - 1):
        arrStats[i + 1] = arrStats[i] + arrStats[i + 1]
    for i in range(len(arrStats)):
        arrStats[i] = (arrStats[i] / len(y))

    # print(arrStats)
    return arrStats


def kill_points(x, y, b, m):
    passBucketY = []
    killBucketY = []

    count = 0
    while (count < len(y)):
        kill_line =  b + (m * x[count])
        if y[count] >= kill_line:
            killBucketY.append(y[count])
        else:
            passBucketY.append(y[count])
        count = count + 1
    passToKillBucket = [ passBucketY,  killBucketY]

    return passToKillBucket


def getLinePoints(x, y, b, m):
    c = 0
    linePoints = []
    while (c < len(x)):
        z = m * x[c] + b
        linePoints.append(z)
        c = c + 1
    return linePoints


def RunFitLine(xy, testName, Flagmulticore,sigma):
    x = xy[0]
    y = xy[1]
    if (len(x) > 100):
        b, m = polyfit(x, y, 1)
        if m>0:
            m=0
            b = np.mean(y)

        stats = distributionStatistic(x, y, b, m)
        linePoints = getLinePoints(x, y, b, m)
        MSE = np.square(np.subtract(y,linePoints)).mean()
        RMSE = math.sqrt(MSE)
        b_sigma = 0

        if (RMSE <= 0.015):
            b_sigma = b + 0.015*float(sigma)
            selcted_sigma = 0.015
            sigma_Val_Offset = 0.015*float(sigma)
        elif (RMSE > 0.015 and RMSE <= 0.025 ) :
            b_sigma = b +(0.02)*float(sigma)
            selcted_sigma = 0.02
            sigma_Val_Offset = (0.02)*float(sigma)
        # elif (RMSE > 0.020 and RMSE < 0.025 ) :
        #     b_sigma = b + (0.025)*float(sigma)
        #     selcted_sigma = 0.025
        #     sigma_Val_Offset = (0.025)*float(sigma)
        elif (RMSE > 0.025) :
            b_sigma = b + (RMSE) * float(sigma)
            selcted_sigma = RMSE
            sigma_Val_Offset = (RMSE) * float(sigma)
        #print(len(y))
        passToKillBucket = kill_points(x, y, b_sigma, m)

        killBucketY = passToKillBucket[1]
        killToPassRatio = len(killBucketY)


    else:
        Empty = []
        b = 0
        m = 0
        stats = np.array(Empty)
        RMSE = 0
        killToPassRatio = 0
        sigma_Val_Offset = 0
        selcted_sigma = 0
        b_sigma = 0

    equation = [b_sigma, m, stats, RMSE, killToPassRatio, sigma_Val_Offset,b,selcted_sigma]

    del x, y
    gc.collect()
    return equation


def SingltonFit(x, y, testName,sigma):
    x = np.array(x)
    y = np.array(y)

    xy = [x, y]
    Flagmulticore = False
    equation = RunFitLine(xy, testName, Flagmulticore,sigma)
    return equation


def MultiCoreData(xyMulticore):
    IDV_Vmin_Dict = {}
    for val in xyMulticore:
        dataStr = val.split("%")
        VminName = dataStr[0]
        IDV = float(dataStr[1])
        Vmin = float(dataStr[2])
        CoreIDV = []
        CoreVmin = []

        if VminName not in IDV_Vmin_Dict:
            if Vmin > 0:
                CoreIDV.append(IDV)
                CoreVmin.append(Vmin)
            IDV_Vmin_Dict[VminName] = [CoreIDV, CoreVmin]

        else:
            if Vmin > 0:
                x = np.array(IDV_Vmin_Dict[VminName][0])
                y = np.array(IDV_Vmin_Dict[VminName][1])
                xNew = np.append(x, IDV)
                yNew = np.append(y, Vmin)
                IDV_Vmin_Dict[VminName] = [xNew, yNew]

    # print(IDV_Vmin_Dict)
    return IDV_Vmin_Dict


def MulticoreFit(xyMulticore, sigma):
    multicoreEquations = {}

    multicoreData = MultiCoreData(xyMulticore)

    for cores in multicoreData:
        Flagmulticore = True
        equation = RunFitLine(multicoreData[cores], cores, Flagmulticore, sigma)
        multicoreEquations[cores] = equation

    return multicoreEquations


def GetJsonObForMulticore(equation, core, IDVName):
    result = {'Slope': equation[1],
              'Intercept': equation[0],
              'SourceTestName': core,
              'XParameter': IDVName,
              'KillRate': equation[4],
              'RootMeanSquareError': equation[3],
              'PopulationStatistics': equation[2].tolist()
              }
    return result

def GetGraphName(dir,key):
    if "::" in key:
        name = key.split("::")
        file_name = dir + "/" + name[0] + name[1] + ".png"
    else:
        file_name = dir + "/" + key + ".png"

    return file_name

def DiePerWaferCount(out_Path, kills):
    dpw = kills/1
    wafersList = out_Path +'/WaferList.txt'

    if path.isfile(wafersList):
        num_lines = sum(1 for line in open(wafersList))
        dpw = kills/num_lines

    return  dpw


def FitLineFactory(path, resulant, worksheet, out_Path, sigma, count):
    with open(path) as data:
        d = json.load(data)
        data.close()


    for tests in d:
        fullName = tests['YName']
        IDVName = ""
        vminTestName = fullName.split('::')[0]
        x = []
        y = []
        xyMulticore = []
        for val in tests['Data']:
            IDVName = val['XName']
            if float(val['YValue']) > 0:
                if float(val['XValue']) > 6000 and float(val['XValue']) < 18000:
                    x.append(float(val['XValue']))
                    y.append(float(val['YValue']))
            if fullName != val['YName']:
                xyMulticore.append(val['YName'] + "%" + str(val['XValue']) + "%" + str(val['YValue']))

        equation = SingltonFit(x, y, fullName,sigma)
        intercept = equation[0]
        slope = equation[1]
        populationStats = equation[2].tolist()
        rmse = equation[3]
        killRate = equation[4]
        Sigma_offset = equation[5]
        intercept_0 = equation[6]
        selcted_sigma = equation[7]

        coreResults = []

        multicoreeqations = MulticoreFit(xyMulticore,sigma)
        resultdir = os.path.join(out_Path + '/GraphData')
        for core in multicoreeqations:
            res = GetJsonObForMulticore(multicoreeqations[core], core, IDVName)
            intercept_0Multi = multicoreeqations[core][6]
            DPW = DiePerWaferCount(out_Path,res['KillRate'])
            rowData = ['',res['SourceTestName'],'','', res['Slope'],intercept_0Multi, res['Intercept'], DPW,
                       res['RootMeanSquareError'],multicoreeqations[core][7],int(sigma),multicoreeqations[core][5], str(res['PopulationStatistics']), ' ',' ', 'MultiCore']
            if ( res['Intercept'] != 0):
                worksheet.write_row(count, 0, rowData)
                count = count + 1
            coreResults.append(res)

        # equation=[ b, m, stats, RMSE, killToPassRatio ]
        result1 = {'Slope': slope,
                   'Intercept': intercept,
                   'SourceTestName': fullName,
                   'PerDomainEquations': coreResults,
                   'XParameter': IDVName,
                   'KillRate': killRate,
                   'RootMeanSquareError': rmse,
                   'PopulationStatistics': populationStats,
                   'VminName': vminTestName
                   }

        frequency = ''
        if fullName.find('TFM')>0:
            frequency = 'TFM'
        elif fullName.find('LFM')>0:
            frequency =  "LFM"
        elif fullName.find('HFM')>0:
            frequency = 'HFM'

        flow = ''
        if fullName.find('POSTHVQK')>0:
            flow = 'POSTHVQK'
        elif fullName.find('PREHVQK')>0:
            flow = 'PREHVQK'
        elif fullName.find('HVQK')>0:
            flow = 'HVQK'
        elif fullName.find('END')>0:
            flow = 'END'
        elif fullName.find('SDTEND')>0:
            flow = 'SDTEND'
        elif fullName.find('BEGIN') > 0:
            flow = 'BEGIN'

        moduleName = ''
        if fullName.find('::') > 0:
            moduleName = fullName.split('::')[0]


        DPW = DiePerWaferCount(out_Path, killRate)

        rowData1 = [moduleName ,result1['SourceTestName'],frequency,flow, result1['Slope'],intercept_0, result1['Intercept'], DPW,
                    result1['RootMeanSquareError'],selcted_sigma,int(sigma),Sigma_offset, str(result1['PopulationStatistics']), ' ',' ', 'MainCore']
        if (result1['Intercept']!=0):
            worksheet.write_row(count, 0, rowData1)
            graphLinq=GetGraphName(resultdir, result1['SourceTestName'])
            worksheet.write_url(count,16,graphLinq)
            count = count + 1

        json_string = json.dumps(result1, default=lambda o: o.__dict__, sort_keys=True, indent=2)
        resulant.write(json_string)
        resulant.write(',')


    return count


def main(args1, args2, args3):
    path = args1
    out_Path = args2
    sigma = args3
    outPath = out_Path + '\\equations.json'
    OutFinalCSVPath = out_Path + '\\ApprovalFile.xlsx'

    workbook = xlsxwriter.Workbook(OutFinalCSVPath)
    worksheet = workbook.add_worksheet()

    datafiles = os.listdir(path)
    with open(outPath, 'w') as file:
        header = ['Module Name','TestName', 'Frequency', 'Flow', 'Slope', 'Intercept_0', 'Intercept', 'DPW',
                  'RootMeanSquareError', 'Selected Sigma', 'Sigma Multiple', 'Calculated_Offset ',
                  'PopulationStatistics', 'Approval', 'Comment', 'MultiCore/MainCore',
                  'Graph']
        worksheet.write_row(0, 0, header)
        file.write("[")
        count = 1
        for datafile in datafiles:
            print(datafile)
            filepath = os.path.join(path, datafile)
            count = FitLineFactory(filepath, file, worksheet, out_Path, sigma, count)
            print(count)
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.write("]")
        workbook.close()


