#! /usr/bin/bash
dt=`date +%Y%m`
dth=`date +%Y%m%d`

# Variables for legacy us-prefixed data stream.
#swe=us_ssmv11034tS__T0001TTNATS
#snowdepth=us_ssmv11036tS__T0001TTNATS
#snowavgtemp=us_ssmv11038wS__A0024TTNATS
#snowmelt=us_ssmv11044bS__T0024TTNATS

# Variables for current zz-prefixed data stream.
swe2=zz_ssmv11034tS__T0001TTNATS
snowdepth2=zz_ssmv11036tS__T0001TTNATS
snowavgtemp2=zz_ssmv11038wS__A0024TTNATS
snowmelt2=zz_ssmv11044bS__T0024TTNATS

cd /fire/study/snow/rawdata

# For regular user.
/usr/bin/wget -N ftp://ftp.nohrsc.noaa.gov/pub/products/collaborators/"$swe2""$dth"05HP001.grz
/usr/bin/wget -N ftp://ftp.nohrsc.noaa.gov/pub/products/collaborators/"$snowdepth2""$dth"05HP001.grz
/usr/bin/wget -N ftp://ftp.nohrsc.noaa.gov/pub/products/collaborators/"$snowavgtemp2""$dth"05DP001.grz
/usr/bin/wget -N ftp://ftp.nohrsc.noaa.gov/pub/products/collaborators/"$snowmelt2""$dth"05DP000.grz
