import os, arcpy, datetime, time, re
from arcpy import env
from arcpy import da
from agrc import parse_address

#I made some changes here.

sgid10 = r'Database Connections\dc_agrc@SGID10@sgid.agrc.utah.gov.sde'
sgid10_GEO = r'C:\ZBECK\BlueStakes\stagingBS.gdb\SGID10_GEOGRAPHIC'
stageDB = r'C:\ZBECK\BlueStakes\stagingBS.gdb'
schemaDB = r'C:\ZBECK\BlueStakes\schemaBS.gdb'
outLoc = r'C:\ZBECK\BlueStakes\outBlueStakes'

env.workspace = sgid10
arcpy.env.overwriteOutput = True

clpCnty = sgid10_GEO + '\\Counties'
if arcpy.Exists(clpCnty):
    arcpy.Delete_management(clpCnty)
    arcpy.CopyFeatures_management('SGID10.BOUNDARIES.Counties', clpCnty)
else:
    arcpy.CopyFeatures_management('SGID10.BOUNDARIES.Counties', clpCnty)


# fipsNum = ['49001', '49003', '49005', '49007', '49009', '49011', '49013', '49015', '49017', '49019', '49021', \
#           '49023', '49025', '49027', '49029', '49031', '49033', '49035', '49037', '49039', '49041', '49043', '49045', \
#           '49047', '49049', '49051', '49053', '49055', '49057']
#
#
# fipsDict = {'Beaver': '49001', 'BoxElder': '49003', 'Cache': '49005', 'Carbon': '49007', 'Daggett': '49009', \
#            'Davis': '49011', 'Duchesne': '49013', 'Emery': '49015', 'Garfield': '49017', 'Grand': '49019', \
#            'Iron': '49021', 'Juab': '49023', 'Kane': '49025', 'Millard': '49027', 'Morgan': '49029', \
#            'Piute': '49031', 'Rich': '49033', 'SaltLake': '49035', 'SanJuan': '49037', 'Sanpete': '49039', \
#            'Sevier': '49041', 'Summit': '49043', 'Tooele': '49045', 'Uintah': '49047', 'Utah': '49049', \
#            'Wasatch': '49051', 'Washington': '49053', 'Wayne': '49055', 'Weber': '49057'}


fipsNum = ['49007', '49053', '49035', '49049']


fipsDict = {'Carbon': '49007', 'Washington': '49053', 'SaltLake': '49035', 'Utah': '49049'}


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

date = str(datetime.datetime.today().strftime("%m%d%Y"))

# if not arcpy.Exists(stageDB):
#     arcpy.CreateFileGDB_management('C:\ZBECK\BlueStakes', 'stagingBS.gdb')



def parcels():

    print 'Starting Parcels  ' + str(datetime.datetime.now())


    #---Copy Parcels to SGID10_GEOGRAPHIC staging area---------------
    # env.workspace = sgid10_GEO
    # arcpy.env.overwriteOutput = True

    idErrors = ['', None, '00-0000-000', '00-0000-0000', '0000000', '00']

# #------Use to run against all parcels in SGID10--------------
#     for fcSGID in arcpy.ListFeatureClasses():
#         if fcSGID[:23][-7:] == 'Parcels':
#             print fcSGID
#             #---Parcel FC name in SGID10_GEOGRAPHIC
#             parFC = sgid10_GEO + '\\' + fcSGID.split('.')[2]
#
#             arcpy.CopyFeatures_management(fcSGID, parFC)
# #-------------------------------------------------------------


#-------Use to run against subset of parcels defined by alternative fipsNum and fipsDict above
    for cnty in sorted(fipsDict):
        fcSGID = 'SGID10.CADASTRE.Parcels_' + cnty
        print fcSGID
        parFC = sgid10_GEO + '\\Parcels_' + cnty

        arcpy.CopyFeatures_management(fcSGID, parFC)
#---------------------------------------------------------------------------------------


        print 'Repair Geometry ' + parFC
        arcpy.RepairGeometry_management(parFC)
        print 'Done repair'
        disFLDS = ['PARCEL_ID', 'PARCEL_ADD']
        arcpy.Dissolve_management(parFC, parFC + 'DIS', disFLDS, '#', 'MULTI_PART')
        print 'Done with dissolve'


    #---Copy empty bluestakes parcels to load features into
    env.workspace = stageDB

    for fips in fipsNum:
        parcelFC =  stageDB + '\\par' + fips
        arcpy.CopyFeatures_management(schemaDB + '\\parSSCCC_schema', parcelFC)
        print 'Copied par' + fips + ' to staging GDB'



    for cnty in fipsDict:
        parFC_Geo = sgid10_GEO + '\\Parcels_' + cnty + 'DIS'
        parFC_BS = stageDB + '\\par' + fipsDict[cnty]

        arcpy.TruncateTable_management(parFC_BS)

        countyErrorLog = open('C:\\ZBECK\\BlueStakes\\ErrorLogs\\' + cnty + '_ERRORS_' + date + '.txt', 'w')

        srcFlds = ['PARCEL_ID', 'PARCEL_ADD', 'SHAPE@', 'OBJECTID', 'SHAPE@AREA']
        tarFlds = ['ADDR_NUMB', 'ADDR_FULL', 'FEDIRP', 'FENAME', 'FETYPE', 'FEDIRS', 'PARCEL_ID', 'SHAPE@']

        tarRows = arcpy.da.InsertCursor(parFC_BS, tarFlds)
        srcRows = arcpy.da.SearchCursor(parFC_Geo, srcFlds)

        print '     Starting ' + parFC_Geo

        for srcRow in srcRows:
            try:
                #if srcRow[1] != '' or (srcRow[0] != '' and srcRow[4] < .00007):
                if srcRow[1] not in idErrors or (srcRow[0] not in idErrors and srcRow[4] < .00007):

                    parID = srcRow[0]
                    addNum = ''
                    addFull = ''
                    preDir = ''
                    fename = ''
                    stype = ''
                    suf = ''

                    if srcRow[1] not in idErrors:

                        addFull = srcRow[1]
                        address = parse_address.parse(srcRow[1])
                        addNum = address.houseNumber
                        if len(addNum) > 10:
                            addNum = ''
                        preDir = address.prefixDirection
                        fename = address.streetName
                        stype = address.suffixType
                        suf = address.suffixDirection

                else:
                    continue

                shp = srcRow[2]

                tarRows.insertRow((addNum, addFull, preDir, fename, stype, suf, parID, shp))


            except:
                if srcRow[0] is None:
                    countyErrorLog.write(cnty + ' Failed at OBJECTID ' + str(srcRow[3]) + ' NULL ' + srcRow[1] + '\n')
                else:
                    countyErrorLog.write(cnty + ' Failed at OBJECTID ' + str(srcRow[3]) + '\n')


        countyErrorLog.close()


        del tarRows
        del srcRows

        parFips = fipsDict[cnty]


        arcpy.CopyFeatures_management(parFC_BS, outLoc + '\\TGR' + parFips + '\\par' + parFips + '.shp')
        print 'Copied ' + parFC_BS + ' to county folder'


    print 'Done Parcels  ' + str(datetime.datetime.now())

def addressPoints():

    print 'Starting Address Points  ' + str(datetime.datetime.now())

    env.workspace = sgid10
    arcpy.env.overwriteOutput = True

    addPts = sgid10_GEO + '\\AddressPoints'
    addPtsBS = stageDB + '\\adr_StWide'
    #clpCnty = 'SGID10.BOUNDARIES.Counties'

    #---Copy Address Points to SGID10_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management(r'Database Connections\DC_Location@SGID10@sgid.agrc.utah.gov.sde\SGID10.LOCATION.AddressPoints', addPts)

    #---Check for statewide Address Points in BlueStakes schema
    if not arcpy.Exists(addPtsBS):
        arcpy.CopyFeatures_management(schemaDB + '\\adrSSCCC_schema', addPtsBS)
    else:
        arcpy.CopyFeatures_management(schemaDB + '\\adrSSCCC_schema', addPtsBS)
