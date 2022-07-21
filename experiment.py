
import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import gc

def DrawGraph(x,y,m,b,testName):
    my_path = os.path.dirname(__file__)
    results_dir = my_path + '\\Result_grapqh'
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
        print('DirectoryMadeResult')
    plt.figure()
    plt.plot(x, y, 'g.')
    plt.plot(x, b + m * x, 'b-')
    plt.plot(x, 0.16 + b + m * x, 'r-')
    plt.title(testName)
    if "::" in testName:
        name=testName.split("::")
        file_name= my_path+'\\'+name[0]+name[1]+".png"
        plt.savefig(file_name)
    else:
        file_name=my_path+'\\'+testName+".png"
        plt.savefig(file_name)
    plt.close()
    del x,y
    gc.collect()




if __name__ == '__main__':
    path = "C:/Users/kaurp/PycharmProjects/FitLine_NewData/idvVminPairs.json"
    outPath = "C:/Users/kaurp/PycharmProjects/FitLine_NewData/results1.json"

    x=numpy.array([100,200,300,400,500])
    y=numpy.array([700,340,900,890,980])
    m=0.5
    b=100
    testName="say::It::along"

    DrawGraph(x,y,m,b,testName)