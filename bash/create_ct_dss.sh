#!/bin/bash
# Set enviroments for cron invocation.
export PATH=/usr/lib64/qt-3.3/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:$PATH

export LD_LIBRARY_PATH=/usr/lib64:/usr/lib:/usr/local/lib:/usr/lib/oracle/11.2/client64:/u01/product/oracle/ofm/11g/Oracle_WT1/lib:$LD_LIBRARY_PATH

# Create DSS files for the CT river watershed.
/usr/bin/python /fire/study/snow/nohrsc_gdal/sgb_code/python/ct_river_extents_dss.py

# Copy over to cwms2 box, using home folder for now.
# scp /fire/study/snow/nohrsc_gdal/nad/results_sn/dss_files/* cwmsgrids@cpc-cwms2.usace.army.mil:/export/home/u4rrcsgb/nae/

# Ultimate destination(s) below.
scp /fire/study/snow/nohrsc_gdal/nad/results_sn/dss_files/* cwmsgrids@cpc-cwms2.usace.army.mil:/netapp/cwmsgrids/data/watershed/nad/nae/
scp /fire/study/snow/nohrsc_gdal/mvd/mvp/results_sn/dss_files/* cwmsgrids@cpc-cwms2.usace.army.mil:/netapp/cwmsgrids/data/watershed/mvd/mvp/
