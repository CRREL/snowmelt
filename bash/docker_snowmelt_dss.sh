#!/bin/bash
# Set enviroments for cron invocation.
export PATH=/usr/lib64/qt-3.3/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:$PATH

export LD_LIBRARY_PATH=/usr/lib64:/usr/lib:/usr/local/lib:/usr/lib/oracle/11.2/client64:/u01/product/oracle/ofm/11g/Oracle_WT1/lib:$LD_LIBRARY_PATH

# Create DSS files for the watersheds.
/usr/bin/docker exec -it --user u4rrcsgb snowmelt python /fire/study/snow/nohrsc_gdal/snowmelt_app/snowmelt/scripts/process_extents.py --all --scp

# Create DSS file for the Missouri River project.
/usr/bin/docker exec -it --user u4rrcsgb snowmelt python /fire/study/snow/nohrsc_gdal/snowmelt_app/snowmelt/scripts/process_extents.py -p missouri_river --scp
