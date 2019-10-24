#!/usr/bin/env python

#Script to plot data, the data and the related config is loaded by a file passed to the script.
#The options for the config are read via argparse in the following:
#All options not specific for input files, can be written in as many lines as wished
#All files to plot, with their corresponding options have to be written into one line, one file per line only
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
import designtables as design
import linecache
import re

def CalcRatio( graph1, graph2 ):
    print ("Ratio calculation")
    print graph1
    print graph2
    bins1 = graph1.GetN()
    bins2 = graph2.GetN()
    if (bins1 != bins2):
        print ("Binning 1: %s - Binning 2: %s"%(bins1, bins2))
        sys.exit("Graph %s and graph %s have different binning, no ratio calculation"%(graph1,graph2))
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
        

    return RatioGraph

def ReadBinning( bincenter, binwidth ):

    print bincenter
    print binwidth

    FileBinning = open(inputconf.binning,'r')
    
    binedges = []

    for li in FileBinning:
        splitline = li.split()
        binedges.append(float(splitline[0]))
    
    for i in range(len(binedges)-1):
        bincenter.append((binedges[i]+binedges[i+1])/2)
        binwidth.append(abs(binedges[i]-binedges[i+1])/2)
    
    
def FillTge( inputfile ):
    print ("TGE")
    InputTge = ROOT.TGraphErrors(inputfile)
    InputTge.SetName("%s"%(inputfile))
    return InputTge

def FillTgae( inputfile ):
    print("TGAE")
    InputTgae = ROOT.TGraphErrors(inputfile)
    InputTgae.SetName("%s"%(inputfile))
    return InputTgae

def FillTge1( inputfile ):
    
    Values = np.loadtxt(inputfile,dtype=object)
    BinCenter = []
    BinXerror = []
    ReadBinning( BinCenter, BinXerror )
    if ( len(BinCenter) != len(Values) ) :
        print( "Size of binning and number of values don't agree. Stopping macro!")
        return

    InputTge1 = ROOT.TGraphErrors(len(BinCenter),np.array(BinCenter,'d'),np.array(Values,'d'),np.array(BinXerror,'d'))
    InputTge1.SetName("%s"%(inputfile))

    return InputTge1

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
    if ( len(BinCenter) != len(Values) ) :
        print( "Size of binning and number of values don't agree. Stopping macro!")
        return

    UnumpyTge = ROOT.TGraphErrors(len(BinCenter),np.array(BinCenter,'d'),unumpy.nominal_values(Values),np.array(BinXerror,'d'),unumpy.std_devs(Values))
    UnumpyTge.SetName("%s"%inputfile)
    #objectlist.append(UnumpyTge)

    return UnumpyTge

def ReadData( datafile , skiprows ):
    # Count number of columns and decide what data format 
    # 1 column & +/- -> unumpy
    # 1 column & binning -> TGraphErrors (To show the bin width)
    # 2-4 columns -> TGraphErrors
    # 6 columns -> TGraphAsymmErrors
    print datafile
    #Skip rows for column identification, Unumpy should not have leading line by default, and filling of TGE and TGAE seem to skip lines which do not start with a number
    #TODO: Check if the assumptions are true
    line = linecache.getline(datafile,skiprows+1)
    columns = len(line.split())
    print ("%s column(s)"%(columns))
    if "+/-" in line:
        return (ReadUnumpy( datafile, columns ))
    elif 1 == columns and inputconf.binning:
        return (FillTge1( datafile ))
    elif columns >= 2 and columns <=4:
        return (FillTge( datafile ))
    elif 6 == columns:
        return (FillTgae( datafile ))
    else:
        sys.exit("Cannot identify input file format. Not Importing %s."%(datafile))

        return

def ReadRootFile( filename ):
    print (filename)
    inputfile = ROOT.TFile.Open(filename)
    #inputfile.ls()
    #objectlist.append(inputfile)
    return inputfile

def GetFromTDirFile( objname, rootfile ):
    print (objname)
    dirfile = rootfile.FindObjectAny(objname)
    if not dirfile:
        print ("empty")
        raise ValueError("Null pointer")
    else:
        #print (dirfile)
        #objectlist.append(dirfile)
        return dirfile