##        arcpy.DeleteFeatures_management(addPtsBS)
##        print 'Deleted Features ' + addPtsBS
        print 'Empty bluestakes address points ready'

    srcFlds = ['FullAdd', 'AddNum', 'PrefixDir', 'StreetName', 'StreetType', 'SuffixDir', 'SHAPE@']
    tarFlds = ['ADDR_NUMB', 'ADDR_FULL', 'FEDIRP', 'FENAME', 'FETYPE', 'FEDIRS', 'OWNER', 'SHAPE@']

    srcRows = arcpy.da.SearchCursor(addPts, srcFlds)
    tarRows = arcpy.da.InsertCursor(addPtsBS, tarFlds)

    for srcRow in srcRows:

        if srcRow[1] != None:
            ADDR_NUMB = srcRow[1]
        else:
            ADDR_NUMB = ''

        if srcRow[0] != None:
            ADDR_FULL = srcRow[0]
        else:
            ADDR_FULL = ''

        if srcRow[2] != None:
            FEDIRP = srcRow[2]
        else:
            FEDIRP = ''

        if srcRow[3] != None:
            FENAME = srcRow[3]
        else:
            FENAME = ''

        if srcRow[4] != None:
            FETYPE = srcRow[4]
        else:
            FETYPE = ''

        if srcRow[5] != None:
            FEDIRS = srcRow[5]
        else:
            FEDIRS = ''

        OWNER = ''

        shp = srcRow[6]

        tarRows.insertRow((ADDR_NUMB, ADDR_FULL, FEDIRP, FENAME, FETYPE, FEDIRS, OWNER, shp))

    del tarRows


    #---Copy State wide address points to Bluestakes root---------------
    arcpy.CopyFeatures_management(addPtsBS, outLoc + '\\adr_StWide.shp')


##    #---Clip Address Points-----------------------------------------------------------
##    print 'Start Clipping Address Points'
##    clip(roadsBS, 'lkA.shp');

    #---Clip by county-------------------------------------------
    clpFlds = ['NAME', 'FIPS_STR', 'SHAPE@']
    clpRows = arcpy.da.SearchCursor(clpCnty, clpFlds)

    for row in clpRows:
        clpFeat = row[2]

        #----Delete shapefiles with no features----
        clp = arcpy.Clip_analysis(addPtsBS, clpFeat, outLoc + '\\TGR' + row[1] + '\\adr' + row[1] + '.shp')
        clpCount = int(arcpy.GetCount_management(clp).getOutput(0))

        if clpCount < 1:
            arcpy.Delete_management(clp)


    print 'Done Translating Address Points  ' + str(datetime.datetime.now())

