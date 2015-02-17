maru zoqueta

# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 12:58:44 2012

@author: markel
"""

import numpy as np
import netCDF4 as ncdf
import sys, os, time, calendar
from datetime import datetime, timedelta
from optparse import OptionParser
from collections import Counter

from netcdf_utils import copy_netcdf_structure, nctime2timeobj, get_nc_freq
#
# Flags
#
parser = OptionParser()
parser.set_defaults(quiet=False,singlerec=False)

parser.add_option(
        "--verbose", action="store_true", dest="verbose", default=False,
        help="Increase verbosity"
)
parser.add_option(
        "-v", "--variable", dest="variable",
        help="Main variable name"
)
parser.add_option(
        "-i", "--ifile", dest="ifile",
        help="Input file name"
)
parser.add_option(
        "-o", "--ofile", dest="ofile",
        help="Output file name"
)
parser.add_option(
        "-d", "--delta", dest="delta",
        help="""Time interval between the 2 time bonds "[integer] [units]".
        available units hours, days"""
)
parser.add_option(
        "-p", "--place", dest="place",
        help="Placement of the interval with respect to the timestep: forward, backward, center"
)
parser.add_option(
        "-s", "--shifttime", dest="displace",
        help="Displace the timesteps before adding the time_bonds"
)
parser.add_option(
        "-c", "--cell-methods", dest="cmethods",
        help="Cell methods attribute: maximum, minimum, mean, etc."
)
(opt, args) = parser.parse_args()
#
# Functions and classes
#
def get_nc_freq(inc):
    time = inc.variables["time"]
    timeobjs = ncdf.num2date(time[:], time.units, time.calendar)
    deltas = timeobjs[1:] - timeobjs[0:-1]
    dcount = Counter(deltas)
    freqdelta = dcount.most_common(1)[0][0]
    return freqdelta
    
def interval2timedelta(interval):
    int_arg, int_units = interval.split(" ")
    if int_units == "hours":
        tdelta = timedelta(hours = int(int_arg))
    elif int_units == "days":
        tdelta = timedelta(days = int(int_arg))
    else:
        print "Deltas with %s time units are not supported" % (int_units)
    return tdelta

def add_time_bonds(ifile, ofile, var, interval, place, cell_methods): 
    inc = ncdf.Dataset(opt.ifile, "r")
    freq =  get_nc_freq(inc)
    inc.close()
    if opt.verbose:
        print "Frequency of the time axis is %s" % (freq)
    onc = copy_netcdf_structure(ifile, ofile, variables="all")
    #
    # Add attributes to the variable and time
    #
    oncvar = onc.variables[var]
    oncvar.cell_methods = "time: %s" % (cell_methods)
    onctime = onc.variables["time"]
    onctime.bounds = "time_bnds"
    #
    # Create time_bnds dimension and variable
    #
    onc.createDimension("tbnds", 2)
    onctb = onc.createVariable("time_bnds", "double", ["time", "tbnds"])
    onctb.units = onctime.units
    onctb.long_name = "time bounds"
    onc.sync()
    #
    # Compute time_bnds values
    #
    #
    # First, handle special cases (month, season)
    #
    if interval.split(" ")[1] == "months":
        dateobjs = ncdf.num2date(onctime[:], onctime.units, onctime.calendar)
        nt = len(dateobjs)
        if place == "backward":
            dateobjs_b = [dateobjs[i].replace(day = 1, hour = 0) for i in range(0, nt)]
            datenums_b = ncdf.date2num(dateobjs_b, onctime.units, calendar='standard')
            datenums_f = onctime[:]
        elif place == "forward":
            datenums_b = onctime[:]
            dateobjs_b = dateobjs
            dateobjs_f = [dateobjs[i].replace(day = calendar.monthrange(dateobjs[i].day)[1], hour = 0 ) for i in range(0, nt)]
            datenums_f = ncdf.date2num(dateobjs_f, onctime.units, calendar='standard')

        elif place == "center":
            dateobjs_f = dateobjs + tdelta/2
            datenums_f = ncdf.date2num(dateobjs_f, onctime.units, calendar='standard')
            dateobjs_b = dateobjs - tdelta/2
            datenums_b = ncdf.date2num(dateobjs_b, onctime.units, calendar='standard')   
    elif interval.split(" ")[1] == "seasons":
    #
    # Now, generic intervals
    #
    else:
        dateobjs = ncdf.num2date(onctime[:], onctime.units, onctime.calendar)
        tdelta = interval2timedelta(interval)
        if place == "backward":
            dateobjs_b = dateobjs - tdelta
            datenums_b = ncdf.date2num(dateobjs_b, onctime.units, calendar='standard')
            datenums_f = onctime[:]
        elif place == "forward":
            dateobjs_f = dateobjs + tdelta
            datenums_f = ncdf.date2num(dateobjs_f, onctime.units, calendar='standard')
            datenums_b = onctime[:]
        elif place == "center":
            dateobjs_f = dateobjs + tdelta/2
            datenums_f = ncdf.date2num(dateobjs_f, onctime.units, calendar='standard')
            dateobjs_b = dateobjs - tdelta/2
            datenums_b = ncdf.date2num(dateobjs_b, onctime.units, calendar='standard')

    onctb[:] = np.transpose(np.vstack([datenums_b, datenums_f]))
    onc.sync()
#
# End functions and classes
#
###############################################################################
#
# Main program
#
if opt.verbose:
    print opt

if os.path.exists(opt.ofile):
    print "%s, already exists, refusing to overwrite" % (opt.ofile)
    sys.exit(0)

add_time_bonds(opt.ifile, opt.ofile, opt.variable, opt.delta, opt.place, opt.cmethods)
    
