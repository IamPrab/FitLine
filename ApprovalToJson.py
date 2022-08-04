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
            print("double Equation ^^")
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
    c=0
    t=0
    post=0
    pre=0

    for i in dataJson:
        SourceTestName = i['SourceTestName']

        if SourceTestName in dataApproval:
            t=t+1
            Flow = dataApproval[SourceTestName][0]
            SlopeA =  float(dataApproval[SourceTestName][1])
            InterceptA = float(dataApproval[SourceTestName][2])
            Sigmaa = dataApproval[SourceTestName][3]
            RootMeanSquareErrorA= float(dataApproval[SourceTestName][4])
            Approval = dataApproval[SourceTestName][5]

            if Approval=='Y' or Approval=='Yes' or Approval == 'yes' or Approval=='y' or Approval=='YES':
                c = c+1
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

                if Flow == "PREHVQK":
                    pre=pre+1
                    postInstance = SourceTestName.replace("PREHVQK", "POSTHVQK")
                    if postInstance in allTestInstances:
                        #print(postInstance)
                        post= post+1
                        result1 = {"ResultVarName": i['ResultVarName'],
                                   "PerDomainEquations": i['PerDomainEquations'],
                                   "EquaionName": i["EquaionName"].replace("PREHVQK", "POSTHVQK"),
                                   "Intercept": float(InterceptA),
                                   "Slope": float(SlopeA),
                                   "Vmin_Sigma": "VminSIGMA"+str(Sigmaa),
                                   "XParameter": "TPI_IDV.D.FMAX_IDV_NESTED_950",
                                   "YParameters": i["YParameters"][0].replace("PRE", "POST"),
                                   "SourceTestName": postInstance,
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
                    else:
                        print(SourceTestName)
                        print("PRE POST missing^")


    for key in dataApproval:
        if dataApproval[key][0]!=True and dataApproval[key][1]!= "Values Passed" :
            Approval =  dataApproval[key][5]
            if Approval == 'Y' or Approval == 'Yes' or Approval == 'yes' or Approval == 'y':
                print('Equatiion missing in json')
    print(c)
    print(t)
    print(post)
    print(pre)


if __name__ == '__main__':
    csvAprrovalFile = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ADL_8PQK_ADL081\\8PQK_61A\\ApprovalFile.xlsx"
    jsonequationFile = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ADL_8PQK_ADL081\\8PQK_61A\\Debug_ADTL_Equations.adtl.json"
    FinalJson = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ADL_8PQK_ADL081\\8PQK_61A\\AfterApproval_ADTL_Equations.adtl.json"

    dataApproval= ReadcsvData(csvAprrovalFile)
    dataJson = ReadjsonData(jsonequationFile)
    allTestInstances=AllTestInstances(dataJson)

    with open (FinalJson, 'w') as file:
        file.write("[")
        MapJsontoApproval(dataApproval, dataJson, file, allTestInstances)
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.write("]")