##def roads():
##
##    print 'Starting Roads  ' + str(datetime.datetime.now())
##
##    roadsSGID = sgid10_GEO + '\\Roads'
##    roadsBS = stageDB + '\\TGR_StWide_lkA'
##
##
##    #----Move Roads to SGID10_GEOGRAPHIC staging area
##    arcpy.CopyFeatures_management('SGID10.TRANSPORTATION.Roads', roadsSGID)
####
####    #----Check for statewide BlueStakes roads
####    if not arcpy.Exists(roadsBS):
####        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCClkA_schema', roadsBS)
####    else:
####        arcpy.DeleteFeatures_management(roadsBS)
##
##
##    srcFlds = ['CARTOCODE', 'PREDIR', 'FULLNAME', 'STREETTYPE', 'SUFDIR', 'L_F_ADD', 'L_T_ADD', 'R_F_ADD', 'R_T_ADD', 'ALIAS1', \
##               'ALIAS2', 'ACSALIAS', 'ACSNAME', 'COFIPS', 'HWYNAME', 'MODIFYDATE', 'ADDR_SYS', 'STREETNAME', 'SHAPE@', 'ALIAS1TYPE', 'ACSSUF', 'ALIAS2TYPE']
##
##
##    tarFlds = ['FEDIRP', 'FENAME', 'FETYPE', 'FEDIRS', 'CFCC', 'FRADDL', 'TOADDL', 'FRADDR', 'TOADDR', 'CFCC1', 'CFCC2', 'FULLNAME', \
##               'HASALT', 'ISALT', 'S_FIPS', 'AGRC_MDATE', 'ADDRESS_SY', 'SHAPE@']
##
##
##    #----Remove empty spaces from roads----------------------------------------------------------------------------
####    with arcpy.da.UpdateCursor(roadsSGID, srcFlds) as rows:
####        count = 0
####        for row in rows:
####            for fld in srcFlds:
####                print fld
####                fldX = srcFlds.index(fld)
####
####                if row[fldX] == ' ':
####                    count = count + 1
####                    print str(count) + ' spaces removed'
####                    row[fldX] = None
####
####                if row[fldX] != None:
####                    row[fldX] = row[fldX].strip()
####
####                rows.updateRow(row)
####
####    del rows
##
####    rdFlds = ['FULLNAME', 'ALIAS1', 'STREETNAME']
####    with arcpy.da.UpdateCursor(roadsSGID, rdFlds) as rows:
####        for row in rows:
####            for fld in rdFlds:
####                fldX = rdFlds.index(fld)
####                if row[fldX] != None:
####                    row[fldX] = row[fldX].strip()
####
####                rows.updateRow(row)
####
####    del rows
##
##
##    srcRows = arcpy.da.SearchCursor(roadsSGID, srcFlds)
##    tarRows = arcpy.da.InsertCursor(roadsBS, tarFlds)
##
##    print 'Start inserting rows'
##
##    #----Format HasAlt isAlt values----
##    def checkAlt(inRow):
##
##        alias1 = srcRow[9]
##        alias2 = srcRow[10]
##        acsalias = srcRow[11]
##        acsname = srcRow[12]
##
##        if alias1 != None and alias1 != '':
##            return '1'
##        if alias2 != None and alias2 != '':
##            return '1'
##        if acsalias != None and acsalias != '':
##            return '1'
##        if acsname != None and acsname != '':
##            return '1'
##        if srcRow[2][-3:] == 'FWY':
##            return '1'
##        if srcRow[2][:3] == 'HWY':
##            return'1'
##        if srcRow[2][:2] == 'US':
##            return '1'
##        else:
##            return '0'
##
##
##    #----RegEx to format street avbreviations (i.e. ST RD TH --> st rd th)----
##    def lowerAbrev(inRow):
##        return inRow.group(0).lower()
##
##    #---RegEx to format route directions (i.e. Nb Wb --> NB WB)
##    def directionCase(inRow):
##        return inRow.group(0).upper()
##
##
##    for srcRow in srcRows:
##
##        #----Prefix Direction----
##        if srcRow[1] == None or srcRow[1] == '':
##            FEDIRP = None
##        else:
##            FEDIRP = srcRow[1]
##
##        #----Root and Full Street Name----
##        if srcRow[2] != None:
##
##            if FEDIRP != None and FEDIRP != '':
##                #FULLNAME = (FEDIRP + ' ' + srcRow[2].replace('US', 'HWY')).title()
##                FULLNAME = (FEDIRP + ' ' + srcRow[2].title()) #+ ' ZZ1'
##        #----modFULLNAME calls lowerAbrev to convert a string like 3Rd to 3rd----
##                modFULLNAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, FULLNAME, flags=re.IGNORECASE)
##                #modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, modFULLNAME, flags=re.IGNORECASE)
##                modFULLNAME = modFULLNAME.replace('Us ', 'Hwy ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF').replace('Fs', 'FS').replace('Blm', 'BLM')
##        #----modFULLNAME calls directionCase to convert a string like Nb to NB----
##                modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, modFULLNAME, flags=re.IGNORECASE)
##                #modFULLNAME = modFULLNAME.replace('Us ', 'Hwy ').replace('Sr ', 'SR ').replace('Usu', 'USU').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF')
##            elif srcRow[3] == 'RAMP':
##                FULLNAME = srcRow[2].title()
##                modFULLNAME = FULLNAME.replace('Us ', 'US ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF').replace('Blm', 'BLM')
##                modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, modFULLNAME, flags=re.IGNORECASE)
##                modFULLNAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, modFULLNAME, flags=re.IGNORECASE)
##            else:
##                #FULLNAME = srcRow[2].replace('US', 'HWY').title().replace('Sr ', 'SR ') + ' ZZ'
##                FULLNAME = srcRow[2].title() #+ ' ZZ'
##                modFULLNAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, FULLNAME, flags=re.IGNORECASE)
##                modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, modFULLNAME, flags=re.IGNORECASE)
##                #modFULLNAME = modFULLNAME.replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF')
##                modFULLNAME = modFULLNAME.replace('Us ', 'Hwy ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF').replace('Fs', 'FS').replace('Blm', 'BLM')
##        else:
##            modFULLNAME = ''
##
##        if srcRow[17] != None:
##            FENAME = srcRow[17].replace('HIGHWAY', 'HWY').title().replace('Us ', 'US ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF').replace('Fs', 'FS').replace('Blm', 'BLM') #+ ' ZZ2'
##            modFENAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, FENAME, flags=re.IGNORECASE)
##            modFENAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, modFENAME, flags=re.IGNORECASE)
##            #modFENAME = modFENAME.replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF')
##            #modFENAME = modFENAME.replace('Us ', 'Hwy ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF')
##            #FENAME = srcRow[17].replace('HIGHWAY', 'HWY').title().replace('Sr ', 'SR ')
####        if srcRow[3] == 'RAMP':
####            FENAME = srcRow[2].title().replace('Us ', 'US ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF') + ' zWTF'
####            #modFENAME = FENAME.replace('Us ', 'US ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF')
####            modFENAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FENAME, flags=re.IGNORECASE)
##        else:
##            modFENAME = ''
##
##
##        #----Street Type----
##        if srcRow[3] != None:
##            FETYPE = srcRow[3].title()
##        else:
##            FETYPE = ''
##
##        #----Sufix Direction----
##        if srcRow[4] != None:
##            FEDIRS = srcRow[4]
##        else:
##            FEDIRS = ''
##
##        #----CFCC----
##        if srcRow[0] != None:
##            if srcRow[0] == '1':
##                CFCC = 'A15'
##            if srcRow[0] == '2':
##                CFCC = 'A20'
##            if srcRow[0] == '3':
##                CFCC = 'A21'
##            if srcRow[0] == '4':
##                CFCC = 'A25'
##            if srcRow[0] == '5':
##                CFCC = 'A20'
##            if srcRow[0] == '6':
##                CFCC = 'A41'
##            if srcRow[0] == '7':
##                CFCC = 'A20'
##            if srcRow[0] == '8':
##                CFCC = 'A31'
##            if srcRow[0] == '9':
##                CFCC = 'A41'
##            if srcRow[0] == '10':
##                CFCC = 'A41'
##            if srcRow[0] == '11':
##                CFCC = 'A41'
##            if srcRow[0] == '12':
##                CFCC = 'A41'
##
##            if srcRow[0] == '14':
##                CFCC = 'A74'
##            if srcRow[0] == '15':
##                CFCC = 'A99'
##
##            CFCC1 = 'A'
##            CFCC2 = CFCC[:2]
##
##        #----From Address Left----
##        if srcRow[5] != None:
##            FRADDL = str(srcRow[5]).split('.')[0]
##        else:
##            FRADDL = 0
##
##        #----To Address Left----
##        if srcRow[6] != None:
##            TOADDL = str(srcRow[6]).split('.')[0]
##        else:
##            TOADDL = 0
##
##        #----From Address Right----
##        if srcRow[7] != None:
##            FRADDR = str(srcRow[7]).split('.')[0]
##        else:
##            FRADDR = 0
##
##        #----To Address Right----
##        if srcRow[8] != None:
##            TOADDR = str(srcRow[8]).split('.')[0]
##        else:
##            TOADDR = 0
##
##        #----FIPS----
##        if srcRow[13] != None:
##            S_FIPS = srcRow[13]
##        else:
##            S_FIPS = ''
##
##        #----AGRC M Date----
##        if srcRow[15] != None:
##            AGRC_MDATE = srcRow[15]
##        else:
##            AGRC_MDATE = '1/1/1000'
##
##        #----Address System----
##        if srcRow[16] != None:
##            ADDRESS_SY = srcRow[16].title()
##        else:
##            ADDRESS_SY = ''
##
##
##        #----Has Alt Name----
##        HASALT = checkAlt(srcRow)
##        ISALT = '0'
##
##
##        shp = srcRow[18]
##
##
##        tarRows.insertRow((FEDIRP, modFENAME, FETYPE, FEDIRS, CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, modFULLNAME, HASALT, \
##                           ISALT, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))
##
##
##
##        #----Add Duplicate SR US and Interstate Highways---------------
##        if srcRow[14] != None and srcRow[14] != '':
##            addHWY = srcRow[14]
##
##            if FEDIRP != None:
##                FULLNAME = FEDIRP + ' ' + addHWY
##            else:
##                FULLNAME = addHWY
##
##            tarRows.insertRow((FEDIRP, addHWY, '', '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME, \
##                               0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))
##
##            if addHWY[:2] == 'SR':
##                if srcRow[2][:3] != 'HWY':
##                    addHWY = addHWY.replace('SR', 'Hwy')
##                    FULLNAME = FULLNAME.replace('SR', 'Hwy')
##
##                    tarRows.insertRow((FEDIRP, addHWY, '', '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME, \
##                                       0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))
##
##            if addHWY[:2] == 'US':
##                if srcRow[2][:2] != 'US':
##                    addHWY = addHWY.replace('US', 'Hwy')
##                    FULLNAME = FULLNAME.replace('US', 'Hwy')
##
##                    tarRows.insertRow((FEDIRP, addHWY, '', '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME, \
##                                       0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))
##
##
##
##        #----Add Duplicate Alias1 and ACSAlias----
##        if srcRow[9] != None and srcRow[9] != ' ' and srcRow[9] != '':
##            if srcRow[9][:7] != 'HIGHWAY':
##                #alsFENAME = srcRow[9].title().replace(' Sr', ' SR').replace('Us ', 'US ') + ' ZZ3'
##                alsFENAME = srcRow[9].title().replace('Us ', 'US ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF').replace('Fs', 'FS').replace('Blm', 'BLM')
##                modFENAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, alsFENAME, flags=re.IGNORECASE)
##
##                if srcRow[19] != None:
##                    FETYPE = srcRow[19].title()
##
##                if FEDIRP != None:
##                    FULLNAME = FEDIRP + ' ' + alsFENAME #+ ' ZZ4'
##                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)
##
##                if FEDIRP != None and srcRow[20] != None:
##                    FULLNAME = FEDIRP + ' ' + alsFENAME + ' ' + srcRow[20][:1]
##                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)
##
##                if FEDIRP != None and FETYPE != None:
##                    FULLNAME = FEDIRP + ' ' + alsFENAME + ' ' + FETYPE
##                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)
##
##                if FEDIRP == None and FETYPE != None:
##                    FULLNAME = alsFENAME + ' ' + FETYPE
##                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)
##
####                else:
####                    FULLNAME = alsFENAME
####                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)
##
##
##                tarRows.insertRow((FEDIRP, modFENAME, FETYPE, '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, \
##                                   modFULLNAME, 0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))
##
##
##
##        #----Add Duplicate Alias2----
##        if srcRow[10] != None and srcRow[10] != ' ' and srcRow[10] != '':
##            if srcRow[10][:7] != 'HIGHWAY':
##                als2FENAME = srcRow[10].title().replace('Us ', 'US ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF').replace('Fs', 'FS').replace('Blm', 'BLM')  #+ ' ZZ5'
##                #als2FENAME = srcRow[10].title().replace(' Sr', ' SR').replace('Us ', 'US ')  + ' ZZ5'
##                modFENAME2 = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, als2FENAME, flags=re.IGNORECASE)
##
##                if srcRow[21] != None:
##                    FETYPE = srcRow[21].title()
##
##                if FEDIRP != None:
##                    FULLNAME = FEDIRP + ' ' + als2FENAME
##                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)
##
##                if FEDIRP != None and srcRow[20] != None:
##                    FULLNAME = FEDIRP + ' ' + als2FENAME + ' ' + srcRow[20][:1]
##                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)
##
##                if FEDIRP != None and FETYPE != None:
##                    FULLNAME = FEDIRP + ' ' + als2FENAME + ' ' + FETYPE
##                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)
##
##                if FEDIRP == None and FETYPE != None:
##                    FULLNAME = als2FENAME + ' ' + FETYPE
##                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)
##
####                else:
####                    FULLNAME = als2FENAME
####                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)
##
##                tarRows.insertRow((FEDIRP, modFENAME2, FETYPE, '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, \
##                                   modFULLNAME, 0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))
##
##
##        if srcRow[12] != None and srcRow[12] != ' ' and srcRow[12] != '':
##            acsFENAME = srcRow[12]
##
##            if FEDIRP != None and FEDIRP != '' and srcRow[20] != None:
##                FULLNAME = srcRow[1] + ' ' + acsFENAME + ' ' + srcRow[20][:1]
##            elif srcRow[20] != None:
##                FULLNAME = acsFENAME + ' ' + srcRow[20][:1]
##            else:
##                FULLNAME = acsFENAME
##
##            if srcRow[20] != None:
##                FEDIRS = srcRow[20]
##            else:
##                FEDIRS = None
##            tarRows.insertRow((FEDIRP, acsFENAME, '', FEDIRS, CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME, \
##                               0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))
##
##
##    del tarRows
##    del srcRows
##
##    #---Copy Roads to Blues Stakes root level-----------------
##    arcpy.CopyFeatures_management(roadsBS, outLoc + '\\TGR_StWide_lkA.shp')
##
##
##    #---Clip Blue Stakes Roads-----------------------------------------------------------
##    print 'Start Clipping Roads'
##    clip(roadsBS, 'lkA.shp');
##
##    print 'Done Translating Roads  ' + str(datetime.datetime.now())

