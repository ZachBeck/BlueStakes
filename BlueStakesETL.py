import os, arcpy, datetime, time, re
from arcpy import env
from arcpy import da
from agrc import parse_address
#from sweeper.address_parser import Address
from AddressAttributes import addAddressAttributes

sgid = r'C:\sde\SGID_internal\SGID_agrc.sde'
sgid_GEO = r'C:\ZBECK\BlueStakes\stagingBS.gdb\SGID_GEOGRAPHIC'
stageDB = r'C:\ZBECK\BlueStakes\stagingBS.gdb'
schemaDB = r'C:\ZBECK\BlueStakes\schemaBS.gdb'
outLoc = r'C:\ZBECK\BlueStakes\outBlueStakes'


fipsNum = ['49001', '49003', '49005', '49007', '49009', '49011', '49013', '49015', '49017', '49019', '49021', \
          '49023', '49025', '49027', '49029', '49031', '49033', '49035', '49037', '49039', '49041', '49043', '49045', \
          '49047', '49049', '49051', '49053', '49055', '49057']

fipsDict = {'Beaver': '49001', 'BoxElder': '49003', 'Cache': '49005', 'Carbon': '49007', 'Daggett': '49009', \
           'Davis': '49011', 'Duchesne': '49013', 'Emery': '49015', 'Garfield': '49017', 'Grand': '49019', \
           'Iron': '49021', 'Juab': '49023', 'Kane': '49025', 'Millard': '49027', 'Morgan': '49029', \
           'Piute': '49031', 'Rich': '49033', 'SaltLake': '49035', 'SanJuan': '49037', 'Sanpete': '49039', \
           'Sevier': '49041', 'Summit': '49043', 'Tooele': '49045', 'Uintah': '49047', 'Utah': '49049', \
           'Wasatch': '49051', 'Washington': '49053', 'Wayne': '49055', 'Weber': '49057'}

typeList = ('ALY', 'AVE', 'BLVD', 'CIR', 'CT', 'CV', 'DR', 'EST', 'ESTS', 'EXPY', 'FWY', 'HWY', 'HOLW', \
            'JCT', 'LN', 'LOOP', 'PKWY', 'PL', 'PLZ', 'PT', 'RAMP', 'RNCH', 'RD', 'RTE', 'RUN', 'RW', 'SQ', \
            'ST', 'TER', 'TRL', 'WAY', 'HTS', 'COR')

typeList2 = ('ALLEY', 'AVENUE', 'BOULEVARD', 'CIRCLE', 'COURT', 'COVE', 'DRIVE', 'ESTATE', 'ESTATES', 'EXPRESSWAY', \
             'FREEWAY', 'HEIGHTS', 'HIGHWAY', 'HOLLOW', 'JUNCTION', 'LANE', 'LOOP', 'PARKWAY', 'PLACE', 'PLAZA', \
             'POINT', 'RAMP', 'RANCH', 'ROAD', 'ROUTE', 'RUN', 'ROW', 'SQUARE', 'STREET', 'TERRACE', 'TRAIL', 'WAY', 'CORNER')

typeDict = {'ALLEY': 'ALY', 'AVENUE': 'AVE', 'BOULEVARD': 'BLVD', 'CIRCLE': 'CIR', 'COURT': 'CT', 'COVE': 'CV', \
            'DRIVE': 'DR', 'ESTATE': 'EST', 'ESTATES': 'ESTS', 'EXPRESSWAY': 'EXPY', 'FREEWAY': 'FWY', 'HIGHWAY': 'HWY', \
            'HOLLOW': 'HOLW', 'JUNCTION': 'JCT', 'LANE': 'LN', 'LOOP': 'LOOP', 'PARKWAY': 'PKWY', 'PLACE': 'PL', \
            'PLAZA': 'PLZ', 'POINT': 'PT', 'RAMP': 'RAMP', 'RANCH': 'RNCH', 'ROAD': 'RD', 'ROUTE': 'RTE', 'RUN': 'RUN', \
            'ROW': 'RW', 'SQUARE': 'SQ', 'STREET': 'ST', 'TERRACE': 'TER', 'TRAIL': 'TRL', 'WAY': 'WAY', 'HEIGHTS': 'HTS', \
            'CORNER': 'COR'}

dirList = ('N', 'S', 'E', 'W')
dirList2 = ('NORTH', 'SOUTH', 'EAST', 'WEST')
dirDict = {'NORTH': 'N', 'SOUTH': 'S', 'EAST': 'E', 'WEST': 'W'}
errorList = [None, '', ' ', '<NULL>', '<NULL> ST']

date = str(datetime.datetime.today().strftime("%m%d%Y"))

def returnEmpty(word, badVals):
    if word == None:
        word = ''
    if word in badVals:
        word = ''
    return word

def removeNone(word):
    if word == None:
        word = ''
    return word

def formatValues(word, inValues):
    returnEmpty(word, errorList)
    if word != None:
        if word.strip() in inValues:
            return word.strip()
        return ''
    return ''

def delete_shape_flds(fc, shp_flds):
    for fld in shp_flds:
        if fld in [f.name for f in arcpy.ListFields(fc)]:
            arcpy.DeleteField_management(fc, fld)
            print(f'Deleted {fld} in {fc}')


def parcels_primary_and_secondary():
    print('Starting Parcels  ' + str(datetime.datetime.now()))

    idErrors = ['', None, '00-0000-000', '00-0000-0000', '0000000', '0', '00']

    '''-----Copy Parcels to SGID_GEOGRAPHIC staging area-----'''
    # {'Beaver':'49001', 'BoxElder':'49003', 'Cache':'49005', 'Carbon':'49007', 'Daggett':'49009',
    #  'Davis':'49011', 'Duchesne':'49013', 'Emery':'49015', 'Garfield':'49017', 'Grand':'49019',
    #  'Iron':'49021', 'Juab':'49023', 'Kane':'49025', 'Millard':'49027', 'Morgan':'49029',
    #  'Piute':'49031', 'Rich':'49033', 'SaltLake':'49035', 'SanJuan':'49037', 'Sanpete':'49039',
    #  'Sevier':'49041', 'Summit':'49043', 'Tooele':'49045', 'Uintah':'49047', 'Utah':'49049',
    #  'Wasatch':'49051', 'Washington':'49053', 'Wayne':'49055', 'Weber':'49057'}

    # parFipsDict = {'Davis':'49011', 'Morgan':'49029', 'SaltLake':'49035', 'Tooele':'49045', 'Utah':'49049',
    #                'Washington':'49053', 'Weber':'49057'}

    parFipsDict = {'Cache':'49005', 'Davis':'49011', 'Tooele':'49045', 'Utah':'49049', 'Washington':'49053', 'Weber':'49057'}


    for cnty in sorted(parFipsDict):

        with arcpy.EnvManager(workspace=stageDB):
            arcpy.env.overwriteOutput = True

            parBS_PrimaryOut = f'par{parFipsDict[cnty]}'
            parBS_SecondaryOut = f'par{parFipsDict[cnty]}_sec'

            if not arcpy.Exists(parBS_PrimaryOut):
                schemaFC = os.path.join(schemaDB, 'parSSCCC_schema')
                arcpy.CopyFeatures_management(schemaFC, parBS_out)
            if not arcpy.Exists(parBS_SecondaryOut):
                schemaFC = os.path.join(schemaDB, 'parSSCCC_schema')
                arcpy.CopyFeatures_management(schemaFC, parBS_SecondaryOut)

        with arcpy.EnvManager(workspace=sgid):
            arcpy.env.overwriteOutput = True

            parSGID = 'SGID.CADASTRE.Parcels_' + cnty
            parSGID_geo = os.path.join(sgid_GEO, f'Parcels_{cnty}')
            arcpy.CopyFeatures_management(parSGID, parSGID_geo)

            print(f'Repair Geometry {parSGID_geo}')
            arcpy.RepairGeometry_management(parSGID_geo)

            #-----Add address point addresses-----
            addAddressAttributes(sgid, parSGID_geo, cnty, parFipsDict, stageDB)

            disFLDS = ['PARCEL_ID', 'PARCEL_ADD']
            parSGID_geoDis = os.path.join(sgid_GEO, f'Parcels_{cnty}DIS')
            arcpy.Dissolve_management(parSGID_geo, parSGID_geoDis, disFLDS, '#', 'MULTI_PART')
            print('Done with dissolve')

            arcpy.TruncateTable_management(parBS_PrimaryOut)
            arcpy.TruncateTable_management(parBS_SecondaryOut)

            sgid_flds = ['PARCEL_ID', 'PARCEL_ADD', 'SHAPE@', 'OBJECTID', 'SHAPE@AREA']
            bs_flds = ['ADDR_NUMB', 'ADDR_FULL', 'FEDIRP', 'FENAME', 'FETYPE', 'FEDIRS', 'PARCEL_ID', 'SHAPE@']

            count_in_parcels = arcpy.GetCount_management(parSGID_geoDis)

            edit = arcpy.da.Editor(stageDB)
            edit.startEditing()
            edit.startOperation()

            icursor_primary = arcpy.da.InsertCursor(parBS_PrimaryOut, bs_flds)
            icursor_secondary = arcpy.da.InsertCursor(parBS_SecondaryOut, bs_flds)

            with arcpy.da.SearchCursor(parSGID_geoDis, sgid_flds) as scursor:

                for row in scursor:
                    if row[1] not in idErrors or row[0] not in idErrors:

                        parID = row[0]
                        addNum = ''
                        addFull = ''
                        preDir = ''
                        fename = ''
                        stype = ''
                        suf = ''

                        if row[1] not in idErrors:

                            addFull = row[1]
                            address = parse_address.parse(row[1])
                            addNum = address.houseNumber
                            if len(addNum) > 10:
                                addNum = ''
                            preDir = address.prefixDirection
                            fename = address.streetName
                            stype = address.suffixType
                            suf = address.suffixDirection

                        shp = row[2]

                        if addFull != '' and row[4] <= .0003:
                            icursor_primary.insertRow((addNum, addFull, preDir, fename, stype, suf, parID, shp))
                        else:
                            icursor_secondary.insertRow((addNum, addFull, preDir, fename, stype, suf, parID, shp))

            edit.stopOperation()
            edit.stopEditing(True)

        count_out_parcels = arcpy.GetCount_management(os.path.join(stageDB, parBS_PrimaryOut))
        count_difference = int(count_in_parcels[0]) - int(count_out_parcels[0])
        count_percent_diff = int(count_out_parcels[0]) / int(count_in_parcels[0]) * 100

        print(f'-----In parcels {count_in_parcels}')
        print(f'-----Out parcels {count_out_parcels}')
        print(f'-----Parcel difference {count_difference} or {round(count_percent_diff, 1)}%')

        parFips = parFipsDict[cnty]
        with arcpy.EnvManager(workspace=os.path.join(outLoc, f'TGR{parFips}')):
            arcpy.env.overwriteOutput = True

            parBS_PrimaryOutShp = os.path.join(outLoc, f'TGR{parFips}', f'par{parFips}.shp')
            parBS_SecondaryOutShp = os.path.join(outLoc, f'TGR{parFips}', f'par{parFips}_sec.shp')

            arcpy.CopyFeatures_management(os.path.join(stageDB, parBS_PrimaryOut), parBS_PrimaryOutShp)
            arcpy.CopyFeatures_management(os.path.join(stageDB, parBS_SecondaryOut), parBS_SecondaryOutShp)

            print(f'Copied {parBS_PrimaryOut} to county folder')
            print('')

    print ('Done Parcels  ' + str(datetime.datetime.now()))

