# Original imports, will try to cull these a bit.
import os
import sys
import datetime
import gzip
import numpy as np
import shutil
import subprocess
import tarfile
from collections import namedtuple

from osgeo import gdal, osr
from osgeo.gdalconst import *

from snowmelt.utils import mkdir_p
from snowmelt import config

# Global vars.  TODO Bit ugly, need to rethink how to do these.
Extent = namedtuple('Extent', 'xmin,ymin,xmax,ymax')  # Convert to a class?

SNODAS_FILENAME_LIST = [
    "{ds}_ssmv11034tS__T0001TTNATS{ymd}05HP001",
    "{ds}_ssmv11036tS__T0001TTNATS{ymd}05HP001",
    "{ds}_ssmv11038wS__A0024TTNATS{ymd}05DP001",
    "{ds}_ssmv11044bS__T0024TTNATS{ymd}05DP000",
]


def print_dashes(length=64):
    print '-' * length


def get_src_dir_by_date(proc_date):
    # Helper function to find the source data, which is stored in
    # a few different places on rsgis-base.
    if proc_date.year > 2012:
        return config.SRC_DIR
    elif proc_date.year == 2012:
        return config.ARCHIVE_DIR_2012
    else:
        month_path = proc_date.strftime('%Y/%B')
        return os.path.join(config.ARCHIVE_DIR, month_path)


def prepare_source_data_for_date(process_date, src_dir, conus_tiff_only=True):
    ''' Builds an unzip directory and extracts data from source files
    for a given day. 
    Returns the directory path to the unzipped files,
    or None if missing any source data. '''
    ymd_str = process_date.strftime('%Y%m%d')
    unzip_dir = os.path.join(config.PROCESSED_SRC_DIR, 'unzipped_data', ymd_str)
    us_tif_dir = os.path.join(config.PROCESSED_SRC_DIR, 'conus_tiffs')
    
    # Use 'us' prefix and adjust nodata value for dates before January 24, 2011.
    ds_type = 'zz'
    nodata_val = '-9999'
    if process_date < datetime.datetime(2011, 1, 24, 0, 0):
        ds_type = 'us'
        nodata_val = '55537'

    masterhdr = os.path.join(config.HEADER_KEY_DIR, ds_type + '_master.hdr')

    # Create list of file names for this date.
    snodas_src_files = [
        f.format(ds=ds_type, ymd=ymd_str) for f in SNODAS_FILENAME_LIST
    ]

    # Make sure all files exist before trying any extractions.
    print_dashes()
    print 'Processing source data for:', process_date.strftime('%Y.%m.%d')
    msgs = []
    for filename in snodas_src_files:
        if not os.path.isfile(os.path.join(src_dir, filename + '.grz')):
            msgs += ['Missing source data file: {0}'.format(filename)]
    if msgs:
        for msg in msgs:
            print msg
        print_dashes()
        return None

    mkdir_p(us_tif_dir)
    mkdir_p(unzip_dir)

    # Loop through our filenames and do the unzipping and other set up.
    for filename in snodas_src_files:
        
        # Cobble together all the file names.
        src_file = os.path.join(src_dir, filename)
        unzip_file = os.path.join(unzip_dir, filename)
        ready_file = unzip_file + '.bil'
        shgtif = os.path.join(us_tif_dir, filename + 'alb.tif')

        # Don't bother doing anything if tiff already exists in conus_tiff_only mode.
        if conus_tiff_only and os.path.isfile(shgtif):
            print 'CONUS SHG tiff already exists:', shgtif
            continue

        if not os.path.isfile(ready_file):
            print 'Processing source to output file:', ready_file
            UnzipLinux(src_file, unzip_file)
            RawFileManip(unzip_file, masterhdr)
        else:
            print 'Using existing source file:', ready_file 
        
        # Save a full version of the day's data set.
        if not os.path.isfile(shgtif):
            print 'Saving CONUS SHG tiff file:', shgtif
            ReprojUseWarpBil(ready_file, shgtif, nodata=nodata_val,
                             tr_x='1000', tr_y='-1000')
        else:
            print 'CONUS SHG tiff already exists:', shgtif

    print_dashes()
    return unzip_dir


