#!/usr/bin/env python

#Script to plot data, the data and the related config is loaded by a file passed to the script.
#The options for the config are read via argparse in the following:
#All options not specific for input file have to be in the first line of the file
#All files to plot, with their corresponding options have to written from the second line on, one file per line only
#Call with <python (-i) plot_data1D.py #CONFIG_FILE (-b)
#The option -i stops python from closing automatically instead it goes to prompt
#The option -b let python run in background

import sys
import ROOT
import uncertainties as unc
from uncertainties import unumpy
from collections import namedtuple
from collections import deque #List with fast operations on both sides (right and left)
from math import sqrt
import numpy as np
import argparse 

def CalcRatio( graph1, graph2 ):
    print ("Ratio calculation")
    bins1 = graph1.GetN()
    bins2 = graph2.GetN()
    if (bins1 != bins2):
        print bins1, bins2
        print ("Graph %s and graph %s have different binning, no ratio calculation"%(graph1,graph2))
        return
    #Implement alternative which works for diffferent binnings and looks up the corresponding bins for ratio calculation
    

    RatioGraph = ROOT.TGraphAsymmErrors()
    for i in range(0,bins1):
        #print i
        x1 = graph1.GetX()[i]
        x2 = graph2.GetX()[i]
        x1low = graph1.GetErrorXlow(i)
        x2low = graph2.GetErrorXlow(i)
        x1up = graph1.GetErrorXhigh(i)
        x2up = graph2.GetErrorXhigh(i)
        if (x1 != x2 ) or (x1low != x2low ) or (x1up != x2up):
            print ("Binning of both graphs do not agree, no ratio calculation")
            print ("Bin center: %s \t %s"%(x1,x2))
            print ("Bin low edge: %s \t %s"%(x1low,x2low))
            print ("Bin up edge: %s \t %s"%(x1up,x2up))
            return
        y1 = graph1.GetY()[i]
        y2 = graph2.GetY()[i]
        e1low = graph1.GetErrorYlow(i)
        e2low = graph2.GetErrorYlow(i)
        e1up = graph1.GetErrorYhigh(i)
        e2up = graph2.GetErrorYhigh(i)
        y1sq = y1*y1
        y2sq = y2*y2
        e1lowsq = e1low*e1low
        e2lowsq = e2low*e2low
        e1upsq = e1up*e1up
        e2upsq = e2up*e2up
        
        try:
            y_ratio = y1/y2
        except ZeroDivisionError:
            y_ratio = 0

        if config.ratiobinomialerr:
            #print ("Use binomial error propagation")
            if (y1 ==y2):
                e_low = 0
                e_up = 0
            else:
                e_low  = sqrt(abs( ( (1 - 2* y1 / y2 ) * e1lowsq + y1sq * e2lowsq / y2sq )/(y2sq) ))
                e_up = sqrt(abs( ( (1 - 2* y1 / y2 ) * e1upsq  + y1sq * e2upsq  / y2sq )/(y2sq) ))
        else:
            try:
                e_low = sqrt( ( e1lowsq * y2sq + e2lowsq * y1sq ) / ( y2sq * y2sq ) )
                e_up = sqrt( ( e1upsq * y2sq + e2upsq * y1sq ) / ( y2sq * y2sq ) )
            except ZeroDivisionError:
                e_low = 0
                e_up = 0
        #print e_low, e_up
        
        RatioGraph.SetPoint(i,x1,y_ratio)
        RatioGraph.SetPointError(i,x1low,x1up,e_low,e_up)
        
    MultiRatio.Add(RatioGraph)

    return


            


  #        Double_t b1 = h1->RetrieveBinContent(i);
  #        Double_t b2 = h2->RetrieveBinContent(i);
  #          if (b2 == 0) { fSumw2.fArray[i] = 0; continue; }
  #        Double_t b1sq = b1 * b1; Double_t b2sq = b2 * b2; #Content
  #        Double_t c1sq = c1 * c1; Double_t c2sq = c2 * c2; #scaling
  #        Double_t e1sq = h1->GetBinErrorSqUnchecked(i); Error
  #        Double_t e2sq = h2->GetBinErrorSqUnchecked(i); Error
  #        if (binomial) {
  #           if (b1 != b2) {
  #              // in the case of binomial statistics c1 and c2 must be 1 otherwise it does not make sense
  #              // c1 and c2 are ignored
  #              //fSumw2.fArray[bin] = TMath::Abs(w*(1-w)/(c2*b2));//this is the formula in Hbook/Hoper1
  #              //fSumw2.fArray[bin] = TMath::Abs(w*(1-w)/b2);     // old formula from G. Flucke
  #              // formula which works also for weighted histogram (see http://root-forum.cern.ch/viewtopic.php?t=3753 )
  #              fSumw2.fArray[i] = TMath::Abs( ( (1. - 2.* b1 / b2) * e1sq  + b1sq * e2sq / b2sq ) / b2sq );
  #           } else {
  #              //in case b1=b2 error is zero
  #              //use  TGraphAsymmErrors::BayesDivide for getting the asymmetric error not equal to zero
  #              fSumw2.fArray[i] = 0;
  #           }
  #        } else {
  #           fSumw2.fArray[i] = c1sq * c2sq * (e1sq * b2sq + e2sq * b1sq) / (c2sq * c2sq * b2sq * b2sq);
  #           fSumw2.fArray[i] = (e1sq * b2sq + e2sq * b1sq) / ( b2sq * b2sq);
  #        }
  #}


    #    print ("y error: %s \t %s"%(graph.GetErrorYlow(i),graph.GetErrorYhigh(i)))

    return