#---KG Version-----------------------------------------------------------------------------------------------------------------------------------------------------------
def roads():

    print 'Starting Roads  ' + str(datetime.datetime.now())
    print 'Starting Roads  ' + str(datetime.datetime.now())

    roadsSGID = sgid10_GEO + '\\Roads'
    roadsBS = stageDB + '\\TGR_StWide_lkA'


    #----Move Roads to SGID10_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID10.TRANSPORTATION.Roads', roadsSGID)
##
    #----Check for statewide BlueStakes roads
    if not arcpy.Exists(roadsBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCClkA_schema', roadsBS)
    else:
        arcpy.DeleteFeatures_management(roadsBS)

    srcFlds = ['CARTOCODE', 'PREDIR', 'FULLNAME', 'STREETTYPE', 'SUFDIR', 'L_F_ADD', 'L_T_ADD', 'R_F_ADD', 'R_T_ADD', 'ALIAS1', \
               'ALIAS2', 'ACSALIAS', 'ACSNAME', 'COFIPS', 'HWYNAME', 'MODIFYDATE', 'ADDR_SYS', 'STREETNAME', 'SHAPE@', 'ALIAS1TYPE', 'ACSSUF', 'ALIAS2TYPE']


    tarFlds = ['FEDIRP', 'FENAME', 'FETYPE', 'FEDIRS', 'CFCC', 'FRADDL', 'TOADDL', 'FRADDR', 'TOADDR', 'CFCC1', 'CFCC2', 'FULLNAME', \
               'HASALT', 'ISALT', 'S_FIPS', 'AGRC_MDATE', 'ADDRESS_SY', 'SHAPE@']


    #----Remove empty spaces from roads----------------------------------------------------------------------------
##    with arcpy.da.UpdateCursor(roadsSGID, srcFlds) as rows:
##        count = 0
##        for row in rows:
##            for fld in srcFlds:
##                print fld
##                fldX = srcFlds.index(fld)
##
##                if row[fldX] == ' ':
##                    count = count + 1
##                    print str(count) + ' spaces removed'
##                    row[fldX] = None
##
##                if row[fldX] != None:
##                    row[fldX] = row[fldX].strip()
##
##                rows.updateRow(row)
##
##    del rows

##    rdFlds = ['FULLNAME', 'ALIAS1', 'STREETNAME']
##    with arcpy.da.UpdateCursor(roadsSGID, rdFlds) as rows:
##        for row in rows:
##            for fld in rdFlds:
##                fldX = rdFlds.index(fld)
##                if row[fldX] != None:
##                    row[fldX] = row[fldX].strip()
##
##                rows.updateRow(row)
##
##    del rows


    srcRows = arcpy.da.SearchCursor(roadsSGID, srcFlds)
    tarRows = arcpy.da.InsertCursor(roadsBS, tarFlds)

    print 'Start inserting rows'

    #----Format HasAlt isAlt values----
    def checkAlt(inRow):

        alias1 = srcRow[9]
        alias2 = srcRow[10]
        acsalias = srcRow[11]
        acsname = srcRow[12]

        if alias1 != None and alias1 != '':
            return '1'
        if alias2 != None and alias2 != '':
            return '1'
        if acsalias != None and acsalias != '':
            return '1'
        if acsname != None and acsname != '':
            return '1'
        if srcRow[2][-3:] == 'FWY':
            return '1'
        if srcRow[2][:3] == 'HWY':
            return'1'
        if srcRow[2][:2] == 'US':
            return '1'
        else:
            return '0'


    #----RegEx to format street avbreviations (i.e. ST RD TH --> st rd th)----
    def lowerAbrev(inRow):
        return inRow.group(0).lower()

    #---RegEx to format route directions (i.e. Nb Wb --> NB WB)
    def directionCase(inRow):
        return inRow.group(0).upper()


    for srcRow in srcRows:

        #----Prefix Direction----
        if srcRow[1] == None or srcRow[1] == '':
            FEDIRP = None
        else:
            FEDIRP = srcRow[1]

        #----Root and Full Street Name----
        if srcRow[2] != None:

            if FEDIRP != None and FEDIRP != '':
                #FULLNAME = (FEDIRP + ' ' + srcRow[2].replace('US', 'HWY')).title()
                FULLNAME = (FEDIRP + ' ' + srcRow[2].title()) #+ ' ZZ1'
        #----modFULLNAME calls lowerAbrev to convert a string like 3Rd to 3rd----
                modFULLNAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, FULLNAME, flags=re.IGNORECASE)
                #modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, modFULLNAME, flags=re.IGNORECASE)
                modFULLNAME = modFULLNAME.replace('Us ', 'Hwy ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF').replace('Fs', 'FS').replace('Blm', 'BLM')
        #----modFULLNAME calls directionCase to convert a string like Nb to NB----
                modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, modFULLNAME, flags=re.IGNORECASE)
                #modFULLNAME = modFULLNAME.replace('Us ', 'Hwy ').replace('Sr ', 'SR ').replace('Usu', 'USU').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF')
            elif srcRow[3] == 'RAMP':
                FULLNAME = srcRow[2].title()
                modFULLNAME = FULLNAME.replace('Us ', 'US ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF').replace('Blm', 'BLM')
                modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, modFULLNAME, flags=re.IGNORECASE)
                modFULLNAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, modFULLNAME, flags=re.IGNORECASE)
            else:
                #FULLNAME = srcRow[2].replace('US', 'HWY').title().replace('Sr ', 'SR ') + ' ZZ'
                FULLNAME = srcRow[2].title() #+ ' ZZ'
                modFULLNAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, FULLNAME, flags=re.IGNORECASE)
                modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, modFULLNAME, flags=re.IGNORECASE)
                #modFULLNAME = modFULLNAME.replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF')
                modFULLNAME = modFULLNAME.replace('Us ', 'Hwy ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF').replace('Fs', 'FS').replace('Blm', 'BLM')
        else:
            modFULLNAME = ''

        if srcRow[17] != None:
            FENAME = srcRow[17].replace('HIGHWAY', 'HWY').title().replace('Us ', 'US ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF').replace('Fs', 'FS').replace('Blm', 'BLM') #+ ' ZZ2'
            modFENAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, FENAME, flags=re.IGNORECASE)
            modFENAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, modFENAME, flags=re.IGNORECASE)
            #modFENAME = modFENAME.replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF')
            #modFENAME = modFENAME.replace('Us ', 'Hwy ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF')
            #FENAME = srcRow[17].replace('HIGHWAY', 'HWY').title().replace('Sr ', 'SR ')
