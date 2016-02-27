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

FillValues = Read_Data(filelist[0])

#print FillValues

########## General histogram
TC1 = ROOT.TCanvas("TC1","",20,20,config.sizex,config.sizey)
TH1Plot = ROOT.TH1D("TH1Plot",config.title,len(NBins),np.array(BinEdges,'d'))

if config.xlog:
    ROOT.gPad.SetLogx()
if config.ylog:
    ROOT.gPad.SetLogy()

if config.tgrapherrors:
    TGE1 = ROOT.TGraphErrors(len(Bins),np.array(Bins,'d'),unumpy.nominal_values(FillValues),ex,unumpy.std_devs(FillValues))
    TGE1.SetMarkerStyle(33)
    TGE1.SetMarkerColor(ROOT.kAzure+2)
    TGE1.SetMarkerSize(1.8)
    if ( len(BinEdges)-1 != len(FillValues) ) :
        sys.exit( "Size of binning and number of values don't agree. Stopping macro!")
else:
    TH1Plot.SetContent(unumpy.nominal_values(FillValues))
    TH1Plot.SetError(unumpy.std_devs(FillValues))
    TH1Plot.SetMarkerColor(ROOT.kAzure+2)
    TH1Plot.SetMarkerStyle(33)
    TH1Plot.SetMarkerSize(1.8)
    if ( len(BinEdges) != len(FillValues) ) :
        sys.exit( "Size of binning and number of values don't agree. Stopping macro!")

TLeg = ROOT.TLegend(0.5,0.5,0.8,0.45)
TLeg.SetFillColor(0)
TLeg.SetMargin(0.00)
TLeg.SetBorderSize(0)

TLeg.AddEntry(TGE1, ("  %s"%(' '.join(filelegend[0]))))

TH1Plot.GetXaxis().SetTitle(config.xtitle)
TH1Plot.GetYaxis().SetTitle(config.ytitle)
if config.xrange:
    TH1Plot.GetXaxis().SetRangeUser(config.xrange[0],config.xrange[1])
if config.yrange:
    TH1Plot.GetYaxis().SetRangeUser(config.yrange[0],config.yrange[1])


########## Plotting

TH1Plot.DrawCopy()
if config.tgrapherrors:
    try:
        TGE1.Draw("sameP")
    except:
        pass
TLeg.Draw("")

#wait()

TC1.SaveAs("%s.pdf"%(config.name))
TC1.SaveAs("%s.png"%(config.name))

