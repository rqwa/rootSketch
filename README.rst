===========
rootSketch
===========

rootSketch should be a macro to create root plots with the help of an easily editbale and readable config file.
As the name suggests the purpose of rootSketch is to create plots in a fast way, which show all relevant points.
It is not designed to create highly customized plots, even though sketches can be quite nice.


Usage
===========

The macro runs with the following command. The created plots are stored in the folder ``plots``.

::

$ python rootSketch plotconfig


Config file
===========

The config file consits of two parts:

1. The general config containing all settings for the plot.
   The settings can be written in multiple lines of the config file and must start with an option flag (i.e -s to save the plots).
   General options written into lines with files to read, will not work.
2. Lines containing one of the following flags:

   - -f
   - --filename
   - -bf
   - --boxfilename

   Each line containing one of the above flags will be interpreted as input file.
   All options related to this file, have to be written into the same line.


Input files
===========

Currently the following input files are supported:

   - .root files, including a path inside the .root file (i.e. file.root TdirectoryName TlistName HistogramName)
     
     - For classes based on THnBase it is possible to access the projection (The last argument needs to be the int value of the axis for the projection)
     - Graphs/histograms can also be accessed if they are stored inside a TCanvas 
   - Multicolumn text files (Files with 1 column will be interpreted as TGraphErrors, but need an addiotional binning file, files with 2 to 4 columns will be interpreted as TGraphErrors, files with 6 columns will be interpreted as TGraphAsymmErrors
   - numpy arrays with uncertainties from the uncertainty package stored into text format

Options
============

A commented config is available in ``example.cfg``. 

Flags
-----

A list of all available flags and a short description is provided by calling ``plot_data1D.py`` with ``-h`` or ``--help``.

Color and marker tables
-----------------------

A few preset of color and marker tables are stored in designtables.py feel free to add your own.

Contributing
============

Any feedback, help, bug reports, and commits are welcome.


