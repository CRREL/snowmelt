import sys
import os
import subprocess

# Update our python path, so python knows where to find the snowmelt module.
SNOW_ROOT = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, SNOW_ROOT)

import snowmelt
from snowmelt import config


def main():

    print 'Transferring files:'

    for division in config.EXTENTS:
        for district in config.EXTENTS[division]:
            src_data = os.path.join(config.TOP_DIR, division, district, 
                                    'results_sn', 'dss_files', '*')
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
