import sys
import os
import re
import datetime
import subprocess

from optparse import OptionParser

# Update our python path, so python knows where to find the snowmelt module.
SNOW_ROOT = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, SNOW_ROOT)

BACKFILL_CMD = os.path.join(SNOW_ROOT, 'bash', 'backfill_noaa.sh')

import snowmelt
from snowmelt import config

DATE_REGEX = re.compile(r'^(?P<start_date>\d{8})-(?P<end_date>\d{8})$')
# ftp://sidads.colorado.edu/DATASETS/NOAA/G02158/unmasked/2013/03_Mar/SNODAS_unmasked_20130326.tar
WGET_BASE = 'ftp://sidads.colorado.edu/DATASETS/NOAA/G02158/{masked}/'
WGET_PATH = '{year}/{month_num}_{month_name}/SNODAS_{infix}{year}{month_num}{day}.tar'


def main():

    def parse_date(date_string):
        return datetime.datetime.strptime(date_string,'%Y%m%d')

    # Create an OptionParser to handle any command-line arguments and options.
    usage = ("usage: %prog [options]")
    parser = OptionParser(usage=usage)

    parser.add_option('-d', '--date', dest='process_date',
        default=datetime.datetime.now().strftime('%Y%m'),
        help='Date should be in YYYYMMDD format. Can also provide a range '
             'of dates with YYYYMMDD-YYYYMMDD format.')

    options, args = parser.parse_args()

    # Parse out our processing date(s).
    process_dates = []

    match = DATE_REGEX.match(options.process_date)
    if match is not None:
        # Build out a list of dates to process.
        match_dict = match.groupdict()
        process_date = parse_date(match_dict['start_date'])
        end_date = parse_date(match_dict['end_date'])
        while process_date <= end_date:
            process_dates += [process_date]
            process_date += datetime.timedelta(days=1)
    else:
        process_dates = [parse_date(options.process_date)]

    if process_dates == []:
        print 'No dates to process, exiting.'
        sys.exit(1)

    # Process the data for this date.
    for process_date in process_dates:
        process_date_ymd = process_date.strftime('%Y%m%d')

        archive_target = snowmelt.get_src_dir_by_date(process_date)
        # Use 'us' prefix for dates before January 24, 2011.
        ds_type = 'zz'
        if process_date < datetime.datetime(2011, 1, 24, 0, 0):
            ds_type = 'us'

        # Check for missing source files.
        snodas_src_files = [
            f.format(ds=ds_type, ymd=process_date_ymd) for f in snowmelt.SNODAS_FILENAME_LIST
        ]

        # Don't check for temperature, some early datasets are missing it.
        snodas_src_files.pop(2)

        missing_data = False
        for filename in snodas_src_files:
            if not os.path.isfile(os.path.join(archive_target, filename + '.grz')):
                print 'Missing source data file: {0}'.format(filename)
                missing_data = True
                break
        
        # If all source files exist, move on to next date.
        if not missing_data:
            print 'All source data already present for {0}'.format(process_date_ymd)
            continue

        # Build up our command line bash call for this date.
        path_args = {
            'year': process_date.year,
            'month_num': process_date.strftime('%m'),
            'month_name': process_date.strftime('%b'),
            'day': process_date.strftime('%d'),
            'masked': 'unmasked',
            'infix': 'unmasked_'
        }
        if process_date < datetime.datetime(2011, 1, 24, 0, 0):
            path_args['masked'] = 'masked'
            path_args['infix'] = ''
        wget_target = (WGET_BASE + WGET_PATH).format(**path_args)
        wget_file = os.path.basename(wget_target)
        print 'Fetching data from:', wget_target
        print 'Source data will be stored here:', archive_target
        # Run the bash call to handle the wget and untar/tar-ing.
        command = 'bash {0} {1} {2} {3} {4} {5}'.format(
            BACKFILL_CMD, process_date_ymd, wget_target,
            wget_file, archive_target, ds_type
        )
        print command
        proc = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate()
        exit_code = proc.wait()
        print stdout
        if exit_code:
            print stderr
            print 'ERROR - could not backfill for date: {0}'.format(process_date_ymd)
        else:
            print 'Source SNODAS data backfilled for date {0}'.format(process_date_ymd)


if __name__ == '__main__':
    main()