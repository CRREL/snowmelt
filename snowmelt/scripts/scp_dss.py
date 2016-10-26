import sys
import os
import re
import datetime
import subprocess

from optparse import OptionParser

# Update our python path, so python knows where to find the snowmelt module.
SNOW_ROOT = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, SNOW_ROOT)

import snowmelt
from snowmelt import config

DATE_REGEX = re.compile(r'^(?P<start_date>\d{6})-(?P<end_date>\d{6})$')


def main():

    def parse_date(date_string):
        return datetime.datetime.strptime(date_string,'%Y%m')

    # Create an OptionParser to handle any command-line arguments and options.
    usage = ("usage: %prog [options]")
    parser = OptionParser(usage=usage)

    parser.add_option('-d', '--date', dest='process_date',
        default=datetime.datetime.now().strftime('%Y%m'),
        help='Date should be in YYYYMM format. Can also provide a range '
             'of dates with YYYYMM-YYYYMM format.')

    options, args = parser.parse_args()

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
                current_month = process_date.month
                while current_month == process_date.month:
                    process_date += datetime.timedelta(weeks=1)
        else:
            process_dates = [parse_date(options.process_date)]
    except:
        print ('Couldn\'t parse time input.  Please use YYYYMM format, or '
               'YYYYMM-YYYYMM for a date range.')
        sys.exit(1)

    print 'Transferring files:'

    for process_date in process_dates:
        dss_file = 'snow.{0}.dss'.format(process_date.strftime('%Y.%m'))
        for division in config.EXTENTS:
            for district in config.EXTENTS[division]:
                src_data = os.path.join(config.TOP_DIR, division, district, 
                                        'results_sn', 'dss_files', dss_file)
                target_dir = config.SCP_TARGET_STR.format(division, district)
                command = 'scp {0} {1}'.format(src_data, target_dir)
                print command
                proc = subprocess.Popen(command, shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                stdout, stderr = proc.communicate()
                exit_code = proc.wait()
                print stdout
                if exit_code:
                    print 'ERROR - could not transfer: {0}'.format(src_data)


if __name__ == '__main__':
    main()
