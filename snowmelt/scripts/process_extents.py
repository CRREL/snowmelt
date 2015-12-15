# Original imports, will try to cull these a bit.
import os
import sys
import re
import datetime
import timeit
import subprocess
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
        if options.verbose or options.dry_run:
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
    parser.add_option('-a', '--all', dest='all_extents', action='store_true',
        default=False, help='Parse all exents defined in config.py')
    parser.add_option('--dry-run', dest='dry_run', action='store_true', 
        default=False, help='Dry run of the script.')
    parser.add_option('--scp', dest='run_scp', action='store_true', 
        default=False, help='Copy files to target location specfied in config '
                            'file upon completion of processing.')

    options, args = parser.parse_args()

    # Check that arguments make sense.
    if (not options.all_extents) and len(args) != 2:
        print 'Error: Script requires two arguments.\n'
        parser.print_help()
        sys.exit(1)
    elif options.all_extents and len(args) != 0:
        print 'Error: No arguments required when using the --all option.\n'
        parser.print_help()
        sys.exit(1)

    # Grab parameters based on division and district inputs.
    inputs_list = []
    if options.all_extents:
        for division in config.EXTENTS:
            for district in config.EXTENTS[division]:
                inputs_list += [
                    (division, district, config.EXTENTS[division][district])
                ]
    else:
        division, district = args
        try:
            extents_list = config.EXTENTS[division][district]
            inputs_list = [(division, district, extents_list)]
        except KeyError:
            print ('Could not find extents list for '
                   'Division "{0}", District "{1}"').format(division, district)
            sys.exit(1)

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

    verbose_print('Process date(s): {0}'.format(options.process_date))

    # Run the actual grid processing for each set of inputs and dates.
    transfer_list = set()
    for input_list in inputs_list:
        division, district, extents_list = input_list
        verbose_print('-' * 64)
        verbose_print('{0} {1} Watersheds:'.format(division.upper(), 
                                                     district.upper()))
        for extent in extents_list:
            verbose_print('{0}: {1}'.format(extent[0], extent[1]))
        for process_date in process_dates:
            verbose_print(
                'Processing extents for location {0} - {1}, date {2}'.format(
                    division, district, process_date
                )
            )
            if not options.dry_run:
                new_data = snowmelt.process_extents(
                    division, district,
                    process_date + datetime.timedelta(hours=2), # 2am.
                    extents_list,
                    options,
                )
                if new_data is not None:
                    transfer_list.add((division, district, new_data))
            else:
                transfer_list.add(division)

    finish = timeit.default_timer()
    print 'Finished Processing {0} {1}  (Duration = {2})'.format(
        os.path.basename(__file__),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        str(datetime.timedelta(seconds=finish - start))
    )

    # Transfer any files we've updated during this run.
    if options.run_scp:
        if not transfer_list:
            print 'No new files to transfer.'
        else:
            print '-' * 64
            print 'Transferring updated files:'
        for (division, district, new_data) in transfer_list:
            target_dir = config.SCP_TARGET_STR.format(division, district)
            command = 'scp {0} {1}'.format(new_data, target_dir)
            print command
            proc = subprocess.Popen(command, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            exit_code = proc.wait()
            print stdout
            if exit_code:
                print 'ERROR - could not transfer: {0}'.format(new_data)


if __name__ == '__main__':
    main()
