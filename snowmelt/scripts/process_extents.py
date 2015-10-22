# Original imports, will try to cull these a bit.
import os
import sys
import datetime
import gzip
import numpy as np
import shutil
import subprocess
import tarfile
import timeit
from collections import namedtuple

from osgeo import gdal,osr
from osgeo.gdalconst import *

# Imports from refactoring.
from optparse import OptionParser

# Update our python path, so python knows where to find the snowmelt module.
SNOW_ROOT = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, SNOW_ROOT)

import snowmelt
from snowmelt import config

# Our main script.
def main():
    
    def verbose_print(to_print):
        if options.verbose:
            print to_print

    # Track our script run time.
    start = timeit.default_timer()

    # Create an OptionParser to handle any command-line arguments and options.
    usage = ("usage: %prog [options] division district ")
    parser = OptionParser(usage=usage)

    # Command line options added here.
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
        default=False)
    parser.add_option('-d', '--date', dest='process_date', 
        default=datetime.datetime.now().strftime('%Y%m%d'), 
        help='Date should be in YYYYMMDD format.')
    parser.add_option('-t', '--dataset', dest='dataset_type', default='zz')
    parser.add_option('-a', '--all', dest='all_extents', action='store_true',
        default=False)

    options, args = parser.parse_args()

    if (not options.all_extents) and len(args) != 2:
        print "Error: Script requires two arguments\n"
        parser.print_help()
        sys.exit(1)

    # Grab extents based on division and district inputs.
    division, district = args
    try:
        extents_list = config.EXTENTS[division][district]
    except KeyError:
        print ('Could not find extents list for '
               'Division "{0}", District "{1}"').format(division, district)
        sys.exit(1)
    verbose_print('Extents list:\n' + '\n'.join([str(ext) for ext in extents_list]))

    # Parse out our processing date.
    try:
        options.process_date = datetime.datetime.strptime(options.process_date,'%Y%m%d')
    except:
        print 'Couldn\'t parse time input.  Please use YYYYMMDD format.'
        sys.exit(1)

    verbose_print(options.process_date)

    # Run the actual grid processing.
    snowmelt.process_extents(division, options.process_date, 
                             options.dataset_type, extents_list)

    finish = timeit.default_timer()
    print 'Finished {0} {1}  (Duration = {2})'.format(
        os.path.basename(__file__),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        str(datetime.timedelta(seconds=finish - start))
    )


if __name__ == '__main__':
    main()
