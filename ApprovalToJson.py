import json
import os
import argparse
import yaml
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
    data = pd.DataFrame(excel_data, columns=['TestName', 'Flow', 'Slope', 'Intercept_0', 'Intercept','Selected Sigma',
                                             'Sigma Multiple','Calculated_Offset','Overide sigma Multiple value','RootMeanSquareError','Approval',
                                             'MultiCore/MainCore'])
    length = (len (data['TestName']))
    count = 0
    #print(length)
    while(count<length):
        if data['TestName'][count] not in dict_data:
            stuff = [ data['Flow'][count], float(data['Slope'][count]),float(data['Intercept_0'][count]),float(data['Intercept'][count]),float(data['Selected Sigma'][count]),
                      data['Sigma Multiple'][count], float(data['Calculated_Offset'][count]),data['Overide sigma Multiple value'][count], float(data['RootMeanSquareError'][count]), data['Approval'][count],
                      data['MultiCore/MainCore'][count]]
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



def MapJsontoApproval(dataApproval, dataJson,resulant, allTestInstances, logFile, Copy_Pre_To_Post, oldEquations):
    Approved=0
    post=0
    pre=0
    old=0
    oldpre=0
    oldpost=0

    for i in dataJson:
        SourceTestName = i['SourceTestName']

        if SourceTestName in dataApproval:
            #['TestName', '1Flow', '2Slope', '3Intercept_0', '4Intercept','5Selected Sigma','6Sigma Multiple','7Calculated_Offset','8Overide sigma Multiple value','9RootMeanSquareError','10Approval', '10MultiCore/MainCore']

            Flow = dataApproval[SourceTestName][0]
            SlopeA =  float(dataApproval[SourceTestName][1])
            Intercept0 = float(dataApproval[SourceTestName][2])
            InterceptA = float(dataApproval[SourceTestName][3])
            SelectedSigmaA = float(dataApproval[SourceTestName][4])
            Sigmaa = dataApproval[SourceTestName][5]
            CalculatedOffset = float(dataApproval[SourceTestName][6])
            Overidesigma = dataApproval[SourceTestName][7]
            RootMeanSquareErrorA= float(dataApproval[SourceTestName][8])
            Approval = dataApproval[SourceTestName][9]

            if (Approval=='Y' or Approval=='Yes' or Approval == 'yes' or Approval=='y' or Approval=='YES'):
                if Overidesigma != ' ':
                    InterceptA = Intercept0 + float(Overidesigma)*float(SelectedSigmaA)
                Approved = Approved+1
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

                if Flow == "PREHVQK" and Copy_Pre_To_Post == True :
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
                        logFile.write("\n Missing POST Instance for :")
                        logFile.write(SourceTestName)
                        print("PRE POST missing^")


            if Approval == 'OLD':
                old=old+1
                result2 = oldEquations[SourceTestName]
                json_string = json.dumps(result2, default=lambda o: o.__dict__, sort_keys=True, indent=2)
                resulant.write(json_string)
                resulant.write(',')

                if Flow == "PREHVQK" and Copy_Pre_To_Post == True:
                    oldpre = oldpre + 1
                    postInstance1 = SourceTestName.replace("PREHVQK", "POSTHVQK")
                    if postInstance1 in oldEquations:
                        oldpost = oldpost + 1
                        result2 = oldEquations[SourceTestName]
                        json_string = json.dumps(result2, default=lambda o: o.__dict__, sort_keys=True, indent=2)
                        resulant.write(json_string)
                        resulant.write(',')
                    else:
                        print(SourceTestName)
                        logFile.write("\n Missing POST Instance in Previous Gold Json File or has a different name for :")
                        logFile.write(SourceTestName)
                        print("PRE POST missing^")



    for key in dataApproval:
        if dataApproval[key][0]!=True and dataApproval[key][1]!= "Values Passed" and dataApproval[key][6]=="MainCore":
            Approval =  dataApproval[key][5]
            if Approval=='Y' or Approval=='Yes' or Approval == 'yes' or Approval=='y' or Approval=='YES':
                #print('Equatiion missing in json')
                #print(key)
                logFile.write("\nEquatiion missing in json : " + str(key) + '\n')

    #print(Approved)
    logFile.write("\nApproved Equations  : "+ str(Approved) +'\n')
    #print(post)
    logFile.write("Post Instances In Case you are Copying POST : " + str(post) + '\n')
    #print(pre)
    logFile.write("Pre Instances In Case you are Copying POST : " + str(pre) + '\n')

    # print(Approved)
    logFile.write("\nOLd Equations  : " + str(old) + '\n')
    # print(post)
    logFile.write("Post Instances In Case you are Copying POST for old Equations: " + str(oldpost) + '\n')
    # print(pre)
    logFile.write("Pre Instances In Case you are Copying POST for old Equations: " + str(oldpre) + '\n')

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('ymlFile', help="YML_FILE")

    args = parser.parse_args()

    inputs = args.ymlFile

    with open(inputs) as file:
        ymlInputs=yaml.load(file,Loader=yaml.FullLoader)


    csvAprrovalFile = ymlInputs["Approval_File"]
    jsonequationFile = ymlInputs["Debug_Json_File"]
    FinalJson = ymlInputs["OutPut_Folder"] + "\\ADTL_Equations.adtl.json"
    logFile = ymlInputs["OutPut_Folder"] + "\\LogApprovalToJson.txt"
    Copy_Pre_To_Post = ymlInputs["Copy_Pre_To_Post"]
    goldenJsonFile = ymlInputs["Golden Json File inside previous TestProgram"]

    if goldenJsonFile == "":
        oldEquations = {}
    else:
        oldEquations = GetOldEquations(goldenJsonFile)

    dataApproval= ReadcsvData(csvAprrovalFile)
    dataJson = ReadjsonData(jsonequationFile)
    allTestInstances=AllTestInstances(dataJson)

    logFileObject = open(logFile, 'a')
    logFileObject.write("\nCreating json from Approval\n")

    with open (FinalJson, 'w') as file:
        file.write("[")
        MapJsontoApproval(dataApproval, dataJson, file, allTestInstances, logFileObject, Copy_Pre_To_Post, oldEquations)
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.write("]")

