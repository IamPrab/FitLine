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


killdies=[]

def distributionStatistic(x, y, b, m):
    c = 0
    max = 0
    distStats = {}
    while (c < len(y)):
        sigma = math.ceil((y[c] - ((m * x[c]) + b)) / 0.01)
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

def getVminPredict(popStats):
    for i in range(len(popStats)):
        if popStats[i] >= 0.95:
            return (i+1)*0.01


    return 0.01


def kill_points(x, y, b, m, uniqueID, testName):
    passBucketY = 0
    killBucketY = []

    kb1,kb2,kb3,kb5,kb43 = ([] for i in range (5))

    count = 0
    while (count < len(y)):
        kill_line =  b + (m * x[count])
        bin = uniqueID[count].split("%")[4]
        if y[count] >= kill_line:
            killBucketY.append(y[count])
            kills = uniqueID[count] + ":   " + testName
            killdies.append(kills)

            if bin == "1":
                kb1.append(uniqueID[count])
            elif bin == "2":
                kb2.append(uniqueID[count])
            elif bin == "3":
                kb3.append(uniqueID[count])
            elif bin == "5":
                kb5.append(uniqueID[count])
            elif bin == "43":
                kb43.append(uniqueID[count])

        else:
            passBucketY = passBucketY + 1
        count = count + 1
        #print(killBucketY)
    passToKillBucket = [len(killBucketY), len(kb1), len(kb2), len(kb3), len(kb5), len(kb43)]
    #print(passToKillBucket)

    return passToKillBucket


def getLinePoints(x, y, b, m):
    c = 0
    linePoints = []
    while (c < len(x)):
        z = m * x[c] + b
        linePoints.append(z)
        c = c + 1
    return linePoints


def RunFitLine(xy, testName, Flagmulticore,sigma, uniqueID):
    x = xy[0]
    y = xy[1]
    if (len(x) > 100):
        b, m = polyfit(x, y, 1)
        if m>0:
            m=0
            b = np.mean(y)

        stats = distributionStatistic(x, y, b, m)
        offsetVminPredict = getVminPredict(stats)


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
        killToPassRatio = kill_points(x, y, b_sigma, m, uniqueID, testName)


    else:
        Empty = []
        b = 0
        m = 0
        stats = np.array(Empty)
        RMSE = 0
        killToPassRatio = []
        sigma_Val_Offset = 0
        selcted_sigma = 0
        b_sigma = 0
        offsetVminPredict = 0
        vminpred = 0

    equation = [b_sigma, m, stats, offsetVminPredict, RMSE, killToPassRatio, sigma_Val_Offset,b,selcted_sigma]

    del x, y
    gc.collect()
    return equation


def SingltonFit(x, y, testName,sigma, uniqueID):
    x = np.array(x)
    y = np.array(y)

    xy = [x, y]
    Flagmulticore = False
    equation = RunFitLine(xy, testName, Flagmulticore,sigma, uniqueID)
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


def MulticoreFit(xyMulticore, sigma, uniqueId):
    multicoreEquations = {}

    multicoreData = MultiCoreData(xyMulticore)

    for cores in multicoreData:
        Flagmulticore = True
        equation = RunFitLine(multicoreData[cores], cores, Flagmulticore, sigma, uniqueId)
        multicoreEquations[cores] = equation

    return multicoreEquations