def ReadBinning( bincenter, binwidth ):

    print bincenter
    print binwidth

    FileBinning = open(inputconf.binning,'r')
    
    binedges = []

    for li in FileBinning:
        splitline = li.split()
        binedges.append(float(splitline[0]))
        #print splitline[0]
    
    for i in range(len(binedges)-1):
        bincenter.append((binedges[i]+binedges[i+1])/2)
        binwidth.append(abs(binedges[i]-binedges[i+1])/2)
    
    #print binedges
    #print bincenter
    #print binwidth
    
def FillTge( inputfile ):
    print ("TGE")
    InputTge = ROOT.TGraphErrors(inputfile)
    InputTge.SetName("%s"%(inputfile))
    objectlist.append(InputTge)
    return

def FillTgae( inputfile ):
    print("TGAE")
    InputTgae = ROOT.TGraphErrors(inputfile)
    InputTgae.SetName("%s"%(inputfile))
    objectlist.append(InputTgae)
    return

def ReadHepData( inputfile ):
    #Should work with hep root files and ReadRootFile
    print ("Read from hep data file not imnplemented. Please try root file from hep data homepage.")
    return

def ReadUnumpy( inputfile, columns ):
    print("unumpy")
    if not inputconf.binning:
        print( "No binning file given cannot process, unumpy input: %s "%(inputfile))
        return
    Converters = dict.fromkeys(range(int(columns)), unc.ufloat_fromstr)
    
    Values = np.loadtxt(inputfile,converters=Converters, dtype=object)
    BinCenter = []
    BinXerror = []
    ReadBinning( BinCenter, BinXerror )
    #print Values
    #print BinCenter
    #print BinXerror
    if ( len(BinCenter) != len(Values) ) :
        print( "Size of binning and number of values don't agree. Stopping macro!")
        return

    UnumpyTge = ROOT.TGraphErrors(len(BinCenter),np.array(BinCenter,'d'),unumpy.nominal_values(Values),np.array(BinXerror,'d'),unumpy.std_devs(Values))
    UnumpyTge.SetName("%s"%inputfile)
    objectlist.append(UnumpyTge)

    return 

def ReadData( datafile ):
    # Count number of columns and decide what data format 
    # 1 column & +/- -> unumpy
    # 2-4 columns -> TGraphErrors
    # 6 columns -> TGraphAsymmErrors
    print datafile
    with file(datafile) as f:
        line = f.readline()
        columns = len(line.split())
        print ("%s column(s)"%(columns))
        if "+/-" in line:
            ReadUnumpy( datafile, columns )
        elif columns >= 2 and columns <=4:
            FillTge( datafile )
        elif columns == 6:
            FillTgae( datafile )
        else:
            print("Cannot identify input file format. Not Importing %s."%(datafile))

    return