def parcels_v1():
    print ('Starting Version One Code of Parcels  ' + str(datetime.datetime.now()))

    idErrors = ['', None, '00-0000-000', '00-0000-0000', '0000000', '0', '00']

    parFipsDict = {'Garfield':'49017', 'Rich':'49033', 'SanJuan':'49037'}

    for cnty in sorted(parFipsDict):

        with arcpy.EnvManager(workspace=stageDB):
            arcpy.env.overwriteOutput = True
            parBS_out = f'par{parFipsDict[cnty]}'
            if not arcpy.Exists(parBS_out):
                schemaFC = os.path.join(schemaDB, 'parSSCCC_schema')
                arcpy.CopyFeatures_management(schemaFC, parBS_out)

        with arcpy.EnvManager(workspace=sgid):
            arcpy.env.overwriteOutput = True

            parSGID = 'SGID.CADASTRE.Parcels_' + cnty # + '_LIR'
            parSGID_geo = os.path.join(sgid_GEO, f'Parcels_{cnty}')
            arcpy.CopyFeatures_management(parSGID, parSGID_geo)

            print (f'Repair Geometry {parSGID_geo}')
            arcpy.RepairGeometry_management(parSGID_geo)

            #-----Add address point addresses-----
            addAddressAttributes(sgid, parSGID_geo, cnty, parFipsDict, stageDB)

            disFLDS = ['PARCEL_ID', 'PARCEL_ADD']
            parSGID_geoDis = os.path.join(sgid_GEO, f'Parcels_{cnty}DIS')
            arcpy.Dissolve_management(parSGID_geo, parSGID_geoDis, disFLDS, '#', 'MULTI_PART')
            print ('Done with dissolve')

            arcpy.TruncateTable_management(parBS_out)

            srcFlds = ['PARCEL_ID', 'PARCEL_ADD', 'SHAPE@', 'OBJECTID', 'SHAPE@AREA']
            tarFlds = ['ADDR_NUMB', 'ADDR_FULL', 'FEDIRP', 'FENAME', 'FETYPE', 'FEDIRS', 'PARCEL_ID', 'SHAPE@']

            count_in_parcels = arcpy.GetCount_management(parSGID_geoDis)

            with arcpy.da.SearchCursor(parSGID_geoDis, srcFlds) as scursor, \
                arcpy.da.InsertCursor(parBS_out, tarFlds) as icursor:

                for row in scursor:
                    if row[1] not in idErrors or (row[0] not in idErrors and row[4] < .00007):

                        parID = row[0]
                        addNum = ''
                        addFull = ''
                        preDir = ''
                        fename = ''
                        stype = ''
                        suf = ''

                        if row[1] not in idErrors:

                            addFull = row[1]
                            address = parse_address.parse(row[1])
                            addNum = address.houseNumber
                            if len(addNum) > 10:
                                addNum = ''
                            preDir = address.prefixDirection
                            fename = address.streetName
                            stype = address.suffixType
                            suf = address.suffixDirection

                        shp = row[2]

                        icursor.insertRow((addNum, addFull, preDir, fename, stype, suf, parID, shp))

        count_out_parcels = arcpy.GetCount_management(os.path.join(stageDB, parBS_out))
        count_difference = int(count_in_parcels[0]) - int(count_out_parcels[0])
        count_percent_diff = int(count_out_parcels[0]) / int(count_in_parcels[0]) * 100

        print(f'-----In parcels {count_in_parcels}')
        print(f'-----Out parcels {count_out_parcels}')
        print(f'-----Parcel difference {count_difference} or {count_percent_diff}%')

        parFips = parFipsDict[cnty]
        with arcpy.EnvManager(workspace=os.path.join(outLoc, f'TGR{parFips}')):
            arcpy.env.overwriteOutput = True
            parBS_outShp = os.path.join(outLoc, f'TGR{parFips}', f'par{parFips}.shp')
            arcpy.CopyFeatures_management(os.path.join(stageDB, parBS_out), parBS_outShp)
            print(f'Copied {parBS_out} to county folder')
            print('')

    print ('Done with Version One Code of Parcels  ' + str(datetime.datetime.now()))

def addressPoints():

    print ('Starting Address Points  ' + str(datetime.datetime.now()))

    addptsSGID_geo = os.path.join(sgid_GEO, 'AddressPoints1')
    addPtsBS = os.path.join(stageDB, 'adr_StWide')

    with arcpy.EnvManager(workspace=sgid_GEO):
        arcpy.env.overwriteOutput = True
        #---Copy Address Points to SGID_GEOGRAPHIC staging area
        arcpy.CopyFeatures_management(os.path.join(sgid, 'SGID.LOCATION.AddressPoints'), addptsSGID_geo)

    with arcpy.EnvManager(workspace=stageDB):
        arcpy.env.overwriteOutput = True
        #---Check for statewide Address Points in BlueStakes schema
        if not arcpy.Exists(addPtsBS):
            arcpy.CopyFeatures_management(os.path.join(schemaDB, 'adrSSCCC_schema'), addPtsBS)
        else:
            arcpy.TruncateTable_management(addPtsBS)
            print('Empty bluestakes address points ready')

        flds = ['FullAdd', 'AddNum', 'PrefixDir', 'StreetName', 'StreetType', 'SuffixDir', 'SHAPE@']
        outFlds = ['ADDR_NUMB', 'ADDR_FULL', 'FEDIRP', 'FENAME', 'FETYPE', 'FEDIRS', 'OWNER', 'SHAPE@']

        with arcpy.da.SearchCursor(addptsSGID_geo, flds) as scursor, \
            arcpy.da.InsertCursor(addPtsBS, outFlds) as icursor:

            for row in scursor:
                ADDR_NUMB = removeNone(row[1])
                ADDR_FULL = removeNone(row[0])
                FEDIRP = removeNone(row[2])
                FENAME = removeNone(row[3])
                FETYPE = removeNone(row[4])
                FEDIRS = removeNone(row[5])
                OWNER = ''
                shp = row[6]

                icursor.insertRow((ADDR_NUMB, ADDR_FULL, FEDIRP, FENAME, FETYPE, FEDIRS, OWNER, shp))

        #---Copy State wide address points to Bluestakes root---------------
        arcpy.CopyFeatures_management(addPtsBS, os.path.join(outLoc, 'adr_StWide.shp'))

        #---Clip by county-------------------------------------------
        clip(addPtsBS, 'adr', '')

    print('Done Translating Address Points  ' + str(datetime.datetime.now()))
    print()

