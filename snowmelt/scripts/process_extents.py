# Original imports, will try to cull these a bit.
import os
import sys
import re
import datetime
import timeit
from collections import namedtuple

# Imports from refactoring.
from optparse import OptionParser

# Update our python path, so python knows where to find the snowmelt module.
SNOW_ROOT = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, SNOW_ROOT)

import snowmelt
from snowmelt import config

DATE_REGEX = re.compile(r'^(?P<start_date>\d{8})-(?P<end_date>\d{8})$')


def main():

    def verbose_print(to_print):
        if options.verbose:
            print to_print

    def parse_date(date_string):
        return datetime.datetime.strptime(date_string,'%Y%m%d')

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
        help='Date should be in YYYYMMDD format. Can also provide a range '
             'of dates with YYYYMMDD-YYYYMMDD format.')
    parser.add_option('-t', '--dataset', dest='dataset_type', default='zz')
    parser.add_option('-a', '--all', dest='all_extents', action='store_true',
        default=False, help='Parse all exents - not implemented yet.')
    parser.add_option('--dry-run', dest='dry_run', action='store_true', 
        default=False, help='Dry run of the script.')

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

    # Parse out our processing date(s).
    process_dates = []
    try:
        match = DATE_REGEX.match(options.process_date)
        if match is not None:
            # Build out a list of dates to process.
            match_dict = match.groupdict()
            process_date = parse_date(match_dict['start_date'])
            end_date = parse_date(match_dict['end_date'])
            assert process_date < end_date
            while process_date <= end_date:
                process_dates += [process_date]
                process_date += datetime.timedelta(days=1)
        else:
            process_dates = [parse_date(options.process_date)]
    except:
        if options.verbose:
            raise
        print ('Couldn\'t parse time input.  Please use YYYYMMDD format, or '
               'YYYYMMDD-YYYYMMDD for a date range.')
        sys.exit(1)

    verbose_print(options.process_date)

    # Run the actual grid processing.
    for process_date in process_dates:
        verbose_print(
            'Processing extents for location {0} - {1}, date {2}'.format(
                division, district, process_date
            )
        )
        if not options.dry_run:
            snowmelt.process_extents(division, district, process_date, 
                                     options.dataset_type, extents_list)

    finish = timeit.default_timer()
    print 'Finished {0} {1}  (Duration = {2})'.format(
        os.path.basename(__file__),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        str(datetime.timedelta(seconds=finish - start))
    )


if __name__ == '__main__':
    main()
