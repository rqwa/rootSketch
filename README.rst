===========
rootSketch
===========

rootSketch should be a macro to create root plots with the help of an easily editbale and readable macro.
The intention is too create 


Usage
===========

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

   - .root files, including a path inside the .root file (i.e. file.root tdirectoryname tlistname histogramname)
   - Multicolumn text files (Files with 2 to 4 columns will be interpreted as TGraphErrors, files with 6 columns will be interpreted as TGraphAsymmErrors
   - unumpy arrays stored into text format

Options
============

Flags
-----

For the time being please refer to the argparse commands in the source code.

Color and marker tables
-----------------------

A few preset of color and marker tables are stored in designtables.py feel free to add your own.

Contributing
============

Any feedback, help, bug reports, and commits are welcome.