def GetFromTList( objname, rootlist ):
    print (objname)
    listfile = rootlist.FindObject(objname)
    if not listfile:
        print ("empty")
        raise ValueError("Null pointer")
    else:
        #print (listfile)
        #objectlist.append(listfile)
        return listfile


def SavePlots():
    for oformat in config.outputformat:
        TCspectrum.SaveAs("plots/%s.%s"%(config.name,oformat))
        if config.ratio:
            TCratio.SaveAs("plots/%s_gratio.%s"%(config.name,oformat))
        if config.plusratio:
            TCplus.SaveAs("plots/%s_plus.%s"%(config.name,oformat))


fileparser = argparse.ArgumentParser()
fileparser.add_argument("-f", "--filename", nargs='+')
fileparser.add_argument("-bf", "--boxfilename", nargs='+') #Data points with errors drawn as boxes
fileparser.add_argument("-ld", "--legend", default="", nargs='+')
fileparser.add_argument("-nm", "--nomarker", action="store_true")
fileparser.add_argument("-rd", "--ratiodivisor", action="store_true") #Ratio can only be calculated with exactly one input variable chosen as divisor - only works if the same binning is chosen for all files
fileparser.add_argument("-rld", "--ratiolegend", default="", nargs='+')
fileparser.add_argument("-rnm", "--rationomarker", action="store_true")
fileparser.add_argument("-rbr", "--ratioboxerror", action="store_true") #Use error from boxfile for error propagation, if both inputs are given
fileparser.add_argument("-sr", "--skipratio", action="store_true")
fileparser.add_argument("-fb", "--filebinning")
fileparser.add_argument("-sro", "--skiprows", type=int, default=0) #Skip first x rows, when reading text file

parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter 
        )
parser.add_argument("-ac", "--alternativecolors", action="store_true")
parser.add_argument("-bc", "--bincenter") #This option will only work with tgrapherrors
parser.add_argument("-bm", "--bottommargin", default=0.1, type=float)
parser.add_argument("-lb", "--label", nargs='+')
parser.add_argument("-lbx", "--labelbox", nargs=4, default=[0.15,0.25,0.6,0.15], type=float)
parser.add_argument("-lm", "--leftmargin", default=0.08, type=float)
parser.add_argument("-l", "--legend", action="store_true")
parser.add_argument("-lox", "--labeloffsetx", default=0.01, type=float)
parser.add_argument("-lp", "--legendposition", nargs =2, default=[0.5,0.8], type=float) #Defines top left corner of TLegend
parser.add_argument("-lt", "--legendtitle", nargs='+')
parser.add_argument("-sc", "--scaling", default=1., type=float, help='Scale markersize and fontsize with constant factor.')
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
parser.add_argument("--ylog", action="store_true")
parser.add_argument("-xbl", "--xbinlabel", nargs='+', help=
        'Change bin labels on x-axis, number of arguments has to agree with number of bins on axis.')
parser.add_argument("-of", "--outputformat", nargs='+', default=["pdf","png"])
parser.add_argument("-sp", "--setpalette", default=77, type=int, choices=range(51,114))
parser.add_argument("-pc","--palettecolors",default=0, type=int, choices=range(0,4), help=('''
        Defines color distribution in palette :
        0: Equidistant distributed over palette, avoid minimum/maximum
        1: Equidistant distributed over palette, start at minimum, avoid maximum
        2: Equidistant distributed over palette, avoid minimum, include maximum
        3: Equidistant distributed over palette, include minimum/maximum '''))
parser.add_argument("-up", "--usepalette", action="store_true")
parser.add_argument("-ct", "--colortable", type=int, default=2)
parser.add_argument("-mt", "--markertable", type=int, default=1)
#ratio config
parser.add_argument("-mxl", "--morexlables", action="store_true",
        help='Add more ticks to x-axis. Only works with log axis')
parser.add_argument("-myl", "--moreylables", action="store_true",
        help='Add more ticks to y-axis. Only works with log axis')
parser.add_argument("-pr", "--plusratio", action="store_true",
        help='Create a combined canvas with ratio below spectrum.')