def roads():
    print('Starting Roads  ' + str(datetime.datetime.now()))

    global annoRdSegsSELECT
    annoRdSegsSELECT = r'C:\ZBECK\BlueStakes\stagingBS.gdb\DOMINION_GEOGRAPHIC\RoadSegs_DominionSelect'

    from DominionLabelConverter import createDominionAnnoRds
    from DominionLabelConverter import outputSelectDominionRdSegs

    env.workspace = sgid
    arcpy.env.overwriteOutput = True

    roadsSGID = os.path.join(sgid_GEO, 'Roads')
    roadsBS = os.path.join(stageDB, 'TGR_StWide_lkA')

    #----Move Roads to SGID_GEOGRAPHIC staging area
    with arcpy.EnvManager(workspace=sgid):
        arcpy.env.overwriteOutput = True
        arcpy.CopyFeatures_management('SGID.TRANSPORTATION.Roads', roadsSGID)
        print('Copied roads to StagingDB')

    # ----Check for statewide BlueStakes roads
    if not arcpy.Exists(roadsBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'TGRSSCCClkA_schema'), roadsBS)
    else:
        arcpy.TruncateTable_management(roadsBS)

    srcFlds = ['CARTOCODE', 'PREDIR', 'FULLNAME', 'POSTTYPE', 'POSTDIR', 'FROMADDR_L', 'TOADDR_L', 'FROMADDR_R', \
               'TOADDR_R', 'A1_NAME', 'A2_NAME', 'AN_NAME', 'AN_POSTDIR', 'COUNTY_L', 'DOT_HWYNAM', 'UPDATED', \
               'ADDRSYS_L', 'NAME', 'SHAPE@', 'A1_POSTTYPE', 'A2_POSTTYPE', 'COUNTY_R', 'ADDRSYS_R', 'INCMUNI_L']

    tarFlds = ['FEDIRP', 'FENAME', 'FETYPE', 'FEDIRS', 'CFCC', 'FRADDL', 'TOADDL', 'FRADDR', 'TOADDR', 'CFCC1',
               'CFCC2', 'FULLNAME', 'HASALT', 'ISALT', 'S_FIPS', 'AGRC_MDATE', 'ADDRESS_SY', 'SHAPE@']

    replaceDict = {'Sr ': 'SR ', 'SR-': 'SR ', 'Sr-': 'SR ', 'Usfs': 'USFS', 'Us ': 'US ', 'Usu ': 'USU ', 'Rr': 'RR', 'Usaf': 'USAF',
                   'Fs': 'FS', 'Blm': 'BLM', 'Mvc': 'MVC'}

    errorList = [None, '', ' ', '<NULL>', '<NULL> ST', '<Null>']

    print ('Start inserting rows')

    def replacePropCase(string, dict):
        for i in dict:
            if i in string:
                return string.replace(i, dict[i])
        return string

    # ----Format HasAlt isAlt values----
    def checkAlt(inRow):

        alias1 = srcRow[9]
        alias2 = srcRow[10]
        aname = srcRow[11]
        acsname = '{} {}'.format(srcRow[11], srcRow[12])

        if alias1 not in errorList:
            return '1'
        if alias2 not in errorList:
            return '1'
        if acsname not in errorList:
            return '1'
        if srcRow[2] not in errorList and srcRow[2][-3:] == 'FWY':
            return '1'
        if srcRow[2] not in errorList and srcRow[2][:3] == 'HWY':
            return '1'
        if srcRow[2] not in errorList and srcRow[2][:3] == 'US ':
            return '1'
        else:
            return '0'

    # ----RegEx to format street avbreviations (i.e. ST RD TH --> st rd th)----
    def lowerAbrev(inRow):
        return inRow.group(0).lower()

    # ---RegEx to format route directions (i.e. Nb Wb --> NB WB)
    def upperAbrev(inRow):
        return inRow.group(0).upper()

    tarRows = arcpy.da.InsertCursor(roadsBS, tarFlds)

    manilaRds = ['1ST', '2ND', '3RD', '4TH', '5TH']
    CartoToCFCC = {'1':'A15', '2':'A20', '3':'A21', '4':'A25', '5':'A20', '6':'A41', '7':'A20', '8':'A31',
                   '9':'A41', '10':'A41', '11':'A41', '12':'A41', '13':'A65', '14':'A74', '15':'A99',
                   '16':'A41', '17':'A41', '18':'A41', '99':'A99'}

    with arcpy.da.SearchCursor(roadsSGID, srcFlds) as srcRows:
        for srcRow in srcRows:

            #----Prefix Direction----
            FEDIRP = formatValues(srcRow[1], dirList)

            #----Sufix Direction----
            FEDIRS = formatValues(srcRow[4], dirList)

            FULLNAME = ''

            #----Root and Full Street Name----
            if srcRow[2] not in errorList:
                FULLNAME = '{} {}'.format(FEDIRP, srcRow[2].title()).strip()

                if srcRow[23] == 'Manila' and srcRow[2].strip() in manilaRds:
                    FULLNAME = '{} {} {}'.format(FEDIRP, srcRow[2].title().strip(), FEDIRS)

            elif srcRow[3] == 'RAMP':
                FULLNAME = srcRow[2].title()

            FULLNAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, FULLNAME, flags=re.IGNORECASE)
            FULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, FULLNAME, flags=re.IGNORECASE)
            FULLNAME = replacePropCase(FULLNAME, replaceDict)

            if srcRow[17] != None:
                FENAME =  srcRow[17].title()
                FENAME = replacePropCase(FENAME, replaceDict)
                FENAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, FENAME, flags=re.IGNORECASE)
                FENAME = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, FENAME, flags=re.IGNORECASE)
            else:
                FENAME = ''

            #----Street Type----
            FETYPE = formatValues(srcRow[3], typeList).title()

            #----CFCC----
            if srcRow[0] != None:
                CFCC = CartoToCFCC[srcRow[0]]
                CFCC1 = 'A'
                CFCC2 = CFCC[:2]

            #----From Address Left----
            if srcRow[5] != None:
                FRADDL = str(srcRow[5]).split('.')[0]
            else:
                FRADDL = 0

            #----To Address Left----
            if srcRow[6] != None:
                TOADDL = str(srcRow[6]).split('.')[0]
            else:
                TOADDL = 0

            #----From Address Right----
            if srcRow[7] != None:
                FRADDR = str(srcRow[7]).split('.')[0]
            else:
                FRADDR = 0

            #----To Address Right----
            if srcRow[8] != None:
                TOADDR = str(srcRow[8]).split('.')[0]
            else:
                TOADDR = 0

            #----FIPS----
            fips13 = returnEmpty(srcRow[13], errorList)
            fips21 = returnEmpty(srcRow[21], errorList)
            if fips13.isdigit() == False:
                S_FIPS = 0
            elif fips13 != fips21:
                S_FIPS = 9999
            else:
                S_FIPS = fips13

            #----AGRC M Date----
            if srcRow[15] != None:
                AGRC_MDATE = srcRow[15]
            else:
                AGRC_MDATE = '1/1/1000'

            #----Address System----
            if srcRow[16] != srcRow[22]:
                ADDRESS_SY = '{} / {} BORDER'.format(srcRow[16], srcRow[22])
            else:
                ADDRESS_SY = returnEmpty(srcRow[16], errorList)

            #----Has Alt Name----
            HASALT = checkAlt(srcRow)
            ISALT = '0'

            shp = srcRow[18]

            tarRows.insertRow((FEDIRP, FENAME, FETYPE, FEDIRS, CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME, HASALT, \
                               ISALT, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))


            #----Add Duplicate SR US and Interstate Highways---------------
            if srcRow[14] not in errorList:
                addHWY = srcRow[14]

                if FEDIRP != None:
                    FULLNAME_hwy = '{} {}'.format(FEDIRP, addHWY).strip() #FEDIRP + ' ' + addHWY
                else:
                    FULLNAME_hwy = addHWY.strip()

                FULLNAME_hwy = replacePropCase(FULLNAME_hwy, replaceDict)

                tarRows.insertRow((FEDIRP, addHWY, '', '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME_hwy, \
                                   0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))

                if addHWY[:2] == 'SR':
                    if srcRow[2][:3] != 'HWY':
                        addHWY = addHWY.replace('SR', 'Hwy')
                        FULLNAME_hwy = FULLNAME_hwy.replace('SR', 'Hwy')

                        tarRows.insertRow((FEDIRP, addHWY, '', '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME_hwy, \
                                           0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))

                if addHWY[:3] == 'US ':
                    if srcRow[2][:3] != 'HWY':
                        addHWY = addHWY.replace('US', 'Hwy')
                        FULLNAME_hwy = FULLNAME_hwy.replace('US', 'Hwy')

                        tarRows.insertRow((FEDIRP, addHWY, '', '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME_hwy, \
                                           0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))


            #----Add Duplicate Alias1 and ACSAlias----
            if srcRow[9] not in errorList and srcRow[23] != 'Manila':
                if srcRow[9][:7] != 'HIGHWAY':
                    alsFENAME = srcRow[9].title()
                    alsFENAME = replacePropCase(alsFENAME, replaceDict)
                    alsFENAME = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, alsFENAME, flags=re.IGNORECASE)

                    if srcRow[19] != None:
                        FETYPE = srcRow[19].title()

                    if FEDIRP != None:
                        FULLNAME_a1 = '{} {}'.format(FEDIRP, alsFENAME).strip()  #FEDIRP + ' ' + alsFENAME #+ ' ZZ4'

                    if FEDIRP != None and srcRow[12] != None:
                        FULLNAME_a1 = '{} {} {}'.format(FEDIRP, alsFENAME, srcRow[12][:1]).strip()   #FEDIRP + ' ' + alsFENAME + ' ' + srcRow[12][:1]

                    if FEDIRP != None and FETYPE != None:
                        FULLNAME_a1 = '{} {} {}'.format(FEDIRP, alsFENAME, FETYPE).strip()       #FEDIRP + ' ' + alsFENAME + ' ' + FETYPE

                    if FEDIRP == None and FETYPE != None:
                        FULLNAME_a1 = '{} {}'.format(alsFENAME, FETYPE).strip()  #alsFENAME + ' ' + FETYPE

                    FULLNAME_a1 = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, FULLNAME_a1, flags=re.IGNORECASE).strip()
                    FULLNAME_a1 = replacePropCase(FULLNAME_a1, replaceDict)

                    tarRows.insertRow((FEDIRP, alsFENAME, FETYPE, '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, \
                                       FULLNAME_a1, 0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))


            #----Add Duplicate Alias2----
            if srcRow[10] not in errorList and srcRow[23] != 'Manila':
                if srcRow[10][:7] != 'HIGHWAY':
                    als2FENAME = srcRow[10].title()
                    FENAME2 = replacePropCase(als2FENAME, replaceDict)
                    FENAME2 = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, FENAME2, flags=re.IGNORECASE)

                    if srcRow[20] != None:
                        FETYPE = srcRow[20].title()

                    if FEDIRP != None:
                        FULLNAME_a2 = '{} {}'.format(FEDIRP, FENAME2).strip()  #FEDIRP + ' ' + modFENAME2

                    if FEDIRP != None and srcRow[12] != None:
                        FULLNAME_a2 = '{} {} {}'.format(FEDIRP, FENAME2, srcRow[12][:1]).strip()  #FEDIRP + ' ' + modFENAME2 + ' ' + srcRow[12][:1]

                    if FEDIRP != None and FETYPE != None:
                        FULLNAME_a2 = '{} {} {}'.format(FEDIRP, FENAME2, FETYPE).strip()  #FEDIRP + ' ' + modFENAME2 + ' ' + FETYPE

                    if FEDIRP == None and FETYPE != None:
                        FULLNAME_a2 = '{} {}'.format(FENAME2, FETYPE)  #modFENAME2 + ' ' + FETYPE

                    FULLNAME_a2 = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, FULLNAME_a2, flags=re.IGNORECASE)
                    FULLNAME_a2 = replacePropCase(FULLNAME_a2, replaceDict)


                    tarRows.insertRow((FEDIRP, FENAME2, FETYPE, '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, \
                                       FULLNAME_a2, 0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))


            if srcRow[12] not in errorList and srcRow[23] != 'Manila':
                if srcRow[11] not in errorList:
                    acsFENAME = srcRow[11]

                    if FEDIRP not in errorList and srcRow[12] != None:
                        FULLNAME_acs = '{} {} {}'.format(srcRow[1], acsFENAME, srcRow[12][:1])   #srcRow[1] + ' ' + acsFENAME + ' ' + srcRow[12][:1]
                    elif srcRow[12] != None:
                        FULLNAME_acs = '{} {}'.format(acsFENAME, srcRow[12][:1]) #acsFENAME + ' ' + srcRow[12][:1]
                    else:
                        FULLNAME_acs = acsFENAME

                    if srcRow[12] != None:
                        FEDIRS = srcRow[12]
                    else:
                        FEDIRS = None

                    FULLNAME_acs = replacePropCase(FULLNAME_acs, replaceDict)

                    tarRows.insertRow((FEDIRP, acsFENAME, '', FEDIRS, CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME_acs, \
                                       0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))

        del tarRows
        del srcRows

    createDominionAnnoRds()
    outputSelectDominionRdSegs(roadsSGID)

     #---Add Dominion Road Segments------------
    count = int(arcpy.GetCount_management(annoRdSegsSELECT).getOutput(0))
    if count > 1:
        print('Appending {} Dominion Road Segments'.format(count))
        arcpy.Append_management(annoRdSegsSELECT, roadsBS, 'NO_TEST')
    else:
        print('NO DOMINION ROAD SEGMENTS ADDED')

     #---Copy Roads to Blues Stakes root level-----------------
    arcpy.CopyFeatures_management(roadsBS, os.path.join(outLoc, 'TGR_StWide_lkA.shp'))
    print('Copied BS roads to output folder')

    #---Clip Blue Stakes Roads-----------------------------------------------------------
    print('Start Clipping Roads')
    clip(roadsBS, '', 'lkA');

    print('Done Translating Roads  ' + str(datetime.datetime.now()))

def municipalities():

    print('Starting Municipalities  ' + str(datetime.datetime.now()))

    munisWithAFB = os.path.join(sgid_GEO, 'Municipalities')
    muni = os.path.join(sgid_GEO, 'Municipalities_AFBclipped')
    muniBS = os.path.join(stageDB, 'TGR_StWide_plc00')
    hillAFB = os.path.join(sgid_GEO, 'HillAFB')
    metroTownships = os.path.join(sgid_GEO, 'MetroTownships')
    cedarHighlandsBS = os.path.join(sgid_GEO, 'CedarHighlands_plc00')

    with arcpy.EnvManager(workspace=sgid):
        arcpy.env.overwriteOutput = True
        #---Copy Municipalites and Townships to SGID_GEOGRAPHIC staging area
        arcpy.CopyFeatures_management('SGID.BOUNDARIES.Municipalities', munisWithAFB)
        arcpy.CopyFeatures_management('SGID.BOUNDARIES.MetroTownships', metroTownships)

    #---Clip out Hill Air force Base
    arcpy.Erase_analysis(munisWithAFB, hillAFB, muni)

    #---Check for statewide municipalities BlueStakes schema
    if not arcpy.Exists(muniBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'TGRSSCCCplc00_schema', muniBS))
    else:
        arcpy.TruncateTable_management(muniBS)

    muniFlds = ['NAME', 'SHAPE@']
    outFlds = ['NAME', 'SHAPE@']
    twnshipFlds = ['NAME', 'SHAPE@']

    with arcpy.da.SearchCursor(muni, muniFlds) as scursor, \
        arcpy.da.InsertCursor(muniBS, outFlds) as icursor:
            for row in scursor:
                name = row[0].replace('St.', 'St')
                shp = row[1]
                icursor.insertRow((name, shp))

    with arcpy.da.SearchCursor(metroTownships, twnshipFlds) as scursor, \
        arcpy.da.InsertCursor(muniBS, outFlds) as icursor:
            for row in scursor:
                name = row[0].title()
                shp = row[1]
                icursor.insertRow((name, shp))

    arcpy.Append_management(cedarHighlandsBS, muniBS, 'NO_TEST')

    #---Copy Municipalities to Blues Stakes root level
    arcpy.CopyFeatures_management(muniBS, os.path.join(outLoc, 'TGR_StWide_plc00.shp'))

    delete_shape_flds(os.path.join(outLoc, 'TGR_StWide_plc00.shp'), ['Shape_Area', 'Shape_Leng', 'SHAPE_Leng', 'SHAPE_Area'])

    #---Clip Blue Stakes Municipalities----------
    clip(muniBS, '', 'plc00');

    print ('Done Translating Municipalities  ' + str(datetime.datetime.now()))

def mileposts():

    print ('Starting Mileposts  ' + str(datetime.datetime.now()))
    
    milePosts = os.path.join(sgid_GEO, 'UDOTMilePosts')
    exits = os.path.join(sgid_GEO, 'Roads_FreewayExits')
    milePostsBS = os.path.join(stageDB, 'Hwy_MPM')

    with arcpy.EnvManager(workspace=sgid):
        arcpy.env.overwriteOutput = True
        #---Copy new Exits and Mileposts to Staging DB
        arcpy.CopyFeatures_management('SGID.TRANSPORTATION.Roads_FreewayExits', exits)
        arcpy.CopyFeatures_management('SGID.TRANSPORTATION.UDOTMileposts', milePosts)
        print ('Copied SGID.TRANSPORTATION.Roads_FreewayExits to staging DB')
        print ('Copied SGID.TRANSPORTATION.UDOTMileposts to staging DB')


    #---Check for Mileposts BlueStakes schema
    if not arcpy.Exists(milePostsBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'Hwy_MPM', milePostsBS))
    else:
        arcpy.TruncateTable_management(milePostsBS)

    mp_flds = ['LABEL', 'MP', 'CARTO', 'RT_DIR', 'SHAPE@']
    exit_flds = ['EXITNAME', 'SHAPE@']
    bs_flds = ['Type', 'Label_Name', 'SHAPE@']

    with arcpy.da.SearchCursor(milePosts, mp_flds) as scursor, \
        arcpy.da.InsertCursor(milePostsBS, bs_flds) as icursor:

        for row in scursor:

            Type = 'mpm'

            hwyDig1 = row[0][3:4]
            hwyDig2 = row[0][2:4]
            hwyDig3 = row[0][1:4]
            mp = str(row[1]).split('.')[0]

            if row[3] == 'N':
                Label_Name = ''
            elif row[2] == '1' and row[3] == 'P':
                if row[0][1:4] == '215':
                    Label_Name = f'I-{hwyDig3} milepost {mp}'
                else:
                    Label_Name = f'I-{hwyDig2} milepost {mp}'
            else:
                if row[0][:3] == '000':
                    Label_Name = f'Hwy {hwyDig1} milepost {mp}'
                elif row[0][:2] == '00':
                    Label_Name = f'Hwy {hwyDig2} milepost {mp}'
                else:
                    Label_Name = f'Hwy {hwyDig3} milepost {mp}'

            shp = row[4]

            icursor.insertRow((Type, Label_Name, shp))

    #----Add Exit Records--------------------------------------------
    with arcpy.da.SearchCursor(exits, exit_flds) as scursor, \
        arcpy.da.InsertCursor(milePostsBS, bs_flds) as icursor:
        for row in scursor:

            Type = 'epm'

            if row[0].split()[0] == 'SR':
                Label_Name = 'Hwy ' + ' '.join(row[0].split()[1:])
            elif row[0].split()[0] == 'US':
                Label_Name = 'Hwy ' + ' '.join(row[0].split()[1:])
            else:
                Label_Name = row[0]

            shp = row[1]

            icursor.insertRow((Type, Label_Name, shp))

    #----Copy Mileposts to shapefile---------------------------------
    arcpy.CopyFeatures_management(milePostsBS, os.path.join(outLoc, 'Hwy_MPM.shp'))

    print('Done Translating Mileposts  ' + str(datetime.datetime.now()))

def milepostsCombined():
    print('Starting Mileposts  ' + str(datetime.datetime.now()))

    milePosts = os.path.join(sgid_GEO, 'UDOTMilePosts')
    exits = os.path.join(sgid_GEO, 'Roads_FreewayExits')
    rr_MilePosts = os.path.join(sgid_GEO, 'Railroad_Mileposts')
    milePostsHwyRR_BS = os.path.join(stageDB, 'HwyRR_MPM')

    with arcpy.EnvManager(workspace=sgid):
        arcpy.env.overwriteOutput = True

        # ---Copy new Exits and Mileposts to Staging DB
        arcpy.CopyFeatures_management('SGID.TRANSPORTATION.Roads_FreewayExits', exits)
        arcpy.CopyFeatures_management('SGID.TRANSPORTATION.UDOTMileposts', milePosts)
        arcpy.CopyFeatures_management('SGID.TRANSPORTATION.Railroad_Mileposts', rr_MilePosts)
        print('Copied SGID.TRANSPORTATION.Roads_FreewayExits to staging DB')
        print('Copied SGID.TRANSPORTATION.UDOTMileposts to staging DB')
        print('Copied SGID.TRANSPORTATION.Railroad_Mileposts to staging DB')

    # ---Check for Mileposts BlueStakes schema
    if not arcpy.Exists(milePostsHwyRR_BS):
        arcpy.CopyFeatures_management(schemaDB + '\\Hwy_MPM', milePostsHwyRR_BS)
    else:
        arcpy.TruncateTable_management(milePostsHwyRR_BS)

    mp_flds = ['LABEL', 'MP', 'CARTO', 'RT_DIR', 'SHAPE@']
    exit_flds = ['EXITNAME', 'SHAPE@', 'EXITNBR']
    RRmp_flds = ['DIVISION', 'RR_Milepos', 'SHAPE@']
    bs_flds = ['NAME', 'LABEL', 'CFCC', 'SHAPE@']

    # ----Add RR Mileposts-----------------------------------------------
    with arcpy.da.SearchCursor(rr_MilePosts, RRmp_flds) as scursor, \
        arcpy.da.InsertCursor(milePostsHwyRR_BS, bs_flds) as icursor:
        for row in scursor:
            if '.' not in row[1]:
                lbl = row[1]
                name = f'{row[0].title()} Division milepost {lbl}'
                cfcc = 'P11'
                shp = row[2]

                icursor.insertRow((name, lbl, cfcc, shp))

    # ----Add Milepost Records-------------------------------------------
    with arcpy.da.SearchCursor(milePosts, mp_flds) as scursor, \
        arcpy.da.InsertCursor(milePostsHwyRR_BS, bs_flds) as icursor:

        for row in scursor:
            cfcc = 'P10'

            hwyDig1 = row[0][3:4]
            hwyDig2 = row[0][2:4]
            hwyDig3 = row[0][1:4]
            mp = str(row[1]).split('.')[0]

            if row[3] == 'N':
                name = ''
            elif row[2] == '1' and row[3] == 'P':
                if row[0][1:4] == '215':
                    name = f'I-{hwyDig3} milepost {mp}'
                else:
                    name = f'I-{hwyDig2} milepost {mp}'
            else:
                if row[0][:3] == '000':
                    name = f'Hwy {hwyDig1} milepost {mp}'
                elif row[0][:2] == '00':
                    name = f'Hwy {hwyDig2} milepost {mp}'
                else:
                    name = f'Hwy {hwyDig3} milepost {mp}'

            shp = row[4]

            icursor.insertRow((name, mp, cfcc, shp))

    # ----Add Exit Records-----------------------------------------------
    with arcpy.da.SearchCursor(exits, exit_flds) as scursor, \
        arcpy.da.InsertCursor(milePostsHwyRR_BS, bs_flds) as icursor:
        for row in scursor:
            if row[2] != None:

                cfcc = 'P20'
                lbl = row[2]

                if row[0].split()[0] == 'SR':
                    name = 'Hwy ' + ' '.join(row[0].split()[1:])
                elif row[0].split()[0] == 'US':
                    name = 'Hwy ' + ' '.join(row[0].split()[1:])
                else:
                    name = row[0]

                shp = row[1]

                icursor.insertRow((name, lbl, cfcc, shp))

    # ----Copy Mileposts to shapefile----------------------------------------
    arcpy.CopyFeatures_management(milePostsHwyRR_BS, os.path.join(outLoc, 'HwyRR_MPM.shp'))

    clip(milePostsHwyRR_BS, '', 'pts');

    print ('Done Translating Mileposts  ' + str(datetime.datetime.now()))

def landownershipLarge():

    print ('Starting Large Landownership  ' + str(datetime.datetime.now()))

    landown = os.path.join(sgid_GEO, 'LandOwnership')
    parks = os.path.join(sgid_GEO, 'Parks')
    cemeteries = os.path.join(sgid_GEO, 'Cemeteries')
    golf = os.path.join(sgid_GEO, 'GolfCourses')

    landownBS = os.path.join(stageDB, 'TGR_StWide_lpy')

    #---Copy Landownership, Parks, and Cemeteries to SGID_GEOGRAPHIC staging area
    with arcpy.EnvManager(workspace=sgid):
        arcpy.env.overwriteOutput = True

        arcpy.CopyFeatures_management('SGID.CADASTRE.LandOwnership', landown)
        arcpy.CopyFeatures_management('SGID.RECREATION.ParksLocal', parks)
        arcpy.CopyFeatures_management('SGID.SOCIETY.Cemeteries_Poly', cemeteries)
        arcpy.CopyFeatures_management('SGID.RECREATION.GolfCourses', golf)

    #---Check for statewide Large Landownership BlueStakes schema
    if not arcpy.Exists(landownBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCClpy_schema', landownBS)
    else:
        arcpy.TruncateTable_management(landownBS)


    landown_flds = ['OWNER', 'DESIG', 'LABEL_STATE', 'LABEL_FEDERAL', 'STATE_LGD', 'SHAPE@']
    park_flds = ['NAME', 'SHAPE@']
    cemetery_flds = ['Name', 'SHAPE@']
    golf_flds = ['NAME', 'SHAPE@']

    bs_flds = ['CFCC', 'LANDNAME', 'SHAPE@']

    monType = ['National Historic Site', 'National Monument', 'National Park', 'National Recreation Area']
    primType = ['Primitive Area', 'Wilderness', 'Wildlife Reserve/Management Area', 'National Wildlife Refuge']

    #----Add Land Ownership-------------------------------------
    print('Adding Land Ownership')
    with arcpy.da.SearchCursor(landown, landown_flds) as scursor, \
        arcpy.da.InsertCursor(landownBS, bs_flds) as icursor:
        for row in scursor:

            if row[0] == 'Tribal':
                CFCC = 'D40'

                if row[3] != None:
                    LANDNAME = row[3].title()
                else:
                    LANDNAME = row[4]

                shp = row[5]


            elif row[1] == 'Military':
                CFCC = 'D10'

                if row[3] != None:
                    LANDNAME = row[3].title()
                else:
                    LANDNAME = row[4]

                shp = row[5]


            elif row[1] in monType:
                CFCC = 'D83'

                if row[3] != None:
                    LANDNAME = row[3].title()
                else:
                    LANDNAME = row[4]

                shp = row[5]

            elif row[1] == 'National Forest':
                CFCC = 'D84'

                if row[3] != None:
                    LANDNAME = row[3].title()
                else:
                    LANDNAME = row[4].title()

                shp = row[5]

            
            elif row[1] in primType:
                CFCC = 'D89'

                if row[3] != None:
                    LANDNAME = row[3].title()
                else:
                    LANDNAME = row[4].title()

                shp = row[5]


            elif row[1] == 'Parks and Recreation' and row[0] == 'State':
                CFCC = 'D85'

                if row[2] != None:
                    LANDNAME = row[2].title()
                else:
                    LANDNAME = row[4]

                shp = row[5]

            else:
                continue

            icursor.insertRow((CFCC, LANDNAME, shp))

    #------Add Golf Courses----------------------------------------
    print('Adding Golf Courses')
    with arcpy.da.SearchCursor(golf, golf_flds) as scursor, \
        arcpy.da.InsertCursor(landownBS, bs_flds) as icursor:

        for row in scursor:

            CFCC = 'D81'
            LANDNAME = removeNone(row[0])
            shp = row[1]

            icursor.insertRow((CFCC, LANDNAME, shp))

    #-----Add Cemeteries--------------------------------------------
    print('Adding Cemeteries')
    with arcpy.da.SearchCursor(cemeteries, cemetery_flds) as scursor, \
        arcpy.da.InsertCursor(landownBS, bs_flds) as icursor:

        for row in scursor:

            CFCC = 'D82'
            LANDNAME = removeNone(row[0])
            shp = row[1]

            icursor.insertRow((CFCC, LANDNAME, shp))

    #-----Add Parks--------------------------------------------
    print('Adding Parks')
    with arcpy.da.SearchCursor(parks, park_flds) as scursor, \
        arcpy.da.InsertCursor(landownBS, bs_flds) as icursor:

        for row in scursor:

            CFCC = 'D85'
            LANDNAME = removeNone(row[0])
            shp = row[1]

            icursor.insertRow((CFCC, LANDNAME, shp))


    #---Copy Landownership to Blue Stakes root level
    arcpy.CopyFeatures_management(landownBS, os.path.join(outLoc, 'TGR_StWide_lpy.shp'))

    delete_shape_flds(os.path.join(outLoc, 'TGR_StWide_lpy.shp'), ['Shape_Area', 'Shape_Leng', 'SHAPE_Leng', 'SHAPE_Area'])


    #---Clip Blue Stakes Landonwership-------------------------------------------------
    clip(landownBS, '', '_lpy')



    print ('Done Translating Large Landownership  ' + str(datetime.datetime.now()))

def waterPoly():

    print ('Starting Lakes  ' + str(datetime.datetime.now()))

    lakes = os.path.join(sgid_GEO, 'LakesNHDHighRes')
    lakesBS = os.path.join(stageDB, 'TGR_StWide_wat')

    #---Copy lakesNHD to SGID_GEOGRAPHIC staging area
    with arcpy.EnvManager(workspace=sgid):
        arcpy.CopyFeatures_management('SGID.WATER.LakesNHDHighRes', lakes)

    #---Check for statewide lakes BlueStakes schema
    if not arcpy.Exists(lakesBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCCWAT_schema', lakesBS)
    else:
        arcpy.TruncateTable_management(lakesBS)

    lakes_flds = ['FCode', 'GNIS_Name', 'InUtah', 'SHAPE@']
    lakesBS_flds = ['CFCC', 'LANDNAME', 'SHAPE@']

    h30_lake = [39000, 39004, 39005, 39006, 39009, 39010, 39011]
    h40_reservoir = [39012, 43600, 43601, 43607, 43616, 43619, 43623, 43624, 43625]

    with arcpy.da.SearchCursor(lakes, lakes_flds) as scursor, \
        arcpy.da.InsertCursor(lakesBS, lakesBS_flds) as icursor:
        for row in scursor:

            if row[2] == 1:

                if row[0] == 36100:
                    cfcc = 'H32'
                    if row[1] != None:
                        landname = row[1]
                    else:
                        landname = 'Playa'

                elif row[0] == 39001:
                    cfcc = 'H32'
                    if row[1] != None:
                        landname = row[1]
                    else:
                        landname = 'Intermittent Salt Lake/Pond'

                elif row[0] in h30_lake:
                    cfcc = 'H30'
                    if row[1] != None:
                        landname = row[1]
                    else:
                        landname = 'Lake/Pond'

                elif row[0] in h40_reservoir:
                    cfcc = 'H40'
                    if row[1] != None:
                        landname = row[1]
                    else:
                        landname = 'Reservoir'

                elif row[0] == 43612:
                    cfcc = 'H40'
                    if row[1] != None:
                        landname = row[1]
                    else:
                        landname = 'Sewage Treatment Pond'

                elif row[0] == 43613:
                    cfcc = 'H40'
                    if row[1] != None:
                        landname = row[1]
                    else:
                        landname = 'Covered Reservoir'

                else:
                    continue

                shp = row[3]

                icursor.insertRow((cfcc, landname, shp))


    #---Copy Lakes to Blue Stakes root level---------------
    arcpy.CopyFeatures_management(lakesBS, os.path.join(outLoc, 'TGR_StWide_WAT.shp'))

    delete_shape_flds(os.path.join(outLoc, 'TGR_StWide_WAT.shp'), ['Shape_Area', 'Shape_Leng', 'SHAPE_Leng', 'SHAPE_Area'])


    #---Clip Blue Stakes Misc Transportation----------------
    clip(lakesBS, '', 'WAT');


    print ('Done Translating Lakes  ' + str(datetime.datetime.now()))

def waterLines():

    print ('Starting Rivers  ' + str(datetime.datetime.now()))

    rivers = os.path.join(sgid_GEO, 'StreamsNHD')
    riversBS = os.path.join(stageDB, 'TGR_StWide_lkH')

    with arcpy.EnvManager(workspace=sgid):
        arcpy.CopyFeatures_management('SGID.WATER.StreamsNHDHighRes', rivers)

    #---Check for Rivers BlueStakes schema
    if not arcpy.Exists(riversBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'TGRSSCCClkH_schema'), riversBS)
    else:
        arcpy.TruncateTable_management(riversBS)

    river_flds = ['GNIS_Name', 'FCode', 'InUtah', 'SHAPE@', 'Submerged']
    riverBS_flds = ['FENAME', 'CFCC2', 'SHAPE@']

    with arcpy.da.SearchCursor(rivers, river_flds) as scursor, \
        arcpy.da.InsertCursor(riversBS, riverBS_flds) as icursor:

        for row in scursor:

            if row[2] == 1:

                if row[4] == 0:

                    if row[1] == 46003:
                        cfcc = 'H2'
                        if row[0] != None:
                            fename = row[0]
                        else:
                            fename = 'unknown'

                    if row[1] != 46003:
                        cfcc = 'H1'
                        if row[0] != None:
                            fename = row[0]
                        else:
                            fename = 'unknown'

                    shp = row[3]

                    icursor.insertRow((fename, cfcc, shp))


    #---Copy Rivers to Blue Stakes root level---------------
    arcpy.CopyFeatures_management(riversBS, os.path.join(outLoc, 'TGR_StWide_lkH.shp'))

    delete_shape_flds(os.path.join(outLoc, 'TGR_StWide_lkH.shp'), ['Shape_Leng', 'SHAPE_Leng'])

    #---Clip Blue Stakes Misc Transportation----------------
    clip(riversBS, '', 'lkH');


    print ('Done Translating Rivers  ' + str(datetime.datetime.now()))

def railroads():

    print ('Starting Railroads  ' + str(datetime.datetime.now()))

    rail = os.path.join(sgid_GEO, 'Railroads')
    railTrax = os.path.join(sgid_GEO, 'LightRail_UTA')
    railCommuter = os.path.join(sgid_GEO, 'CommuterRailRoute_UTA')

    railBS = os.path.join(stageDB , 'TGR_StWide_lkB')

    #---Check for statewide railroad BlueStakes schema
    if not arcpy.Exists(railBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'TGRSSCCClkB_schema'), railBS)
    else:
        arcpy.TruncateTable_management(railBS)


    with arcpy.EnvManager(workspace=sgid):
        arcpy.env.overwriteOutput = True

        arcpy.CopyFeatures_management('SGID.TRANSPORTATION.Railroads', rail)
        arcpy.CopyFeatures_management('SGID.TRANSPORTATION.LightRail_UTA', railTrax)
        arcpy.CopyFeatures_management('SGID.TRANSPORTATION.CommuterRailRoutes_UTA', railCommuter)


    rr_flds = ['RAILROAD', 'SHAPE@']
    uta_flds = ['SHAPE@']

    railBS_flds = ['FENAME', 'CFCC2', 'SHAPE@']


    #---Add Railroads---------------------------------
    with arcpy.da.SearchCursor(rail, rr_flds) as scursor, \
        arcpy.da.InsertCursor(railBS, railBS_flds) as icursor:
        for row in scursor:

            if row[0] != 'UTA' and row[0] != 'UT Transit Auth':

                FENAME = row[0]
                CFCC2 = 'B1'
                shp = row[1]

                icursor.insertRow((FENAME, CFCC2, shp))

    #----Add Light Rail-------------------------------
    with arcpy.da.SearchCursor(railTrax, uta_flds) as scursor, \
        arcpy.da.InsertCursor(railBS, railBS_flds) as icursor:
        for row in scursor:

            FENAME = 'UTA Trax light rail'
            CFCC2 = 'B1'
            shp = row[0]

            icursor.insertRow((FENAME, CFCC2, shp))

    #----Add Commuter Rail------------------------------------
    with arcpy.da.SearchCursor(railCommuter, uta_flds) as scursor, \
        arcpy.da.InsertCursor(railBS, railBS_flds) as icursor:
        for row in scursor:

            FENAME = 'UTA Frontrunner railroad'
            CFCC2 = 'B1'
            shp = row[0]

            icursor.insertRow((FENAME, CFCC2, shp))

    #---Copy Railroads to Blue Stakes root level----------------------
    arcpy.CopyFeatures_management(railBS, os.path.join(outLoc, 'TGR_StWide_lkB.shp'))

    delete_shape_flds(os.path.join(outLoc, 'TGR_StWide_lkB.shp'), ['Shape_Leng', 'SHAPE_Leng'])


    #---Clip Blue Stakes Railroads-----------------------------------------------------------
    clip(railBS, '', 'lkB');

    print ('Done Translating Railroads  ' + str(datetime.datetime.now()))

def airstrips():

    print ('Starting Airstrips  ' + str(datetime.datetime.now()))

    airstrips = os.path.join(sgid_GEO, 'Airports')
    airstripsBS = os.path.join(stageDB, 'TGR_StWide_lkD')


    #---Check for statewide airports BlueStakes schema
    if not arcpy.Exists(airstripsBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'TGRSSCCClkD_schema'), airstripsBS)
    else:
        arcpy.TruncateTable_management(airstripsBS)

    with arcpy.EnvManager(workspace=sgid):

        arcpy.CopyFeatures_management('SGID.TRANSPORTATION.Airports', airstrips)

    sgid_flds = ['FAC_TYPE', 'FULLNAME', 'SHAPE@']
    bs_flds = ['FENAME', 'CFCC2', 'SHAPE@']


    with arcpy.da.SearchCursor(airstrips, sgid_flds) as scursor, \
        arcpy.da.InsertCursor(airstripsBS, bs_flds) as icursor:
        for row in scursor:

            if row[0] == 'AIRPORT':
                FENAME = f'{row[1]} {row[0]}'.replace('MUNI', 'MUNICIPAL')

            else:
                FENAME = row[1]

            CFCC2 = 'D5'

            shp = row[2]

            icursor.insertRow((FENAME, CFCC2, shp))

    #---Copy Airstrips to Blue Stakes root level-------------------------
    arcpy.CopyFeatures_management(airstripsBS, os.path.join(outLoc, 'TRG_StWide_lkD.shp'))

    delete_shape_flds(os.path.join(outLoc, 'TRG_StWide_lkD.shp'), ['Shape_Leng', 'SHAPE_Leng'])

    #---Clip Blue Stakes Airstrips---------------------------------------
    clip(airstripsBS, '', 'lkD');


    print ('Done Translating Airstrips  ' + str(datetime.datetime.now()))

def miscTransportation():

    print ('Starting Misc Transportation  ' + str(datetime.datetime.now()))

    ski_lifts = os.path.join(sgid_GEO, 'SkiLifts')
    transmission_lines = os.path.join(sgid_GEO, 'TransmissionLines')
    electric_lines = os.path.join(sgid_GEO, 'ElectricLines')
    dominion_parcelsBS = os.path.join(stageDB, 'DOMINION_GEOGRAPHIC\Parcels_Dominion')
    source_dominion = r'C:\ZBECK\BlueStakes\DominionEnergy\DEUWI_BlueStakes_UGRC.gdb\Property'
    miscTransBS = os.path.join(stageDB, 'TGR_StWide_lkC')

    #---Load Dominion parcels from past year---
    count = int(arcpy.GetCount_management(dominion_parcelsBS).getOutput(0))
    if count > 1:
        print (count)
        arcpy.TruncateTable_management(dominion_parcelsBS)
        print ('Truncated Dominion Parcels')

    today = datetime.datetime.now()

    flds = ['OBJECTID', 'DATECREATED', 'DATEMODIFIED', 'SHAPE@', 'SUBTYPECD']
    iFlds = ['DATECREATED', 'DATEMODIFIED', 'SUBTYPECD', 'SHAPE@']

    with arcpy.da.SearchCursor(source_dominion, flds) as scursor, \
        arcpy.da.InsertCursor(dominion_parcelsBS, iFlds) as icursor:
        for row in scursor:
            oid = row[0]

            dateC = row[1]
            if dateC in [None, '']:
                dateC = datetime.datetime.strptime('9/9/1973', '%m/%d/%Y')
            dateM = row[2]
            if dateM in [None, '']:
                dateM = datetime.datetime.strptime('9/9/1973', '%m/%d/%Y')

            propType = row[4]

            if dateC >= dateM:
                dateC_delta = today - dateC
                #print(row[0], today, dateC, dateC_delta)
                if int(str(dateC_delta).split()[0]) < 366:
                    icursor.insertRow((dateC, None, propType, row[3]))
            elif dateM != '9/9/1973':
                dateM_delta = today - dateM
                if int(str(dateM_delta).split()[0]) < 366:
                    icursor.insertRow((None, dateM, propType, row[3]))
            else:
                print (oid)


    with arcpy.EnvManager(workspace=sgid):
        arcpy.env.overwriteOutput = True
        arcpy.CopyFeatures_management('SGID.RECREATION.SkiLifts', ski_lifts)
        arcpy.CopyFeatures_management('SGID.UTILITIES.TransmissionLines', transmission_lines)
        arcpy.CopyFeatures_management('SGID.UTILITIES.ElectricalLines', electric_lines)
        print ('Copied SkiLifts, TransmissionLines, ElectricalLines')


    #---Check for statewide misc transportation BlueStakes schema
    if not arcpy.Exists(miscTransBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'TGRSSCCClkC_schema'), miscTransBS)
    else:
        arcpy.TruncateTable_management(miscTransBS)

    ski_flds = ['LIFT_NAME', 'SHAPE@']
    transmission_flds = ['LAYER', 'SHAPE@']
    electric_flds = ['SHAPE@']
    dominion_flds = ['SHAPE@']
    bs_flds = ['FENAME', 'CFCC2', 'SHAPE@']

    #-------Ski lifts--------
    with arcpy.da.SearchCursor(ski_lifts, ski_flds) as scursor, \
        arcpy.da.InsertCursor(miscTransBS, bs_flds) as icursor:

        for row in scursor:

            fename = row[0] + ' Ski Lift'
            cfcc2 = 'C3'
            shp = row[1]

            icursor.insertRow((fename, cfcc2, shp))


    #-------Transmission Lines---------
    with arcpy.da.SearchCursor(transmission_lines, transmission_flds) as scursor, \
        arcpy.da.InsertCursor(miscTransBS, bs_flds) as icursor:

        badVals = ['SUB-CO', 'SUB-PP']

        for row in scursor:
            if row[0] not in badVals:
                fename = 'Overhead Power Line Corridor'
                cfcc2 = 'C2'
                shp = row[1]
            else:
                continue

            icursor.insertRow((fename, cfcc2, shp))


    #-------Electrical Lines---------
    with arcpy.da.SearchCursor(electric_lines, electric_flds) as scursor, \
        arcpy.da.InsertCursor(miscTransBS, bs_flds) as icursor:

        for row in scursor:
            fename = 'Overhead Power Line Corridor'
            cfcc2 = 'C2'
            shp = row[0]

            icursor.insertRow((fename, cfcc2, shp))


    #--------Dominion Parcels---------
    dominion_roads = r'C:\ZBECK\BlueStakes\stagingBS.gdb\DOMINION_GEOGRAPHIC\RoadSegs_DominionSelect'
    dominion_roads_FL = arcpy.MakeFeatureLayer_management(dominion_roads, 'dominion_roads_FL')

    dominion_parcelsBS_FL = arcpy.MakeFeatureLayer_management(dominion_parcelsBS, 'dominion_parcelsBS')

    arcpy.SelectLayerByLocation_management(dominion_parcelsBS_FL, 'WITHIN_A_DISTANCE', \
                                           dominion_roads_FL, '175 Meters')

    selected = arcpy.GetCount_management(dominion_parcelsBS_FL)
    selCount = int(selected.getOutput(0))
    print (selCount)

    with arcpy.da.SearchCursor(dominion_parcelsBS_FL, 'SHAPE@') as scursor, \
        arcpy.da.InsertCursor(miscTransBS, bs_flds) as icursor:
        for row in scursor:
            fename = ''
            cfcc2 = 'A9'
            shp = row[0]

            icursor.insertRow((fename, cfcc2, shp))


    #---Copy Misc Trans to Blue Stakes root level---------------
    arcpy.CopyFeatures_management(miscTransBS, os.path.join(outLoc, 'TGR_StWide_lkC.shp'))

    #---Clip Blue Stakes Misc Transportation-----------------------------------------------------------
    clip(miscTransBS, '', 'lkC');


    print ('Done Translating Misc Transportation  ' + str(datetime.datetime.now()))

def townships():

    print ('Starting Townships  ' + str(datetime.datetime.now()))

    twnShips = os.path.join(sgid_GEO, 'PLSSTownships')
    twnShipsBS = os.path.join(stageDB, 'UT_TR')

    #---Copy Townships in SGID_GEOGRAPHIC staging area
    with arcpy.EnvManager(workspace=sgid):
        arcpy.CopyFeatures_management('SGID.CADASTRE.PLSSTownships_GCDB', twnShips)

    #---Check for statewide township BlueStakes schema
    if not arcpy.Exists(twnShipsBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'UT_TR_schema'), twnShipsBS)
    else:
        arcpy.TruncateTable_management(twnShipsBS)

    sgid_flds = ['BASEMERIDIAN', 'LABEL', 'SHAPE@']
    bs_flds = ['NAME', 'SHAPE@']

    with arcpy.da.SearchCursor(twnShips, sgid_flds) as scursor, \
        arcpy.da.InsertCursor(twnShipsBS, bs_flds) as icursor:
        for row in scursor:

            name = ('SL' if row[0] == '26' else 'UI') + ' ' + row[1]
            shp = row[2]

            icursor.insertRow((name, shp))

    #---Export to shapefile-------------------------------------------
    outTwnshps = os.path.join(outLoc, 'UT_TR.shp')
    arcpy.CopyFeatures_management(twnShipsBS, outTwnshps)
    delete_shape_flds(outTwnshps, ['Shape_Area', 'Shape_Leng'])

    print ('Done Translating Townships  ' + str(datetime.datetime.now()))

def sections():

    print ('Starting Sections  ' + str(datetime.datetime.now()))

    meridianDict = {'26':'SL', '30':'UI'}

    sections = os.path.join(sgid_GEO, 'PLSSSections')
    sectionsBS = os.path.join(stageDB, 'UT_TRS')

    #---Move Sections to SGID_GEOGRAPHIC staging area
    with arcpy.EnvManager(workspace=sgid):
        arcpy.CopyFeatures_management('SGID.CADASTRE.PLSSSections_GCDB', sections)

    #---Check for statewide BlueStakes sections
    if not arcpy.Exists(sectionsBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'UT_TRS_schema'), sectionsBS)
    else:
        arcpy.TruncateTable_management(sectionsBS)

    sgid_flds = ['SNUM', 'BASEMERIDIAN', 'LABEL', 'SHAPE@']
    bs_flds = ['NAME', 'FULLNAME', 'SHAPE@']

    with arcpy.da.SearchCursor(sections, sgid_flds) as scursor, \
        arcpy.da.InsertCursor(sectionsBS, bs_flds) as icursor:
        for row in scursor:

            name = row[0]

            if row[1] in meridianDict:
                base_meridian = meridianDict[row[1]]
                full_name = f'{base_meridian} {row[2]} SEC {name}'
            else:
                continue

            shp = row[3]

            icursor.insertRow((name, full_name, shp))


    #---Export to shapefile-------------------------------------------
    outSections = os.path.join(outLoc, 'UT_TRS.shp')
    arcpy.CopyFeatures_management(sectionsBS, outSections)

    delete_shape_flds(outSections, ['Shape_Area', 'Shape_Leng'])


    print ('Done Translating Sections  ' + str(datetime.datetime.now()))