def GetJsonObForMulticore(equation, core, IDVName):
    kill =0
    if len(equation[5])>0:
        kill = equation[5][0]
    result = {'Slope': equation[1],
              'Intercept': equation[0],
              'SourceTestName': core,
              'XParameter': IDVName,
              'KillRate': kill,
              'RootMeanSquareError': equation[4],
              'PopulationStatistics': "",
              'VminPredOffset': equation[3],
              'Intercept_0': equation[7]
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
    wafersList = out_Path +'/WaferList.txt'
    dpwPerBin = kills

    if path.isfile(wafersList):
        dpwPerBin = []
        num_lines = sum(1 for line in open(wafersList))
        for killperbin in kills:
            dpwPerBin.append(killperbin/num_lines)
    #print(dpwPerBin, "bnjfb")

    return  dpwPerBin


def FitLineFactory(path, resulant, worksheet, out_Path, sigma, count, oldEquations):
    with open(path) as data:
        d = json.load(data)
        data.close()


    for tests in d:
        fullName = tests['YName']
        IDVName = ""
        vminTestName = fullName.split('::')[0]
        x = []
        y = []
        uniqueId = []
        xyMulticore = []
        for val in tests['Data']:
            IDVName = val['XName']
            if float(val['YValue']) > 0:
                if float(val['XValue']) > 2000 and float(val['XValue']) < 18000:
                    x.append(float(val['XValue']))
                    y.append(float(val['YValue']))
                    uniqueId.append(val['UniqueID'])
            if fullName != val['YName']:
                xyMulticore.append(val['YName'] + "%" + str(val['XValue']) + "%" + str(val['YValue']))

        equation = SingltonFit(x, y, fullName,sigma, uniqueId)
        intercept = equation[0]
        slope = equation[1]
        populationStats = equation[2].tolist()
        vminPredOffset = equation[3]
        rmse = equation[4]
        killRate = equation[5]
        Sigma_offset = equation[6]
        intercept_0 = equation[7]
        selcted_sigma = equation[8]
        #print (killRate)

        coreResults = []

        multicoreeqations = MulticoreFit(xyMulticore,sigma, uniqueId)
        resultdir = os.path.join(out_Path + '/GraphData')
        for core in multicoreeqations:
            res = GetJsonObForMulticore(multicoreeqations[core], core, IDVName)
            intercept_0Multi = multicoreeqations[core][6]
            DPW = DiePerWaferCount(out_Path,multicoreeqations[core][5])
            kills= "NA"
            dpw1m = "NA"
            dpw2m = "NA"
            dpw3m = "NA"
            dpw5m = "NA"
            dpw43m = "NA"
            if len(DPW)>0:
                kills = DPW[0]
                dpw1m = DPW[1]
                dpw2m = DPW[2]
                dpw3m = DPW[3]
                dpw5m = DPW[4]
                dpw43m = DPW[5]

            rowData = ['',res['SourceTestName'],' ',' ', res['Slope'],intercept_0Multi, res['Intercept'], kills,dpw1m,dpw2m,dpw3m,dpw5m,dpw43m,
                       res['RootMeanSquareError'],multicoreeqations[core][8],int(sigma),multicoreeqations[core][6], ' ',res['VminPredOffset'],str(multicoreeqations[core][2].tolist()), ' ', ' ',' ','MultiCore']
            if ( res['Intercept'] != 0):
                worksheet.write_row(count, 0, rowData)
                count = count + 1
            coreResults.append(res)

        dpw1= "NA"
        dpw2 = "NA"
        dpw3 = "NA"
        dpw5 = "NA"
        dpw43 = "NA"


        DPW = DiePerWaferCount(out_Path, killRate)
        killRate = 0
        if len(DPW) > 0:
            killRate = DPW[0]
            dpw1 = DPW[1]
            dpw2 = DPW[2]
            dpw3 = DPW[3]
            dpw5 = DPW[4]
            dpw43 = DPW[5]

        # equation=[ b, m, stats, RMSE, killToPassRatio ]
        result1 = {'Slope': slope,
                   'Intercept': intercept,
                   'SourceTestName': fullName,
                   'PerDomainEquations': coreResults,
                   'XParameter': IDVName,
                   'KillRate': killRate,
                   'RootMeanSquareError': rmse,
                   'PopulationStatistics': "",
                   'VminName': vminTestName,
                   'VminPredOffset': vminPredOffset,
                   'Intercept_0': intercept_0
                   }

        frequency = ''
        if fullName.find('XTFM')>0:
            frequency = 'XTFM'
        elif fullName.find('TFM')>0:
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
        elif fullName.find('SDTEND')>0:
            flow = 'SDTEND'
        elif fullName.find('END')>0:
            flow = 'END'
        elif fullName.find('BEGIN') > 0:
            flow = 'BEGIN'

        moduleName = ''
        if fullName.find('::') > 0:
            moduleName = fullName.split('::')[0]

        testInstance = result1['SourceTestName']

        status= " "
        oldDPW= " "
        oldSigma=" "
        oldRMSE=" "
        if testInstance in oldEquations:
            status = "ADTL Implemented in Previous Test Program"
            #oldEquations[testInstance] = "Freed"
            oldDPW = oldEquations[testInstance]["KillRate"]
            oldSigma = oldEquations[testInstance]["Vmin_Sigma"]
            oldRMSE = oldEquations[testInstance]["RootMeanSquareError"]

            #print(oldDPW)

        rowData1 = [moduleName ,result1['SourceTestName'],frequency,flow, result1['Slope'],intercept_0, result1['Intercept'], killRate, dpw1, dpw2, dpw3, dpw5, dpw43,
                    result1['RootMeanSquareError'],selcted_sigma,int(sigma),Sigma_offset,' ', vminPredOffset, str(populationStats),status,' ',' ', 'MainCore']
        if (result1['Intercept']!=0) :
            worksheet.write_row(count, 0, rowData1)
            graphLinq=GetGraphName(resultdir, result1['SourceTestName'])
            worksheet.write_url(count,24,graphLinq)
            additionalData = [str(oldSigma),oldRMSE,str(oldDPW)]
            worksheet.write_row(count, 25, additionalData)
            count = count + 1

        # for key in oldEquations:
        #     if oldEquations[key] != "Freed":
        #         rowData2 = [key]
        #         worksheet.write_row

        json_string = json.dumps(result1, default=lambda o: o.__dict__, sort_keys=True, indent=2)
        resulant.write(json_string)
        resulant.write(',')


    return count

def GetOldEquations(goldenJsonFile):
    with open(goldenJsonFile) as data:
        d = json.load(data)
        data.close()

    oldEquations={}

    for i in d:
        testInstance = i["SourceTestName"]

        if testInstance not in oldEquations:
            oldEquations[testInstance] = i

    return oldEquations

def CalculateOverallDPW(out_Path):
    fileName= out_Path + "\\Kills.txt"

    uniqueKills = {}
    with open(fileName,'w') as file:
        file.write('All Killed Dies \nX%Y%Wafer%Lot%IBin   IDV VMIN\n')
        for kill in killdies:
            file.write(f"{kill}\n")
            key = kill.split(":")[0]

            if key not in uniqueKills:
                uniqueKills[key] = kill
            else:
                uniqueKills[key] = uniqueKills[key]+","+ kill
        file.write("\nUNIQUE KILLS")
        for key in uniqueKills:
            file.write(key+","+uniqueKills[key]+"\n")

    uniKills= len(uniqueKills)
    dpw = uniKills/1
    wafersList = out_Path + '/WaferList.txt'

    if path.isfile(wafersList):
        num_lines = sum(1 for line in open(wafersList))
        dpw = uniKills / num_lines
    #print(uniKills)
    print(dpw)
    return dpw



def main(args1, args2, args3, args4):
    path = args1
    out_Path = args2
    sigma = args3
    goldenJsonFile = args4
    outPath = out_Path + '\\equations.json'
    OutFinalCSVPath = out_Path + '\\ApprovalFile.xlsx'

    workbook = xlsxwriter.Workbook(OutFinalCSVPath)
    worksheet = workbook.add_worksheet()

    if goldenJsonFile== "blank":
        oldEquations={}
    else:
        oldEquations= GetOldEquations(goldenJsonFile)
    #print(oldEquations)


    datafiles = os.listdir(path)
    with open(outPath, 'w') as file:
        header = ['Module Name','TestName', 'Frequency', 'Flow', 'Slope', 'Intercept_0', 'Intercept', 'DPWOverAll', 'Bin1 dpw', 'Bin2 dpw', 'Bin3 dpw', 'Bin5 dpw', 'Bin43 dpw',
                  'RootMeanSquareError', 'Selected Sigma', 'Sigma Multiple', 'Calculated_Offset', 'Overide sigma Multiple value', 'Vmin Pred',
                  'PopulationStatistics', 'Status', 'Approval', 'Comment', 'MultiCore/MainCore',
                  'Graph', 'Previous eqn Sigma', 'Previous eqn RMSE', 'Previous eqn DPW Overall']
        worksheet.write_row(0, 0, header)
        file.write("[")
        count = 1
        for datafile in datafiles:
            print(datafile)
            filepath = os.path.join(path, datafile)
            count = FitLineFactory(filepath, file, worksheet, out_Path, sigma, count, oldEquations)
            print(count)
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.write("]")

        dpw = CalculateOverallDPW(out_Path)
        rowData = ["DPW overall", str(dpw)]
        worksheet.write_row(count, 0, rowData)

        workbook.close()


