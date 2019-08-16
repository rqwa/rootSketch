import ROOT

def LoadColor ( cnum ):

    print ("Load color table: %s "%(cnum))
    
    colortable = {
            0:[1,2,3,4,5,6,7,8,9],
            1:[ROOT.kBlue+2,ROOT.kOrange+10,ROOT.kTeal-6,ROOT.kMagenta+3,ROOT.kBlue+2,ROOT.kPink,ROOT.kOrange+10,ROOT.kTeal+3],
            2:[ROOT.kAzure+2,ROOT.kSpring-8,ROOT.kRed+1,ROOT.kOrange+1,ROOT.kAzure+2,ROOT.kSpring-8,ROOT.kRed+1,ROOT.kOrange+1],
            3:[ROOT.kBlue+1,ROOT.kRed+1,ROOT.kBlack,ROOT.kGreen+3,ROOT.kMagenta+1,ROOT.kOrange-1,ROOT.kCyan+2,ROOT.kYellow+2]
            }

    return colortable.get(cnum)

def LoadMarker ( mnum ):
    
    print ("Load marker table: %s "%(mnum))

    markertable = {
            0:[[20,1.0],[21,1.0],[34,1.4],[33,1.7],[29,1.6],[24,1.0],[25,1.0],[28,1.4],[27,1.7],[30,1.6]],
            1:[[33,1.7],[8,1.0],[21,1.0],[34,1.4],[22,1.2],[23,1.2],[29,1.6],[21,1.0]]
            }


    return markertable.get(mnum)
