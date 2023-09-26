import arcpy
import os


def addAddressAttributes(sgid, parcels, county, cntyFipsDict, ws):

    arcpy.env.workspace = ws
    arcpy.env.overwriteOutput = True

    pts = os.path.join(sgid, 'SGID.LOCATION.AddressPoints')

    nearFLDS = ['IN_FID', 'NEAR_FID', 'NEAR_DIST']

    nearTBL = os.path.join(ws, f'NearTbl_{county}')
    sql = f'"CountyID" = \'{cntyFipsDict[county]}\''
    cntyPts_FL = arcpy.MakeFeatureLayer_management(pts, 'cntyPts_FL', sql)

    print('Adding Address Attributes')

    arcpy.GenerateNearTable_analysis(parcels, cntyPts_FL, nearTBL, '2 Meters', 'NO_LOCATION', 'NO_ANGLE', 'CLOSEST')

    pt2Poly_Dict = {}
    polyDict = {}

    with arcpy.da.SearchCursor(nearTBL, nearFLDS) as sCursor:
        for row in sCursor:
            pt2Poly_Dict[row[0]] = row[1]
            polyDict.setdefault(row[1])
    with arcpy.da.SearchCursor(pts, ['OBJECTID', 'FullAdd']) as sCursor:
        for row in sCursor:
            if row[0] in polyDict:
                polyDict[row[0]] = row[1]

    parcelFlds = ['OBJECTID', 'PARCEL_ADD']

    ucursor = arcpy.da.UpdateCursor(parcels, parcelFlds)
    for urow in ucursor:
        try:
            if pt2Poly_Dict[urow[0]] in polyDict:
               urow[1] = polyDict[pt2Poly_Dict[urow[0]]]
        except:
            urow[1] = ''

        ucursor.updateRow(urow)

    del ucursor
    arcpy.Delete_management(nearTBL)