def deciPoints():

    print ('Starting Deci Points (GNIS) ' + str(datetime.datetime.now()))

    gnis = os.path.join(sgid_GEO, 'PlaceNamesGNIS')
    deciPts = os.path.join(stageDB, 'TGR_StWide_deci')

    #---Move GNIS to SGID_GEOGRAPHIC staging area
    with arcpy.EnvManager(workspace=sgid):
        arcpy.CopyFeatures_management('SGID.LOCATION.PlaceNamesGNIS', gnis)

    #---Check for statewide Deci Points BlueStakes schema
    if not arcpy.Exists(deciPts):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'TGRSSCCCdeci_schema'), deciPts)
    else:
        arcpy.TruncateTable_management(deciPts)

    flds = ['NAME', 'SHAPE@']

    with arcpy.da.SearchCursor(gnis, flds) as scursor, \
        arcpy.da.InsertCursor(deciPts, flds) as icursor:
        for row in scursor:

            name = removeNone(row[0])

            shp = row[1]

            icursor.insertRow((name, shp))


    #---Copy Deci Points to Blue Stakes root level---------------
    arcpy.CopyFeatures_management(deciPts, os.path.join(outLoc, 'TGR_StWide_deci.shp'))

    #---Clip Blue Stakes Deci Points-----------------------------------------------------------
    clip(deciPts, '', 'deci');


    print ('Done Translating Deci Points (GNIS) ' + str(datetime.datetime.now()))