parser.add_argument("-ppr", "--pluspadratio", default=0.3, type=float)
parser.add_argument("-r", "--ratio", action="store_true")
parser.add_argument("-rbe", "--ratiobinomialerr", action="store_true")
parser.add_argument("-rl", "--ratiolegend", action="store_true")
parser.add_argument("-rlp", "--ratiolegendposition", nargs =2, default=[0.5,0.8], type=float, 
        help='Set top left corner of legend in ratio plot')
parser.add_argument("-xrr", "--xratiorange", nargs=2, type=float, 
        help='Set x-axis range for ratio.')
parser.add_argument("-yrr", "--yratiorange", nargs=2, type=float, 
        help='Set y-axis range for ratio.')
parser.add_argument("--xrlog", action="store_true", 
        help='Plot log x-axis for ratio.')
parser.add_argument("--yrlog", action="store_true", 
        help='Plot log y-axis for ratio.')
parser.add_argument("-v", "--verbose", action="store_true",
        help='Enable verose output')

#parser.add_argument("-", "--")
helper = re.compile('--help|-h')
if helper.match(sys.argv[1]):
    print("Possible flags for loaded files:")
    fileparser.print_help()
    print("Possible flags for general plotting:")
    parser.print_help()
    sys.exit()

config_line = ''

filecheck = ['-f ', '-bf ', '--filename ', '--boxfilename ']

inputdeque = deque()
fileconfig = namedtuple('fileconfig','path boxpath ratiobox legend ratiolegend skipmarker skipratiomarker skipratio divisor binning skiprows')

with open(sys.argv[1],'r') as f:    #path to file with config of plot
    for li in f:
        if li[0] is "#":
            continue
        elif any ([x in li for x in filecheck]):
            lineargs = fileparser.parse_args(li.split())
            #Alternative storing scheme to store ratio divisor always at first object
            #if lineargs.ratiodivisor:
            #    #Put the ratiodivisor always on the first place
            #    inputdeque.appendleft(fileconfig(lineargs.filename, lineargs.legend, lineargs.ratiolegend, lineargs.nomarker, lineargs.rationomarker, lineargs.skipratio, lineargs.ratiodivisor, lineargs.filebinning)) 
            #else:
            #    inputdeque.append(fileconfig(lineargs.filename, lineargs.legend, lineargs.ratiolegend, lineargs.nomarker, lineargs.rationomarker, lineargs.skipratio, lineargs.ratiodivisor, lineargs.filebinning)) 
            inputdeque.append(fileconfig(lineargs.filename, lineargs.boxfilename, lineargs.ratioboxerror, lineargs.legend, lineargs.ratiolegend, lineargs.nomarker, lineargs.rationomarker, lineargs.skipratio, lineargs.ratiodivisor, lineargs.filebinning, lineargs.skiprows)) 
            

        else:
            li = li.strip()
            li = li.strip('\n')
            if li[0] is "-":
                config_line += li 
                config_line += ' '
            else:
                print ('Line \"' + li +'\" does not start with an option for a variable')
            #print config_line


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

