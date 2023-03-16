import arcpy
from arcpy import env
import re

annoRdSegsALL = r'C:\ZBECK\BlueStakes\stagingBS.gdb\DOMINION_STAGING\RoadSegs_DominionALL'
#annoRdSegsSELECT = r'C:\ZBECK\BlueStakes\stagingBS.gdb\DOMINION_GEOGRAPHIC\RoadSegs_DominionSelect'

def createDominionAnnoRds():
    dominionFldr = r'C:\ZBECK\BlueStakes\DominionEnergy'
    streetAnnotation = r'C:\ZBECK\BlueStakes\DominionEnergy\DEUWI_BlueStakes_UGRC.gdb\Street_Name_Anno'
    annoPolygons = r'C:\ZBECK\BlueStakes\DominionEnergy\Street_Name_Anno.shp'

    if arcpy.Exists(annoPolygons):
        arcpy.Delete_management(annoPolygons)
        print ('Deleted Old Street_Name_Anno.shp')
    arcpy.FeatureClassToShapefile_conversion(streetAnnotation, dominionFldr)

    count = int(arcpy.GetCount_management(annoRdSegsALL).getOutput(0))
    if count > 1:
        print (count)
        arcpy.TruncateTable_management(annoRdSegsALL)
        print ('Truncated Anno Road Segments')

    annoFlds = ['FID', 'TextString', 'SHAPE@']
    iFlds = ['FENAME', 'FULLNAME', 'CFCC', 'CFCC1', 'CFCC2', 'SHAPE@']

    iCursor = arcpy.da.InsertCursor(annoRdSegsALL, iFlds)

    segmentDict = {}
    textDict = {}

    endList = ['N', 'S', 'E', 'W', 'DR', 'CIR', 'ST', 'RD', 'CT', 'AVE', 'WAY', 'HWY', 'BLVD', 'LN',\
               'PKWY', 'CV', 'TRAIL', 'PL', 'PARK', 'BAY', 'LOOP', 'VW']

    badVals = ['#2', '(725 N0', '*', '? S', '<FNT name="Arial" size="8.00">SUNNINGDALE CT</FNT>', 'STATE HWY 117',\
               'STATE HWY 18', 'STATE HWY 56', 'HWY 10', 'HWY 177', 'HWY 18', 'HWY 191', 'HWY 38', 'HWY 9', 'I-15',\
               'I-80', 'UTAH HW Y 89', 'UTAH HWY 118', 'UTAH HWY 132', 'UTAH HWY 137', 'UTAH HWY 143', 'UTAH HWY 143',\
               'UTAH HWY 171', 'UTAH HWY 18', 'UTAH HWY 186', 'UTAH HWY 224', 'UTAH HWY 31', 'UTAH HWY 32', 'UTAH HWY 56',\
               'UTAH HWY 65', 'UTAH HWY 71', 'UTAH HWY 89', 'UTAH HWY 90', 'US HWY 50', 'UNKNOWN', 'UNKNOWN ST NAME', '* LN']

    emptyVals = [None, '', ' ', 0]

    for row in arcpy.da.SearchCursor(annoPolygons, annoFlds):

        part = row[2].getPart(0)
        oID = row[0]

        textDict.update({oID:row[1]})

        if row[1] not in endList:
            name = row[1].strip()
            name = ' '.join(name.split())
            pntCnt = 0

            for pnt in part:
                pntCnt += 1

                if pntCnt == 1:
                    x1 = pnt.X
                    y1 = pnt.Y

                if pntCnt == 4:
                    x4 = pnt.X
                    y4 = pnt.Y

            array = arcpy.Array([arcpy.Point(x1, y1), arcpy.Point(x4, y4)])
            line = arcpy.Polyline(array)

            segmentDict.update({oID:[name, line]})

        else:
            if oID-1 != -1:
                if textDict[oID-1] in endList:
                    continue
                elif name.split()[-1] in endList:
                    continue
                elif name.endswith(')'):
                    continue
                else:
                    pastID = oID-1
                    name2 = name + ' ' + row[1]
                    segmentDict[pastID] = [name2, segmentDict[pastID][1]]

    p = '\(+(.*?)\)+'

    for seg in segmentDict:

        quoteMatch = re.search(p, segmentDict[seg][0])

        if quoteMatch:
            streetInQuotes = quoteMatch.group(1).title()
            streetOutsideQuotes = re.sub(p, '', segmentDict[seg][0]).title()

            if streetOutsideQuotes != '':
                iCursor.insertRow((streetOutsideQuotes, streetOutsideQuotes, '99', 'A', 'A9', segmentDict[seg][1]))

            iCursor.insertRow((streetInQuotes, streetInQuotes, '99', 'A', 'A9', segmentDict[seg][1]))

        elif segmentDict[seg][0] in badVals:
            continue
        else:
            iCursor.insertRow((segmentDict[seg][0].title(), segmentDict[seg][0].title(), '99', 'A', 'A9', segmentDict[seg][1]))

def outputSelectDominionRdSegs(rdsSGID):
    utSGID = r'C:\ZBECK\BlueStakes\stagingBS.gdb\SGID_GEOGRAPHIC\Utah'
    annoRdSegsALL_FL = arcpy.MakeFeatureLayer_management(annoRdSegsALL, 'annoRdSegsALL_FL')
    roadsSGID_FL = arcpy.MakeFeatureLayer_management(rdsSGID, 'roadsSGID_FL')
    sql = """"STATE" = 'Utah'"""
    utah_FL = arcpy.MakeFeatureLayer_management(utSGID, 'utah_FL', sql)

    annoRdSegsALL_Selected = arcpy.SelectLayerByLocation_management(annoRdSegsALL_FL, 'INTERSECT', utah_FL)
    annoRdSegsALL_Selected = arcpy.SelectLayerByLocation_management(annoRdSegsALL_FL, 'WITHIN_A_DISTANCE', \
                                                                       roadsSGID_FL, '75 Meters', 'SUBSET_SELECTION',
                                                                       'INVERT')

    selected = arcpy.GetCount_management(annoRdSegsALL_Selected)
    selected_Count = int(selected.getOutput(0))
    print('Dominion Road Segments Selected = {}'.format(selected_Count))

    outLocation = r'C:\ZBECK\BlueStakes\stagingBS.gdb\DOMINION_GEOGRAPHIC'
    with arcpy.EnvManager(workspace=outLocation):
        arcpy.env.overwriteOutput = True

        outRoadSegs = 'RoadSegs_DominionSelect'
        if arcpy.Exists(outRoadSegs):
            arcpy.Delete_management(outRoadSegs)

        arcpy.FeatureClassToFeatureClass_conversion(annoRdSegsALL_Selected, outLocation, outRoadSegs)