def addedPoints():

    print ('Starting Added Points ' + str(datetime.datetime.now()))

    correctionsPts = os.path.join(sgid_GEO, 'CorrectionalFacilities')
    fireStnPts = os.path.join(sgid_GEO, 'FireStations')
    libraryPts = os.path.join(sgid_GEO, 'PublicLibraries')
    liquorPts = os.path.join(sgid_GEO, 'LiquorStores')
    policePts = os.path.join(sgid_GEO, 'PoliceStations')
    postOfficePts = os.path.join(sgid_GEO, 'PostOffices')
    schoolPts = os.path.join(sgid_GEO, 'Schools_preKto12')
    schoolHigherEdPts = os.path.join(sgid_GEO, 'Schools_HigherEd')
    healthCarePts = os.path.join(sgid_GEO, 'HealthCareFacilities')
    # churchPts = os.path.join(sgid_GEO, 'PlacesOfWorship') No longer in SGID
    # mallPts = os.path.join(sgid_GEO, 'ShoppingMalls') No longer in SGID

    addedPtsBS = os.path.join(stageDB, 'TGR_StWide_added')

    #---Move Points to SGID_GEOGRAPHIC staging area
    with arcpy.EnvManager(workspace=sgid):
        arcpy.env.overwriteOutput = True

        arcpy.CopyFeatures_management('SGID.SOCIETY.CorrectionalFacilities', correctionsPts)
        arcpy.CopyFeatures_management('SGID.SOCIETY.FireStations', fireStnPts)
        arcpy.CopyFeatures_management('SGID.SOCIETY.PublicLibraries', libraryPts)
        arcpy.CopyFeatures_management('SGID.SOCIETY.LiquorStores', liquorPts)
        arcpy.CopyFeatures_management('SGID.SOCIETY.LawEnforcement', policePts)
        arcpy.CopyFeatures_management('SGID.SOCIETY.PostOffices', postOfficePts)
        arcpy.CopyFeatures_management('SGID.SOCIETY.Schools_PreKto12', schoolPts)
        arcpy.CopyFeatures_management('SGID.SOCIETY.Schools_HigherEducation', schoolHigherEdPts)
        arcpy.CopyFeatures_management('SGID.HEALTH.HealthCareFacilities', healthCarePts)
        # arcpy.CopyFeatures_management('SGID.SOCIETY.PlacesOfWorship', churchPts) No longer in SGID
        # arcpy.CopyFeatures_management('SGID.SOCIETY.ShoppingMalls', mallPts) No longer in SGID
        print ('Done copying features from SGID to staging area')

    #---Check for statewide Deci Points BlueStakes schema
    if not arcpy.Exists(addedPtsBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'TGRSSCCCdeci_schema'), addedPtsBS)
    else:
        arcpy.DeleteFeatures_management(addedPtsBS)


    bs_flds = ['NAME', 'SHAPE@']

    pointFC_List = [correctionsPts, policePts, fireStnPts, healthCarePts]

    #---Loop through feature classes that have common fields-------
    for pointFC in pointFC_List:

        agrc_flds = ['NAME', 'SHAPE@']
        with arcpy.da.SearchCursor(pointFC, agrc_flds) as scursor, \
            arcpy.da.InsertCursor(addedPtsBS, bs_flds) as icursor:
            for row in scursor:
                if row[0] != None:
                    if len(row[0]) > 79:
                        NAME = row[0].title().replace('United States', 'U.S.')[:79]
                    else:
                        NAME = row[0].title().replace('United States', 'U.S.')
                else:
                    NAME = ''

                shp = row[1]

                icursor.insertRow((NAME, shp))

            print ('Added ' + pointFC)

    library_flds = ['LIBRARY', 'SHAPE@']
    with arcpy.da.SearchCursor(libraryPts, library_flds) as scursor, \
        arcpy.da.InsertCursor(addedPtsBS, bs_flds) as icursor:
        for row in scursor:
            if row[0] != None:
                NAME = row[0]
            else:
                NAME = 'Public Library'

            shp = row[1]

            icursor.insertRow((NAME, shp))

    print ('Added ' + libraryPts)


    liquor_flds = ['TYPE', 'SHAPE@']
    with arcpy.da.SearchCursor(liquorPts, liquor_flds) as scursor, \
        arcpy.da.InsertCursor(addedPtsBS, bs_flds) as icursor:
        for row in scursor:
            if row[0] != None:
                NAME = row[0]
            else:
                NAME = 'Liquor Store'

            shp = row[1]

            icursor.insertRow((NAME, shp))

    print ('Added ' + liquorPts)


    post_office_flds = ['TOWN', 'SHAPE@']
    with arcpy.da.SearchCursor(postOfficePts, post_office_flds) as scursor, \
        arcpy.da.InsertCursor(addedPtsBS, bs_flds) as icursor:
        for row in scursor:

            NAME = f'{removeNone(row[0])} Post Office'.strip()

            shp = row[1]

            icursor.insertRow((NAME, shp))

    print ('Added ' + postOfficePts)


    school_flds = ['SchoolName', 'SHAPE@']
    with arcpy.da.SearchCursor(schoolPts, school_flds) as scursor, \
        arcpy.da.InsertCursor(addedPtsBS, bs_flds) as icursor:

        for row in scursor:
            NAME = removeNone(row[0]).title()
            if len(NAME) > 79:
                print(f'truncating {NAME}')
                NAME = NAME[:79]

            shp = row[1]

            icursor.insertRow((NAME, shp))

    print ('Added ' + schoolPts)


    with arcpy.da.SearchCursor(schoolHigherEdPts, school_flds) as scursor, \
        arcpy.da.InsertCursor(addedPtsBS, bs_flds) as icursor:

        for row in scursor:
            NAME = removeNone(row[0]).title()
            if len(NAME) > 79:
                print(f'truncating {NAME}')
                NAME = NAME[:79]

            shp = row[1]

            icursor.insertRow((NAME, shp))

    print ('Added ' + schoolHigherEdPts)



    #---Copy Added Points to Blue Stakes root level---------------
    arcpy.CopyFeatures_management(addedPtsBS, os.path.join(outLoc, 'TGR_StWide_added.shp'))

    #---Clip Blue Stakes Deci Points-----------------------------------------------------------
    clip(addedPtsBS, '', 'added');


    print ('Done Translating Added Points ' + str(datetime.datetime.now()))

