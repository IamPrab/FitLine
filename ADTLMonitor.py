import gc
import uuid
import xlsxwriter
import json
import numpy as np
from numpy.polynomial.polynomial import polyfit
import os
import math
import os.path
from os import path
import matplotlib.pyplot as plt
import argparse

def distributionStatistic(y,mean):
    c = 0
    max = 0

    distStats = {}
    while (c < len(y)):
        sigma = math.ceil((y[c] - mean) / 0.02)
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

def GetMeanVal(drift,y, testName,dpw):
    mean_drift = 0
    median_drift = 0
    mean_y = 0
    #print(drift)

    if (len(drift) > 50):
        mean_drift = np.mean(drift)
        median_drift = np.median(drift)
        mean_y = np.mean(y)

    popDistribution = distributionStatistic(y,mean_y)
    equation = [mean_drift, median_drift,popDistribution,dpw]

    del  drift
    gc.collect()
    return equation


def SingltonMonitor(k, y, testName):
    drift = []
    dpw = 0
    for i in range(len(k)-2):
        driftval = k[i] - y[i]
        drift.append(driftval)
        if k[i]<y[i]:
            dpw = dpw + 1

    drift = np.array(drift)
    y= np.array(y)
    #print(drift)
    equation = GetMeanVal(drift,y, testName,dpw)

    return equation



def ResultStringParser(result):
    vminval = 0
    killpoint = 0
    if result.find('|')>0:
        results=result.split('|')
        if (len(results)==6):
            vminval= results[1]
            killpoint= results[2]

    return [vminval, killpoint]


def ADTLMonitorFactory(path, resulant, worksheet, out_Path, count, workWeek):
    with open(path) as data:
        d = json.load(data)
        data.close()

    test_data = {}

    for tests in d['Data']:
        fullName = tests['test']
        vmintest = fullName
        if fullName.find('::ADTL')>0:
            vmintest = fullName.split('::ADTL')[0]

        result = ResultStringParser(tests['result'])
        vminval = float(result[0])
        killpoint = float(result[1])


        if vmintest not in test_data :
            y = []
            k = []

            if 0 < float(vminval) < 5 and 0 < float(killpoint) < 5:
                y.append(float(vminval))
                k.append(float(killpoint))
                test_data[vmintest]= [y,k]
        else:
            if 0 < vminval < 5 and 0 < killpoint < 5:
                y_temp = test_data[vmintest][0]
                k_temp = test_data[vmintest][1]

                y_temp.append(float(vminval))
                k_temp.append(float(killpoint))

                test_data[vmintest]= [y_temp,k_temp]

    for vmin in test_data:
        #print(vmin)
        yp= test_data[vmin][0]
        kp = test_data[vmin][1]
        fullName = vmin

        equation = SingltonMonitor(kp, yp, fullName)
        #print(equation)
        mean_y = equation[0]
        median_y = equation[1]
        popStats = equation[2].tolist()
        dpw= equation[3]/100


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


        if (mean_y>0):
            result1 = {
                        'WorkWeek': workWeek,
                        'TestName': fullName,
                        'Mean': mean_y,
                        'Median': median_y,
                        'PopulationStats': popStats,
                        'DPW': dpw
                       }

            rowData1 = [moduleName ,result1['TestName'],frequency,flow, result1['Mean'],result1['Median'],'MainCore']
            worksheet.write_row(count, 0, rowData1)
            #graphLinq=GetGraphName(resultdir, result1['SourceTestName'])
            #worksheet.write_url(count,24,graphLinq)
            count = count + 1


            json_string = json.dumps(result1, default=lambda o: o.__dict__, sort_keys=True, indent=2)
            resulant.write(json_string)
            resulant.write(',')

    return count

def ADTLMonitorMain(arg1,arg2,arg3):
    path = arg1
    out_Path = arg2
    workWeek = arg3

    outPath = out_Path + '\\ADTLMonitor.json'
    OutFinalCSVPath = out_Path + '\\ADTLMonitorView.xlsx'

    workbook = xlsxwriter.Workbook(OutFinalCSVPath)
    worksheet = workbook.add_worksheet()

    datafiles = os.listdir(path)
    with open(outPath, 'w') as file:
        header = ['Module Name','TestName', 'Frequency', 'Flow', 'Mean', 'Median','MultiCore/MainCore']
        worksheet.write_row(0, 0, header)
        file.write("[")
        count = 1
        for datafile in datafiles:
            print(datafile)
            filepath = os.path.join(path, datafile)
            count = ADTLMonitorFactory(filepath, file, worksheet, out_Path, count, int(workWeek))
            print(count)
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.write("]")

        workbook.close()

parser = argparse.ArgumentParser()

parser.add_argument('input',help="inputFile")
parser.add_argument('output',help="outputFile")
parser.add_argument('WW',help="WorkWeek")

args = parser.parse_args()
ADTLMonitorMain(args.input,args.output,args.WW)