for idx,inputconf in enumerate(inputdeque):
    boxgraph= None
    returngraph = None
    if inputconf.path:
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
                    objectlist.append(ReadRootFile(listin))
                else:
                    print ("Read values from text based file %s"%(listin))
                    objectlist.append(ReadData( listin, inputconf.skiprows ))
            else:
                try:
                    if objectlist[jdx-1].InheritsFrom("TDirectoryFile"):
                        print ("TDirectoryFile")
                        objectlist.append(GetFromTDirFile( listin, objectlist[jdx-1] ))
                    elif objectlist[jdx-1].InheritsFrom("TList"):
                        print ("TList")
                        objectlist.append(GetFromTList( listin, objectlist[jdx-1] ))
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
                print ("Storing TH1")
                #Use inputconf for storing and replace path by TGraph
                returngraph=ROOT.TGraphAsymmErrors(objectlist[jdx])
            elif objectlist[jdx].InheritsFrom("TGraph"):
                print ("Storing TGraph")
                returngraph=objectlist[jdx]
        #TODO: Add possibilty to add function (TF1)
        except Exception as e:
            print ("Cannot not process: \'%s\', no inheritance from TH1 or TGraph. No plotting.  "%(listin))
            #break
    if inputconf.boxpath:
        #print (idx)
        boxobjectlist = []
        print (inputconf)
        listsize = len(inputconf.boxpath)
        print (listsize)
        for jdx,listin in enumerate(inputconf.boxpath): #Take element [0] as it represents the object name to be processed
            print (jdx)
            print (listin)
            if jdx is 0: 
                #open file and decide between root files and text based files
                if listin.endswith(".root"):
                    boxobjectlist.append(ReadRootFile(listin))
                else:
                    print ("Read values from text based file %s"%(listin))
                    boxobjectlist.append(ReadData( listin, inputconf.skiprows ))
            else:
                try:
                    if boxobjectlist[jdx-1].InheritsFrom("TDirectoryFile"):
                        print ("TDirectoryFile")
                        boxobjectlist.append(GetFromTDirFile( listin, boxobjectlist[jdx-1] ))
                    elif boxobjectlist[jdx-1].InheritsFrom("TList"):
                        print ("TList")
                        boxobjectlist.append(GetFromTList( listin, boxobjectlist[jdx-1] ))
                    else:
                        print ("Unsupported class")
                        break
                except Exception as e:
                    print (e)
                    print ("Cannot not process: \'%s\', no inheritance from TObject "%(listin))
                    break
        print ("%s \n"%(boxobjectlist))
        try:
            if boxobjectlist[jdx].InheritsFrom("TH1"):
                print ("Storing TH1")
                    #Use inputconf for storing and replace path by TGraph
                #graphlist.append(inputconf._replace(boxpath=ROOT.TGraphAsymmErrors(boxobjectlist[jdx]),))
                boxgraph=ROOT.TGraphAsymmErrors(boxobjectlist[jdx])
            elif boxobjectlist[jdx].InheritsFrom("TGraph"):
                print ("Storing TGraph")
                #graphlist.append(inputconf._replace(boxpath=boxobjectlist[jdx],))
                boxgraph=boxobjectlist[jdx]
        #TODO: Add possibilty to add function (TF1)
        except Exception as e:
            #print (e)
            print ("Cannot not process: \'%s\', no inheritance from TH1 or TGraph. No plotting.  "%(listin))
            #break
    graphlist.append(inputconf._replace(path=returngraph,boxpath=boxgraph,))

print "Graph list:"
print ("%s \n"%(graphlist))
NrGraphs = len(graphlist)

DivPos = 0
DivPos2 = 0
Divisor = 0
DivGraph = None
for idx,inputdata in enumerate(graphlist):
    if inputdata.ratiobox or not inputdata.path:
        graph = inputdata.boxpath
    else:
        graph = inputdata.path
    print graph

    bins = graph.GetN()


    print bins
    if inputdata.divisor:
        print ("Divisor: %s"%(graph))
        DivPos = idx
        DivGraph = graph
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
fontsize = 20*config.scaling

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

NrColors =  ROOT.TColor.GetNumberOfColors()



markertable = design.LoadMarker(config.markertable)
LenMarker = len(markertable)


colortable = []
if config.usepalette:
    for i in range(NrGraphs):
        if config.palettecolors is 0:
            colortable.append(ROOT.TColor.GetColorPalette((i)*int(NrColors/(NrGraphs))+int(NrColors/(2*NrGraphs))))
        elif config.palettecolors is 1: 
            colortable.append(ROOT.TColor.GetColorPalette(i*int(NrColors/(NrGraphs)))) #Alternative color scheme with using lowest value
        elif config.palettecolors is 2: 
            colortable.append(ROOT.TColor.GetColorPalette((i+1)*int(NrColors/(NrGraphs)))) #Alternative color scheme with using highest value
        elif config.palettecolors is 3: 
            colortable.append(ROOT.TColor.GetColorPalette(i*int(NrColors/(NrGraphs-1)))) #Alternative color scheme with using maximum range
else:
    colortable = design.LoadColor(config.colortable)

LenColor = len(colortable)

########## General histogram
TCspectrum = ROOT.TCanvas("TCspectrum","",20,20,config.sizex,config.sizey)

MultiSpec = ROOT.TMultiGraph()

if config.xlog:
    ROOT.gPad.SetLogx()
if config.ylog:
    ROOT.gPad.SetLogy()



if config.legendtitle:
    TLeg = ROOT.TLegend(config.legendposition[0],config.legendposition[1],config.legendposition[0]+0.05,config.legendposition[1]-(len(inputdeque)+1)*(0.02*config.scaling))