def counties():

    print ('Starting Counties ' + str(datetime.datetime.now()))

    cnty = os.path.join(sgid_GEO, 'Counties')
    utah = os.path.join(sgid_GEO, 'Utah')
    cntyBS = os.path.join(stageDB, 'TGRSSCCCcty00')
    cntyBS_All = os.path.join(stageDB, 'CO49_D90')
    stateBS = os.path.join(stageDB, 'ST49_D00')

    #---Move Utah boundary to SGID_GEOGRAPHIC staging area
    with arcpy.EnvManager(workspace=sgid_GEO):
        arcpy.env.overwriteOutput = True
        arcpy.CopyFeatures_management(os.path.join(sgid, 'SGID.BOUNDARIES.Utah'), utah)

    #---Check for County BlueStakes schema
    if not arcpy.Exists(cntyBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'TGRSSCCCcty00_schema'), cntyBS)
    if not arcpy.Exists(cntyBS_All):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'CO49_D90_schema'), cntyBS_All)
    if not arcpy.Exists(stateBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'ST49_D00_schema'), stateBS)
    else:
        arcpy.TruncateTable_management(cntyBS)
        arcpy.TruncateTable_management(cntyBS_All)
        arcpy.TruncateTable_management(stateBS)

    sgid_cnty_flds = ['NAME', 'SHAPE@', 'FIPS_STR']
    sgid_ut_flds = ['STATE', 'SHAPE@']
    cntySingleFlds = ['COUNTY', 'SHAPE@']
    cntyAllFlds = ['NAME', 'ST', 'CO', 'SHAPE@']
    stFlds = ['NAME', 'STATE', 'SHAPE@']

    #---Create individual county shapefiles----------------------
    with arcpy.da.SearchCursor(cnty, sgid_cnty_flds) as scursor, \
        arcpy.da.InsertCursor(cntyBS, cntySingleFlds) as icursor:

        for row in scursor:
            county = row[0]
            shp = row[1]
            icursor.insertRow((county, shp))

    with arcpy.da.SearchCursor(cntyBS, cntySingleFlds) as scursor:

        export_count = 0
        for row in scursor:

            cnty_name = ''.join(row[0].title().split())
            out_fldr = os.path.join(outLoc, f'TGR{fipsDict[cnty_name]}')

            with arcpy.EnvManager(workspace=out_fldr):
                arcpy.env.overwriteOutput = True

                out_cnty_shp = f'TGR{fipsDict[cnty_name]}cty00.shp'
                sql = f'"COUNTY" = \'{row[0]}\''

                cnty_fl = arcpy.MakeFeatureLayer_management(cntyBS, f'{cnty_name}_fl', sql)
                arcpy.CopyFeatures_management(cnty_fl, out_cnty_shp)

                export_count += 1

                delete_shape_flds(out_cnty_shp, ['Shape_Area', 'SHAPE_Area', 'Shape_Leng', 'SHAPE_Leng'])

    print(f'{export_count} counties exported to shapefiles')

    #---Create Statewide County Shapefile------------------------------
    with arcpy.da.SearchCursor(cnty, sgid_cnty_flds) as scursor, \
        arcpy.da.InsertCursor(cntyBS_All, cntyAllFlds) as icursor:

        for row in scursor:
            name = row[0]
            st = '49'
            co = row[2][-3:]
            shp = row[1]

            icursor.insertRow((name, st, co, shp))

    cntyBS_All_shp = os.path.join(outLoc, 'CO49_D90.shp')
    arcpy.CopyFeatures_management(cntyBS_All, cntyBS_All_shp)
    delete_shape_flds(cntyBS_All_shp, ['Shape_Area', 'Shape_Leng'])

    #---Create State shapfile-------------------------------------------
    with arcpy.da.SearchCursor(utah, sgid_ut_flds) as scursor, \
        arcpy.da.InsertCursor(stateBS, stFlds) as icursor:
        for row in scursor:
            if row[0] == 'Utah':

                name = 'Utah'
                st = '49'
                shp = row[1]

                icursor.insertRow((name, st, shp))

    stateBS_shp = outLoc + '\\ST49_D00.shp'
    arcpy.CopyFeatures_management(stateBS, stateBS_shp)
    delete_shape_flds(stateBS_shp, ['Shape_Area', 'Shape_Leng'])

    print ('Done Translating Counties ' + str(datetime.datetime.now()))