##        if srcRow[3] == 'RAMP':
##            FENAME = srcRow[2].title().replace('Us ', 'US ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF') + ' zWTF'
##            #modFENAME = FENAME.replace('Us ', 'US ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF')
##            modFENAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FENAME, flags=re.IGNORECASE)
        else:
            modFENAME = ''


        #----Street Type----
        if srcRow[3] != None:
            FETYPE = srcRow[3].title()
        else:
            FETYPE = ''

        #----Sufix Direction----
        if srcRow[4] != None:
            FEDIRS = srcRow[4]
        else:
            FEDIRS = ''

        #----CFCC----
        if srcRow[0] != None:
            if srcRow[0] == '1':
                CFCC = 'A15'
            if srcRow[0] == '2':
                CFCC = 'A20'
            if srcRow[0] == '3':
                CFCC = 'A21'
            if srcRow[0] == '4':
                CFCC = 'A25'
            if srcRow[0] == '5':
                CFCC = 'A20'
            if srcRow[0] == '6':
                CFCC = 'A41'
            if srcRow[0] == '7':
                CFCC = 'A20'
            if srcRow[0] == '8':
                CFCC = 'A31'
            if srcRow[0] == '9':
                CFCC = 'A41'
            if srcRow[0] == '10':
                CFCC = 'A41'
            if srcRow[0] == '11':
                CFCC = 'A41'
            if srcRow[0] == '12':
                CFCC = 'A41'
            if srcRow[0] == '13':
                CFCC = 'A65'
            if srcRow[0] == '14':
                CFCC = 'A74'
            if srcRow[0] == '15':
                CFCC = 'A99'

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
        if srcRow[13] != None:
            S_FIPS = srcRow[13]
        else:
            S_FIPS = ''

        #----AGRC M Date----
        if srcRow[15] != None:
            AGRC_MDATE = srcRow[15]
        else:
            AGRC_MDATE = '1/1/1000'

        #----Address System----
        if srcRow[16] != None:
            ADDRESS_SY = srcRow[16].title()
        else:
            ADDRESS_SY = ''


        #----Has Alt Name----
        HASALT = checkAlt(srcRow)
        ISALT = '0'


        shp = srcRow[18]


        tarRows.insertRow((FEDIRP, modFENAME, FETYPE, FEDIRS, CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, modFULLNAME, HASALT, \
                           ISALT, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))



        #----Add Duplicate SR US and Interstate Highways---------------
        if srcRow[14] != None and srcRow[14] != '':
            addHWY = srcRow[14]

            if FEDIRP != None:
                FULLNAME = FEDIRP + ' ' + addHWY
            else:
                FULLNAME = addHWY

            tarRows.insertRow((FEDIRP, addHWY, '', '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME, \
                               0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))

            if addHWY[:2] == 'SR':
                if srcRow[2][:3] != 'HWY':
                    addHWY = addHWY.replace('SR', 'Hwy')
                    FULLNAME = FULLNAME.replace('SR', 'Hwy')

                    tarRows.insertRow((FEDIRP, addHWY, '', '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME, \
                                       0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))

            if addHWY[:2] == 'US':
                if srcRow[2][:2] != 'US':
                    addHWY = addHWY.replace('US', 'Hwy')
                    FULLNAME = FULLNAME.replace('US', 'Hwy')

                    tarRows.insertRow((FEDIRP, addHWY, '', '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME, \
                                       0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))



        #----Add Duplicate Alias1 and ACSAlias----
        if srcRow[9] != None and srcRow[9] != ' ' and srcRow[9] != '':
            if srcRow[9][:7] != 'HIGHWAY':
                #alsFENAME = srcRow[9].title().replace(' Sr', ' SR').replace('Us ', 'US ') + ' ZZ3'
                alsFENAME = srcRow[9].title().replace('Us ', 'US ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF').replace('Fs', 'FS').replace('Blm', 'BLM')
                modFENAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, alsFENAME, flags=re.IGNORECASE)

                if srcRow[19] != None:
                    FETYPE = srcRow[19].title()

                if FEDIRP != None:
                    FULLNAME = FEDIRP + ' ' + alsFENAME #+ ' ZZ4'
                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)

                if FEDIRP != None and srcRow[20] != None:
                    FULLNAME = FEDIRP + ' ' + alsFENAME + ' ' + srcRow[20][:1]
                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)

                if FEDIRP != None and FETYPE != None:
                    FULLNAME = FEDIRP + ' ' + alsFENAME + ' ' + FETYPE
                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)

                if FEDIRP == None and FETYPE != None:
                    FULLNAME = alsFENAME + ' ' + FETYPE
                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)

##                else:
##                    FULLNAME = alsFENAME
##                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)


                tarRows.insertRow((FEDIRP, modFENAME, FETYPE, '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, \
                                   modFULLNAME, 0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))



        #----Add Duplicate Alias2----
        if srcRow[10] != None and srcRow[10] != ' ' and srcRow[10] != '':
            if srcRow[10][:7] != 'HIGHWAY':
                als2FENAME = srcRow[10].title().replace('Us ', 'US ').replace('Sr ', 'SR ').replace('Usfs', 'USFS').replace('Usu', 'USU').replace('Rr', 'RR').replace('Usaf', 'USAF').replace('Fs', 'FS').replace('Blm', 'BLM')  #+ ' ZZ5'
                #als2FENAME = srcRow[10].title().replace(' Sr', ' SR').replace('Us ', 'US ')  + ' ZZ5'
                modFENAME2 = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, als2FENAME, flags=re.IGNORECASE)

                if srcRow[21] != None:
                    FETYPE = srcRow[21].title()

                if FEDIRP != None:
                    FULLNAME = FEDIRP + ' ' + als2FENAME
                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)

                if FEDIRP != None and srcRow[20] != None:
                    FULLNAME = FEDIRP + ' ' + als2FENAME + ' ' + srcRow[20][:1]
                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)

                if FEDIRP != None and FETYPE != None:
                    FULLNAME = FEDIRP + ' ' + als2FENAME + ' ' + FETYPE
                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)

                if FEDIRP == None and FETYPE != None:
                    FULLNAME = als2FENAME + ' ' + FETYPE
                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)