def process_extents(div_name, dist_name, process_date,
                    src_dir, extents_list, options):
    ''' Main function for processing extents.  Calls lots of helper
    and utility functions. 
    div_name: string - Name of division, used in output file format.
    process_date: datetime.datetime object - date for which data is desired.
    extents_list: list - list of namedtuples for each watershed.

    Returns the path to the file if new data was written to a DSS file, 
    None otherwise.
    '''

    def verbose_print(to_print):
        if options.verbose:
            print to_print

    def clean_up_tmp_dir(tmp_dir):
        if not options.keep_tmp_dir:
            shutil.rmtree(tmp_dir)

    verbose_print('Source directory: {0}'.format(src_dir))

    # Use 'us' prefix and adjust nodata value for dates before January 24, 2011.
    dataset_type = 'zz'
    nodata_val = '-9999'
    if process_date < datetime.datetime(2011, 1, 24, 0, 0):
        dataset_type = 'us'
        nodata_val = '55537'

    projdir = os.path.join(config.TOP_DIR, div_name, dist_name)

    # Use the proper results dir structure based on the config file.
    if config.LEGACY_DIRECTORY_STRUCTURE:
        projresdir = os.path.join(projdir, 'results_sn')
        projascdir = os.path.join(projresdir, 'asc_files')
        projdssdir = os.path.join(projresdir, 'dss_files')
        histdir = os.path.join(projresdir, 'history')
    else:
        projascdir = os.path.join(config.ASC_BASE_DIR, div_name, dist_name)
        projdssdir = os.path.join(config.DSS_BASE_DIR, div_name, dist_name)
        histdir = os.path.join(config.HISTORY_BASE_DIR, div_name, dist_name)

    # Build our results directories if needed.
    mkdir_p(projascdir)
    mkdir_p(projdssdir)
    mkdir_p(histdir)

    dstr = datetime.datetime.now().strftime('%y%m%d%H%M%S')
    ymdDate = process_date.strftime('%Y%m%d')

    # Break out if processing for the given date has already happened.
    histfile = os.path.join(histdir, 'proccomplete' + ymdDate + '.txt')
    if os.path.isfile(histfile):
        print '{0} {1} grids already processed for: {2}'.format(
            div_name, dist_name, process_date.strftime('%Y.%m.%d')
        )
        return None
    print 'Processing {0} {1} grids for: {2}'.format(
        div_name, dist_name, process_date.strftime('%Y.%m.%d')
    )

    tmpdir = os.path.join(projascdir, 'tmp' + dstr)
    os.mkdir(tmpdir)

    # Set up a dictionary mapping the various properties to their DSS names.
    PropDict = SetProps(process_date, div_name)
    enameDict = {}
    zerolist = ["0001", "0002", "0003"]
    extentGProps = {}
    maxExtent = getMaxExtent(extents_list)
    dssbasename = GetDSSBaseName(process_date)
    dssfile = os.path.join(projdssdir, dssbasename)

    # Define our files and make sure they all exist.
    snodaslist = [
        s.format(ds=dataset_type, ymd=ymdDate) for s in SNODAS_FILENAME_LIST
    ]

    # Loop through our source SNODAS files.
    for f in snodaslist:

        varcode = f[8:12]
        varprops = PropDict[varcode]
        path = "/" + "/".join(varprops[0]) + "/"
        dtype = varprops[1]

        easiername = \
            div_name + "_" + varprops[0][2].replace(" ", "_").lower() + ymdDate
        enameDict[varcode] = os.path.join(projascdir, easiername + ".asc")
        shgtif = os.path.join(tmpdir, f + "alb.tif")
        shgtifmath = os.path.join(tmpdir, easiername + ".tif")

        src_file = os.path.join(src_dir, f + '.bil')
        ReprojUseWarpBil(src_file, shgtif, maxExtent, nodata_val)
        mathranokay = True
        if varprops[2]:
            # NOTE: enamedict populated only for prior product numbers
            mathranokay = RasterMath(shgtif, shgtifmath, varcode, enameDict)
        else:
            shgtifmath = shgtif
        if mathranokay:
            enameDict[varcode] = shgtifmath
            for extentarr in extents_list:
                ds = gdal.Open(shgtifmath)
                if ds is None:
                    print 'Could not open ' + shgtifmath
                    return None
                nodata = ds.GetRasterBand(1).GetNoDataValue()
                fullext = GetDatasetExtent(ds)
                cellsize = ds.GetGeoTransform()[1]

                subext = extentarr[1]
                fullof, subof = min_box_os(fullext, subext, cellsize)
                xsize = int(fullof[2])
                ysize = int(fullof[3])
                dsProj = ds.GetProjection()

                cliparr = ds.GetRasterBand(1).ReadAsArray(
                    int(round(fullof[0])), int(round(fullof[1])),
                    xsize, ysize
                )
                outtmpname = os.path.join(tmpdir, extentarr[0] + "tmp.asc")
                driver = gdal.GetDriverByName("MEM")

                clipgeot = [subext[0], cellsize, 0, subext[3], 0, -cellsize]
                extentGProps[extentarr[0]] = [
                    dsProj, clipgeot, xsize, ysize, nodata]

                clipds = driver.Create("", xsize, ysize, 1, GDT_Float32)
                clipds.SetGeoTransform(clipgeot)
                clipds.SetProjection(ds.GetProjection())
                clipds.GetRasterBand(1).SetNoDataValue(nodata)
                clipds.GetRasterBand(1).WriteArray(cliparr, 0, 0)
                clipds.FlushCache()
                ascbasename = extentarr[0] + "_" + \
                    varprops[0][2].replace(" ", "_").lower() + ymdDate
                CreateASCII(clipds, ascbasename, tmpdir)
                clipds = None
                ds = None

                tmpasc = os.path.join(tmpdir, ascbasename + ".asc")
                projasc = os.path.join(projascdir, ascbasename + ".asc")
                shutil.copy(tmpasc, projasc)
                shutil.copy(
                    os.path.join(tmpdir, ascbasename + "tmp.prj"),
                    os.path.join(projascdir, ascbasename + ".prj")
                )

                varprops = PropDict[varcode]
                p = varprops[0]
                dtype = varprops[1]

                path = "/SHG/" + extentarr[0].upper() + "/" + p[2] + \
                    "/" + p[3] + "/" + p[4] + "/" + p[5] + "/"
                WriteToDSS(projasc, dssfile, dtype, path)
                outarr = None
                cliparr = None

    if len(extentGProps) == 0:
        print "An error occurred identifying extent properties."
        clean_up_tmp_dir(tmpdir)
        return None

    for varcode in zerolist:
        varprops = PropDict[varcode]
        for extentarr in extents_list:
            p = varprops[0]
            dtype = varprops[1]
            path = "/SHG/" + extentarr[0].upper() + "/" + p[2] + \
                "/" + p[3] + "/" + p[4] + "/" + p[5] + "/"
            ascbasename = extentarr[0] + "_" + \
                varprops[0][2].replace(" ", "_").lower() + ymdDate
            tmpasc = os.path.join(tmpdir, ascbasename + ".asc")
            projasc = os.path.join(projascdir, ascbasename + ".asc")

            WriteZeroDStoAsc(extentGProps[extentarr[0]], ascbasename, tmpdir)
            shutil.copy(tmpasc, projasc)
            shutil.copy(os.path.join(tmpdir, ascbasename + "tmp.prj"),
                        os.path.join(projascdir, ascbasename + ".prj"))
            dssdunits = varprops[3]
            WriteToDSS(projasc, dssfile, dtype, path, dssdunits)

    clean_up_tmp_dir(tmpdir)

    # Write out file to track that we've run for this day.
    with open(histfile, "w") as fo:
        dstr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fo.write(process_date.strftime("%a %b %d %H:%M:%S %Y"))
        fo.close
    return dssfile


