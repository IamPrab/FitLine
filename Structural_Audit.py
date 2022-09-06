import json
import csv
import os
import re
import pandas as pd


def ReadJson(file):
    with open(file) as data:
        d = json.load(data)
        data.close()
    return d


def GetValuesofEquationFromTesterFile(testerDataJson):
    testerdata={}
    for i in testerDataJson:
        key = i["SourceTestName"]
        if key not in testerdata:
            testerdata[key] = [i["Intercept"], i["Slope"]]
        else :
            print("Element repeated")
    #print(testerdata)
    return testerdata


def GetTestSlopeIntercept(resultstring):
    pipes = resultstring.count('|')
    intercept = "Null"
    slope = "Null"

    if pipes == 5:
        values = resultstring.split('|')
        if len(values) == 6:
            intercept = float(values[4])
            slope = float(values[3])

    if pipes == 7:
        values = resultstring.split('|')
        if len(values) == 8:
            intercept = float(values[4])
            slope = float(values[3])

    return [intercept,slope]


def GetValuesofEquationFromAdtlData(adtlDataJson):
    adtlData={}
    for i in adtlDataJson["Data"]:
        if "::ADTL" in i["test"]:
            testInstance = i["test"].split("::ADTL")[0]
        else:
            testInstance = i["test"]
        value = GetTestSlopeIntercept(i["result"])
        intercept = value[0]
        slope = value[1]

        if testInstance not in adtlData:
            adtlData[testInstance]=[intercept,slope]
        else:
            values = adtlData[testInstance]
            #if values[0] != intercept or values[1] != slope:
                #print("Same Test Instance Different Equations")
    #print(adtlData)
    return adtlData

def CompareEquationsInJsonAndTester_TestInstance(testerDatajson, adtlData, outSCV):
    outSCV.writerow([" "])
    outSCV.writerow(["Mismatch Equations"])
    outSCV.writerow(["Test", "Intercept", "Slope","Mismatch"])
    json={}
    database = {}
    countjson=0
    countDatabase=0

    for i in testerDatajson:
        json[i] = "APPROVED TEST"

    for i in adtlData:
        database[i] =  "IMPLEMENTED TEST"

    for i in json:
        if i in database:
            countjson = countjson +1
            #print(i,"Implemented and Approved")
        else:
            #print(i, "Approvedd Not Implemented")
            outSCV.writerow([i,str(testerDatajson[i][0]), str(testerDatajson[i][1]), "Approvedd Not Implemented"])

    for i in database:
        if i in json:
            countDatabase = countDatabase +1
            #print(i,"Implemented and Approved")
        else:
            #print(i, "Implemented not in Json File")
            #print(database[i])
            outSCV.writerow([i,str(adtlData[i][0]),str(adtlData[i][1]),"Implemented not in Json File"])

    print(countjson,countDatabase)

def CompareEquationsInJsonAndTester_SlopeAndIntcept(testerData, adtlData, outSCV):
    outSCV.writerow([" "])
    outSCV.writerow(["Test with Different Slope and Intercept"])
    outSCV.writerow(["Test", "Slope in json", "Slope in DataBase", "Intercept in json", "Intercept in DataBase"])
    for test in testerData:
        if test in adtlData:
            if testerData[test][0] == adtlData[test][0] and testerData[test][1] == adtlData[test][1]:
                print("Equations Match")
            else:
                #print("for", test, "slope and intercept are different. In JSON" ,testerData[test], "In Database", adtlData[test])
                outSCV.writerow([test, testerData[test][1] , adtlData[test][1], testerData[test][0], adtlData[test][0]])


def main(args1, args2, args3):

    pathEquationsJson = args3
    pathADTLData = args1
    outCSV = args2 + "/StructuralAuditSummary.csv"

    testerDataJson = ReadJson(pathEquationsJson)
    testerData = GetValuesofEquationFromTesterFile(testerDataJson)

    adtlDataJson = ReadJson(pathADTLData)
    adtlData = GetValuesofEquationFromAdtlData(adtlDataJson)

    print(len(adtlData),len(testerData))


    with open(outCSV, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["No of equations in json:", len(testerData)])
        writer.writerow(([ "No of Equations in Database:", len(adtlData)]))
        CompareEquationsInJsonAndTester_SlopeAndIntcept(testerData, adtlData, writer)
        CompareEquationsInJsonAndTester_TestInstance(testerData, adtlData, writer)