def ReadRootFile( filename ):
    print (filename)
    inputfile = ROOT.TFile.Open(filename)
    #inputfile.ls()
    objectlist.append(inputfile)

def GetFromTDirFile( objname, rootfile ):
    print (objname)
    dirfile = rootfile.FindObjectAny(objname)
    if not dirfile:
        print ("empty")
        raise ValueError("Null pointer")
    else:
        #print (dirfile)
        objectlist.append(dirfile)

def GetFromTList( objname, rootlist ):
    print (objname)
    listfile = rootlist.FindObject(objname)
    if not listfile:
        print ("empty")
        raise ValueError("Null pointer")
    else:
        #print (listfile)
        objectlist.append(listfile)


def PlotHisto():
    print "Test PlotHisto"

def PlotRatio():
    print "Test PlotRatio"


def SavePlots():
    for oformat in config.outputformat:
        TCspectrum.SaveAs("plots/%s.%s"%(config.name,oformat))
        if config.ratio:
            TCratio.SaveAs("plots/%s_gratio.%s"%(config.name,oformat))
        if config.plusratio:
            TCplus.SaveAs("plots/%s_plus.%s"%(config.name,oformat))





    

fileparser = argparse.ArgumentParser()
fileparser.add_argument("-f", "--filename", nargs='+')
fileparser.add_argument("-ld", "--legend", default="", nargs='+')
fileparser.add_argument("-nc", "--numbercolumns") #Define columns for unumpy import. No longer needed? Should be replaced by automatic column detection
fileparser.add_argument("-nm", "--nomarker", action="store_true")
fileparser.add_argument("-rd", "--ratiodivisor", action="store_true") #Ratio can only be calculated with exactly one input variable chosen as divisor - only works if the same binning is chosen for all files
fileparser.add_argument("-rld", "--ratiolegend", default="", nargs='+')
fileparser.add_argument("-rnm", "--rationomarker", action="store_true")
fileparser.add_argument("-sr", "--skipratio", action="store_true")
fileparser.add_argument("-fb", "--filebinning")

parser = argparse.ArgumentParser()
parser.add_argument("-ac", "--alternativecolors", action="store_true")
parser.add_argument("-bc", "--bincenter") #This option will only work with tgrapherrors
parser.add_argument("-bm", "--bottommargin", default=0.1, type=float)
parser.add_argument("-lb", "--label", nargs='+')
parser.add_argument("-lbx", "--labelbox", nargs=4, default=[0.15,0.25,0.6,0.15], type=float)
parser.add_argument("-lm", "--leftmargin", default=0.08, type=float)
parser.add_argument("-lp", "--legendposition", nargs =2, default=[0.5,0.8], type=float) #Defines top left corner of TLegend
parser.add_argument("-lt", "--legendtitle", nargs='+')
parser.add_argument("-ms", "--markersize", default=1., type=float)
parser.add_argument("-n", "--name", default="plot")
parser.add_argument("-rm", "--rightmargin", default=0.04, type=float)
parser.add_argument("-s", "--save", action="store_true")
parser.add_argument("-sx", "--sizex", default=1200, type=int)
parser.add_argument("-sy", "--sizey", default=900, type =int)
parser.add_argument("-t", "--title", default="")
parser.add_argument("-tm", "--topmargin", default=0.04, type=float)
parser.add_argument("-tox", "--titleoffsetx", default=1., type=float)
parser.add_argument("-toy", "--titleoffsety", default=1., type=float)
parser.add_argument("-xr", "--xrange", nargs=2, type=float)
parser.add_argument("-xt", "--xtitle", default="", nargs='+')
parser.add_argument("-yr", "--yrange", nargs=2, type=float)
parser.add_argument("-yt", "--ytitle", default="", nargs='+')
parser.add_argument("--xlog", action="store_true")
parser.add_argument("--xrlog", action="store_true")
parser.add_argument("--ylog", action="store_true")
parser.add_argument("--yrlog", action="store_true")
parser.add_argument("-st", "--stack", action="store_true")
#ratio config
parser.add_argument("-mxl", "--morexlables", action="store_true") #Only works with log axis
parser.add_argument("-myl", "--moreylables", action="store_true") #Only works with log axis
parser.add_argument("-pr", "--plusratio", action="store_true")
parser.add_argument("-ppr", "--pluspadaratio", default=0.3, type=float)
parser.add_argument("-r", "--ratio", action="store_true")
parser.add_argument("-rbe", "--ratiobinomialerr", action="store_true")
parser.add_argument("-rl", "--ratiolegend", action="store_true")
parser.add_argument("-rlp", "--ratiolegendposition", nargs =2, default=[0.5,0.8], type=float) #Defines top left corner of TLegend
parser.add_argument("-xrr", "--xratiorange", nargs=2, type=float)
parser.add_argument("-yrr", "--yratiorange", nargs=2, type=float)
parser.add_argument("-of", "--outputformat", nargs='+', default=["pdf","png"])
parser.add_argument("-sp", "--setpalette", default=77, type=int, choices=range(51,113))
parser.add_argument("-up", "--usepalette", action="store_true")

