import os, arcpy, datetime, time, re
from arcpy import env
from arcpy import da
from agrc import parse_address
from AddressAttributes import addAddressAttributes

sgid = r'C:\sde\SGID_internal\SGID_agrc.sde'
sgid_GEO = r'C:\ZBECK\BlueStakes\stagingBS.gdb\SGID_GEOGRAPHIC'
stageDB = r'C:\ZBECK\BlueStakes\stagingBS.gdb'
schemaDB = r'C:\ZBECK\BlueStakes\schemaBS.gdb'
outLoc = r'C:\ZBECK\BlueStakes\outBlueStakes'

with arcpy.EnvManager(workspace=sgid_GEO):
    arcpy.env.overwriteOutput = True
    clpCnty = os.path.join(sgid_GEO, 'Counties')
    if arcpy.Exists(clpCnty):
        arcpy.Delete_management(clpCnty)
        arcpy.CopyFeatures_management(os.path.join(sgid, 'SGID.BOUNDARIES.Counties'), clpCnty)
        print('copied new counties')
    else:
        arcpy.CopyFeatures_management(os.path.join(sgid, 'SGID.BOUNDARIES.Counties'), clpCnty)


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

def parcels():
    print ('Starting Parcels  ' + str(datetime.datetime.now()))

    idErrors = ['', None, '00-0000-000', '00-0000-0000', '0000000', '0', '00']

    #-----Copy Parcels to SGID_GEOGRAPHIC staging area-----
    # {'Beaver':'49001', 'BoxElder':'49003', 'Cache':'49005', 'Carbon':'49007', 'Daggett':'49009',
    #  'Davis':'49011', 'Duchesne':'49013', 'Emery':'49015', 'Garfield':'49017', 'Grand':'49019',
    #  'Iron':'49021', 'Juab':'49023', 'Kane':'49025', 'Millard':'49027', 'Morgan':'49029',
    #  'Piute':'49031', 'Rich':'49033', 'SaltLake':'49035', 'SanJuan':'49037', 'Sanpete':'49039',
    #  'Sevier':'49041', 'Summit':'49043', 'Tooele':'49045', 'Uintah':'49047', 'Utah':'49049',
    #  'Wasatch':'49051', 'Washington':'49053', 'Wayne':'49055', 'Weber':'49057'}

    parFipsDict = {'Davis':'49011', 'Grand':'49019', 'Kane':'49025', 'SaltLake':'49035',\
                   'Summit':'49043', 'Utah':'49049', 'Washington':'49053', 'Weber':'49057'}


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

    print ('Done Parcels  ' + str(datetime.datetime.now()))

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
            print ('Empty bluestakes address points ready')

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

    roadsSGID = sgid_GEO + '\\Roads'
    roadsBS = stageDB + '\\TGR_StWide_lkA'

    #----Move Roads to SGID_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID.TRANSPORTATION.Roads', roadsSGID)
    print('Copied roads to StagingDB')

    # ----Check for statewide BlueStakes roads
    if not arcpy.Exists(roadsBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCClkA_schema', roadsBS)
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
                   '16':'A41', '17':'A41', '18':'A41'}

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

     #---Add Questar Road Segments------------
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

    with arcpy.EnvManager(workspace=sgid):
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
    cntyFlds = ['NAME', 'FIPS_STR', 'SHAPE@']

    with arcpy.da.SearchCursor(muni, muniFlds) as scursor, \
        arcpy.da.InsertCursor(muniBS, outFlds) as icursor:
            for row in scursor:
                name = row[0].replace('St.', 'St')
                shp = row[1]
                icursor.insertRow((name, shp))

    with arcpy.da.SearchCursor(metroTownships, twnshipFlds) as scursor, \
        arcpy.da.InsertCursor(muniBS, outFlds) as icursor:
            for row in scursor:
                name = trow[0].title()
                shp = trow[1]
                icursor.insertRow((name, shp))

    #---Copy Municipalities to Blues Stakes root level
    arcpy.CopyFeatures_management(os.path.join(muniBS, outLoc, 'TGR_StWide_plc00.shp'))

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

    with arcpy.da.SearchCursor(mileposts, mp_flds) as scursor, \
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

            shp = srcMP_Row[4]

            icursor.insertRow((Type, Label_Name, shp))

    #----Add Exit Records--------------------------------------------
    with arcpy.da.SearchCursor(exits, exit_flds) as scursor, \
        with arcpy.da.InsertCursor(milePostsBS, bs_flds) as icursor:
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
        env.workspace = sgid
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

    srcMP_Rows = arcpy.da.SearchCursor(milePosts, srcMP_Flds)
    srcEX_Rows = arcpy.da.SearchCursor(exits, srcEX_Flds)
    srcMPrr_Rows = arcpy.da.SearchCursor(rr_MilePosts, srcMPrr_Flds)
    tarRows = arcpy.da.InsertCursor(milePostsHwyRR_BS, tarFlds)

    # ----Add RR Mileposts-----------------------------------------------
    with arcpy.da.SearchCursor(rr_MilePosts, RRmp_flds) as scursor, \
        with arcpy.da.InsertCursor(milePostsHwyRR_BS, bs_flds) as icursor:
            for row in scursors:
                if '.' not in row[1]:
                    lbl = row[1]
                    name = f'{row[0].title()} Division milepost {lbl}'
                    cfcc = 'P11'
                    shp = row[2]

                    icursor.insertRow((name, lbl, cfcc, shp))

    # ----Add Milepost Records-------------------------------------------
    with arcpy.da.SearchCursor(milePosts, mp_flds) as scursor, \
        with arcpy.da.InsersCursor(milePostsHwyRR_BS, bs_flds) as icursor:

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
        with arcpy.da.InsertCursor(milePostsHwyRR_BS, bs_flds) as icursor:
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

    env.workspace = sgid
    arcpy.env.overwriteOutput = True

    landown = sgid_GEO + '\\LandOwnership'
    parks = sgid_GEO + '\\Parks'
    cemeteries = sgid_GEO + '\\Cemeteries'
    golf = sgid_GEO + '\\GolfCourses'

    landownBS = stageDB + '\\TGR_StWide_lpy'

    clpCnty = 'SGID.BOUNDARIES.Counties'

    #---Copy Landownership, Parks, and Cemeteries to SGID_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID.CADASTRE.LandOwnership', landown)
    arcpy.CopyFeatures_management('SGID.RECREATION.ParksLocal', parks)
    arcpy.CopyFeatures_management('SGID.SOCIETY.Cemeteries_Poly', cemeteries)
    arcpy.CopyFeatures_management('SGID.RECREATION.GolfCourses', golf)

    #---Check for statewide Large Landownership BlueStakes schema
    if not arcpy.Exists(landownBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCClpy_schema', landownBS)
    else:
        arcpy.DeleteFeatures_management(landownBS)


    srcLnd_Flds = ['OWNER', 'DESIG', 'LABEL_STATE', 'LABEL_FEDERAL', 'STATE_LGD', 'SHAPE@']
    srcPrk_Flds = ['NAME', 'SHAPE@']
    srcCem_Flds = ['Name', 'SHAPE@']
    srcGlf_Flds = ['NAME', 'SHAPE@']

    tarFlds = ['CFCC', 'LANDNAME', 'SHAPE@']

    cntyFlds = ['NAME', 'FIPS_STR', 'SHAPE@']


    srcLnd_Rows = arcpy.da.SearchCursor(landown, srcLnd_Flds)
    srcPrk_Rows = arcpy.da.SearchCursor(parks, srcPrk_Flds)
    srcCem_Rows = arcpy.da.SearchCursor(cemeteries, srcCem_Flds)
    srcGlf_Rows = arcpy.da.SearchCursor(golf, srcGlf_Flds)

    tarRows = arcpy.da.InsertCursor(landownBS, tarFlds)

    monType = ['National Historic Site', 'National Monument', 'National Park', 'National Recreation Area']

    #----Add LandOwn features-------------------------------------
    for srcLnd_Row in srcLnd_Rows:

        if srcLnd_Row[0] == 'Tribal':

            CFCC = 'D40'

            if srcLnd_Row[3] != None:
                LANDNAME = srcLnd_Row[3].title()
            else:
                LANDNAME = srcLnd_Row[4]

            shp = srcLnd_Row[5]

            tarRows.insertRow((CFCC, LANDNAME, shp))

        if srcLnd_Row[1] == 'Military':

            CFCC = 'D10'

            if srcLnd_Row[3] != None:
                LANDNAME = srcLnd_Row[3].title()
            else:
                LANDNAME = srcLnd_Row[4]

            shp = srcLnd_Row[5]

            tarRows.insertRow((CFCC, LANDNAME, shp))

        # if srcLnd_Row[1] == 'National Historic Site' or srcLnd_Row[1] == 'National Monument' \
        #                     or srcLnd_Row[1] == 'National Park' or srcLnd_Row == 'National Recreation Area':

        if srcLnd_Row[1] in monType:

            CFCC = 'D83'

            if srcLnd_Row[3] != None:
                LANDNAME = srcLnd_Row[3].title()
            else:
                LANDNAME = srcLnd_Row[4]

            shp = srcLnd_Row[5]

            tarRows.insertRow((CFCC, LANDNAME, shp))

        if srcLnd_Row[1] == 'National Forest':

            CFCC = 'D84'

            if srcLnd_Row[3] != None:
                LANDNAME = srcLnd_Row[3].title()
            else:
                LANDNAME = srcLnd_Row[4].title()

            shp = srcLnd_Row[5]

            tarRows.insertRow((CFCC, LANDNAME, shp))

        primType = ['Primitive Area', 'Wilderness', 'Wildlife Reserve/Management Area', 'National Wildlife Refuge']
        if srcLnd_Row[1] == primType:

            CFCC = 'D89'

            if srcLnd_Row[3] != None:
                LANDNAME = srcLnd_Row[3].title()
            else:
                LANDNAME = srcLnd_Row[4].title()

            shp = srcLnd_Row[5]

            tarRows.insertRow((CFCC, LANDNAME, shp))

        if srcLnd_Row[1] == 'Parks and Recreation' and srcLnd_Row[0] == 'State':

            CFCC = 'D85'

            if srcLnd_Row[2] != None:
                LANDNAME = srcLnd_Row[2].title()
            else:
                LANDNAME = srcLnd_Row[4]

            shp = srcLnd_Row[5]

            tarRows.insertRow((CFCC, LANDNAME, shp))

    #----Add Parks--------------------------------------------
    for srcPrk_Row in srcPrk_Rows:

        CFCC = 'D85'

        if srcPrk_Row[0] != None:
            LANDNAME = srcPrk_Row[0]

        else:
            LANDNAME = ''

        shp = srcPrk_Row[1]

        tarRows.insertRow((CFCC, LANDNAME, shp))


    #----Add Cemeteries--------------------------------------------
    for srcCem_Row in srcCem_Rows:

        CFCC = 'D82'

        if srcCem_Row[0] != None:
            LANDNAME = srcCem_Row[0]

        else:
            LANDNAME = ''

        shp = srcCem_Row[1]

        tarRows.insertRow((CFCC, LANDNAME, shp))

    del tarRows


    #---Copy Landownership to Blue Stakes root level
    arcpy.CopyFeatures_management(landownBS, outLoc + '\\TGR_StWide_lpy.shp')


    #---Clip Blue Stakes Landonwership-----------------------------------------------------------
    clip(landownBS, '', 'lpy');


    print ('Done Translating Large Landownership  ' + str(datetime.datetime.now()))

def waterPoly():

    print ('Starting Lakes  ' + str(datetime.datetime.now()))

    lakes = sgid_GEO + '\\LakesNHDHighRes'
    lakesBS = stageDB + '\\TGR_StWide_wat'

    #---Copy lakesNHD to SGID_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID.WATER.LakesNHDHighRes', lakes)

    #---Check for statewide lakes BlueStakes schema
    if not arcpy.Exists(lakesBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCCWAT_schema', lakesBS)
    else:
        arcpy.DeleteFeatures_management(lakesBS)

    srcFlds = ['FCode', 'GNIS_Name', 'InUtah', 'SHAPE@']
    tarFlds = ['CFCC', 'LANDNAME', 'SHAPE@']

    srcRows = arcpy.da.SearchCursor(lakes, srcFlds)
    tarRows = arcpy.da.InsertCursor(lakesBS, tarFlds)

    for srcRow in srcRows:
        if srcRow[2] == 1:
            if srcRow[0] == 36100:
                CFCC = 'H32'
                if srcRow[1] != None:
                    LANDNAME = srcRow[1]
                else:
                    LANDNAME = 'Playa'
            elif srcRow[0] == 39001:
                CFCC = 'H32'
                if srcRow[1] != None:
                    LANDNAME = srcRow[1]
                else:
                    LANDNAME = 'Intermittent Salt Lake/Pond'
            elif srcRow[0] == 39004 or srcRow[0] == 39005 or srcRow[0] == 39006 or srcRow[0] == 39009 or srcRow[0] == 39010:
                CFCC = 'H30'
                if srcRow[1] != None:
                    LANDNAME = srcRow[1]
                else:
                    LANDNAME = 'Lake/Pond'
            elif srcRow[0] == 39012 or srcRow[0] == 43600 or srcRow[0] == 43601 or srcRow[0] == 43607:
                CFCC = 'H40'
                if srcRow[1] != None:
                    LANDNAME = srcRow[1]
                else:
                    LANDNAME = 'Reservoir'
            elif srcRow[0] == 43612:
                CFCC = 'H40'
                if srcRow[1] != None:
                    LANDNAME = srcRow[1]
                else:
                    LANDNAME = 'Sewage Treatment Pond'
            elif srcRow[0] == 43613:
                CFCC = 'H40'
                if srcRow[1] != None:
                    LANDNAME = srcRow[1]
                else:
                    LANDNAME = 'Covered Reservoir'
            elif srcRow[0] == 43616 or srcRow[0] == 43619 or srcRow[0] == 43623 or srcRow[0] == 43624 or srcRow[0] == 43625:
                CFCC = 'H40'
                if srcRow[1] != None:
                    LANDNAME = srcRow[1]
                else:
                    LANDNAME = 'Reservoir'


            else:
                continue

            shp = srcRow[3]

            tarRows.insertRow((CFCC, LANDNAME, shp))


    #---Copy Lakes to Blue Stakes root level---------------
    arcpy.CopyFeatures_management(lakesBS, outLoc + '\\TGR_StWide_WAT.shp')


    #---Clip Blue Stakes Misc Transportation-----------------------------------------------------------
    clip(lakesBS, '', 'WAT');


    print ('Done Translating Lakes  ' + str(datetime.datetime.now()))

def waterLines():

    print ('Starting Rivers  ' + str(datetime.datetime.now()))

    rivers = sgid_GEO + '\\StreamsNHD'
    riversBS = stageDB + '\\TGR_StWide_lkH'

    arcpy.CopyFeatures_management('SGID.WATER.StreamsNHDHighRes', rivers)

    #---Check for Rivers BlueStakes schema
    if not arcpy.Exists(riversBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCClkH_schema', riversBS)
    else:
        arcpy.DeleteFeatures_management(riversBS)

    srcFlds = ['GNIS_Name', 'FCode', 'InUtah', 'SHAPE@', 'Submerged']
    tarFlds = ['FENAME', 'CFCC2', 'SHAPE@']

    srcRows = arcpy.da.SearchCursor(rivers, srcFlds)
    tarRows = arcpy.da.InsertCursor(riversBS, tarFlds)

    for srcRow in srcRows:

        if srcRow[2] == 1:
            if srcRow[4] == 0:
                if srcRow[1] == 46003:
                    CFCC2 = 'H2'
                    if srcRow[0] != None:
                        FENAME = srcRow[0]
                    else:
                        FENAME = 'unknown'
                if srcRow[1] != 46003:
                    CFCC2 = 'H1'
                    if srcRow[0] != None:
                        FENAME = srcRow[0]
                    else:
                        FENAME = 'unknown'

                shp = srcRow[3]

                tarRows.insertRow((FENAME, CFCC2, shp))

    del tarRows


    #---Copy Rivers to Blue Stakes root level---------------
    arcpy.CopyFeatures_management(riversBS, outLoc + '\\TGR_StWide_lkH.shp')


    #---Clip Blue Stakes Misc Transportation-----------------------------------------------------------
    clip(riversBS, '', 'lkH');


    print ('Done Translating Rivers  ' + str(datetime.datetime.now()))

def railroads():

    print ('Starting Railroads  ' + str(datetime.datetime.now()))

    env.workspace = sgid
    arcpy.env.overwriteOutput = True

    rail = sgid_GEO + '\\Railroads'
    railLt = sgid_GEO + '\\LightRail_UTA'
    #railLt_new = sgid_GEO + '\\LightRailNewRoutes_UTA'
    railCommut = sgid_GEO + '\\CommuterRailRoute_UTA'
    #railCommut_new = sgid_GEO + '\\CommuterRailNewRoutes_UTA'

    railBS = stageDB + '\\TGR_StWide_lkB'

    arcpy.CopyFeatures_management('SGID.TRANSPORTATION.Railroads', rail)
    arcpy.CopyFeatures_management('SGID.TRANSPORTATION.LightRail_UTA', railLt)
    arcpy.CopyFeatures_management('SGID.TRANSPORTATION.CommuterRailRoutes_UTA', railCommut)


    #---Check for statewide railroad BlueStakes schema
    if not arcpy.Exists(railBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCClkB_schema', railBS)
    else:
        arcpy.DeleteFeatures_management(railBS)


    srcRail_Flds = ['RAILROAD', 'SHAPE@']
    srcRailLt_Flds = ['SHAPE@']
    srcRailLtNew_Flds = ['SHAPE@']
    srcRailCommut_Flds = ['SHAPE@']
    srcRailCommutNew_Flds = ['SHAPE@']

    tarFlds = ['FENAME', 'CFCC2', 'SHAPE@']

    srcRail_Rows = arcpy.da.SearchCursor(rail, srcRail_Flds)
    srcRailLt_Rows = arcpy.da.SearchCursor(railLt, srcRailLt_Flds)
    #srcRailLtNew_Rows = arcpy.da.SearchCursor(railLt_new, srcRailLtNew_Flds)
    srcRailCommut_Rows = arcpy.da.SearchCursor(railCommut, srcRailCommut_Flds)
    #srcRailCommutNew_Rows = arcpy.da.SearchCursor(railCommut_new, srcRailCommutNew_Flds)

    tarRows = arcpy.da.InsertCursor(railBS, tarFlds)

    #---Add Railroads---------------------------------
    for srcRail_Row in srcRail_Rows:

        if srcRail_Row[0] != 'UTA' and srcRail_Row[0] != 'UT Transit Auth':

            FENAME = srcRail_Row[0]
            CFCC2 = 'B1'
            shp = srcRail_Row[1]

            tarRows.insertRow((FENAME, CFCC2, shp))

    #----Add Light Rail------------------------------------
    for srcRailLt_Row in srcRailLt_Rows:

        FENAME = 'UTA Trax light rail'
        CFCC2 = 'B1'
        shp = srcRailLt_Row[0]

        tarRows.insertRow((FENAME, CFCC2, shp))

    #----Add Light New Rail------------------------------------
    # for srcRailLtNew_Row in srcRailLtNew_Rows:
    #
    #     FENAME = 'UTA Trax light rail'
    #     CFCC2 = 'B1'
    #     shp = srcRailLtNew_Row[0]
    #
    #     tarRows.insertRow((FENAME, CFCC2, shp))

    #----Add Commuter Rail------------------------------------
    for srcRailCommut_Row in srcRailCommut_Rows:

        FENAME = 'UTA Frontrunner railroad'
        CFCC2 = 'B1'
        shp = srcRailCommut_Row[0]

        tarRows.insertRow((FENAME, CFCC2, shp))

    #----Add Commuter New Rail------------------------------------
    # for srcRailCommutNew_Row in srcRailCommutNew_Rows:
    #
    #     FENAME = 'UTA Frontrunner railroad'
    #     CFCC2 = 'B1'
    #     shp = srcRailCommutNew_Row[0]
    #
    #     tarRows.insertRow((FENAME, CFCC2, shp))

    del tarRows


    #---Copy Railroads to Blue Stakes root level----------------------
    arcpy.CopyFeatures_management(railBS, outLoc + '\\TGR_StWide_lkB.shp')


    #---Clip Blue Stakes Railroads-----------------------------------------------------------
    clip(railBS, '', 'lkB');

    print ('Done Translating Railroads  ' + str(datetime.datetime.now()))

def airstrips():

    print ('Starting Airstrips  ' + str(datetime.datetime.now()))

    airstrips = sgid_GEO + '\\Airports'
    airstripsBS = stageDB + '\\TGR_StWide_lkD'
    clpCnty = 'SGID.BOUNDARIES.Counties'

    arcpy.CopyFeatures_management('SGID.TRANSPORTATION.Airports', airstrips)

    #---Check for statewide airports BlueStakes schema
    if not arcpy.Exists(airstripsBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCClkD_schema', airstripsBS)
    else:
        arcpy.DeleteFeatures_management(airstripsBS)

    srcFlds = ['FAC_TYPE', 'FULLNAME', 'SHAPE@']
    tarFlds = ['FENAME', 'CFCC2', 'SHAPE@']

    srcRows = arcpy.da.SearchCursor(airstrips, srcFlds)
    tarRows = arcpy.da.InsertCursor(airstripsBS, tarFlds)

    for srcRow in srcRows:

        if srcRow[0] == 'AIRPORT':
            if srcRow[0].find('AIRFIELD') != -1:
                FENAME = srcRow[1].replace('MUNI', 'MUNICIPAL')
            elif srcRow[0].find('BASE') != -1:
                FENAME = srcRow[1]
            else:
                FENAME = srcRow[1].replace('MUNI', 'MUNICIPAL') + ' ' + srcRow[0]
        else:
            FENAME = srcRow[1]

        CFCC2 = 'D5'

        shp = srcRow[2]

        tarRows.insertRow((FENAME, CFCC2, shp))

    del tarRows


    #---Copy Airstrips to Blue Stakes root level-------------------------
    arcpy.CopyFeatures_management(airstripsBS, outLoc + '\\TRG_StWide_lkD.shp')


    #---Clip Blue Stakes Airstrips-----------------------------------------------------------
    clip(airstripsBS, '', 'lkD');


    print ('Done Translating Airstrips  ' + str(datetime.datetime.now()))

def miscTransportation():

    print ('Starting Misc Transportation  ' + str(datetime.datetime.now()))

    miscTrans_ski = sgid_GEO + '\\SkiLifts'
    miscTrans_TransLines = sgid_GEO + '\\TransmissionLines'
    miscTrans_ElecLines = sgid_GEO + '\\ElectricLines'
    miscTransBS = stageDB + '\\TGR_StWide_lkC'
    miscTrans_QuestarParcels = r'C:\ZBECK\BlueStakes\stagingBS.gdb\DOMINION_GEOGRAPHIC\Parcels_Questar'
    source_QuestarParcels = r'C:\ZBECK\BlueStakes\DominionEnergy\OneCall.gdb\Property'

    #---Load Questar parcels from past year---
    count = int(arcpy.GetCount_management(miscTrans_QuestarParcels).getOutput(0))
    if count > 1:
        print (count)
        arcpy.TruncateTable_management(miscTrans_QuestarParcels)
        print ('Truncated Questar Parcels')

    today = datetime.datetime.now()

    flds = ['OBJECTID', 'DATECREATED', 'DATEMODIFIED', 'SHAPE@', 'SUBTYPECD']
    iFlds = ['DATECREATED', 'DATEMODIFIED', 'SUBTYPECD', 'SHAPE@']

    iCursor = arcpy.da.InsertCursor(miscTrans_QuestarParcels, iFlds)

    with arcpy.da.SearchCursor(source_QuestarParcels, flds) as sCursor:
        for row in sCursor:
            oid = row[0]

            dateC = row[1]
            if dateC == None:
                dateC = datetime.datetime.strptime('9/9/1973', '%m/%d/%Y')
            dateM = row[2]
            if dateM == None:
                dateM = datetime.datetime.strptime('9/9/1973', '%m/%d/%Y')

            propType = row[4]

            if dateC >= dateM:
                dateC_delta = today - dateC
                if int(str(dateC_delta).split()[0]) < 366:
                    iCursor.insertRow((dateC, None, propType, row[3]))
            elif dateM != '9/9/1973':
                dateM_delta = today - dateM
                if int(str(dateM_delta).split()[0]) < 366:
                    iCursor.insertRow((None, dateM, propType, row[3]))
            else:
                print (oid)

    del sCursor
    del iCursor


    arcpy.CopyFeatures_management('SGID.RECREATION.SkiLifts', miscTrans_ski)
    arcpy.CopyFeatures_management('SGID.UTILITIES.TransmissionLines', miscTrans_TransLines)
    arcpy.CopyFeatures_management('SGID.UTILITIES.ElectricalLines', miscTrans_ElecLines)
    print ('Copied Features')


    #---Check for statewide misc transportation BlueStakes schema
    if not arcpy.Exists(miscTransBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCClkC_schema', miscTransBS)
    else:
        arcpy.DeleteFeatures_management(miscTransBS)

    srcFlds_ski = ['LIFT_NAME', 'SHAPE@']
    srcFlds_trans = ['LAYER', 'SHAPE@']
    srcFlds_elec = ['SHAPE@']
    srcFlds_Qparcels = ['SHAPE@']
    tarFlds = ['FENAME', 'CFCC2', 'SHAPE@']

    tarRows = arcpy.da.InsertCursor(miscTransBS, tarFlds)

    #-------Ski lifts--------
    srcRows_ski = arcpy.da.SearchCursor(miscTrans_ski, srcFlds_ski)

    for srcRow_ski in srcRows_ski:

        FENAME = srcRow_ski[0] + ' Ski Lift'
        CFCC2 = 'C3'
        shp = srcRow_ski[1]

        tarRows.insertRow((FENAME, CFCC2, shp))

    del srcRows_ski

    #-------Transmission Lines---------
    srcRows_trans = arcpy.da.SearchCursor(miscTrans_TransLines, srcFlds_trans)
    badVals = ['SUB-CO', 'SUB-PP']

    for srcRow_trans in srcRows_trans:
        if srcRow_trans[0] not in badVals:
            FENAME = 'Overhead Power Line Corridor'
            CFCC2 = 'C2'
            shp = srcRow_trans[1]
        else:
            continue

        tarRows.insertRow((FENAME, CFCC2, shp))

    del srcRows_trans


    #-------Electrical Lines---------
    srcRows_elec = arcpy.da.SearchCursor(miscTrans_ElecLines, srcFlds_elec)

    for srcRow_elec in srcRows_elec:
        FENAME = 'Overhead Power Line Corridor'
        CFCC2 = 'C2'
        shp = srcRow_elec[0]

        tarRows.insertRow((FENAME, CFCC2, shp))

    del srcRows_elec

    #--------Questar Parcels---------
    rdSegs_Questar = r'C:\ZBECK\BlueStakes\stagingBS.gdb\DOMINION_GEOGRAPHIC\RoadSegs_DominionSelect'
    rdSegs_Questar_FL = arcpy.MakeFeatureLayer_management(rdSegs_Questar, 'rdSegs_Questar_FL')

    miscTrans_QuestarParcels_FL = arcpy.MakeFeatureLayer_management(miscTrans_QuestarParcels, 'miscTrans_QuestarParcels')

    arcpy.SelectLayerByLocation_management(miscTrans_QuestarParcels_FL, 'WITHIN_A_DISTANCE', \
                                           rdSegs_Questar_FL, '175 Meters')

    selected = arcpy.GetCount_management(miscTrans_QuestarParcels_FL)
    selCount = int(selected.getOutput(0))
    print (selCount)

    srcRows_Qparcels = arcpy.da.SearchCursor(miscTrans_QuestarParcels_FL, srcFlds_Qparcels)
    for row_Qparcels in srcRows_Qparcels:
        FENAME = ''
        CFCC2 = 'A9'
        shp = row_Qparcels[0]

        tarRows.insertRow((FENAME, CFCC2, shp))

    del tarRows

    #---Copy Misc Trans to Blue Stakes root level---------------
    arcpy.CopyFeatures_management(miscTransBS, outLoc + '\\TGR_StWide_lkC.shp')

    #---Clip Blue Stakes Misc Transportation-----------------------------------------------------------
    clip(miscTransBS, '', 'lkC');


    print ('Done Translating Misc Transportation  ' + str(datetime.datetime.now()))

def townships():

    print ('Starting Townships  ' + str(datetime.datetime.now()))

    twnShips = sgid_GEO + '\\PLSSTownships'
    twnShipsBS = stageDB + '\\UT_TR'

    #---Copy Townships in SGID_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID.CADASTRE.PLSSTownships_GCDB', twnShips)

    #---Check for statewide township BlueStakes schema
    if not arcpy.Exists(twnShipsBS):
        arcpy.CopyFeatures_management(schemaDB + '\\UT_TR_schema', twnShipsBS)
    else:
        arcpy.DeleteFeatures_management(twnShipsBS)

    srcFlds = ['BASEMERIDIAN', 'LABEL', 'SHAPE@']
    tarFlds = ['NAME', 'SHAPE@']

    srcRows = arcpy.da.SearchCursor(twnShips, srcFlds)
    tarRows = arcpy.da.InsertCursor(twnShipsBS, tarFlds)

    for srcRow in srcRows:

        NAME = ("SL" if srcRow[0] == "26" else "UI") + " " + srcRow[1]
        shp = srcRow[2]

        tarRows.insertRow((NAME, shp))

    del tarRows

    #---Export to shapefile-------------------------------------------
    outTwnshps = outLoc + '\\UT_TR.shp'
    arcpy.CopyFeatures_management(twnShipsBS, outTwnshps)

    flds = arcpy.ListFields(outTwnshps)
    for fld in flds:
        if fld.name == 'Shape_Area':
            arcpy.DeleteField_management(outTwnshps, 'Shape_Area')
        if fld.name == 'Shape_Leng':
            arcpy.DeleteField_management(outTwnshps, 'Shape_Leng')


    print ('Done Translating Townships  ' + str(datetime.datetime.now()))

def sections():

    print ('Starting Sections  ' + str(datetime.datetime.now()))

    meridianDict = {'26':'SL', '30':'UI'}

    sections = sgid_GEO + '\\PLSSSections'
    sectionsBS = stageDB + '\\UT_TRS'

    #---Move Sections to SGID_GEOGRAPHIC staging area

    arcpy.CopyFeatures_management('SGID.CADASTRE.PLSSSections_GCDB', sections)

    #---Check for statewide BlueStakes sections
    if not arcpy.Exists(sectionsBS):
        arcpy.CopyFeatures_management(schemaDB + '\\UT_TRS_schema', sectionsBS)
    else:
        arcpy.DeleteFeatures_management(sectionsBS)

    srcFlds = ['SNUM', 'BASEMERIDIAN', 'LABEL', 'SHAPE@']
    tarFlds = ['NAME', 'FULLNAME', 'SHAPE@']

    srcRows = arcpy.da.SearchCursor(sections, srcFlds)
    tarRows = arcpy.da.InsertCursor(sectionsBS, tarFlds)

    for srcRow in srcRows:

        NAME = srcRow[0]

        if srcRow[1] in meridianDict:
            baseMer = meridianDict[srcRow[1]]
            fullName = '{0} {1} SEC {2}'.format(baseMer, srcRow[2], NAME)
            print (fullName)
        else:
            continue

        shp = srcRow[3]

        tarRows.insertRow((NAME, fullName, shp))

    del tarRows


    #---Export to shapefile-------------------------------------------
    outSections = outLoc + '\\UT_TRS.shp'
    arcpy.CopyFeatures_management(sectionsBS, outSections)

    flds = arcpy.ListFields(outSections)
    for fld in flds:
        if fld.name == 'Shape_Area':
            arcpy.DeleteField_management(outSections, 'Shape_Area')
        if fld.name == 'Shape_Leng':
            arcpy.DeleteField_management(outSections, 'Shape_Leng')


    print ('Done Translating Sections  ' + str(datetime.datetime.now()))

def deciPoints():

    print ('Starting Deci Points (GNIS) ' + str(datetime.datetime.now()))

    deciPts = sgid_GEO + '\\GNIS2010'
    deciPtsBS = stageDB + '\\TGR_StWide_deci'

    #---Move GNIS to SGID_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID.LOCATION.PlaceNamesGNIS2010', deciPts)

    #---Check for statewide Deci Points BlueStakes schema
    if not arcpy.Exists(deciPtsBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCCdeci_schema', deciPtsBS)
    else:
        arcpy.DeleteFeatures_management(deciPtsBS)

    srcFlds = ['NAME', 'SHAPE@']
    tarFlds = ['NAME', 'SHAPE@']

    srcRows = arcpy.da.SearchCursor(deciPts, srcFlds)
    tarRows = arcpy.da.InsertCursor(deciPtsBS, tarFlds)

    for srcRow in srcRows:

        if srcRow[0] != None:
            NAME = srcRow[0]
        else:
            NAME = ''

        shp = srcRow[1]

        tarRows.insertRow((NAME, shp))

    del tarRows


    #---Copy Deci Points to Blue Stakes root level---------------
    arcpy.CopyFeatures_management(deciPtsBS, outLoc + '\\TGR_StWide_deci.shp')


    #---Clip Blue Stakes Deci Points-----------------------------------------------------------
    clip(deciPtsBS, '', 'deci');


    print ('Done Translating Deci Points (GNIS) ' + str(datetime.datetime.now()))

def addedPoints():

    print ('Starting Added Points ' + str(datetime.datetime.now()))

    correctionsPts = sgid_GEO + '\\CorrectionalFacilities'
    fireStnPts = sgid_GEO + '\\FireStations'
    libraryPts = sgid_GEO + '\\Libraries'
    liquorPts = sgid_GEO + '\\LiquorStores'
    churchPts = sgid_GEO + '\\PlacesOfWorship'
    policePts = sgid_GEO + '\\PoliceStations'
    postOfficePts = sgid_GEO + '\\PostOffices'
    schoolPts = sgid_GEO + '\\Schools'
    mallPts = sgid_GEO + '\\ShoppingMalls'
    healthCarePts = sgid_GEO + '\\HealthCareFacilities'

    addedPtsBS = stageDB + '\\TGR_StWide_added'

    #---Move Points to SGID_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID.SOCIETY.CorrectionalFacilities', correctionsPts)
    arcpy.CopyFeatures_management('SGID.SOCIETY.FireStations', fireStnPts)
    arcpy.CopyFeatures_management('SGID.SOCIETY.Libraries', libraryPts)
    arcpy.CopyFeatures_management('SGID.SOCIETY.LiquorStores', liquorPts)
    arcpy.CopyFeatures_management('SGID.SOCIETY.PlacesOfWorship', churchPts)
    arcpy.CopyFeatures_management('SGID.SOCIETY.LawEnforcement', policePts)
    arcpy.CopyFeatures_management('SGID.SOCIETY.PostOffices', postOfficePts)
    arcpy.CopyFeatures_management('SGID.SOCIETY.Schools', schoolPts)
    arcpy.CopyFeatures_management('SGID.SOCIETY.ShoppingMalls', mallPts)
    arcpy.CopyFeatures_management('SGID.HEALTH.HealthCareFacilities', healthCarePts)
    print ('Done copying features from SGID to staging area')

    #---Check for statewide Deci Points BlueStakes schema
    if not arcpy.Exists(addedPtsBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCCdeci_schema', addedPtsBS)
    else:
        arcpy.DeleteFeatures_management(addedPtsBS)


    tarFlds = ['NAME', 'SHAPE@']
    tarRows = arcpy.da.InsertCursor(addedPtsBS, tarFlds)

    pointFC_List = [correctionsPts, fireStnPts, libraryPts, churchPts, mallPts, healthCarePts]

    #---Loop through feature classes that have common fields-------
    for pointFC in pointFC_List:

        srcFlds = ['NAME', 'SHAPE@']
        srcRows = arcpy.da.SearchCursor(pointFC, srcFlds)

        for srcRow in srcRows:

            if srcRow[0] != None:
                if len(srcRow[0]) > 79:
                    NAME = ' '.join(srcRow[0].split()[:-1]).title()
                else:
                    NAME = srcRow[0].title()
            else:
                NAME = ''

            shp = srcRow[1]

            tarRows.insertRow((NAME, shp))

        print ('Added ' + pointFC)


    liquorFlds = ['TYPE', 'SHAPE@']
    policeFlds = ['NAME', 'SHAPE@']
    postOfficeFlds = ['TOWN', 'STREET', 'SHAPE@']
    schoolFlds = ['SCHOOL', 'SHAPE@']

    liquorRows = arcpy.da.SearchCursor(liquorPts, liquorFlds)
    policeRows = arcpy.da.SearchCursor(policePts, policeFlds)
    postOfficeRows = arcpy.da.SearchCursor(postOfficePts, postOfficeFlds)
    schoolRows = arcpy.da.SearchCursor(schoolPts, schoolFlds)


    for liquorRow in liquorRows:

        if liquorRow[0] != None:
            NAME = 'Liquor ' + liquorRow[0]
        else:
            NAME = 'Liquor Store'

        shp = liquorRow[1]

        tarRows.insertRow((NAME, shp))

    print ('Added ' + liquorPts)


    for policeRow in policeRows:

        if policeRow[0] != None:
            # if policeRow[0] == 'UNITED STATES FISH AND WILDLIFE SERVICE - OFFICE OF LAW ENFORCEMENT - BEAR RIVER MIGRATORY BIRD REFUGE':
            #     NAME = 'U.S. Fish And Wildlife Service - Law Enforcement - Bear River Bird Refuge'
            # else:
            #     NAME = (policeRow[0].title().replace('United States', 'U.S.'))
            if len(policeRow[0]) > 79:
                NAME = policeRow[0][:79]
            else:
                NAME = (policeRow[0].title().replace('United States', 'U.S.'))
        else:
            NAME = ''

        shp = policeRow[1]

        tarRows.insertRow((NAME, shp))

    print ('Added ' + policePts)


    for postOfficeRow in postOfficeRows:

        if postOfficeRow[0] != None:
            NAME = postOfficeRow[0] + ' Post Office'
        else:
            NAME = 'Post Office'

        shp = policeRow[1]

        tarRows.insertRow((NAME, shp))

    print ('Added ' + postOfficePts)


    for schoolRow in schoolRows:

        if schoolRow[0] != None:
            NAME = schoolRow[0].title()
        else:
            NAME = ''

        shp = schoolRow[1]

        tarRows.insertRow((NAME, shp))

    print ('Added ' + schoolPts)


    del tarRows


    #---Copy Added Points to Blue Stakes root level---------------
    arcpy.CopyFeatures_management(addedPtsBS, outLoc + '\\TGR_StWide_added.shp')

    #---Clip Blue Stakes Deci Points-----------------------------------------------------------
    clip(addedPtsBS, '', 'added');


    print ('Done Translating Added Points ' + str(datetime.datetime.now()))

def counties():

    print ('Starting Counties ' + str(datetime.datetime.now()))

    cnty = sgid_GEO + '\\Counties'
    utah = sgid_GEO + '\\Utah'
    cntyBS = stageDB + '\\TGRSSCCCcty00'
    cntyBS_All = stageDB + '\\CO49_D90'
    stateBS = stageDB + '\\ST49_D00'

    #---Move Counties to SGID_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID.BOUNDARIES.Counties', cnty)
    arcpy.CopyFeatures_management('SGID.BOUNDARIES.Utah', utah)

    #---Check for County BlueStakes schema
    if not arcpy.Exists(cntyBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCCcty00_schema', cntyBS)
    if not arcpy.Exists(cntyBS_All):
        arcpy.CopyFeatures_management(schemaDB + '\\CO49_D90_schema', cntyBS_All)
    if not arcpy.Exists(stateBS):
        arcpy.CopyFeatures_management(schemaDB + '\\ST49_D00_schema', stateBS)
    else:
        arcpy.DeleteFeatures_management(cntyBS)
        arcpy.DeleteFeatures_management(cntyBS_All)
        arcpy.DeleteFeatures_management(stateBS)

    srcFlds = ['NAME', 'FIPS_STR', 'SHAPE@']
    srcFldsUT = ['STATE', 'SHAPE@']
    cntyFlds = ['COUNTY', 'SHAPE@']
    cntyAllFlds = ['NAME', 'ST', 'CO', 'SHAPE@']
    stFlds = ['NAME', 'STATE', 'SHAPE@']

    srcRows = arcpy.da.SearchCursor(cnty, srcFlds)
    srcRowsUT = arcpy.da.SearchCursor(utah, srcFldsUT)
    cntyRows = arcpy.da.InsertCursor(cntyBS, cntyFlds)
    cntyAllRows = arcpy.da.InsertCursor(cntyBS_All, cntyAllFlds)
    stRows = arcpy.da.InsertCursor(stateBS, stFlds)

    #---Create individual county shapefiles--------------------------------------------------------
    for srcRow in srcRows:

        if srcRow[0] != None:
            COUNTY = srcRow[0]
        else:
            COUNTY = ''

        shp = srcRow[2]

        cntyRows.insertRow((COUNTY, shp))

    del cntyRows


    #---Copy each county to Bluestakes folder----------
    cntyBSRows = arcpy.da.SearchCursor(cntyBS, cntyFlds)

    for cntyBSRow in cntyBSRows:

        cntyName = ''.join(cntyBSRow[0].title().split())
        fldrPrefix = '\\TGR'
        outFldr = outLoc + '\\TGR' + fipsDict[cntyName]
        outCntyShp = fldrPrefix + fipsDict[cntyName] + 'cty00.shp'

        cntyFL = arcpy.MakeFeatureLayer_management(cntyBS, cntyName + '_FL', " \"COUNTY\" = '{0}' ".format(cntyBSRow[0]))
        arcpy.CopyFeatures_management(cntyFL, outFldr + outCntyShp)

        flds = arcpy.ListFields(outFldr + outCntyShp)
        for fld in flds:
            if fld.name == 'Shape_Area':
                arcpy.DeleteField_management(outFldr + outCntyShp, 'Shape_Area')
            if fld.name == 'Shape_Leng':
                arcpy.DeleteField_management(outFldr + outCntyShp, 'Shape_Leng')



    #---Create Statewide County Shapefile----------------------------------------------------------
    srcRows = arcpy.da.SearchCursor(cnty, srcFlds)
    for srcRow in srcRows:

        NAME = srcRow[0]
        ST = '49'
        CO = srcRow[1][-3:]
        shp = srcRow[2]

        cntyAllRows.insertRow((NAME, ST, CO, shp))

    del cntyAllRows


    cntyBS_All_shp = outLoc + '\\CO49_D90.shp'
    arcpy.CopyFeatures_management(cntyBS_All, cntyBS_All_shp)

    flds = arcpy.ListFields(cntyBS_All_shp)
    for fld in flds:
        if fld.name == 'Shape_Area':
            arcpy.DeleteField_management(cntyBS_All_shp, 'Shape_Area')
        if fld.name == 'Shape_Leng':
            arcpy.DeleteField_management(cntyBS_All_shp, 'Shape_Leng')


    #---Create State shapfile--------------------------------------------------------------------
    for srcRowUT in srcRowsUT:
        if srcRowUT[0] == 'Utah':

            NAME = 'Utah'
            STATE = '49'
            shp = srcRowUT[1]

            stRows.insertRow((NAME, STATE, shp))

    del stRows

    stateBS_shp = outLoc + '\\ST49_D00.shp'
    arcpy.CopyFeatures_management(stateBS, stateBS_shp)

    flds = arcpy.ListFields(stateBS_shp)
    for fld in flds:
        if fld.name == 'Shape_Area':
            arcpy.DeleteField_management(stateBS_shp, 'Shape_Area')
        if fld.name == 'Shape_Leng':
            arcpy.DeleteField_management(stateBS_shp, 'Shape_Leng')



    print ('Done Translating Counties ' + str(datetime.datetime.now()))

def addressZones():

    print ('Starting Address Zones  ' + str(datetime.datetime.now()))

    addZones = sgid_GEO + '\\AddressSystemQuadrants'
    addZonesBS = stageDB + '\\addrsys'

    #---Add Address Zones to SGID_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID.LOCATION.AddressSystemQuadrants', addZones)

    #---Check for Address Zones BlueStakes schema
    if not arcpy.Exists(addZonesBS):
        arcpy.CopyFeatures_management(schemaDB + '\\addrsys_schema', addZonesBS)
    else:
        arcpy.DeleteFeatures_management(addZonesBS)

    srcFlds = ['GRID_NAME', 'QUADRANT', 'SHAPE@']
    tarFlds = ['NAME', 'SHAPE@']

    srcRows = arcpy.da.SearchCursor(addZones, srcFlds)
    tarRows = arcpy.da.InsertCursor(addZonesBS, tarFlds)

    for srcRow in srcRows:
        if srcRow[0] != None:
            if srcRow[1] != None:
                NAME = srcRow[0] + ' ' + srcRow[1]
            else:
                NAME = srcRow[0]
        shp = srcRow[2]

        tarRows.insertRow((NAME, shp))

    del tarRows


    #---Copy Address Zones to Blues Stakes root level
    arcpy.CopyFeatures_management(addZonesBS, outLoc + '\\addrsys_StWide.shp')

    #---Clip by county-------------------------------------------
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
        arcpy.CopyFeatures_management('SGID.ENERGY.OilGasWells', og)

    #---Check for Address Zones BlueStakes schema
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
        lat = srow[4]
        long = srow[5]
        shp = srow[6]

        tarRows.insertRow((api, name, field, operator, lat, long, shp))

    del tarRows

     #----Copy Mileposts to shapefile--------------------------------------------------
    arcpy.CopyFeatures_management(ogBS, outLoc + '\\wells_oil_gas.shp')

    #---Clip Blue Stakes Oil and Gas Wells----------------------------------------------------
    #clip(ogBS, '', 'ogw')


def clip(clipMe, outNamePrefix, outNameSuffix):

    clpCnty = os.path.join(sgid_GEO, 'Counties')
    with arcpy.EnvManager(workspace=sgid):
        arcpy.env.overwriteOutput = True
        if not arcpy.Exists(clpCnty):
            arcpy.CopyFeatures_management('SGID.BOUNDARIES.Counties', clpCnty)

    with arcpy.EnvManager(workspace=outLoc):
        arcpy.env.overwriteOutput = True

        #---Clip Blue Stakes output, delete empty shapefiles, delete Shape_Leng field----
        print ('Clipping ' + clipMe)

        clpFlds = ['NAME', 'FIPS_STR', 'SHAPE@']
        clpRows = arcpy.da.SearchCursor(clpCnty, clpFlds)
        fldrPrefix = 'TGR'

        for row in clpRows:
            clpShp = row[2]
            print ('Clipping ' + row[0] + ' County')

            outFldr = f'TGR{row[1]}'
            if outNamePrefix == '':
                outClippedFC = os.path.join(outLoc, outFldr, f'TGR{row[1]}{outNameSuffix}.shp')
                arcpy.Clip_analysis(clipMe, clpShp, outClippedFC)
            else:
                outClippedFC = os.path.join(outLoc, outFldr, f'{outNamePrefix}{row[1]}.shp')
                arcpy.Clip_analysis(clipMe, clpShp, outClippedFC)

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
            print ('Deleted ' + deleteme)
            os.remove(deleteme)




cleanOutFldr();

parcels();
#roads();
#addressPoints();
#municipalities();
#mileposts();
#milepostsCombined()
#landownershipLarge();
#waterPoly();
#waterLines();
#railroads();
#airstrips();
#miscTransportation();
#townships();
#sections();
#deciPoints();
#addedPoints();
#counties();
#addressZones();
#oilAndGasWells();

