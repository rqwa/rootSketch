#!/usr/bin/env python

#Script to plot data, the data and the related config is loaded by a file passed to the script.
#The options for the config are read via argparse in the following:
#All options not specific for input file have to be in the first line of the file
#All files to plot, with their corresponding options have to written from the second line on

import sys
import ROOT
import uncertainties as unc
from uncertainties import unumpy
import numpy as np
from rootpy.interactive import wait
from rootpy.plotting import Hist
import argparse 

def Read_Data( datafile ):
    
    Converters = dict.fromkeys(range(int(datafile[1])), unc.ufloat_fromstr)
    
    Value0 = np.array(unc.ufloat(0.,0.), dtype=object) #Adding underflow bin
    Values = np.loadtxt(datafile[0],converters=Converters, dtype=object)
    if config.tgrapherrors:
        FillValues = Values
    else:
        FillValues = np.hstack((Value0,Values))
    #print FillValues

    return FillValues
fileparser = argparse.ArgumentParser()
fileparser.add_argument("-f", "--filename")
fileparser.add_argument("-nc", "--numbercolumns")
fileparser.add_argument("-ld", "--legend", default="", nargs='+')
fileparser.add_argument("-rld", "--ratiolegend", default="", nargs='+')
fileparser.add_argument("-nm", "--nomarker", action="store_true")
fileparser.add_argument("-rd", "--ratiodivisor", action="store_true") #Ratio can only be calculated with exactly one input variable chosen




parser = argparse.ArgumentParser()
parser.add_argument("-fb", "--filebining")
parser.add_argument("-xt", "--xtitle", default="", nargs='+')
parser.add_argument("-yt", "--ytitle", default="", nargs='+')
parser.add_argument("-t", "--title", default="")
parser.add_argument("-xr", "--xrange", nargs=2, type=float)
parser.add_argument("-yr", "--yrange", nargs=2, type=float)
parser.add_argument("-tge", "--tgrapherrors", action="store_true")
parser.add_argument("-bc", "--bincenter") #This option will only work with tgrapherrors
parser.add_argument("--xlog", action="store_true")
parser.add_argument("--xrlog", action="store_true")
parser.add_argument("--ylog", action="store_true")
parser.add_argument("--yrlog", action="store_true")
parser.add_argument("-sx", "--sizex", default=1200)
parser.add_argument("-sy", "--sizey", default=900)
parser.add_argument("-n", "--name", default="plot")
parser.add_argument("-s", "--save", action="store_true")
parser.add_argument("-ms", "--markersize", default=1., type=float)
parser.add_argument("-w", "--wait", action="store_true")
parser.add_argument("-lp", "--legendposition", nargs =2, default=[0.5,0.8], type=float) #Defines top left corner of TLegend
parser.add_argument("-lm", "--leftmargin", default=0.08, type=float)
parser.add_argument("-rm", "--rightmargin", default=0.04, type=float)
parser.add_argument("-tm", "--topmargin", default=0.04, type=float)
parser.add_argument("-bm", "--bottommargin", default=0.1, type=float)
parser.add_argument("-tox", "--titleoffsetx", default=1., type=float)
parser.add_argument("-toy", "--titleoffsety", default=1., type=float)
parser.add_argument("-ac", "--alternativecolors", action="store_true")
parser.add_argument("-lt", "--legendtitle", nargs='+')
parser.add_argument("-lb", "--label", nargs='+')
parser.add_argument("-lbx", "--labelbox", nargs=4, default=[0.15,0.25,0.6,0.15], type=float)
parser.add_argument("-r", "--ratio", action="store_true")
parser.add_argument("-pr", "--plusratio", action="store_true")
parser.add_argument("-mxl", "--morexlables", action="store_true")
parser.add_argument("-myl", "--moreylables", action="store_true")
parser.add_argument("-rl", "--ratiolegend", action="store_true")
parser.add_argument("-xrr", "--xratiorange", nargs=2, type=float)
parser.add_argument("-yrr", "--yratiorange", nargs=2, type=float)
parser.add_argument("-rbe", "--ratiobinomialerr", action="store_true")


#parser.add_argument("-", "--")

filelist = ()
filelegend = ()
ratiolegend = ()
skipmarker = ()

ratiobase = -1
counter = 0

filecheck = ['-f ','--filename ']

with open(sys.argv[1],'r') as f:    #path to file with config of plot
    for li in f:
        if any ([x in li for x in filecheck]):
            lineargs = fileparser.parse_args(li.split())
            filelist +=(lineargs.filename, lineargs.numbercolumns),
            filelegend +=(lineargs.legend),
            ratiolegend +=(lineargs.ratiolegend),
            skipmarker +=(lineargs.nomarker),
            if lineargs.ratiodivisor:
                ratiobase = counter
            counter += 1
        else:
            config_line = li


