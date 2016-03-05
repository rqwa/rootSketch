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

    return FillValues

font2use = 43;
fontsize = 20;

ROOT.gStyle.SetTextFont(font2use)
ROOT.gStyle.SetTitleFontSize(fontsize)

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadLeftMargin(0.08)
ROOT.gStyle.SetPadRightMargin(0.04)
ROOT.gStyle.SetPadTopMargin(0.06)
ROOT.gStyle.SetPadBottomMargin(0.1)
ROOT.gStyle.SetTitleOffset(1.1,"y")

markertable = {0:[ROOT.kAzure+2,33,1.8],1:[ROOT.kSpring-8,8,1.0],2:[ROOT.kRed+1,21,1.0],3:[ROOT.kOrange+1,34,1.2],4:[ROOT.kAzure+2,22,1.2],5:[ROOT.kSpring-8,23,1.2],6:[ROOT.kRed+1,29,1.6],7:[ROOT.kOrange+1,21,1.0]}


fileparser = argparse.ArgumentParser()
fileparser.add_argument("-f", "--filename")
fileparser.add_argument("-nc", "--numbercolumns")
fileparser.add_argument("-ld", "--legend", default="", nargs='+')


parser = argparse.ArgumentParser()
parser.add_argument("-fb", "--filebining")
parser.add_argument("-xt", "--xtitle", default="")
parser.add_argument("-yt", "--ytitle", default="")
parser.add_argument("-t", "--title", default="")
parser.add_argument("-xr", "--xrange", nargs=2, type=float)
parser.add_argument("-yr", "--yrange", nargs=2, type=float)
parser.add_argument("-tge", "--tgrapherrors", action="store_true")
parser.add_argument("-bc", "--bincenter") #This option will only work with tgrapherrors
parser.add_argument("--xlog", action="store_true")
parser.add_argument("--ylog", action="store_true")
parser.add_argument("-sx", "--sizex", default=1200)
parser.add_argument("-sy", "--sizey", default=900)
parser.add_argument("-n", "--name", default="plot")
parser.add_argument("-s", "--save", action="store_true")
parser.add_argument("-ms", "--markersize", default=1., type=float)
parser.add_argument("-w", "--wait", action="store_true")
parser.add_argument("-lp", "--legendposition", nargs =2, default=[0.5,0.8], type=float) #Defines top left corner of TLegend
#parser.add_argument("-", "--")

filelist = ()
filelegend = ()

with open(sys.argv[1],'r') as f:    #path to file with config of plot
    config_line = next(f)
    for li in f:
        lineargs = fileparser.parse_args(li.split())
        filelist +=(lineargs.filename, lineargs.numbercolumns),
        filelegend +=(lineargs.legend),

config = parser.parse_args(config_line.split())

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


if config.xlog:
    ROOT.gPad.SetLogx()
if config.ylog:
    ROOT.gPad.SetLogy()


TLeg = ROOT.TLegend(config.legendposition[0],config.legendposition[1],config.legendposition[0]+0.05,config.legendposition[1]-len(filelist)*(0.03*config.markersize))
TLeg.SetFillColor(0)
TLeg.SetMargin(0.00)
TLeg.SetBorderSize(0)
TLeg.SetTextFont(font2use)
TLeg.SetTextSize(fontsize*config.markersize)

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
    THSt1.GetXaxis().SetTitle(config.xtitle)
    THSt1.GetYaxis().SetTitle(config.ytitle)
    if config.xrange:
        THSt1.GetXaxis().SetRangeUser(config.xrange[0],config.xrange[1])
        print "set x-range"
    if config.yrange:
        THSt1.SetMinimum(config.yrange[0])
        THSt1.SetMaximum(config.yrange[1])
        print "set y-range"


########## Plotting

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

if config.wait:
    wait()

if config.save:
    TC1.SaveAs("plots/%s.pdf"%(config.name))
    TC1.SaveAs("plots/%s.png"%(config.name))