else:
    TLeg = ROOT.TLegend(config.legendposition[0],config.legendposition[1],config.legendposition[0]+0.05,config.legendposition[1]-len(inputdeque)*(0.02*config.scaling))
TLeg.SetFillColor(0)
TLeg.SetMargin(0.075*config.scaling)
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
    if graphdata.boxpath:
        graphdata.boxpath.SetLineColor(colortable[idx%LenColor])
        graphdata.boxpath.SetFillStyle(0)
        graphdata.boxpath.SetLineWidth(int(1*config.scaling)) #May need improvement with config.scaling, but only accepts int
        MultiSpec.Add(graphdata.boxpath,"5")
    if graphdata.path:
        graphdata.path.SetMarkerColor(colortable[idx%LenColor])
        graphdata.path.SetLineColor(colortable[idx%LenColor])
        graphdata.path.SetLineWidth(int(1*config.scaling)) #May need improvement with config.scaling, but only accepts int
        graphdata.path.SetMarkerStyle(markertable[idx%LenMarker][0])
        graphdata.path.SetMarkerSize(markertable[idx%LenMarker][1]*config.scaling)
        MultiSpec.Add(graphdata.path,"P")
    if graphdata.skipmarker:
        TLeg.AddEntry("", ("  %s"%(' '.join(graphdata.legend))),"")
    elif graphdata.path:
        if graphdata.boxpath:
            TLeg.AddEntry(graphdata.path, ("  %s"%(' '.join(graphdata.legend))),"fp")
        else:
            TLeg.AddEntry(graphdata.path, ("  %s"%(' '.join(graphdata.legend))),"p")
    elif graphdata.boxpath:
        TLeg.AddEntry(graphdata.boxpath, ("  %s"%(' '.join(graphdata.legend))),"f")

MultiSpec.SetTitle("%s;%s;%s"%(' '.join(config.title),' '.join(config.xtitle),' '.join(config.ytitle)))

if config.xbinlabel:
    xlabels=' '.join(config.xbinlabel)
    xlabels=xlabels.split(";")
    #print (xlabels,len(xlabels))
    MultiSpec.GetXaxis().SetNdivisions(-len(xlabels))
    MultiSpec.GetXaxis().CenterLabels()
    for i in range(len(xlabels)):
        MultiSpec.GetXaxis().ChangeLabel(i+1,30,-1,-1,-1,-1,xlabels[i])


MultiSpec.GetXaxis().SetLabelOffset(config.labeloffsetx)

MultiSpec.Draw("A")

    
if config.xrange:
    MultiSpec.GetXaxis().SetRangeUser(config.xrange[0],config.xrange[1])
if config.yrange:
    MultiSpec.GetYaxis().SetRangeUser(config.yrange[0],config.yrange[1])
if config.morexlables:
    MultiSpec.GetXaxis().SetMoreLogLabels(True)
if config.moreylables:
    MultiSpec.GetYaxis().SetMoreLogLabels(True)
if config.legend:
    TLeg.Draw("")

if config.label:
    Label.Draw("")

ROOT.gPad.RedrawAxis()
ROOT.gPad.Modified()
ROOT.gPad.Update()



if not config.xratiorange:
    if not config.xrange:
        config.xratiorange=[ MultiSpec.GetXaxis().GetXmin(),  MultiSpec.GetXaxis().GetXmax()]
    else:
        config.xratiorange=config.xrange

#print config.xrange
#print config.xratiorange

########## Ratio graph