#parser.add_argument("-", "--")

config_line = ''

filecheck = ['-f ','--filename ']

inputdeque = deque()
fileconfig = namedtuple('fileconfig','path legend ratiolegend skipmarker skipratiomarker skipratio divisor binning')

with open(sys.argv[1],'r') as f:    #path to file with config of plot
    for li in f:
        if any ([x in li for x in filecheck]):
            lineargs = fileparser.parse_args(li.split())
#Alternative storing scheme to store ratio divisor always at first object
            #if lineargs.ratiodivisor:
            #    #Put the ratiodivisor always on the first place
            #    inputdeque.appendleft(fileconfig(lineargs.filename, lineargs.legend, lineargs.ratiolegend, lineargs.nomarker, lineargs.rationomarker, lineargs.skipratio, lineargs.ratiodivisor, lineargs.filebinning)) 
            #else:
            #    inputdeque.append(fileconfig(lineargs.filename, lineargs.legend, lineargs.ratiolegend, lineargs.nomarker, lineargs.rationomarker, lineargs.skipratio, lineargs.ratiodivisor, lineargs.filebinning)) 
            inputdeque.append(fileconfig(lineargs.filename, lineargs.legend, lineargs.ratiolegend, lineargs.nomarker, lineargs.rationomarker, lineargs.skipratio, lineargs.ratiodivisor, lineargs.filebinning)) 
            

        else:
            li = li.strip()
            li = li.strip('\n')
            if '-' in li:
                config_line += li 
                config_line += ' '
            else:
                print ('Line \"' + li +'\" does not start with an option for a variable')
            print config_line


config = parser.parse_args(config_line.split())
#print config
#print filelist
#print filelegend
#for idx,inputconf in enumerate(inputdeque):
#    print idx
#    print inputconf


########## Process input

print "START PROCESSING"

graphlist = []
ratiolist = []


for idx,inputconf in enumerate(inputdeque):
    #print (idx)
    objectlist = []
    print (inputconf)
    listsize = len(inputconf.path)
    print (listsize)
    for jdx,listin in enumerate(inputconf.path): #Take element [0] as it represents the object name to be processed
        print (jdx)
        print (listin)
        if jdx is 0: 
            #open file and decide between root files and text based files
            if listin.endswith(".root"):
                ReadRootFile(listin)
            else:
                print ("Read values from text based file %s"%(listin))
                ReadData( listin )   
        else:
            try:
                if objectlist[jdx-1].InheritsFrom("TDirectoryFile"):
                    print ("TDirectoryFile")
                    GetFromTDirFile( listin, objectlist[jdx-1] )
                elif objectlist[jdx-1].InheritsFrom("TList"):
                    print ("TList")
                    GetFromTList( listin, objectlist[jdx-1] )
                else:
                    print ("Unsupported class")
                    break
            except Exception as e:
                print (e)
                print ("Cannot not process: \'%s\', no inheritance from TObject "%(listin))
                break
    print ("%s \n"%(objectlist))
    try:
        if objectlist[jdx].InheritsFrom("TH1"):
                #Use inputconf for storing and replace path by TGraph
            graphlist.append(inputconf._replace(path=ROOT.TGraphAsymmErrors(objectlist[jdx]),))
        elif objectlist[jdx].InheritsFrom("TGraph"):
            print ("Storing TGraph...")
            graphlist.append(inputconf._replace(path=objectlist[jdx],))
    except Exception as e:
        #print (e)
        print ("Cannot not process: \'%s\', no inheritance from TH1 or TGraph. No plotting.  "%(listin))
        #break

