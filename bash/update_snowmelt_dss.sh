#!/bin/bash
# Set enviroments for cron invocation.
export PATH=/usr/lib64/qt-3.3/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:$PATH

export LD_LIBRARY_PATH=/usr/lib64:/usr/lib:/usr/local/lib:/usr/lib/oracle/11.2/client64:/u01/product/oracle/ofm/11g/Oracle_WT1/lib:$LD_LIBRARY_PATH

# Create DSS files for the watersheds.
/usr/bin/python /home/u4rrcsgb/sandbox/snowmelt/snowmelt/scripts/process_extents.py --all

# Hard code in the SCP calls for now.
scp /fire/study/snow/nohrsc_gdal/nwd/nwo/results_sn/dss_files/* cwmsgrids@cpc-cwms2.usace.army.mil:/netapp/cwmsgrids/data/watershed/nwd/nwo/
scp /fire/study/snow/nohrsc_gdal/mvd/mvp/results_sn/dss_files/* cwmsgrids@cpc-cwms2.usace.army.mil:/netapp/cwmsgrids/data/watershed/mvd/mvp/
scp /fire/study/snow/nohrsc_gdal/mvd/mvs/results_sn/dss_files/* cwmsgrids@cpc-cwms2.usace.army.mil:/netapp/cwmsgrids/data/watershed/mvd/mvs/
scp /fire/study/snow/nohrsc_gdal/lrd/lrl/results_sn/dss_files/* cwmsgrids@cpc-cwms2.usace.army.mil:/netapp/cwmsgrids/data/watershed/lrd/lrl/
scp /fire/study/snow/nohrsc_gdal/nad/nab/results_sn/dss_files/* cwmsgrids@cpc-cwms2.usace.army.mil:/netapp/cwmsgrids/data/watershed/nad/nab/
scp /fire/study/snow/nohrsc_gdal/nad/nae/results_sn/dss_files/* cwmsgrids@cpc-cwms2.usace.army.mil:/netapp/cwmsgrids/data/watershed/nad/nae/