########################################################################
# Helper functions below.
########################################################################


def CreateASCII(inds, ascname, tmpdir):
    outtmpname = os.path.join(tmpdir, ascname + "tmp.asc")
    ascdriver = gdal.GetDriverByName("AAIGrid")
    outds = ascdriver.CreateCopy(outtmpname, inds, 0,
                                 options=['DECIMAL_PRECISION=4'])
    outds = None
    outasc = os.path.join(tmpdir, ascname + ".asc")
    RewriteASCII(outtmpname, outasc)
    return


def GetDatasetExtent(ds):
    """Usage: get_extent(input_dataset)  """
    geot = ds.GetGeoTransform()
    cellsize = geot[1]
    return ([geot[0], geot[3] - (ds.RasterYSize * cellsize),
             geot[0] + (ds.RasterXSize * cellsize), geot[3]])


def GetDSSBaseName(inDT):
    # snow.<yyyy>.<mm>.dss
    # Account for dss using 2400 as midnight And nws data using 0000
    if inDT.strftime("%H") == "00" and inDT.strftime("%d") == "01":
        return "snow." + (inDT - datetime.timedelta(hours=1)).strftime("%Y.%m.dss")
    else:
        return "snow." + inDT.strftime("%Y.%m.dss")


def GetGridExtent(infile):
    driver = gdal.GetDriverByName("AIG")
    ds = gdal.Open(infile, GA_ReadOnly)
    if ds is None:
        raise IOError("Could not open '%s'" % (infile))

    geot = ds.GetGeoTransform()
    cellsize = geot[1]
    YSize = ds.RasterYSize
    XSize = ds.RasterXSize
    ds = None
    return (Extent(geot[0], geot[3] - (YSize * cellsize),
                   geot[0] + (XSize * cellsize), geot[3]))