##                else:
##                    FULLNAME = als2FENAME
##                    modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', directionCase, FULLNAME, flags=re.IGNORECASE)

                tarRows.insertRow((FEDIRP, modFENAME2, FETYPE, '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, \
                                   modFULLNAME, 0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))


        if srcRow[12] != None and srcRow[12] != ' ' and srcRow[12] != '':
            acsFENAME = srcRow[12]

            if FEDIRP != None and FEDIRP != '' and srcRow[20] != None:
                FULLNAME = srcRow[1] + ' ' + acsFENAME + ' ' + srcRow[20][:1]
            elif srcRow[20] != None:
                FULLNAME = acsFENAME + ' ' + srcRow[20][:1]
            else:
                FULLNAME = acsFENAME

            if srcRow[20] != None:
                FEDIRS = srcRow[20]
            else:
                FEDIRS = None
            tarRows.insertRow((FEDIRP, acsFENAME, '', FEDIRS, CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME, \
                               0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))


    del tarRows
    del srcRows

    #---Copy Roads to Blues Stakes root level-----------------
    arcpy.CopyFeatures_management(roadsBS, outLoc + '\\TGR_StWide_lkA.shp')


    #---Clip Blue Stakes Roads-----------------------------------------------------------
    print 'Start Clipping Roads'
    clip(roadsBS, 'lkA.shp');

    #arcpy.CopyFeatures_management (r'Database Connections\DC_KELLY_EDIT@UTRANS@GRDB01SPR.sde\UTRANS.TRANSADMIN.StatewideStreets', roadsAGRCSchema)
    arcpy.CopyFeatures_management('SGID10.TRANSPORTATION.Roads', roadsSGID)
    print 'Done Translating Roads  ' + str(datetime.datetime.now())
#---------------------------------------------------------------------------------------------------------------------------------------------------------------

def municipalities():

    print 'Starting Municipalities  ' + str(datetime.datetime.now())

    env.workspace = sgid10
    arcpy.env.overwriteOutput = True

    muni = sgid10_GEO + '\\Municipalities'
    muniBS = stageDB + '\\TGR_StWide_plc00'

    #---Copy Municipalites to SGID10_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID10.BOUNDARIES.Municipalities', muni)

    #---Check for statewide municipalities BlueStakes schema
    if not arcpy.Exists(muniBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCCplc00_schema', muniBS)
    else:
        arcpy.DeleteFeatures_management(muniBS)

    srcFlds = ['NAME', 'SHAPE@']
    tarFlds = ['NAME', 'SHAPE@']
    cntyFlds = ['NAME', 'FIPS_STR', 'SHAPE@']

    srcRows = arcpy.da.SearchCursor(muni, srcFlds)
    tarRows = arcpy.da.InsertCursor(muniBS, tarFlds)

    for srcRow in srcRows:

        NAME = srcRow[0].replace('St.', 'St')
        shp = srcRow[1]

        tarRows.insertRow((NAME, shp))

    del tarRows


    #---Copy Municipalities to Blues Stakes root level
    arcpy.CopyFeatures_management(muniBS, outLoc + '\\TGR_StWide_plc00.shp')


    #---Clip Blue Stakes Municipalities-----------------------------------------------------------
    clip(muniBS, 'plc00.shp');


    print 'Done Translating Municipalities  ' + str(datetime.datetime.now())

def mileposts():

    print 'Starting Mileposts  ' + str(datetime.datetime.now())

    env.workspace = sgid10
    arcpy.env.overwriteOutput = True

    milePosts = sgid10_GEO + '\\UDOTMilePosts'
    exits = sgid10_GEO + '\\Roads_FreewayExits'
    milePostsBS = stageDB + '\\Hwy_MPM'

    #---Copy new Exits and Mileposts to Staging DB
    arcpy.CopyFeatures_management('SGID10.TRANSPORTATION.Roads_FreewayExits', exits)
    arcpy.CopyFeatures_management('SGID10.TRANSPORTATION.UDOTMileposts', milePosts)
    print 'Copied SGID10.TRANSPORTATION.Roads_FreewayExits to staging DB'
    print 'Copied SGID10.TRANSPORTATION.UDOTMileposts to staging DB'


    #---Check for Mileposts BlueStakes schema
    if not arcpy.Exists(milePostsBS):
        arcpy.CopyFeatures_management(schemaDB + '\\Hwy_MPM', milePostsBS)
    else:
        arcpy.DeleteFeatures_management(milePostsBS)


    srcMP_Flds = ['LABEL', 'MP', 'CARTO', 'RT_DIR', 'SHAPE@']
    srcEX_Flds = ['EXITNAME', 'SHAPE@']
    tarFlds = ['Type', 'Label_Name', 'SHAPE@']


    srcMP_Rows = arcpy.da.SearchCursor(milePosts, srcMP_Flds)
    srcEX_Rows = arcpy.da.SearchCursor(exits, srcEX_Flds)
    tarRows = arcpy.da.InsertCursor(milePostsBS, tarFlds)

    #----Add Milepost Records--------------------------------------------------------
    for srcMP_Row in srcMP_Rows:

        Type = 'mpm'

        hwyDig1 = srcMP_Row[0][3:4]
        hwyDig2 = srcMP_Row[0][2:4]
        hwyDig3 = srcMP_Row[0][1:4]
        mp = str(srcMP_Row[1]).split('.')[0]

        if srcMP_Row[3] == 'N':
            Label_Name = ''
        elif srcMP_Row[2] == '1' and srcMP_Row[3] == 'P':
            Label_Name = 'I-{0} milepost {1}'.format(hwyDig2, mp)
        else:
            if srcMP_Row[0][:3] == '000':
                Label_Name = 'Hwy {0} milepost {1}'.format(hwyDig1, mp)
            elif srcMP_Row[0][:2] == '00':
                Label_Name = 'Hwy {0} milepost {1}'.format(hwyDig2, mp)
            else:
                Label_Name = 'Hwy {0} milepost {1}'.format(hwyDig3, mp)

        shp = srcMP_Row[4]

        tarRows.insertRow((Type, Label_Name, shp))

    #----Add Exit Records-------------------------------------------------------------
    for srcEX_Row in srcEX_Rows:

        Type = 'epm'

        if srcEX_Row[0].split()[0] == 'SR':
            Label_Name = 'Hwy ' + ' '.join(srcEX_Row[0].split()[1:])
        elif srcEX_Row[0].split()[0] == 'US':
            Label_Name = 'Hwy ' + ' '.join(srcEX_Row[0].split()[1:])
        else:
            Label_Name = srcEX_Row[0]

        shp = srcEX_Row[1]

        tarRows.insertRow((Type, Label_Name, shp))

    del tarRows


    #----Copy Mileposts to shapefile--------------------------------------------------
    arcpy.CopyFeatures_management(milePostsBS, outLoc + '\\Hwy_MPM.shp')


    print 'Done Translating Mileposts  ' + str(datetime.datetime.now())

def landownershipLarge():

    print 'Starting Large Landownership  ' + str(datetime.datetime.now())

    env.workspace = sgid10
    arcpy.env.overwriteOutput = True

    landown = sgid10_GEO + '\\LandOwnership'
    parks = sgid10_GEO + '\\Parks'
    cemeteries = sgid10_GEO + '\\Cemeteries'
    golf = sgid10_GEO + '\\GolfCourses'

    landownBS = stageDB + '\\TGR_StWide_lpy'

    clpCnty = 'SGID10.BOUNDARIES.Counties'

    #---Copy Landownership, Parks, and Cemeteries to SGID10_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID10.CADASTRE.LandOwnership', landown)
    arcpy.CopyFeatures_management('SGID10.RECREATION.ParksLocal', parks)
    arcpy.CopyFeatures_management('SGID10.SOCIETY.Cemeteries_Poly', cemeteries)
    arcpy.CopyFeatures_management('SGID10.RECREATION.GolfCourses', golf)

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
                LANDNAME = srcLnd_Row[3]
            else:
                LANDNAME = srcLnd_Row[4]

            shp = srcLnd_Row[5]

            tarRows.insertRow((CFCC, LANDNAME, shp))

        if srcLnd_Row[1] == 'Military':

            CFCC = 'D10'

            if srcLnd_Row[3] != None:
                LANDNAME = srcLnd_Row[3]
            else:
                LANDNAME = srcLnd_Row[4]

            shp = srcLnd_Row[5]

            tarRows.insertRow((CFCC, LANDNAME, shp))

        # if srcLnd_Row[1] == 'National Historic Site' or srcLnd_Row[1] == 'National Monument' \
        #                     or srcLnd_Row[1] == 'National Park' or srcLnd_Row == 'National Recreation Area':

        if srcLnd_Row[1] in monType:

            CFCC = 'D83'

            if srcLnd_Row[3] != None:
                LANDNAME = srcLnd_Row[3]
            else:
                LANDNAME = srcLnd_Row[4]

            shp = srcLnd_Row[5]

            tarRows.insertRow((CFCC, LANDNAME, shp))

        if srcLnd_Row[1] == 'National Forest':

            CFCC = 'D84'

            if srcLnd_Row[3] != None:
                LANDNAME = srcLnd_Row[3]
            else:
                LANDNAME = srcLnd_Row[4]

            shp = srcLnd_Row[5]

            tarRows.insertRow((CFCC, LANDNAME, shp))

        if srcLnd_Row[1] == 'Primitive Area' or srcLnd_Row[1] == 'Wilderness' or srcLnd_Row[1] == 'Wildlife Reserve/Management Area' \
                             or srcLnd_Row[1] == 'National Wildlife Refuge':

            CFCC = 'D89'

            if srcLnd_Row[3] != None:
                LANDNAME = srcLnd_Row[3]
            else:
                LANDNAME = srcLnd_Row[4]

            shp = srcLnd_Row[5]

            tarRows.insertRow((CFCC, LANDNAME, shp))

        if srcLnd_Row[1] == 'Parks and Recreation':

            CFCC = 'D85'

            if srcLnd_Row[3] != None:
                LANDNAME = srcLnd_Row[3]
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
    clip(landownBS, 'lpy.shp');


    print 'Done Translating Large Landownership  ' + str(datetime.datetime.now())

def waterPoly():

    print 'Starting Lakes  ' + str(datetime.datetime.now())

    lakes = sgid10_GEO + '\\LakesNHDHighRes'
    lakesBS = stageDB + '\\TGR_StWide_wat'

    #---Copy lakesNHD to SGID10_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID10.WATER.LakesNHDHighRes', lakes)

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

        # else:
        #     continue

    #---Copy Lakes to Blue Stakes root level---------------
    arcpy.CopyFeatures_management(lakesBS, outLoc + '\\TGR_StWide_WAT.shp')


    #---Clip Blue Stakes Misc Transportation-----------------------------------------------------------
    clip(lakesBS, 'WAT.shp');


    print 'Done Translating Lakes  ' + str(datetime.datetime.now())

def waterLines():

    print 'Starting Rivers  ' + str(datetime.datetime.now())

    rivers = sgid10_GEO + '\\StreamsNHD'
    riversBS = stageDB + '\\TGR_StWide_lkH'

    arcpy.CopyFeatures_management('SGID10.WATER.StreamsNHDHighRes', rivers)

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
    clip(riversBS, 'lkH.shp');


    print 'Done Translating Rivers  ' + str(datetime.datetime.now())

def railroads():

    print 'Starting Railroads  ' + str(datetime.datetime.now())

    env.workspace = sgid10
    arcpy.env.overwriteOutput = True

    rail = sgid10_GEO + '\\Railroads'
    railLt = sgid10_GEO + '\\LightRail_UTA'
    #railLt_new = sgid10_GEO + '\\LightRailNewRoutes_UTA'
    railCommut = sgid10_GEO + '\\CommuterRailRoute_UTA'
    #railCommut_new = sgid10_GEO + '\\CommuterRailNewRoutes_UTA'

    railBS = stageDB + '\\TGR_StWide_lkB'

    arcpy.CopyFeatures_management('SGID10.TRANSPORTATION.Railroads', rail)
    arcpy.CopyFeatures_management('SGID10.TRANSPORTATION.LightRail_UTA', railLt)
    arcpy.CopyFeatures_management('SGID10.TRANSPORTATION.CommuterRailRoutes_UTA', railCommut)


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
    clip(railBS, 'lkB.shp');

    print 'Done Translating Railroads  ' + str(datetime.datetime.now())

def airstrips():

    print 'Starting Airstrips  ' + str(datetime.datetime.now())

    airstrips = sgid10_GEO + '\\Airports'
    airstripsBS = stageDB + '\\TGR_StWide_lkD'
    clpCnty = 'SGID10.BOUNDARIES.Counties'

    arcpy.CopyFeatures_management('SGID10.TRANSPORTATION.Airports', airstrips)

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
    clip(airstripsBS, 'lkD.shp');


    print 'Done Translating Airstrips  ' + str(datetime.datetime.now())

def miscTransportation():

    print 'Starting Misc Transportation  ' + str(datetime.datetime.now())

    miscTrans_ski = sgid10_GEO + '\\SkiLifts'
    miscTrans_TransLines = sgid10_GEO + '\\TransmissionLines'
    miscTrans_ElecLines = sgid10_GEO + '\\ElectricLines'
    miscTransBS = stageDB + '\\TGR_StWide_lkC'
    clpCnty = 'SGID10.BOUNDARIES.Counties'


    # arcpy.CopyFeatures_management('SGID10.RECREATION.SkiLifts', miscTrans_ski)
    # arcpy.CopyFeatures_management('SGID10.UTILITIES.TransmissionLines', miscTrans_TransLines)
    # arcpy.CopyFeatures_management('SGID10.UTILITIES.ElectricalLines', miscTrans_ElecLines)


    #---Check for statewide municipalities BlueStakes schema
    if not arcpy.Exists(miscTransBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCClkC_schema', miscTransBS)
    else:
        arcpy.DeleteFeatures_management(miscTransBS)

    srcFlds_ski = ['LIFT_NAME', 'SHAPE@']
    srcFlds_trans = ['LAYER', 'SHAPE@']
    srcFlds_elec = ['SHAPE@']
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


    #---Copy Misc Trans to Blue Stakes root level---------------
    arcpy.CopyFeatures_management(miscTransBS, outLoc + '\\TGR_StWide_lkC.shp')


    #---Clip Blue Stakes Misc Transportation-----------------------------------------------------------
    clip(miscTransBS, 'lkC.shp');


    print 'Done Translating Misc Transportation  ' + str(datetime.datetime.now())

def townships():

    print 'Starting Townships  ' + str(datetime.datetime.now())

    twnShips = sgid10_GEO + '\\PLSSTownships'
    twnShipsBS = stageDB + '\\UT_TR'

    #---Copy Townships in SGID10_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID10.CADASTRE.PLSSTownships_GCDB', twnShips)

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


    print 'Done Translating Townships  ' + str(datetime.datetime.now())

def sections():

    print 'Starting Sections  ' + str(datetime.datetime.now())

    meridianDict = {'26':'SL', '30':'UI'}

    sections = sgid10_GEO + '\\PLSSSections'
    sectionsBS = stageDB + '\\UT_TRS'

    #---Move Sections to SGID10_GEOGRAPHIC staging area

    arcpy.CopyFeatures_management('SGID10.CADASTRE.PLSSSections_GCDB', sections)

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
            print fullName
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


    print 'Done Translating Sections  ' + str(datetime.datetime.now())

def deciPoints():

    print 'Starting Deci Points (GNIS) ' + str(datetime.datetime.now())

    deciPts = sgid10_GEO + '\\GNIS2010'
    deciPtsBS = stageDB + '\\TGR_StWide_deci'

    #---Move GNIS to SGID10_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID10.LOCATION.PlaceNamesGNIS2010', deciPts)

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
    clip(deciPtsBS, 'deci.shp');


    print 'Done Translating Deci Points (GNIS) ' + str(datetime.datetime.now())

def addedPoints():

    print 'Starting Added Points ' + str(datetime.datetime.now())

    correctionsPts = sgid10_GEO + '\\CorrectionalFacilities'
    fireStnPts = sgid10_GEO + '\\FireStations'
    libraryPts = sgid10_GEO + '\\Libraries'
    liquorPts = sgid10_GEO + '\\LiquorStores'
    churchPts = sgid10_GEO + '\\PlacesOfWorship'
    policePts = sgid10_GEO + '\\PoliceStations'
    postOfficePts = sgid10_GEO + '\\PostOffices'
    schoolPts = sgid10_GEO + '\\Schools'
    mallPts = sgid10_GEO + '\\ShoppingMalls'
    healthCarePts = sgid10_GEO + '\\HealthCareFacilities'

    addedPtsBS = stageDB + '\\TGR_StWide_added'

    #---Move Points to SGID10_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID10.SOCIETY.CorrectionalFacilities', correctionsPts)
    arcpy.CopyFeatures_management('SGID10.SOCIETY.FireStations', fireStnPts)
    arcpy.CopyFeatures_management('SGID10.SOCIETY.Libraries', libraryPts)
    arcpy.CopyFeatures_management('SGID10.SOCIETY.LiquorStores', liquorPts)
    arcpy.CopyFeatures_management('SGID10.SOCIETY.PlacesOfWorship', churchPts)
    arcpy.CopyFeatures_management('SGID10.SOCIETY.PoliceStations', policePts)
    arcpy.CopyFeatures_management('SGID10.SOCIETY.PostOffices', postOfficePts)
    arcpy.CopyFeatures_management('SGID10.SOCIETY.Schools', schoolPts)
    arcpy.CopyFeatures_management('SGID10.SOCIETY.ShoppingMalls', mallPts)
    arcpy.CopyFeatures_management('SGID10.HEALTH.HealthCareFacilities', healthCarePts)
    print 'Done copying features from SGID10 to staging area'

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

        print 'Added ' + pointFC


    liquorFlds = ['TYPE', 'SHAPE@']
    policeFlds = ['NAME', 'SHAPE@']
    postOfficeFlds = ['TOWN', 'STREET', 'SHAPE@']
    schoolFlds = ['INSTITUTION_NAME', 'SHAPE@']

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

    print 'Added ' + liquorPts


    for policeRow in policeRows:

        if policeRow[0] != None:
            if policeRow[0] == 'UNITED STATES FISH AND WILDLIFE SERVICE - OFFICE OF LAW ENFORCEMENT - BEAR RIVER MIGRATORY BIRD REFUGE':
                NAME = 'U.S. Fish And Wildlife Service - Law Enforcement - Bear River Bird Refuge'
            else:
                NAME = (policeRow[0].title().replace('United States', 'U.S.'))
        else:
            NAME = ''

        shp = policeRow[1]

        tarRows.insertRow((NAME, shp))

    print 'Added ' + policePts


    for postOfficeRow in postOfficeRows:

        if postOfficeRow[0] != None:
            NAME = postOfficeRow[0] + ' Post Office'
        else:
            NAME = 'Post Office'

        shp = policeRow[1]

        tarRows.insertRow((NAME, shp))

    print 'Added ' + postOfficePts


    for schoolRow in schoolRows:

        if schoolRow[0] != None:
            NAME = schoolRow[0].title()
        else:
            NAME = ''

        shp = schoolRow[1]

        tarRows.insertRow((NAME, shp))

    print 'Added ' + schoolPts


    del tarRows


    #---Copy Added Points to Blue Stakes root level---------------
    arcpy.CopyFeatures_management(addedPtsBS, outLoc + '\\TGR_StWide_added.shp')

    #---Clip Blue Stakes Deci Points-----------------------------------------------------------
    clip(addedPtsBS, 'added.shp');


    print 'Done Translating Added Points ' + str(datetime.datetime.now())

def counties():

    print 'Starting Counties ' + str(datetime.datetime.now())

    cnty = sgid10_GEO + '\\Counties'
    utah = sgid10_GEO + '\\Utah'
    cntyBS = stageDB + '\\TGRSSCCCcty00'
    cntyBS_All = stageDB + '\\CO49_D90'
    stateBS = stageDB + '\\ST49_D00'

    #---Move Counties to SGID10_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID10.BOUNDARIES.Counties', cnty)
    arcpy.CopyFeatures_management('SGID10.BOUNDARIES.Utah', utah)

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



    print 'Done Translating Counties ' + str(datetime.datetime.now())

def addressZones():

    print 'Starting Address Zones  ' + str(datetime.datetime.now())

    addZones = sgid10_GEO + '\\AddressSystemQuadrants'
    addZonesBS = stageDB + '\\addrsys'

    #---Add Address Zones to SGID10_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID10.LOCATION.AddressSystemQuadrants', addZones)

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
    clpFlds = ['NAME', 'FIPS_STR', 'SHAPE@']
    clpRows = arcpy.da.SearchCursor(clpCnty, clpFlds)

    for row in clpRows:
        clpFeat = row[2]

        #----Delete shapefiles with no features----
        clp = arcpy.Clip_analysis(addZonesBS, clpFeat, outLoc + '\\TGR' + row[1] + '\\addrsys' + row[1] + '.shp')
        clpCount = int(arcpy.GetCount_management(clp).getOutput(0))

        if clpCount < 1:
            arcpy.Delete_management(clp)

        flds = arcpy.ListFields(clp)
        for fld in flds:
            if fld.name == 'Shape_Area':
                arcpy.DeleteField_management(clp, 'Shape_Area')
            if fld.name == 'Shape_Leng':
                arcpy.DeleteField_management(clp, 'Shape_Leng')


    print 'Done Translating Address Zones  ' + str(datetime.datetime.now())

def oilAndGasWells():

    print 'Starting Oil and Gas  ' + str(datetime.datetime.now())

    og = sgid10_GEO + '\\DNROilGasWells'
    ogBS = stageDB + '\\wells_oil_gas'

    #---Add Address Zones to SGID10_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID10.ENERGY.DNROilGasWells', og)

    #---Check for Address Zones BlueStakes schema
    if not arcpy.Exists(ogBS):
        arcpy.CopyFeatures_management(schemaDB + '\\OilGasWells_Schema', ogBS)
    else:
        arcpy.DeleteFeatures_management(ogBS)

    srcFlds = ['API', 'WELL_NAME', 'FIELD_NAME', 'COMPANY_NAME', 'LAT_SURF', 'LONG_SURF', 'SHAPE@']
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
    #clip(ogBS, 'ogw.shp')


def clip(clipMe, outNameSuffix):

    #---Clip Blue Stakes output, delete empty shapefiles, delete Shape_Leng field----
    print 'Clipping ' + clipMe

    clpCnty = sgid10_GEO + '\\Counties'

    if arcpy.Exists(clpCnty):
        arcpy.Delete_management(clpCnty)
        arcpy.CopyFeatures_management('SGID10.BOUNDARIES.Counties', clpCnty)
    else:
        arcpy.CopyFeatures_management('SGID10.BOUNDARIES.Counties', clpCnty)

    clpFlds = ['NAME', 'FIPS_STR', 'SHAPE@']
    clpRows = arcpy.da.SearchCursor(clpCnty, clpFlds)
    fldrPrefix = '\\TGR'

    for row in clpRows:
        clpFeat = row[2]
        print 'Clipping ' + row[0] + ' County'

        #----Delete shapefiles with no features----
        clp = arcpy.Clip_analysis(clipMe, clpFeat, outLoc + fldrPrefix + row[1] + fldrPrefix + row[1] + outNameSuffix)
        clpCount = int(arcpy.GetCount_management(clp).getOutput(0))

        flds = arcpy.ListFields(clp)
        for fld in flds:
            if fld.name == 'Shape_Area':
                arcpy.DeleteField_management(clp, 'Shape_Area')
            if fld.name == 'Shape_Length':
                arcpy.DeleteField_management(clp, 'Shape_Length')
            if fld.name == 'Shape_Leng':
                arcpy.DeleteField_management(clp, 'Shape_Leng')

        if clpCount < 1:
            arcpy.Delete_management(clp)

def cleanOutFldr():
    #----Delete all shapefiles from----
    for root, dirs, files in os.walk(outLoc):
        for f in files:
            deleteme = os.path.join(root, f)
            print 'Deleted ' + deleteme
            os.remove(deleteme)




#cleanOutFldr();

#parcels();
#roads();
#municipalities();
#mileposts();
#landownershipLarge();
#waterPoly();
#waterLines();
#railroads();
#airstrips();
#miscTransportation();
addressPoints();
#townships();
#sections();
#deciPoints();
#addedPoints();
#counties();
#addressZones();
#oilAndGasWells();

