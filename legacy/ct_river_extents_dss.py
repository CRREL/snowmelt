import os
import sys
import datetime
import gzip
import numpy as np
import shutil
import subprocess
import tarfile
import timeit
from collections import namedtuple

from osgeo import gdal,osr
from osgeo.gdalconst import *

def CreateASCII(inds,ascname,tmpdir):
    outtmpname = os.path.join(tmpdir,ascname + "tmp.asc")
    ascdriver = gdal.GetDriverByName("AAIGrid")
    outds = ascdriver.CreateCopy(outtmpname,inds,0,
                                 options = ['DECIMAL_PRECISION=4'])
    outds = None
    outasc = os.path.join(tmpdir,ascname + ".asc")
    RewriteASCII(outtmpname,outasc)

    return

def GetDatasetExtent(ds):
    """Usage: get_extent(input_dataset)  """
    geot = ds.GetGeoTransform()
    cellsize = geot[1]
    return ([geot[0],geot[3] - (ds.RasterYSize * cellsize),
                 geot[0] + (ds.RasterXSize * cellsize),geot[3]])

def GetDSSBaseName(inDT):
    #airtemp.yyyy.mm.dss
    #account for dss using 2400 as midnight And nws data using 0000
    if inDT.strftime("%H") == "00" and inDT.strftime("%d") == "01":
        return "snow." + (inDT - datetime.timedelta(hours=1)).strftime("%Y.%m.dss")
    else:
        return "snow." + inDT.strftime("%Y.%m.dss")

def GetGridExtent(infile):
    driver = gdal.GetDriverByName("AIG")
    ds = gdal.Open(infile,GA_ReadOnly)
    if ds is None:
        raise IOError("Could not open '%s'" % (infile))

    geot = ds.GetGeoTransform()
    cellsize = geot[1]
    YSize = ds.RasterYSize
    XSize = ds.RasterXSize
    ds = None

    return (Extent(geot[0],geot[3] - (YSize * cellsize),
                 geot[0] + (XSize * cellsize),geot[3]))

def getMaxExtent(extents):
    xmin = extents[0][1][0]
    ymin = extents[0][1][1]
    xmax = extents[0][1][2]
    ymax = extents[0][1][3]
    for ext in extents:
        ecoords = ext[1]
        xmin = min(xmin,ecoords[0])
        ymin = min(ymin,ecoords[1])
        xmax = max(xmax,ecoords[2])
        ymax = max(ymax,ecoords[3])

    return Extent(xmin,ymin,xmax,ymax)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def min_box_os(ext1,ext2,cellsize):
    """
    Calculate minimum bounding box for two input extents and matching
    cellsize.
    Returns 2 lists containing xoffset, yoffset, xsize, ysize for each input
    extent.  These can be used to subset images using ReadAsArray (e.g.)
    Input extents needs to be lists of (xmin,ymin,xmax,ymax).
    """
    maxxl = max(ext1[0],ext2[0])
    minxr = min(ext1[2],ext2[2])
    maxyb = max(ext1[1],ext2[1])
    minyt = min(ext1[3],ext2[3])

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

    os1 = (offx1,offy1,xsize,ysize)
    os2 = (offx2,offy2,xsize,ysize)

    return os1,os2

def RawFileManip(file_noext,masterhdr):
    try:
        os.remove(file_noext + ".Hdr")
        shutil.copy(masterhdr,file_noext + ".hdr")
        if os.path.exists(file_noext + ".bil"):
            os.remove(file_noext + ".bil")
        os.rename(file_noext + ".dat",file_noext + ".bil")
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno,e.strerror)
        raise

def ReprojUseWarpBil(infile,outfile,ext):
    to_srs = "'+proj=aea +lat_1=29.5n +lat_2=45.5n +lat_0=23.0n +lon_0=96.0w +x_0=0.0 +y_0=0.0 +units=m +datum=WGS84'"