print "Graph list:"
print ("%s \n"%(graphlist))

DivPos = 0
DivPos2 = 0
Divisor = 0
for idx,inputdata in enumerate(graphlist):
    graph = inputdata.path
    print graph
    bins = graph.GetN()


    print bins
    if inputdata.divisor:
        print ("Divisor: %s"%(graph))
        DivPos = idx
        Divisor+=1
    #for i in range(0,bins):
    #    print i
    #    print ("points: %s \t %s"%(graph.GetX()[i],graph.GetY()[i]))
    #    print ("x error: %s \t %s"%(graph.GetErrorXlow(i),graph.GetErrorXhigh(i)))
    #    print ("y error: %s \t %s"%(graph.GetErrorYlow(i),graph.GetErrorYhigh(i)))

if  config.ratio or config.plusratio:
    if Divisor > 1:
        sys.exit("Cannot calculate ratio, because %s divisors are defined. Expecting only 1!"%(Divisor))
        
    elif Divisor < 1:
        sys.exit("Cannot calculate ratio, because %s divisor are defined. Expecting 1."%(Divisor))
        

########## ROOT config

font2use = 43
fontsize = 20*config.markersize

ROOT.gStyle.SetTextFont(font2use)
ROOT.gStyle.SetTitleFontSize(fontsize)

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadLeftMargin(config.leftmargin)
ROOT.gStyle.SetPadRightMargin(config.rightmargin)
ROOT.gStyle.SetPadTopMargin(config.topmargin)
ROOT.gStyle.SetPadBottomMargin(config.bottommargin)
ROOT.gStyle.SetTitleOffset(config.titleoffsety,"y")
ROOT.gStyle.SetTitleOffset(config.titleoffsetx,"x")
ROOT.gStyle.SetLabelFont(font2use,"x")
ROOT.gStyle.SetLabelFont(font2use,"y")
ROOT.gStyle.SetLabelSize(fontsize,"x")
ROOT.gStyle.SetLabelSize(fontsize,"y")
ROOT.gStyle.SetTitleFont(font2use,"x")
ROOT.gStyle.SetTitleFont(font2use,"y")
ROOT.gStyle.SetTitleYSize(fontsize)
ROOT.gStyle.SetTitleXSize(fontsize)
ROOT.gStyle.SetPalette(config.setpalette)


#Dictionary with combinations of marker, color and size
if config.alternativecolors:
    markertable = {0:[ROOT.kBlue+2,33,1.7],1:[ROOT.kOrange+10,8,1.0],2:[ROOT.kTeal-6,21,1.0],3:[ROOT.kMagenta+3,34,1.4],4:[ROOT.kBlue+2,22,1.2],5:[ROOT.kPink,23,1.2],6:[ROOT.kOrange+10,29,1.6],7:[ROOT.kTeal+3,21,1.0]}
else:
    markertable = {0:[ROOT.kAzure+2,33,1.7],1:[ROOT.kSpring-8,8,1.0],2:[ROOT.kRed+1,21,1.0],3:[ROOT.kOrange+1,34,1.4],4:[ROOT.kAzure+2,22,1.2],5:[ROOT.kSpring-8,23,1.2],6:[ROOT.kRed+1,29,1.6],7:[ROOT.kOrange+1,21,1.0]}


