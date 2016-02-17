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
import argparse 

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadLeftMargin(0.06)
ROOT.gStyle.SetPadRightMargin(0.05)
ROOT.gStyle.SetPadTopMargin(0.06)
ROOT.gStyle.SetPadBottomMargin(0.1)

ConfigFile = open(sys.argv[1],'r')  #path to file with config of plot

for li in ConfigFile:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename")
    parser.add_argument("-fb", "--filebining")
    parser.add_argument("-nc", "--numbercolumns")
    parser.add_argument("-xt", "--xtitle")
    parser.add_argument("-yt", "--ytitle")
    parser.add_argument("-xr", "--xrange", nargs=2, type=float)
    parser.add_argument("-yr", "--yrange", nargs=2, type=float)
    parser.add_argument("-tge", "--tgrapherrors", action="store_true")
    parser.add_argument("-bc", "--bincenter") #This option will only work with tgrapherrors
    parser.add_argument("--xlog", action="store_true")
    parser.add_argument("--ylog", action="store_true")
    parser.add_argument("-sx", "--sizex", default=1200)
    parser.add_argument("-sy", "--sizey", default=900)
    #parser.add_argument("-", "--")

    config = parser.parse_args(li.split())
    
    
Converters = dict.fromkeys(range(int(config.numbercolumns)), unc.ufloat_fromstr)

FileBinning = open(config.filebining,'r')

BinEdges = []
for li in FileBinning:
    splitline = li.split()
    BinEdges.append(float(splitline[0]))
    print splitline[0]

Bins = BinEdges[0:len(BinEdges)-1]

ex = np.zeros(len(Bins))

Value0 = np.array(unc.ufloat(0.,0.), dtype=object)
Values = np.loadtxt(config.filename,converters=Converters, dtype=object)

FillValues = np.hstack((Value0,Values))
print FillValues

TC1 = ROOT.TCanvas("TC1","",20,20,config.sizex,config.sizey)
TH1Plot = ROOT.TH1D("H1Plot","Purity",len(Bins),np.array(BinEdges,'d'))


if config.xlog:
    ROOT.gPad.SetLogx()

TH1Plot.SetContent(unumpy.nominal_values(FillValues))
TH1Plot.SetError(unumpy.std_devs(FillValues))
TH1Plot.GetXaxis().SetTitle(config.xtitle)
if config.xrange:
    TH1Plot.GetXaxis().SetRangeUser(config.xrange[0],config.xrange[1])
if config.yrange:
    TH1Plot.GetYaxis().SetRangeUser(config.yrange[0],config.yrange[1])

if ( len(BinEdges) - len(Values) !=  1 ) :
    sys.exit( "Size of binning and number of values don't agree. Stopping macro!")

TH1Plot.Draw()

wait()