##    "-t_srs" ,to_srs,"-r","bilinear",
##              "-dstnodata","-9999",
##              "-tr","2000","-2000",
##              "-tap",
##              "-te",str(ext.xmin),str(ext.ymin),str(ext.xmax),str(ext.ymax),
    from_srs = '"+proj=longlat +datum=WGS84"'

    cmdlist = ' '.join(["gdalwarp","-s_srs",from_srs,"-t_srs",to_srs,
                        "-r","bilinear","-srcnodata","-9999",
                        "-dstnodata","-9999",
                        "-tr","2000","-2000","-tap",
                        "-te",str(ext.xmin),str(ext.ymin),
                        str(ext.xmax),str(ext.ymax),
                        infile,outfile])
    print cmdlist
    proc = subprocess.Popen(cmdlist,shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout,stderr=proc.communicate()
    exit_code=proc.wait()

    if exit_code:
        print stdout
        raise RuntimeError(stderr)
    else:print stdout

def RewriteASCII(inasc,outasc):
    with open(outasc,"w") as fo:
        with open(inasc,"r") as fi:
            for line in fi:
                newline = line.strip()
                if newline:
                    fo.write(newline +"\n")
            fi.close
        fo.close

def RewriteASCII_flt(inasc,outasc):
    prec = 1
    with open(outasc,"w") as fo:
        with open(inasc,"r") as fi:
            for line in fi:
                newline = line.strip()
                if newline:
                    splitline = newline.split()
                    if not is_number(splitline[0]):
                        fo.write(newline +"\n")
                    else:
                        y = [float(elem) for elem in splitline]
                        z = [round(elem, prec) for elem in y]
                        fo.write(" ".join(map(str,z)) +"\n")
            fi.close
        fo.close

def RasterMath(shgtif,shgtifmath,varcode,nameDict):
    # VarCode 1038:  Converts snow pack temp to CC.  ** Assumes that
    #   1034 data (swe) listed in nameDict is same size as 1038 data.  This
    #   is the case currently b/c of gdalwarp process

    Status = False

    driver = gdal.GetDriverByName("GTiff")
    ds = gdal.Open(shgtif,GA_ReadOnly)
    if ds is None:
        #raise IOError("Could not open '%s'" % (shgtif))
        return False

    in_geot = ds.GetGeoTransform()
##    in_prj = osr.SpatialReference()
##    in_prj.ImportFromWkt(ds.GetProjection())

    xsize = ds.RasterXSize
    ysize = ds.RasterYSize


    band = ds.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    arr = band.ReadAsArray(0,0,xsize,ysize).astype(np.dtype("float32"))

    if varcode == "1038":
        #Cold Content
        sweasc = nameDict["1034"]

        #sweds = gdal.Open(swetif,GA_ReadOnly)
        sweds = gdal.Open(sweasc,GA_ReadOnly)
        if sweds is None:
            #raise IOError("Could not open '%s'" % (swetif))
            return False
        #swe ds will have same boundaries and cell size as cold content

        swearr = sweds.GetRasterBand(1).ReadAsArray(0,0,xsize,ysize).astype(np.dtype("float32"))
        ccarr = np.where(arr == nodata,nodata,arr - 273.15)
        #print swearr[0,729]
        #print arr[0,729]
        #print ccarr[0,729]
        #print swearr[0,729] * 2114 * ccarr[0,729] / 333000
        #print ",".join(map(str,[swearr.dtype,arr.dtype,ccarr.dtype]))
        newarr = np.where(ccarr >= 0,0,
                          np.where((swearr == nodata) | (ccarr == nodata),
                                    nodata,swearr * 2114 * ccarr / 333000))
        #print newarr[0,729]
    elif varcode == "1044":
        #Snow Melt
        newarr = np.where(arr == nodata,nodata,arr / 100.0)
    else:
        newarr = arr

    dsout = driver.Create(shgtifmath, xsize, ysize, 1, gdal.GDT_Float32,
                          options = ['COMPRESS=LZW'])
    dsout.SetGeoTransform(in_geot)
    dsout.SetProjection(ds.GetProjection())
    dsout.GetRasterBand(1).SetNoDataValue(nodata)
    dsout.GetRasterBand(1).WriteArray(newarr)
    dsout.FlushCache()
    dsout.GetRasterBand(1).GetStatistics(0,1)

    arr = None
    dsout = None
    Status = True
    return Status

def SetProps(inDate,basin):
    # dict[0] = Pathname Part list
    # dict[1] = Data type
    # dict[2] = Run var thru RasterMath sub

    DSSdate = inDate.strftime("%d%b%Y").upper() + ":0600"
    DSSdateYest = (inDate - datetime.timedelta(1)).strftime("%d%b%Y").upper() \
         + ":0600"
    bup = basin.upper()
    inDict = {}

    #SWE
    inDict["1034"] = [["SHG",bup,"SWE",DSSdate,"","SNODAS"],
                      "INST-VAL",False]
    #Snow Depth
    inDict["1036"] = [["SHG",bup,"SNOW DEPTH",DSSdate,"","SNODAS"],
                      "INST-VAL",False]
    #Cold Content
    inDict["1038"] = [["SHG",bup,"COLD CONTENT",DSSdate,"","SNODAS"],
                      "INST-VAL",True]
    #Snow Melt
    inDict["1044"] = [["SHG",bup,"SNOW MELT",DSSdateYest,DSSdate,
                      "SNODAS"], "PER-CUM",True]
    #Liquid Water (Zero)
    inDict["0001"] = [["SHG",bup,"LIQUID WATER",DSSdate,"","ZERO"],
                      "INST-VAL",False,"MM"]
    #Cold Content ATI (Zero)
    inDict["0002"] = [["SHG",bup,"COLD CONTENT ATI",DSSdate,"","ZERO"],
                      "INST-VAL",False,"DEG C"]
    #Melt Rate ATI (Zero)
    inDict["0003"] = [["SHG",bup,"MELTRATE ATI",DSSdate,"","ZERO"],
                      "INST-VAL",False,"DEGC-D"]
    return inDict

def UnzipLinux(origfile_noext,file_noext):
    if not os.path.exists(origfile_noext + ".grz"):
        print "File does not exist: " + file_noext + ".grz"
        sys.exit()

    bname = os.path.basename(file_noext)
    pname = os.path.dirname(file_noext)

    if os.path.exists(file_noext + ".Hdr"):
        os.remove(file_noext + ".Hdr")
    if os.path.exists(file_noext + ".dat"):
        os.remove(file_noext + ".dat")

    tar = tarfile.open(origfile_noext + ".grz",'r')
    tar.extractall(pname)

def WriteToDSS(asc2dssdir,inasc,outdss,dtype,path):
    pname = os.path.dirname(inasc)
    bname = os.path.basename(inasc)
    os.chdir(pname)
    asc2dsscmd = os.path.join(asc2dssdir,"asc2dssGriddash")
    cmdlist = ["python",asc2dsscmd,"gridtype=SHG","dunits=MM", \
               "dtype=" + dtype,"in=" + bname,"dss=" + outdss, \
               "path=" + path]
    print pname
    print cmdlist
    proc = subprocess.Popen(cmdlist,stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout,stderr=proc.communicate()
    exit_code=proc.wait()

    if exit_code:
        raise RuntimeError(stderr)
    else:print stdout

    return

def WriteToDSS2(asc2dssdir,inasc,outdss,dtype,path,dunits):
    pname = os.path.dirname(inasc)
    bname = os.path.basename(inasc)
    os.chdir(pname)
    asc2dsscmd = os.path.join(asc2dssdir,"asc2dssGriddash")
    cmdlist = ["python",asc2dsscmd,"gridtype=SHG","dunits=" + dunits, \
               "dtype=" + dtype,"in=" + bname,"dss=" + outdss, \
               "path=" + path]
    print pname
    print cmdlist
    proc = subprocess.Popen(cmdlist,stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout,stderr=proc.communicate()
    exit_code=proc.wait()

    if exit_code:
        raise RuntimeError(stderr)
    else:print stdout

    return

def ZeroDStoAsc2(gProps,ascname,tmpdir):

##    ds = gdal.Open(template,GA_ReadOnly)
##    if ds is None:
##        #raise IOError("Could not open '%s'" % (shgtif))
##        return False

    xsize = gProps[2]
    ysize = gProps[3]

    memdrv = gdal.GetDriverByName("MEM")
    memds = memdrv.Create("",xsize,ysize,1,gdal.GDT_Byte)
    memds.SetProjection(gProps[0])
    memds.SetGeoTransform(gProps[1])
    memds.GetRasterBand(1).SetNoDataValue(-9999)
    ndarr = np.zeros([ysize,xsize],np.dtype('byte'))
    memds.GetRasterBand(1).WriteArray(ndarr,0,0)
    memds.FlushCache()

    outtmpname = os.path.join(tmpdir,ascname + "tmp.asc")
    ascdriver = gdal.GetDriverByName("AAIGrid")
    outds = ascdriver.CreateCopy(outtmpname,memds,0,
                                 options = ['DECIMAL_PRECISION=0'])
    outds = None
    outasc = os.path.join(tmpdir,ascname + ".asc")
    RewriteASCII(outtmpname,outasc)

    ndarr = None
    memds = None


def main(locid, procdate, reg,extentList):

    # Sandbox dir, not to be used in production.
    # topdir = "/home/u4rrcsgb/sandbox/snowmelt/nohrsc_gdal"
    
    topdir = "/fire/study/snow/nohrsc_gdal"

    srcrddir = "/fire/study/snow/rawdata"

    keydir = os.path.join(topdir,"key")
    rddir = os.path.join(topdir,"rawdata")
    projdir = os.path.join(topdir,locid)

    projresdir = os.path.join(projdir,"results_sn")
    #projaoidir = os.path.join(projdir,"aoi")
    projascdir = os.path.join(projresdir,"asc_files")
    projdssdir = os.path.join(projresdir,"dss_files")
    histdir = os.path.join(projresdir,"history")
    #asc2dsscmd = os.path.join(topdir,"Asc2DssGridUtility","asc2dssGrid")
    asc2dssdir = os.path.join(topdir,"Asc2DssGridUtility")

    #shgextentgrid = os.path.join(projaoidir,locid + "_shg")

    masterhdr = os.path.join(keydir,reg + "_master.hdr")

    dstr = datetime.datetime.now().strftime("%y%m%d%H%M%S")
    ymdDate = procdate.strftime("%Y%m%d")

    histfile = os.path.join(histdir,"proccomplete" + ymdDate + ".txt")
    if os.path.isfile(histfile):
        print ("Grids processed earlier today.")
        return

    tmpdir = os.path.join(projresdir,"tmp" + dstr)  #tempfile.mkdtemp(dir=projdir)
    os.mkdir(tmpdir)

    PropDict = SetProps(procdate,locid)
    enameDict = {}

    zerolist = ["0001","0002","0003"]
    ##shgtiftemplate = ""

    extentGProps = {}

    snodaslist = [
        reg + "_ssmv11034tS__T0001TTNATS" + ymdDate + "05HP001",
        reg + "_ssmv11036tS__T0001TTNATS" + ymdDate + "05HP001",
        reg + "_ssmv11038wS__A0024TTNATS" + ymdDate + "05DP001",
        reg + "_ssmv11044bS__T0024TTNATS" + ymdDate + "05DP000",
    ]

    #SHGExtent = GetGridExtent(shgextentgrid)
    maxExtent = getMaxExtent(extentList)

    #dssfile = os.path.join(projdssdir,locid + ymdDate + ".dss")
    dssbasename = GetDSSBaseName(procdate)
    dssfile = os.path.join(projdssdir,dssbasename)

    FileStatus = True
    for f in snodaslist:
        #print os.path.join(srcrddir,f + ".grz")
        if not os.path.isfile(os.path.join(srcrddir,f + ".grz")):
            FileStatus = False

    if not FileStatus:
        print ("All source data not available.")
        return

    for f in snodaslist:

        origf_noext = os.path.join(srcrddir,f)  #rddir,f)
        f_noext = os.path.join(tmpdir,f)

        varcode = f[8:12]
        varprops = PropDict[varcode]
        path = "/" + "/".join(varprops[0]) + "/"
        dtype = varprops[1]

        easiername = locid + "_" + varprops[0][2].replace(" ","_").lower() + \
                ymdDate
        enameDict[varcode] = os.path.join(projascdir, easiername + ".asc")
        shgtif = os.path.join(tmpdir,f + "alb.tif")
        shgtifmath = os.path.join(tmpdir, easiername + ".tif")
##        shgasc = os.path.join(tmpdir, easiername + ".asc")
##        shgascfin = os.path.join(projascdir, easiername + ".asc")
##        FileStatus = False
##        if not os.path.isfile(shgascfin) and os.path.isfile(os.path.join(srcrddir,f + ".grz")):
##            FileStatus = True
##        if varprops[0][2] == "COLD CONTENT":
##            swename = locid + "_swe"  + ymdDate
##            if not os.path.isfile(os.path.join(projascdir,swename + ".asc")):
##                FileStatus = False

##        if FileStatus:
        #shutil.copy(os.path.join(srcrddir,f + ".grz"),origf_noext + ".grz")

        #Unzip7za(f_noext)
        UnzipLinux(origf_noext,f_noext)
        RawFileManip(f_noext,masterhdr)

        ReprojUseWarpBil(f_noext + ".bil",shgtif,maxExtent) #SHGExtent)
        mathranokay = True
        if varprops[2]:
            #note: enamedict populated only for prior product #'s
            mathranokay = RasterMath(shgtif,shgtifmath,varcode,enameDict)

        else:
            shgtifmath = shgtif
        if mathranokay:
            #enameDict[varcode] = os.path.join(projascdir, easiername + ".asc") #shgtifmath
            enameDict[varcode] = shgtifmath
            for extentarr in extentList:
                ds = gdal.Open(shgtifmath)
                if ds is None:
                    #Write to log
                    print 'Could not open ' + fname
                    return 1
                nodata = ds.GetRasterBand(1).GetNoDataValue()
                fullext = GetDatasetExtent(ds)
                cellsize = ds.GetGeoTransform()[1]

                subext = extentarr[1]
                fullof,subof = min_box_os(fullext,subext,cellsize)
                #print fullof
                #print subof
                xsize = int(fullof[2])
                ysize = int(fullof[3])
                dsProj = ds.GetProjection()

                cliparr = ds.GetRasterBand(1).ReadAsArray(int(round(fullof[0])),
                                int(round(fullof[1])),
                                xsize,ysize)
                outtmpname = os.path.join(tmpdir,extentarr[0] + "tmp.asc")
                driver = gdal.GetDriverByName("MEM")

                clipgeot = [subext[0],cellsize,0,subext[3],0,-cellsize]
                extentGProps[extentarr[0]] = [dsProj,clipgeot,xsize,ysize,nodata]

                clipds = driver.Create("",xsize,ysize,1,GDT_Float32) #ds.GetRasterBand(1).DataType) #,
                    #options = ['DECIMAL_PRECISION=4'])
                clipds.SetGeoTransform(clipgeot)
                clipds.SetProjection(ds.GetProjection())
                clipds.GetRasterBand(1).SetNoDataValue(nodata)
                clipds.GetRasterBand(1).WriteArray(cliparr,0,0)
                clipds.FlushCache()
                ascbasename = extentarr[0] + "_" + \
                    varprops[0][2].replace(" ","_").lower() + ymdDate
                CreateASCII(clipds,ascbasename,tmpdir)
                clipds = None

                ds = None

                tmpasc = os.path.join(tmpdir,ascbasename + ".asc")
                projasc = os.path.join(projascdir, ascbasename + ".asc")
                shutil.copy(tmpasc,projasc)
                shutil.copy(os.path.join(tmpdir, ascbasename + "tmp.prj"),
                                os.path.join(projascdir, ascbasename + ".prj"))


                #DSSdate = procdate.strftime("%d%b%Y").upper() + ":0600"
                #path = "/SHG/"+extentarr[0].upper()+"/AIRTEMP/"+DSSdate+"/"+"/"+FPart+"/"
                varprops = PropDict[varcode]
                p = varprops[0]
                dtype = varprops[1]
                #path = path = "/" + "/".join(varprops[0]) + "/"
                path = "/SHG/" + extentarr[0].upper() + "/" + p[2] + \
                    "/" + p[3] +"/" + p[4] + "/" + p[5] + "/"
                WriteToDSS(asc2dssdir,projasc,dssfile,dtype,path)
                if not dssbasename in transferlist:
                    transferlist.append(dssbasename)
                    print"translist = " + ",".join(transferlist)
                outarr = None
                cliparr = None

##                if shgtiftemplate == "":
##                    shgtiftemplate = shgtifmath

    ##if shgtiftemplate <> "":
        # ^ Assume this will run when one of the primary data files was
        # found and processed
    if len(extentGProps) == 0:
        print "An error occurred identifying extent properties."
        return
    for varcode in zerolist:
        varprops = PropDict[varcode]

        for extentarr in extentList:
            p = varprops[0]
            dtype = varprops[1]
            path = "/SHG/" + extentarr[0].upper() + "/" + p[2] + \
                "/" + p[3] +"/" + p[4] + "/" + p[5] + "/"
            ascbasename = extentarr[0] + "_" + \
                    varprops[0][2].replace(" ","_").lower() + ymdDate
            tmpasc = os.path.join(tmpdir,ascbasename + ".asc")
            projasc = os.path.join(projascdir, ascbasename + ".asc")

##            easiername = locid + "_" + varprops[0][2].replace(" ","_").lower() + \
##                ymdDate
##
##            shgasc = os.path.join(tmpdir, easiername + ".asc")
##            shgascfin = os.path.join(projascdir, easiername + ".asc")

            #if not os.path.isfile(projasc):
            ZeroDStoAsc2(extentGProps[extentarr[0]],ascbasename,tmpdir)
            shutil.copy(tmpasc,projasc)
            shutil.copy(os.path.join(tmpdir, ascbasename + "tmp.prj"),
                        os.path.join(projascdir, ascbasename + ".prj"))
            dssdunits = varprops[3]
            WriteToDSS2(asc2dssdir,projasc,dssfile,dtype,path,dssdunits)

    #shutil.rmtree(tmpdir)

    with open(histfile,"w") as fo:
        dstr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fo.write(procdate.strftime("%a %b %d %H:%M:%S %Y" ))
        fo.close

    return


if __name__ == '__main__':

    tic = timeit.default_timer()

    Extent = namedtuple('Extent','xmin,ymin,xmax,ymax') #Convert to a class?

    a_locid = "nad"
    a_dataset = "zz"

    #this is global for now...
    transferlist = []

    extarrlist = [
        ['Connecticut River', [1820000, 2266000, 1958000, 2734000]],
    ]

    todaysdate = datetime.datetime.now()

    # TEST DATE
    # todaysdate = datetime.datetime.strptime('20151005',"%Y%m%d")

    main(a_locid,todaysdate,a_dataset,extarrlist)

    toc = timeit.default_timer()
    print("Finished " + os.path.basename(sys.argv[0]) + " " + \
          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + \
          "  (Duration = " + \
          str(datetime.timedelta(seconds=toc - tic)) + ")")