def getMaxExtent(extents):
    xmin = extents[0][1][0]
    ymin = extents[0][1][1]
    xmax = extents[0][1][2]
    ymax = extents[0][1][3]
    for ext in extents:
        ecoords = ext[1]
        xmin = min(xmin, ecoords[0])
        ymin = min(ymin, ecoords[1])
        xmax = max(xmax, ecoords[2])
        ymax = max(ymax, ecoords[3])
    return Extent(xmin, ymin, xmax, ymax)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def min_box_os(ext1, ext2, cellsize):
    """
    Calculate minimum bounding box for two input extents and matching
    cellsize.
    Returns 2 lists containing xoffset, yoffset, xsize, ysize for each input
    extent.  These can be used to subset images using ReadAsArray (e.g.)
    Input extents needs to be lists of (xmin,ymin,xmax,ymax).
    """
    maxxl = max(ext1[0], ext2[0])
    minxr = min(ext1[2], ext2[2])
    maxyb = max(ext1[1], ext2[1])
    minyt = min(ext1[3], ext2[3])

    offx1 = 0.0
    offx2 = 0.0
    offy1 = 0.0
    offy2 = 0.0

    if ext1[0] < maxxl:
        offx1 = (maxxl - ext1[0]) / cellsize
    else:
        offx2 = (maxxl - ext2[0]) / cellsize
    if ext1[3] > minyt:
        offy1 = (ext1[3] - minyt) / cellsize
    else:
        offy2 = (ext2[3] - minyt) / cellsize

    xsize = (minxr - maxxl) / cellsize
    ysize = (minyt - maxyb) / cellsize

    os1 = (offx1, offy1, xsize, ysize)
    os2 = (offx2, offy2, xsize, ysize)

    return os1, os2


def RawFileManip(file_noext, masterhdr):
    ''' Replaces header with custom header file and renames .dat to .bil '''
    if os.path.exists(file_noext + ".Hdr"):
        os.remove(file_noext + ".Hdr")
    shutil.copy(masterhdr, file_noext + ".hdr")
    if os.path.exists(file_noext + ".bil"):
        os.remove(file_noext + ".bil")
    os.rename(file_noext + ".dat", file_noext + ".bil")
    return file_noext + ".bil"