if  config.ratio or config.plusratio:
    TCratio = ROOT.TCanvas("TCratio","",20,20,config.sizex,config.sizey)
    MultiRatio = ROOT.TMultiGraph()

    TRatioLeg = ROOT.TLegend(config.ratiolegendposition[0],config.ratiolegendposition[1],config.ratiolegendposition[0]+0.25,config.ratiolegendposition[1]-(len(inputdeque)-1)*(0.02*config.scaling))
    TRatioLeg.SetFillColor(0)
    TRatioLeg.SetMargin(0.075*config.scaling)
    TRatioLeg.SetBorderSize(0)
    TRatioLeg.SetTextFont(font2use)
    TRatioLeg.SetTextSize(fontsize)

    TFconst1 = ROOT.TF1("TFconst1","1.",MultiSpec.GetXaxis().GetXmin(),  MultiSpec.GetXaxis().GetXmax())
    TGconst1 = ROOT.TGraph(TFconst1)
    TGconst1.SetLineColor(colortable[DivPos%LenColor])
    TGconst1.SetLineWidth(4)
    MultiRatio.Add(TGconst1,"l")
    for idx,graphdata in enumerate(graphlist):
        print graphdata
        if graphdata.skipratio:
            continue
        if not graphdata.ratiolegend:
            graphdata._replace(ratiolegend= graphdata.legend)
        if graphdata.divisor:
            TRatioLeg.AddEntry(TGconst1, ("  %s"%(' '.join(graphdata.ratiolegend))),"l")
            continue
        if graphdata.skipratiomarker:
            TRatioLeg.AddEntry("", ("  %s"%(' '.join(graphdata.ratiolegend))),"")
        else:
            TRatioLeg.AddEntry(graphdata.path, ("  %s"%(' '.join(graphdata.ratiolegend))),"p")
        
        if graphdata.ratiobox or not graphdata.path:
            ratiograph = CalcRatio(graphdata.boxpath,DivGraph)
        else:
            ratiograph = CalcRatio(graphdata.path,DivGraph)
        ratiograph.SetMarkerColor(colortable[idx%LenColor])
        ratiograph.SetLineColor(colortable[idx%LenColor])
        ratiograph.SetLineWidth(int(1*config.scaling)) #May need improvement with config.scaling, but only accepts int
        ratiograph.SetMarkerStyle(markertable[idx%LenMarker][0])
        ratiograph.SetMarkerSize(markertable[idx%LenMarker][1]*config.scaling)
        MultiRatio.Add(ratiograph,"P")


    MultiRatio.Draw("A")

    MultiRatio.GetXaxis().SetTitle("%s"%(' '.join(config.xtitle)))
    MultiRatio.SetTitle("%s_ratio"%(' '.join(config.xtitle)))
    
    if config.xratiorange:
        MultiRatio.GetXaxis().SetRangeUser(config.xratiorange[0],config.xratiorange[1])
    if config.yratiorange:
        MultiRatio.GetYaxis().SetRangeUser(config.yratiorange[0],config.yratiorange[1])

    if config.ratiolegend:
        TRatioLeg.Draw("same")

    ROOT.gPad.RedrawAxis()
    ROOT.gPad.Modified()
    ROOT.gPad.Update()

########## Plot spectrum + ratio

    if config.plusratio:
        TCplus = ROOT.TCanvas("TCplus","",20,20,config.sizex,config.sizey)
        TCplus.Divide(1,2)
        TCplus.cd(1).SetPad(0., config.pluspadratio, 1., 1.);  # top pad
        TCplus.cd(1).SetBottomMargin(0.001);
        TCplus.cd(2).SetPad(0., 0., 1., config.pluspadratio);  # bottom pad
        TCplus.cd(2).SetTopMargin(0);
        TCplus.cd(2).SetBottomMargin(config.bottommargin/config.pluspadratio); # for x-axis label
        
        TLegPlus = TLeg.Clone("TLegPlus")
        if config.legendtitle:  #Extend legend size due to shrinked canvas. NEED TO RESET Y1 instead of Y2, because TBox orders Y1 and Y2 by size and the legend position is defined by the top left corner (Y1 > Y2).
            TLegPlus.SetY1(config.legendposition[1]-((len(inputdeque)+1)*(0.02*config.scaling))/(1-config.pluspadratio))
        else:
            TLegPlus.SetY1(config.legendposition[1]-(len(inputdeque)*(0.02*config.scaling))/(1-config.pluspadratio))
        
    
        TCplus.cd(1)
        if config.xlog:
            ROOT.gPad.SetLogx()
        if config.ylog:
            ROOT.gPad.SetLogy()
        MultiSpec.Draw("AP")
        
        TLegPlus.Draw("")
        if config.label:
            Label.Draw("")
#        
        TCplus.cd(2)
        MultiRatio.GetXaxis().SetTitleOffset(config.titleoffsetx/config.pluspadratio)
        MultiRatio.Draw("AP")
        
        ROOT.gPad.RedrawAxis()

        
if config.save:
    SavePlots()