config = parser.parse_args(config_line.split())

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

if config.alternativecolors:
    markertable = {0:[ROOT.kBlue+2,33,1.7],1:[ROOT.kOrange+10,8,1.0],2:[ROOT.kTeal-6,21,1.0],3:[ROOT.kMagenta+3,34,1.4],4:[ROOT.kBlue+2,22,1.2],5:[ROOT.kPink,23,1.2],6:[ROOT.kOrange+10,29,1.6],7:[ROOT.kTeal+3,21,1.0]}
else:
    markertable = {0:[ROOT.kAzure+2,33,1.7],1:[ROOT.kSpring-8,8,1.0],2:[ROOT.kRed+1,21,1.0],3:[ROOT.kOrange+1,34,1.4],4:[ROOT.kAzure+2,22,1.2],5:[ROOT.kSpring-8,23,1.2],6:[ROOT.kRed+1,29,1.6],7:[ROOT.kOrange+1,21,1.0]}

#print config
#print filelist

########## General input

FileBinning = open(config.filebining,'r')

BinEdges = []
for li in FileBinning:
    splitline = li.split()
    BinEdges.append(float(splitline[0]))
    #print splitline[0]

NBins = BinEdges[0:len(BinEdges)-1]

Bins = []
Ex = []

for i in range(len(BinEdges)-1):
    Bins.append((BinEdges[i]+BinEdges[i+1])/2)

ex = np.zeros(len(NBins))

#print len(BinEdges)

########## Data point input

#FillValues = np.zeros((len(filelist),len(BinEdges)-1), dtype=object)
FillValues = []

for i in range (len(filelist)):
    FillValues.append(Read_Data(filelist[i]))


########## General histogram
TC1 = ROOT.TCanvas("TC1","",20,20,config.sizex,config.sizey)
if config.tgrapherrors:
    TH1Plot = ROOT.TH1D("TH1Plot",config.title,len(NBins),np.array(BinEdges,'d'))
else:
    THSt1 = ROOT.THStack("THStack1",config.title)
    TH1Plot = []

if config.ratio or config.plusratio:
    THSRatio = ROOT.THStack("THSRatio","%s_ratio"%(config.title))

if config.xlog:
    ROOT.gPad.SetLogx()
if config.ylog:
    ROOT.gPad.SetLogy()

if config.legendtitle:
    TLeg = ROOT.TLegend(config.legendposition[0],config.legendposition[1],config.legendposition[0]+0.05,config.legendposition[1]-(len(filelist)+1)*(0.03*config.markersize))
else:
    TLeg = ROOT.TLegend(config.legendposition[0],config.legendposition[1],config.legendposition[0]+0.05,config.legendposition[1]-len(filelist)*(0.03*config.markersize))
TLeg.SetFillColor(0)
TLeg.SetMargin(0.00)
TLeg.SetBorderSize(0)
TLeg.SetTextFont(font2use)
TLeg.SetTextSize(fontsize)
if config.legendtitle:
    TLeg.AddEntry("", "  %s"%(' '.join(config.legendtitle)),"")

if config.label:
    print config.labelbox
    Label = ROOT.TLegend(config.labelbox[0],config.labelbox[1],config.labelbox[2],config.labelbox[3])
    Label.SetFillColor(0)
    Label.SetMargin(0.00)
    Label.SetBorderSize(0)
    Label.SetTextFont(font2use)
    Label.SetTextSize(fontsize)
    Label.AddEntry("","%s"%(' '.join(config.label)),"")
    