def ReprojUseWarpBil(infile, outfile, ext=None, nodata='-9999',
                     tr_x='2000', tr_y='-2000'):
    to_srs = ("'+proj=aea +lat_1=29.5n +lat_2=45.5n +lat_0=23.0n "
              "+lon_0=96.0w +x_0=0.0 +y_0=0.0 +units=m +datum=WGS84'")
    from_srs = '"+proj=longlat +datum=WGS84"'

    cmdlist = ["gdalwarp", "-s_srs", from_srs, "-t_srs", to_srs,
                "-r", "bilinear",
                "-srcnodata", nodata,
                "-dstnodata", nodata,
                "-tr", tr_x, tr_y, "-tap"]
    if ext is not None:
        cmdlist += ["-te", str(ext.xmin), str(ext.ymin),
                           str(ext.xmax), str(ext.ymax),]
    cmdlist += [infile, outfile]
                        
    run_cmd = ' '.join(cmdlist)
    if not config.SUBPROCESS_QUIET:
        print run_cmd
    proc = subprocess.Popen(run_cmd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    exit_code = proc.wait()

    if not config.SUBPROCESS_QUIET:
        print stdout
    if exit_code:
        raise RuntimeError(stderr)
    return outfile


def RewriteASCII(inasc, outasc):
    with open(outasc, "w") as fo:
        with open(inasc, "r") as fi:
            for line in fi:
                newline = line.strip()
                if newline:
                    fo.write(newline + "\n")
            fi.close
        fo.close


def RewriteASCII_flt(inasc, outasc):
    prec = 1
    with open(outasc, "w") as fo:
        with open(inasc, "r") as fi:
            for line in fi:
                newline = line.strip()
                if newline:
                    splitline = newline.split()
                    if not is_number(splitline[0]):
                        fo.write(newline + "\n")
                    else:
                        y = [float(elem) for elem in splitline]
                        z = [round(elem, prec) for elem in y]
                        fo.write(" ".join(map(str, z)) + "\n")
            fi.close
        fo.close


def RasterMath(shgtif, shgtifmath, varcode, nameDict):
    # VarCode 1038:  Converts snow pack temp to CC.  ** Assumes that
    #   1034 data (swe) listed in nameDict is same size as 1038 data.  This
    #   is the case currently because of gdalwarp process.

    driver = gdal.GetDriverByName("GTiff")
    ds = gdal.Open(shgtif, GA_ReadOnly)
    if ds is None:
        return False

    in_geot = ds.GetGeoTransform()

    xsize = ds.RasterXSize
    ysize = ds.RasterYSize

    band = ds.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    arr = band.ReadAsArray(0, 0, xsize, ysize).astype(np.dtype("float32"))

    if varcode == "1038":
        # Cold Content
        sweasc = nameDict["1034"]

        # Make sure the SWE dataset has already been written.
        sweds = gdal.Open(sweasc, GA_ReadOnly)
        if sweds is None:
            return False

        # SWE ds will have same boundaries and cell size as cold content.
        swearr = sweds.GetRasterBand(1).ReadAsArray(
            0, 0, xsize, ysize).astype(np.dtype("float32"))
        ccarr = np.where(arr == nodata, nodata, arr - 273.15)
        newarr = np.where(ccarr >= 0, 0,
                          np.where((swearr == nodata) | (ccarr == nodata),
                                   nodata, swearr * 2114 * ccarr / 333000))
    elif varcode == "1044":
        # Snow Melt
        newarr = np.where(arr == nodata, nodata, arr / 100.0)
    else:
        newarr = arr

    dsout = driver.Create(shgtifmath, xsize, ysize, 1, gdal.GDT_Float32,
                          options=['COMPRESS=LZW'])
    dsout.SetGeoTransform(in_geot)
    dsout.SetProjection(ds.GetProjection())
    dsout.GetRasterBand(1).SetNoDataValue(nodata)
    dsout.GetRasterBand(1).WriteArray(newarr)
    dsout.FlushCache()
    dsout.GetRasterBand(1).GetStatistics(0, 1)

    # Close any potentially open datasets.
    dsout = None
    newarr = None
    swearr = None
    ccarr = None
    sweds = None
    arr = None
    band = None
    ds = None

    return True


def SetProps(inDate, basin):
    # dict[0] = Pathname Part list
    # dict[1] = Data type
    # dict[2] = Run var thru RasterMath sub

    DSSdate = inDate.strftime("%d%b%Y").upper() + ":0600"
    DSSdateYest = (inDate - datetime.timedelta(1)).strftime("%d%b%Y").upper() \
        + ":0600"
    bup = basin.upper()
    inDict = {}

    # SWE
    inDict["1034"] = [["SHG", bup, "SWE", DSSdate, "", "SNODAS"],
                      "INST-VAL", False]
    # Snow Depth
    inDict["1036"] = [["SHG", bup, "SNOW DEPTH", DSSdate, "", "SNODAS"],
                      "INST-VAL", False]
    # Cold Content
    inDict["1038"] = [["SHG", bup, "COLD CONTENT", DSSdate, "", "SNODAS"],
                      "INST-VAL", True]
    # Snow Melt
    inDict["1044"] = [["SHG", bup, "SNOW MELT", DSSdateYest, DSSdate,
                       "SNODAS"], "PER-CUM", True]
    # Liquid Water (Zero)
    inDict["0001"] = [["SHG", bup, "LIQUID WATER", DSSdate, "", "ZERO"],
                      "INST-VAL", False, "MM"]
    # Cold Content ATI (Zero)
    inDict["0002"] = [["SHG", bup, "COLD CONTENT ATI", DSSdate, "", "ZERO"],
                      "INST-VAL", False, "DEG C"]
    # Melt Rate ATI (Zero)
    inDict["0003"] = [["SHG", bup, "MELTRATE ATI", DSSdate, "", "ZERO"],
                      "INST-VAL", False, "DEGC-D"]
    return inDict


def UnzipLinux(origfile_noext, file_noext):
    ''' Extract our tarball of data. '''
    if not os.path.exists(origfile_noext + '.grz'):
        print 'File does not exist: ' + file_noext + '.grz'
        sys.exit()

    bname = os.path.basename(file_noext)
    pname = os.path.dirname(file_noext)

    OUTPUT_EXTS = ('.Hdr', '.dat')
    for output_ext in OUTPUT_EXTS:
        if os.path.exists(file_noext + output_ext):
            os.remove(file_noext + output_ext)

    tar = tarfile.open(origfile_noext + '.grz', 'r')
    tar.extractall(pname)

    # Do one more layer of extraction if needed.
    for output_ext in OUTPUT_EXTS:
        gz_filename = file_noext + output_ext + '.gz'
        if os.path.isfile(file_noext + output_ext + '.gz'):
            cmdlist = ['gunzip', gz_filename]
            proc = subprocess.Popen(cmdlist, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            exit_code = proc.wait()


def WriteToDSS(inasc, outdss, dtype, path, dunits='MM'):
    pname = os.path.dirname(inasc)
    bname = os.path.basename(inasc)
    os.chdir(pname)
    
    # Old subroutine
    # asc2dsscmd = os.path.join(config.TOP_DIR, 'Asc2DssGridUtility', 
    #                           'asc2dssGriddash')
    # cmdlist = [
    #     'python', asc2dsscmd, 'gridtype=SHG', 'dunits=' + dunits,
    #     'dtype=' + dtype, 'in=' + bname, 'dss=' + outdss, 'path=' + path
    # ]
    asc2dsscmd = os.path.join(
        config.TOP_DIR, 'Asc2DssGridUtility', 'asc2dssBash'
    )
    quote_str = '"{0}"'
    cmdlist = [
        asc2dsscmd, 'gridtype=SHG', 'dunits=' + quote_str.format(dunits),
        'dtype=' + quote_str.format(dtype), 'in=' + quote_str.format(bname), 
        'dss=' + quote_str.format(outdss), 'path=' + quote_str.format(path)
    ]
    if not config.SUBPROCESS_QUIET:
        print pname
        print ' '.join(cmdlist)
    proc = subprocess.Popen(
        cmdlist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    exit_code = proc.wait()

    if not config.SUBPROCESS_QUIET:
        print stdout
    if exit_code:
        raise RuntimeError(stderr)
    return


def WriteZeroDStoAsc(gProps, ascname, tmpdir):
    xsize = gProps[2]
    ysize = gProps[3]

    memdrv = gdal.GetDriverByName("MEM")
    memds = memdrv.Create("", xsize, ysize, 1, gdal.GDT_Byte)
    memds.SetProjection(gProps[0])
    memds.SetGeoTransform(gProps[1])
    memds.GetRasterBand(1).SetNoDataValue(-9999)
    ndarr = np.zeros([ysize, xsize], np.dtype('byte'))
    memds.GetRasterBand(1).WriteArray(ndarr, 0, 0)
    memds.FlushCache()

    outtmpname = os.path.join(tmpdir, ascname + "tmp.asc")
    ascdriver = gdal.GetDriverByName("AAIGrid")
    outds = ascdriver.CreateCopy(outtmpname, memds, 0,
                                 options=['DECIMAL_PRECISION=0'])
    outds = None
    outasc = os.path.join(tmpdir, ascname + ".asc")
    RewriteASCII(outtmpname, outasc)

    ndarr = None
    memds = None
