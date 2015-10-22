'''
Description:  Creates a test file of polygon labels and extents from an ArcGIS 
              polygon feature class.

    Polygon Feature class --
              Name of ArcGIS feature class or shapefile that contains a polygon 
              dataset, with a properly identified coordinate system.

    Label Attribute --
              Name of the field in the polygon feature class's attribute 
              table that contains the polygon label.  

    output file --
              Name of the text file to be created

'''

import os
import sys
import arcpy
import math

verbose = True

def usage():
   print '''
Usage:  %s <Polygon Feature Class> <Label Attribute> <output file>
   ''' % sys.argv[0]

def help():
   print __doc__


def main(args):
    
    if len(args) != 4:
        usage()
        return 1
    
    if args[1] == "-h":
        usage()
        print __doc__
        return 0

    # Find ourselves in the file system and find out if we're working in 
    # a geodatabase
    
    print "Loaded arcpy scripting module for version %s" % arcpy.GetInstallInfo()["Version"]
    # gp.Toolbox = "management"
    
    # get arguments from command line 
    polygonFCinput = args[1]
    labelField = args[2]
    outFileName = os.path.abspath(args[3])
    workingDir = os.path.split(outFileName)[0]
    
    # these are hard coded for our grid-extraction boundaries
    cellsize = 2000
    buffer = 2

    dscPolygonFC = arcpy.Describe(polygonFCinput)
    inFC = dscPolygonFC.name
    arcpy.env.workspace = dscPolygonFC.path
    shapeField = dscPolygonFC.ShapeFieldName
    dscWorkspace = arcpy.Describe(arcpy.env.workspace)
    if dscWorkspace.dataElementType == 'DEFeatureDataset':
        arcpy.env.workspace = dscWorkspace.path
        dscWorkspace = arcpy.Describe(arcpy.env.workspace)
#    except:
#        print "Failure opening features in " + polygonFCinput + '.'
#        print arcpy.GetMessages()
#        return 1
    
    if dscWorkspace.dataElementType != "DEFolder" and dscWorkspace.dataElementType != "DEWorkspace":
        print "Workspace %s not found.  \nExiting program." % arcpy.env.workspace
        return 1

    if arcpy.Exists(inFC) != True:
        print "Workspace type: " + dscWorkspace.dataElementType
        print "Feature class %s not found.  \nExiting program." % inFC
        return 1

    if verbose:
        print "Input data set is a " + dscPolygonFC.DatasetType
        print "Input feature contains %s shapes.\n" % dscPolygonFC.ShapeType 
    if (dscPolygonFC.ShapeType).lower() != "polygon":
        print "Input data set must be a polygon feature class or shape file."
        return 1

    fields = arcpy.ListFields(inFC, labelField)
    if len(fields) == 0:
        print "Field %s not found in attributes for %s.  \nExiting program" % (
          labelField, inFC)
        return 1

    # dscWorkspace = arcpy.Describe(arcpy.env.workspace)
    if dscWorkspace.WorkspaceType == "FileSystem":
        workingDataType = "Shapefile"
    else:
        workingDataType = "FeatureClass"

    if verbose:
        print "ArcGIS workspace = " + arcpy.env.workspace
        print "  Polygon feature class = %s\n" % inFC
    try:
        outFile = open(outFileName, 'w')
    except:
        print "Could not open " + outFileName + + " for output."
        return 1

    sCursor = arcpy.SearchCursor(inFC)

    for row in sCursor:
        theExtent = row.getValue(shapeField).extent
        minX = cellsize * int(math.floor(theExtent.XMin / cellsize) - buffer)
        minY = cellsize * int(math.floor(theExtent.YMin / cellsize) - buffer)
        maxX = cellsize * int(math.ceil(theExtent.XMax / cellsize) + buffer)
        maxY = cellsize * int(math.ceil(theExtent.YMax / cellsize) + buffer)
        outFile.write("\"%s\", \"%s\", \"%s\", %.0f, %.0f, %.0f, %.0f\n" % (
          row.getValue("Division"), row.getValue("Dist_Sym"), row.getValue(labelField),
          minX, minY, maxX, maxY))

    outFile.close()
    return 0
if __name__ == '__main__':
    main(sys.argv)