for i in range(0,len(FillValues)):
    if config.tgrapherrors:
        TGE1 = ROOT.TGraphErrors(len(Bins),np.array(Bins,'d'),unumpy.nominal_values(FillValues[i]),ex,unumpy.std_devs(FillValues[i]))
        TGE1.SetMarkerColor(markertable.get(i)[0])
        TGE1.SetMarkerStyle(markertable.get(i)[1])
        TGE1.SetMarkerSize(markertable.get(i)[2]*config.markersize)
        if ( len(BinEdges)-1 != len(FillValues[i]) ) :
            sys.exit( "Size of binning and number of values don't agree. Stopping macro!")
        TLeg.AddEntry(TGE1, ("  %s"%(' '.join(filelegend[i]))))
    else:
        TH1Plot.append(ROOT.TH1D("TH1Plot","%i"%(i),len(NBins),np.array(BinEdges,'d')))
        TH1Plot[i].SetContent(unumpy.nominal_values(FillValues[i]))
        TH1Plot[i].SetError(unumpy.std_devs(FillValues[i]))
        TH1Plot[i].SetMarkerColor(markertable.get(i)[0])
        TH1Plot[i].SetMarkerStyle(markertable.get(i)[1])
        TH1Plot[i].SetMarkerSize(markertable.get(i)[2]*config.markersize)
        if ( len(BinEdges) != len(FillValues[i]) ) :
            sys.exit( "Size of binning and number of values don't agree. Stopping macro!")
        THSt1.Add(TH1Plot[i])
        if skipmarker[i]:
            TLeg.AddEntry("", ("  %s"%(' '.join(filelegend[i]))),"")
        else:
            TLeg.AddEntry(TH1Plot[i], ("  %s"%(' '.join(filelegend[i]))))
    
    
if config.tgrapherrors:
    TH1Plot.GetXaxis().SetTitle(config.xtitle)
    TH1Plot.GetYaxis().SetTitle(config.ytitle)
    if config.xrange:
        TH1Plot.GetXaxis().SetRangeUser(config.xrange[0],config.xrange[1])
    if config.yrange:
        TH1Plot.GetYaxis().SetRangeUser(config.yrange[0],config.yrange[1])
else:
    THSt1.Draw("nostack")
    THSt1.GetXaxis().SetTitle("%s"%(' '.join(config.xtitle)))
    THSt1.GetYaxis().SetTitle("%s"%(' '.join(config.ytitle)))
    if config.xrange:
        THSt1.GetXaxis().SetRangeUser(config.xrange[0],config.xrange[1])
        print "set x-range"
    if config.yrange:
        THSt1.SetMinimum(config.yrange[0])
        THSt1.SetMaximum(config.yrange[1])
        print "set y-range"
    if config.morexlables:
        THSt1.GetXaxis().SetMoreLogLabels(True)


########## Plot spectrum

if config.tgrapherrors:
    try:
        TH1Plot.DrawCopy()
        TGE1.Draw("sameP")
    except:
        pass
else:
    THSt1.Draw("nostack")

#TLeg = TC1.BuildLegend()
#TLeg.AddEntry("","test", "")
TLeg.Draw("")

if config.label:
    Label.Draw("")


if config.save:
    TC1.SaveAs("plots/%s.pdf"%(config.name))
    TC1.SaveAs("plots/%s.png"%(config.name))


########## Ratio histogram

THSRatio = ROOT.THStack("THStackRatio",config.title)

TRatioLeg = ROOT.TLegend(config.legendposition[0],config.legendposition[1],config.legendposition[0]+0.05,config.legendposition[1]-len(filelist)*(0.03*config.markersize))
TRatioLeg.SetFillColor(0)
TRatioLeg.SetMargin(0.00)
TRatioLeg.SetBorderSize(0)
TRatioLeg.SetTextFont(font2use)
TRatioLeg.SetTextSize(fontsize)



if  config.ratio or config.plusratio:
    TC2 = ROOT.TCanvas("TC2","",20,20,config.sizex,config.sizey)
    for i in range(0,len(FillValues)):
        print i
        THDiv=TH1Plot[i].Clone()
        THDiv.Sumw2
        if i == ratiobase:
            print "skip event "
            continue
        if config.ratiobinomialerr:
            THDiv.Divide(TH1Plot[i],TH1Plot[ratiobase],1.,1.,"B")
            print "Bionmial errors used"
        else:
            THDiv.Divide(TH1Plot[i],TH1Plot[ratiobase])
        THSRatio.Add(THDiv)

THSRatio.Draw("nostack")
THSRatio.GetXaxis().SetTitle("%s"%(' '.join(config.xtitle)))
if config.xratiorange:
    THSRatio.GetXaxis().SetRangeUser(config.xratiorange[0],config.xratiorange[1])
    print "set x-range"

if config.yratiorange:
    THSRatio.SetMinimum(config.yratiorange[0])
    THSRatio.SetMaximum(config.yratiorange[1])
    print "set y-range"

TRatioLeg.AddEntry(TH1Plot[i], ("  %s"%(' '.join(ratiolegend[i]))))

########## Plot ratio

if config.ratio:
    THSRatio.Draw("nostack")
if config.ratiolegend:
    TRatioLeg.Draw("")

if config.save:
    TC2.SaveAs("plots/%s_ratio.pdf"%(config.name))
    TC2.SaveAs("plots/%s_ratio.png"%(config.name))

if config.wait:
    wait()