def addressZones():

    print ('Starting Address Zones  ' + str(datetime.datetime.now()))

    addZones = os.path.join(sgid_GEO, 'AddressSystemQuadrants')
    addZonesBS = os.path.join(stageDB, 'addrsys')

    #---Add Address Zones to SGID_GEOGRAPHIC staging area
    with arcpy.EnvManager(workspace=sgid):
        arcpy.env.overwriteOutput = True
        arcpy.CopyFeatures_management('SGID.LOCATION.AddressSystemQuadrants', addZones)

    #---Check for Address Zones BlueStakes schema
    if not arcpy.Exists(addZonesBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'addrsys_schema'), addZonesBS)
    else:
        arcpy.TruncateTable_management(addZonesBS)

    sgid_flds = ['GRID_NAME', 'QUADRANT', 'SHAPE@']
    bs_flds = ['NAME', 'SHAPE@']

    empty = [None, '', ' ']

    with arcpy.da.SearchCursor(addZones, sgid_flds) as scursor, \
        arcpy.da.InsertCursor(addZonesBS, bs_flds) as icursor:
        for row in scursor:
            if row[0] not in empty:
                if row[1] not in empty:
                    name = f'{row[0]} {row[1]}'
                else:
                    name = row[0]
            shp = row[2]

            icursor.insertRow((name, shp))


    #---Copy Address Zones to Blues Stakes root level
    arcpy.CopyFeatures_management(addZonesBS, os.path.join(outLoc, 'addrsys_StWide.shp'))

    #---Clip by county--------------------------------
    clip(addZonesBS, 'addrsys', '')

    # clpFlds = ['NAME', 'FIPS_STR', 'SHAPE@']
    # clpRows = arcpy.da.SearchCursor(clpCnty, clpFlds)

    # for row in clpRows:
    #     clpFeat = row[2]

    #     #----Delete shapefiles with no features----
    #     clp = arcpy.Clip_analysis(addZonesBS, clpFeat, outLoc + '\\TGR' + row[1] + '\\addrsys' + row[1] + '.shp')
    #     clpCount = int(arcpy.GetCount_management(clp).getOutput(0))

    #     if clpCount < 1:
    #         arcpy.Delete_management(clp)

    #     flds = arcpy.ListFields(clp)
    #     for fld in flds:
    #         if fld.name == 'Shape_Area':
    #             arcpy.DeleteField_management(clp, 'Shape_Area')
    #         if fld.name == 'Shape_Leng':
    #             arcpy.DeleteField_management(clp, 'Shape_Leng')


    print ('Done Translating Address Zones  ' + str(datetime.datetime.now()))