#print config
#print filelist


########## General histogram
TCspectrum = ROOT.TCanvas("TCspectrum","",20,20,config.sizex,config.sizey)

MultiSpec = ROOT.TMultiGraph()

#if config.ratio or config.plusratio:
#    THSRatio = ROOT.THStack("THSRatio","%s_ratio"%(config.title))



if config.xlog:
    ROOT.gPad.SetLogx()
if config.ylog:
    ROOT.gPad.SetLogy()

if config.legendtitle:
    TLeg = ROOT.TLegend(config.legendposition[0],config.legendposition[1],config.legendposition[0]+0.05,config.legendposition[1]-(len(inputdeque)+1)*(0.02*config.markersize))
else:
    TLeg = ROOT.TLegend(config.legendposition[0],config.legendposition[1],config.legendposition[0]+0.05,config.legendposition[1]-len(inputdeque)*(0.02*config.markersize))
TLeg.SetFillColor(0)
TLeg.SetMargin(0.075*config.markersize)
TLeg.SetBorderSize(0)
TLeg.SetTextFont(font2use)
TLeg.SetTextSize(fontsize)
if config.legendtitle:
    TLeg.AddEntry("", "  %s"%(' '.join(config.legendtitle)),"")

if config.label:
    print config.labelbox
    Label = ROOT.TLegend(config.labelbox[0],config.labelbox[1],config.labelbox[2],config.labelbox[3])
    Label.SetFillColor(0)
    Label.SetBorderSize(0)
    Label.SetTextFont(font2use)
    Label.SetTextSize(fontsize)
    Label.AddEntry("","%s"%(' '.join(config.label)),"")


for idx,graphdata in enumerate(graphlist):
    graphdata.path.SetMarkerColor(markertable.get(idx)[0])
    graphdata.path.SetLineColor(markertable.get(idx)[0])
    graphdata.path.SetLineWidth(int(1*config.markersize)) #May need improvement with config.markersize, but only accepts int
    graphdata.path.SetMarkerStyle(markertable.get(idx)[1])
    graphdata.path.SetMarkerSize(markertable.get(idx)[2]*config.markersize)
    TLeg.AddEntry(graphdata.path, ("  %s"%(' '.join(graphdata.legend))))
    if graphdata.skipmarker:
        TLeg.AddEntry("", ("  %s"%(' '.join(graphdata.legend))),"")
    MultiSpec.Add(graphdata.path)
if config.usepalette:
    MultiSpec.Draw("AP pmc plc")
else:
    MultiSpec.Draw("AP")

MultiSpec.SetTitle("%s;%s;%s"%(' '.join(config.title),' '.join(config.xtitle),' '.join(config.ytitle)))
    
if config.xrange:
    MultiSpec.GetXaxis().SetRangeUser(config.xrange[0],config.xrange[1])
if config.yrange:
    MultiSpec.GetYaxis().SetRangeUser(config.yrange[0],config.yrange[1])
if config.morexlables:
    MultiSpec.GetXaxis().SetMoreLogLabels(True)
if config.moreylables:
    MultiSpec.GetYaxis().SetMoreLogLabels(True)

TLeg.Draw("")

if config.label:
    Label.Draw("")

ROOT.gPad.Modified()
ROOT.gPad.Update()
if not config.xratiorange:
    if not config.xrange:
        config.xratiorange=[ MultiSpec.GetXaxis().GetXmin(),  MultiSpec.GetXaxis().GetXmax()]
    else:
        config.xratiorange=config.xrange

print config.xrange
print config.xratiorange

########## Ratio graph


