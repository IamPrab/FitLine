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



def GetMeanVal(xy, testName, Flagmulticore, uniqueID):
    x = xy[0]
    y = xy[1]
    if (len(x) > 100):
        mean_y = np.mean(y)
        median_y = np.median(y)

    else:
        mean_y = 0
        median_y = 0


    equation = [mean_y, median_y]

    del x, y
    gc.collect()
    return equation


def SingltonMonitor(x, y, testName, uniqueID):
    x = np.array(x)
    y = np.array(y)

    xy = [x, y]
    Flagmulticore = False
    equation = GetMeanVal(xy, testName, Flagmulticore, uniqueID)
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


def MulticoreFit(xyMulticore, uniqueId):
    multicoreEquations = {}

    multicoreData = MultiCoreData(xyMulticore)

    for cores in multicoreData:
        Flagmulticore = True
        equation = GetMeanVal(multicoreData[cores], cores, Flagmulticore, uniqueId)
        multicoreEquations[cores] = equation

    return multicoreEquations


def GetJsonObForMulticore(equation, core, IDVName):
    result = {
            'SourceTestName': core,
            'Mean': equation[0],
            'Median': equation[1],
              }
    return result



def ADTLMonitorFactory(path, resulant, worksheet, out_Path, count):
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

        equation = SingltonMonitor(x, y, fullName, uniqueId)
        mean_y = equation[0]
        median_y = equation[1]
        coreResults = []

        multicoreeqations = MulticoreFit(xyMulticore, uniqueId)
        #resultdir = os.path.join(out_Path + '/GraphData')
        for core in multicoreeqations:
            res = GetJsonObForMulticore(multicoreeqations[core], core, IDVName)

            rowData = ['',res['SourceTestName'],' ',' ', res['Mean'],res['Median']]
            worksheet.write_row(count, 0, rowData)
            count = count + 1
            coreResults.append(res)

        # equation=[ b, m, stats, RMSE, killToPassRatio ]
        result1 = {
                    'Uuid': uuid.uuid4().hex,
                    'SourceTestName': fullName,
                    'Mean': mean_y,
                    'Median': median_y,
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



        rowData1 = [moduleName ,result1['SourceTestName'],frequency,flow, result1['Mean'],result1['Median'],'MainCore']
        worksheet.write_row(count, 0, rowData1)
        #graphLinq=GetGraphName(resultdir, result1['SourceTestName'])
        #worksheet.write_url(count,24,graphLinq)
        count = count + 1


        json_string = json.dumps(result1, default=lambda o: o.__dict__, sort_keys=True, indent=2)
        resulant.write(json_string)
        resulant.write(',')

    return count

def ADTLMonitorMain(arg1,arg2):
    path = arg1
    out_Path = arg2

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
            count = ADTLMonitorFactory(filepath, file, worksheet, out_Path, count)
            print(count)
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.write("]")

        workbook.close()

parser = argparse.ArgumentParser()

parser.add_argument('input',help="inputFile")
parser.add_argument('output',help="outputFile")

args = parser.parse_args()
ADTLMonitorMain(args.input,args.output)
