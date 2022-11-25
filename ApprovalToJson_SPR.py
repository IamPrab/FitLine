from os import path
import json
import json
import os
import argparse
import yaml
import pandas as pd


def ReadcsvData(csvAprrovalFile):

    excel_data = pd.read_excel(csvAprrovalFile)
    dict_data={}
    data = pd.DataFrame(excel_data, columns=['TestName', 'Flow', 'Slope', 'Intercept_0', 'Intercept','Selected Sigma',
                                             'Sigma Multiple','Calculated_Offset','Overide sigma Multiple value','RootMeanSquareError','Vmin Pred','Approval',
                                             'MultiCore/MainCore'])
    length = (len (data['TestName']))
    count = 0
    #print(length)
    while(count<length):
        if data['TestName'][count] not in dict_data:

            stuff = [ float(data['Selected Sigma'][count]),
                          data['Sigma Multiple'][count], float(data['Calculated_Offset'][count]),data['Overide sigma Multiple value'][count],
                          data['Vmin Pred'][count],
                          data['Approval'][count],
                          data['MultiCore/MainCore'][count]]
            dict_data[data['TestName'][count]] = stuff

        else:
            print(data['TestName'][count])
            print(dict_data[data['TestName'][count]])
            print("double Equation ^^")
        count = count + 1
    # print(count)
    # print(len(dict_data))
    #print(dict_data)
    return dict_data


if __name__ == '__main__':
    path = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\XEE_8PSK_XEE\\8PSK_H10A00\\ADTL_Equations.adtl.json"
    csvAprrovalFile= "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\XEE_8PSK_XEE\\8PSK_H10A00\\ApprovalFile.xlsx"

    sdList = "SDList = (\n"
    mdList = "MDList = (\n"
    with open(path) as data:
        d = json.load(data)
        data.close()


    csvdata = ReadcsvData(csvAprrovalFile)
    #print(csvdata)


    for tests in d:
        #print (len(tests['PerDomainEquations']));
        #print(tests['SourceTestName'])
        o_TestName= tests['SourceTestName'].split("::")[1]
        o_slope = tests['Slope']
        o_Intercept = tests['Intercept']
        o_Intercept0 = tests['Intercept_0']
        if (tests['SourceTestName'].find('POSTHVQK')>0):
            #print(tests['SourceTestName'])
            o_selectedSigma = csvdata[tests['SourceTestName'].replace("POSTHVQK", "PREHVQK")][0]
            o_sigmamultiple = int(csvdata[tests['SourceTestName'].replace("POSTHVQK", "PREHVQK")][1])
        else:
            o_selectedSigma = csvdata[tests['SourceTestName']][0]
            o_sigmamultiple = int(csvdata[tests['SourceTestName']][1])
        o_vminPred = tests['VminPredOffset']

        if len(tests['YParameters'])==0:
            o_GUDToken = "#" + o_TestName + "GUD TOKEN Missing from mtpl file--"
        else:
            o_GUDToken = tests['YParameters'][0]
            print(tests['YParameters'])
        if o_GUDToken == "":
            o_GUDToken = "#"+o_TestName+ "GUD TOKEN Missing from mtpl file--"


        #print(o_GUDToken)
        # if (csvdata[tests['SourceTestName']][3]!= " "):
        #     o_sigmamultiple = int(csvdata[tests['SourceTestName']][3])
        #     #print(o_selectedSigma)

        o_vminPredIntercept = o_Intercept0 - o_vminPred #wrong take intercept 0
        o_domainLength = len(tests['PerDomainEquations'])
        o_ValdStringOffset = ",'VADTLOFFSETSTR"
        o_VminpredOffset = ",'VMINPREDOFFSETSTR"

        if o_domainLength==0:
            sdList = sdList + "('" + o_GUDToken + "'," + "'VADTSTR," + str(o_slope) + "," + str(o_Intercept) + ","+ str(o_selectedSigma) + ","+ str(o_sigmamultiple) + \
                     "','VMINPREDSTR," + str(o_slope) + "," + str(o_vminPredIntercept) + ",0.02,0.01," + str(o_vminPred) +"'),\n"
        else:
            for i in range(o_domainLength):
                o_ValdStringOffset = o_ValdStringOffset + ",0"
                o_VminpredOffset = o_VminpredOffset + ",0"

            o_ValdStringOffset = o_ValdStringOffset + "'"
            mdList = mdList + "('" + o_GUDToken + "'," + "'VADTSTR," + str(o_slope) + "," + str(o_Intercept) + "," + str(o_selectedSigma) + ","+ str(o_sigmamultiple) + o_ValdStringOffset + \
                     ",'VMINPREDSTR," + str(o_slope) + "," + str(o_vminPredIntercept) + ",0.02,0.01," + str(o_vminPred) + o_VminpredOffset + ",'IDSK,1.60')\n"

    print(sdList + ")")
    print(mdList + ")")