if  config.ratio or config.plusratio:
    TCratio = ROOT.TCanvas("TCratio","",20,20,config.sizex,config.sizey)
    MultiRatio = ROOT.TMultiGraph()

    TRatioLeg = ROOT.TLegend(config.ratiolegendposition[0],config.ratiolegendposition[1],config.ratiolegendposition[0]+0.25,config.ratiolegendposition[1]-(len(inputdeque)-1)*(0.02*config.markersize))
    TRatioLeg.SetFillColor(0)
    TRatioLeg.SetMargin(0.075*config.markersize)
    TRatioLeg.SetBorderSize(0)
    TRatioLeg.SetTextFont(font2use)
    TRatioLeg.SetTextSize(fontsize)

    TFconst1 = ROOT.TF1("TFconst1","1.",config.xratiorange[0],config.xratiorange[1])
    for idx,graphdata in enumerate(graphlist):
        if graphdata.skipratio:
            continue
        if graphdata.divisor:
            TFconst1.SetLineColor(markertable.get(idx)[0])
            TFconst1.SetLineWidth(4)
            TRatioLeg.AddEntry(TFconst1, ("  %s"%(' '.join(graphdata.legend))),"l")
            continue
        if graphdata.skipratiomarker:
            TRatioLeg.AddEntry("", ("  %s"%(' '.join(graphdata.legend))),"")
        else:
            TRatioLeg.AddEntry(graphdata.path, ("  %s"%(' '.join(graphdata.legend))),"p")

        CalcRatio(graphdata.path,graphlist[DivPos].path)

    if config.usepalette:
        MultiRatio.Draw("AP pmc plc")
    else:
        MultiRatio.Draw("AP")


    MultiRatio.GetXaxis().SetTitle("%s"%(' '.join(config.xtitle)))
    
    if config.xratiorange:
        MultiRatio.GetXaxis().SetRangeUser(config.xratiorange[0],config.xratiorange[1])
    if config.yratiorange:
        MultiRatio.GetYaxis().SetRangeUser(config.yratiorange[0],config.yratiorange[1])
    
    TFconst1.Draw("same")
    if config.ratiolegend:
        TRatioLeg.Draw("")

    ROOT.gPad.Modified()
    ROOT.gPad.Update()

########## Plot spectrum + ratio

#    if config.plusratio:
#        TCplus = ROOT.TCanvas("TCplus","",20,20,config.sizex,config.sizey)
#        TCplus.Divide(1,2)
#        TCplus.cd(1).SetPad(0., config.pluspadratio, 1., 1.);  # top pad
#        TCplus.cd(1).SetBottomMargin(0.001);
#        TCplus.cd(2).SetPad(0., 0., 1., config.pluspadratio);  # bottom pad
#        TCplus.cd(2).SetTopMargin(0);
#        TCplus.cd(2).SetBottomMargin(config.bottommargin/config.pluspadratio); # for x-axis label
#        
#        TLegPlus = TLeg.Clone("TLegPlus")
#        if config.legendtitle:  #Extend legend size due to shrinked canvas. NEED TO RESET Y1 instead of Y2, because TBox orders Y1 and Y2 by size and the legend position is defined by the top left corner (Y1 > Y2).
#            TLegPlus.SetY1(config.legendposition[1]-((len(filelist)+1)*(0.02*config.markersize))/(1-config.pluspadratio))
#            #TLegPlus.SetY2(config.legendposition[1]-((len(filelist)+1)*(0.02*config.markersize)))
#        else:
#            TLegPlus.SetY1(config.legendposition[1]-(len(filelist)*(0.02*config.markersize))/(1-config.pluspadratio))
#            #TLegPlus.SetY2(config.legendposition[1]-(len(filelist)*(0.02*config.markersize)))
#        
#    
#        TCplus.cd(1)
#        if config.xlog:
#            ROOT.gPad.SetLogx()
#        if config.ylog:
#            ROOT.gPad.SetLogy()
#        THSt1.Draw("nostack")
#        #TLegPlus.SetY2(0.0)
#        TLegPlus.Draw("")
#        if config.label:
#            Label.Draw("")
#        
#        TCplus.cd(2)
#        THSRatio.GetXaxis().SetTitleOffset(config.titleoffsetx/config.pluspadratio)
#        THSRatio.Draw("nostack")
#        TFconst1.Draw("same")
#        THSRatio.Draw("nostacksame")
#        #TRatioLeg.Draw("")
#        #if config.ratio:
#        #    THSRatio.DrawCopy("nostacksame")
#        #if config.ratiolegend:

        
    
SavePlots()

