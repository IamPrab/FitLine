import ADTL_Auditing
import argparse
import FitLineMulticore
import DrawGraphs

parser = argparse.ArgumentParser()

parser.add_argument('operation', help="FitLine/AuditADTL/DrawGraphs")
parser.add_argument('input',help="inputFile")
parser.add_argument('output',help="outputFile")
parser.add_argument('sigma',help="sigma")


args = parser.parse_args()

if args.operation == 'FitLine':
    FitLineMulticore.main(args.input,args.output,args.sigma)
    print('FitLine Success')

if args.operation == 'AuditADTL':
    ADTL_Auditing.main(args.input,args.output)
    print('Audit Success')

if args.operation == 'DrawGraphs':
    DrawGraphs.main(args.input,args.output,args.sigma)
    print('Graphs Success')
