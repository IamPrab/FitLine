import json
import os

import pandas as pd

class ApprovalData:
    SourceTestName : str
    Slope : float
    Intercept_0 : float
    Intercept : float
    Flow : str
    XParameter: str
    KillRate: float
    RootMeanSquareError: float
    ApprovalData: str
    Vmin_Sigma: str

def ReadcsvData(csvAprrovalFile):

    excel_data = pd.read_excel(csvAprrovalFile)
    dict_data={}
    data = pd.DataFrame(excel_data, columns=['TestName', 'Flow', 'Slope', 'Intercept','Sigma Multiple','RootMeanSquareError','Approval'])
    length = (len (data['TestName']))
    count = 0
    #print(length)
    while(count<length):
        if data['TestName'][count] not in dict_data:
            stuff = [ data['Flow'][count], float(data['Slope'][count]),
                              float(data['Intercept'][count]), data['Sigma Multiple'][count],
                              float(data['RootMeanSquareError'][count]), data['Approval'][count]]
            dict_data[data['TestName'][count]] = stuff
        else:
            print(data['TestName'][count])
            print(dict_data[data['TestName'][count]])
            print("double Equation" )
        count = count + 1
    # print(count)
    # print(len(dict_data))

    return dict_data

def ReadjsonData(jsonequationFile):

    with open(jsonequationFile) as data:
        d = json.load(data)
        data.close()
    #print(d)
    return d

def AllTestInstances(datajson):
    testInstance={}
    for i in datajson:
        SourceTestName = i['SourceTestName']

        if SourceTestName not in testInstance:
            testInstance[SourceTestName] = True
        else:
            print("repeat stuff in json")

    return testInstance



def MapJsontoApproval(dataApproval, dataJson,resulant, allTestInstances):

    for i in dataJson:
        SourceTestName = i['SourceTestName']

        if SourceTestName in dataApproval:
            Flow = dataApproval[SourceTestName][0]
            SlopeA =  float(dataApproval[SourceTestName][1])
            InterceptA = float(dataApproval[SourceTestName][2])
            Sigmaa = dataApproval[SourceTestName][3]
            RootMeanSquareErrorA= float(dataApproval[SourceTestName][4])
            Approval = dataApproval[SourceTestName][5]

            if Approval=='Y' or Approval=='Yes' or Approval == 'yes' or Approval=='y':
                result1 = {"ResultVarName": i['ResultVarName'],
                            "PerDomainEquations": i['PerDomainEquations'],
                            "EquaionName": i["EquaionName"],
                            "Intercept": float(InterceptA),
                            "Slope":float(SlopeA),
                            "Vmin_Sigma": "VminSIGMA"+str(Sigmaa),
                            "XParameter": "TPI_IDV.D.FMAX_IDV_NESTED_950",
                            "YParameters":i["YParameters"],
                            "SourceTestName": SourceTestName,
                            "SourceFileName": i["SourceFileName"],
                            "Status": i["Status"],
                            "RootMeanSquareError": RootMeanSquareErrorA,
                            "KillRate": 'NA',
                            "PopulationStatistics": i["PopulationStatistics"],
                            "ResultVar": i["ResultVar"]
                }

                json_string = json.dumps(result1, default=lambda o: o.__dict__, sort_keys=True, indent=2)
                resulant.write(json_string)
                resulant.write(',')
                dataApproval[SourceTestName] = [True, "Values Passed"]


    for key in dataApproval:
        if dataApproval[key][0]!=True and dataApproval[key][1]!= "Values Passed" :
            Approval =  dataApproval[key][5]
            if Approval == 'Y' or Approval == 'Yes' or Approval == 'yes' or Approval == 'y':
                print('Equation missing in json')


if __name__ == '__main__':
    csvAprrovalFile = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\RPL_8PRO_RPL282\\8PROC_90F\\8Sigma\\8ApprovalFile_aviad.xlsx"
    jsonequationFile = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\RPL_8PRO_RPL282\\8PROC_90F\\8Sigma\\ADTL_Equations.adtl.json"
    FinalJson = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\RPL_8PRO_RPL282\\8PROC_90F\\8Sigma\\AfterApproval_ADTL_Equations.adtl.json"

    dataApproval= ReadcsvData(csvAprrovalFile)
    dataJson = ReadjsonData(jsonequationFile)
    allTestInstances=AllTestInstances(dataJson)

    with open (FinalJson, 'w') as file:
        file.write("[")
        MapJsontoApproval(dataApproval, dataJson, file, allTestInstances)
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.write("]")

