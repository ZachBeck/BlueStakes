import arcpy

sgid10 = r'Database Connections\dc_agrc@SGID10@sgid.agrc.utah.gov.sde'
inFeatures = r'C:\ZBECK\Addressing\Sevier\Sevier.gdb\Wayne_DB' #AddressPointSchema_Ksource'
inFeatures_FL = arcpy.MakeFeatureLayer_management(inFeatures)

flds = ['OBJECTID', 'City', 'ZipCode', 'AddSystem', 'FLAG']

##inputDict = {
##'AddSystem':['SGID10.LOCATION.AddressSystemQuadrants', 'GRID_NAME'],
##'City':['SGID10.BOUNDARIES.Municipalities', 'NAME'],
##'ZipCode':['SGID10.BOUNDARIES.ZipCodes', 'ZIP5']
##}


sCursor_Pts = arcpy.da.SearchCursor(inFeatures, flds)

for row in sCursor_Pts:
    print row['FLAG']
##for pt in sCursor_Pts:
##    oid = pt[0]
##    sql = """"{}" = '{}'""".format('OBJECTID', oid)
##    ptFl = arcpy.MakeFeatureLayer_management(pt)
##
##
##inputDict = {'City':['SGID10.BOUNDARIES.Municipalities', 'NAME']}
##
##for input in inputDict:
##
##    polyFC = sgid10 + '\\' + inputDict[input][0]
##    polyFL = arcpy.MakeFeatureLayer_management(polyFC)
##    polyFL = arcpy.SelectLayerByLocation_management(polyFL, 'INTERSECT', inFeatures_FL, '', 'NEW_SELECTION')
##
##    polyFLD = inputDict[input][1]
##    inFLD = [input]
##
##    sCursorPoly = arcpy.da.SearchCursor(polyFL, polyFLD)
##
##    for polys in sorted(set(sCursorPoly)):
##
##        uniquePoly = ''.join(polys)
##        sql = """"{}" = '{}'""".format(polyFLD, uniquePoly)
##
##        print '---------------------' + uniquePoly + '-------------------------'
##
##        arcpy.SelectLayerByAttribute_management(polyFL, "NEW_SELECTION", sql)
##        selectedPts = arcpy.SelectLayerByLocation_management(inFeatures_FL, 'WITHIN', polyFL, '', 'NEW_SELECTION')
##
##        sCursor_Pts = arcpy.da.SearchCursor(selectedPts, flds)
##
##        for pt in sCursor_Pts:
##            if pt[1] != polys[0].upper():
##                print pt[1]
##
##
####
####            if zpt != polys[0].upper():
####                print zpt + '  ' + polys[0].upper()
##
##
##
