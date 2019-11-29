import arcpy
import os

##sgid10 = r'C:\zConnections\SGID10.sde'
##
##cnty = 'Beaver'
##
##parFipsDict = {'Beaver': '49001', 'BoxElder': '49003', 'Cache': '49005', 'Carbon': '49007', 'Daggett': '49009',
##               'Davis': '49011', 'Duchesne': '49013', 'Emery': '49015', 'Garfield': '49017', 'Grand': '49019',
##               'Iron': '49021', 'Juab': '49023', 'Kane': '49025', 'Millard': '49027', 'Morgan': '49029',
##               'Piute': '49031', 'Rich': '49033', 'SaltLake': '49035', 'SanJuan': '49037', 'Sanpete': '49039',
##               'Sevier': '49041', 'Summit': '49043', 'Tooele': '49045', 'Uintah': '49047', 'Utah': '49049',
##               'Wasatch': '49051', 'Washington': '49053', 'Wayne': '49055', 'Weber': '49057'}
##
##stageDB = r'C:\ZBECK\BlueStakes\stagingBS.gdb'

def addAddressAttributes(sgid10, parcels, county, cntyFipsDict, ws):

    arcpy.env.workspace = ws
    arcpy.env.overwriteOutput = True

    pts = os.path.join(sgid10, 'SGID10.LOCATION.AddressPoints')

    nearFLDS = ['IN_FID', 'NEAR_FID', 'NEAR_DIST']

    nearTBL = os.path.join(ws, 'NearTbl_{}'.format(county))
    sql =  """"{}" = '{}'""".format('CountyID', cntyFipsDict[county])
    cntyPts_FL = arcpy.MakeFeatureLayer_management(pts, 'cntyPts_FL', sql)

    print('Adding Address Attributes')

    arcpy.GenerateNearTable_analysis(parcels, cntyPts_FL, nearTBL, '5 Meters', 'NO_LOCATION', 'NO_ANGLE', 'CLOSEST')

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


##parcels = r'C:\ZBECK\BlueStakes\stagingBS.gdb\SGID10_GEOGRAPHIC\Parcels_Beaver'
##
##
##addAddressAttributes(sgid10, parcels, cnty)