def oilAndGasWells():

    print ('Starting Oil and Gas  ' + str(datetime.datetime.now()))

    og = os.path.join(sgid_GEO, 'DNROilGasWells')
    ogBS = os.path.join(stageDB, 'wells_oil_gas')

    with arcpy.EnvManager(workspace=sgid):
        arcpy.env.overwriteOutput = True
        arcpy.CopyFeatures_management('SGID.ENERGY.OilGasWells', og)

    #---Check for BlueStakes schema
    if not arcpy.Exists(ogBS):
        arcpy.CopyFeatures_management(os.path.join(schemaDB, 'OilGasWells_Schema', ogBS))
    else:
        arcpy.TruncateTable_management(ogBS)

    srcFlds = ['API', 'WellName', 'FieldName', 'Operator', 'Latitude', 'Longitude', 'SHAPE@']
    tarFlds = ['API', 'NAME', 'FIELD', 'OPERATOR', 'LATITUDE', 'LONGITUDE', 'SHAPE@']

    srcRows = arcpy.da.SearchCursor(og, srcFlds)
    tarRows = arcpy.da.InsertCursor(ogBS, tarFlds)

    for srow in srcRows:

        api = srow[0]
        name = srow[1]
        field = srow[2]
        operator = srow[3]
        latitude = srow[4]
        longitude = srow[5]
        shp = srow[6]

        tarRows.insertRow((api, name, field, operator, latitude, longitude, shp))

    del tarRows

     #----Copy Oil & Gas wells to shapefile--------------------------------------------------
    arcpy.CopyFeatures_management(ogBS, outLoc + '\\wells_oil_gas.shp')

    #---Clip Blue Stakes Oil and Gas Wells----------------------------------------------------
    clip(ogBS, '', 'ogw')


def clip(clipMe, outNamePrefix, outNameSuffix):

    counties = os.path.join(sgid_GEO, 'Counties')

    with arcpy.EnvManager(workspace=outLoc):
        arcpy.env.overwriteOutput = True

        #---Clip Blue Stakes output, delete empty shapefiles, delete Shape_Leng field----
        print (f'Clipping {clipMe}')

        clpFlds = ['NAME', 'FIPS_STR', 'SHAPE@']
        clpRows = arcpy.da.SearchCursor(counties, clpFlds)

        for row in clpRows:
            clpShp = row[2]
            print (f'Clipping {row[0]} County')

            outFldr = f'TGR{row[1]}'
            if outNamePrefix == '':
                outClippedFC = os.path.join(outLoc, outFldr, f'TGR{row[1]}{outNameSuffix}.shp')
                arcpy.Clip_analysis(clipMe, clpShp, outClippedFC)
            else:
                outClippedFC = os.path.join(outLoc, outFldr, f'{outNamePrefix}{row[1]}.shp')
                arcpy.Clip_analysis(clipMe, clpShp, outClippedFC)

            delete_shape_flds(outClippedFC, ['Shape_Area', 'SHAPE_Area', 'Shape_Leng', 'SHAPE_Leng', 'SHAPE_Le_1'])

            #----Delete shapefiles with no features----
            clpCount = int(arcpy.GetCount_management(outClippedFC).getOutput(0))
            if clpCount < 1:
                print(f'NO FEATURES IN {outClippedFC}')
                arcpy.Delete_management(outClippedFC)


def cleanOutFldr():
    #----Delete all shapefiles from----
    for root, dirs, files in os.walk(outLoc):
        for f in files:
            deleteme = os.path.join(root, f)
            print (f'Deleted {deleteme}')
            os.remove(deleteme)

def copyCounties():
    #----Copy SGID county boundaries to staging DB----
    print('Moving county boundaries to staging area')
    counties = os.path.join(sgid_GEO, 'Counties')
    with arcpy.EnvManager(workspace=sgid_GEO):
        arcpy.env.overwriteOutput = True

        arcpy.CopyFeatures_management(os.path.join(sgid, 'SGID.BOUNDARIES.Counties'), counties)


# cleanOutFldr()
# copyCounties()

parcels_primary_and_secondary();
#parcels_v1(); '''old parcel version, don't run unless requested'''
# counties(); #Last updated 6/23/2020
roads(); #Last updated 6/24/2020
# addressPoints(); #Last updated 6/24/2020
# municipalities(); #Last updated 6/23/2020
# mileposts(); #Last updated 6/24/2020
# milepostsCombined() #Last updated 6/24/2020
# landownershipLarge(); #Last updated 6/23/2020
# waterPoly(); #Last updated 6/24/2020
# waterLines(); #Last updated 6/23/2020
# railroads(); #Last updated 6/23/2020
# airstrips(); #Last updated 6/23/2020
miscTransportation(); #Last updated 6/24/2020
# townships(); #Last updated 6/23/2020
# sections(); #Last updated 6/23/2020
# deciPoints(); #Last updated 6/23/2020
# addedPoints(); #Last updated 6/23/2020
# addressZones(); #Last updated 6/23/2020
# oilAndGasWells(); #Last updated 6/23/2020

