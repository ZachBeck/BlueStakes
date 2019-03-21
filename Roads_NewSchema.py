import os, arcpy, datetime, time, re
from arcpy import env
from arcpy import da
from agrc import parse_address



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


fipsNum = ['49001', '49003', '49005', '49007', '49009', '49011', '49013', '49015', '49017', '49019', '49021', \
          '49023', '49025', '49027', '49029', '49031', '49033', '49035', '49037', '49039', '49041', '49043', '49045', \
          '49047', '49049', '49051', '49053', '49055', '49057']


fipsDict = {'Beaver':'49001', 'BoxElder':'49003', 'Cache':'49005', 'Carbon':'49007', 'Daggett':'49009', \
           'Davis':'49011', 'Duchesne':'49013', 'Emery':'49015', 'Garfield':'49017', 'Grand':'49019', \
           'Iron':'49021', 'Juab':'49023', 'Kane':'49025', 'Millard':'49027', 'Morgan':'49029', \
           'Piute':'49031', 'Rich':'49033', 'SaltLake':'49035', 'SanJuan':'49037', 'Sanpete':'49039', \
           'Sevier':'49041', 'Summit':'49043', 'Tooele':'49045', 'Uintah':'49047', 'Utah':'49049', \
           'Wasatch':'49051', 'Washington':'49053', 'Wayne':'49055', 'Weber':'49057'}

typeList = ['ALY', 'AVE', 'BAY', 'BLVD', 'CIR', 'COR', 'CRK', 'CT', 'CTR', 'CV', 'CYN', 'DR', 'ESTS', 'EXPY', 'FRK', \
            'FWY', 'GRV', 'HL', 'HOLW', 'HTS', 'HWY', 'JCT', 'LN', 'LNDG', 'LOOP', 'MDW', 'MDWS', 'MNR', 'PARK', \
            'PASS', 'PATH', 'PKWY', 'PL', 'PT', 'RAMP', 'RD', 'RDG', 'RNCH', 'ROW', 'RTE', 'RUN', 'SPUR', 'SQ', 'ST', \
            'TER', 'TRCE', 'TRL', 'VIS', 'VLG', 'VW', 'WAY', 'XING']

typeList2 = ('ALLEY', 'AVENUE', 'BAY', 'BOULEVARD', 'CIRCLE', 'COURT', 'COVE', 'DRIVE', 'ESTATE', 'ESTATES', 'EXPRESSWAY', \
             'FREEWAY', 'HEIGHTS', 'HIGHWAY', 'HOLLOW', 'JUNCTION', 'LANE', 'LOOP', 'PARKWAY', 'PLACE', 'PLAZA', \
             'POINT', 'RAMP', 'RANCH', 'ROAD', 'ROUTE', 'RUN', 'ROW', 'SQUARE', 'STREET', 'TERRACE', 'TRAIL', 'WAY', 'CORNER')

typeDict = {'ALLEY':'ALY', 'AVENUE':'AVE', 'BOULEVARD':'BLVD', 'CIRCLE':'CIR', 'COURT':'CT', 'COVE':'CV', \
            'DRIVE':'DR', 'ESTATE':'EST', 'ESTATES':'ESTS', 'EXPRESSWAY':'EXPY', 'FREEWAY':'FWY', 'HIGHWAY':'HWY', \
            'HOLLOW':'HOLW', 'JUNCTION':'JCT', 'LANE':'LN', 'LOOP':'LOOP', 'PARKWAY':'PKWY', 'PLACE':'PL', \
            'PLAZA':'PLZ', 'POINT':'PT', 'RAMP':'RAMP', 'RANCH':'RNCH', 'ROAD':'RD', 'ROUTE':'RTE', 'RUN':'RUN', \
            'ROW':'RW', 'SQUARE':'SQ', 'STREET':'ST', 'TERRACE':'TER', 'TRAIL':'TRL', 'WAY':'WAY', 'HEIGHTS':'HTS', \
            'CORNER':'COR'}

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

def formatValues(word, inValues):
    returnEmpty(word, errorList)
    if word != None:
        if word.strip() in inValues:
            return word.strip()
        return ''
    return ''


def roads():

    print 'Starting Roads  ' + str(datetime.datetime.now())

    env.workspace = sgid10
    arcpy.env.overwriteOutput = True

    roadsSGID = sgid10_GEO + '\\Roads'
    roadsBS = stageDB + '\\TGR_StWide_lkA_NewSchema_1'
    roadSegsQuestar = stageDB + '\\QUESTAR_GEOGRAPHIC\RoadSegs_Questar'

    # #----Move Roads to SGID10_GEOGRAPHIC staging area
    # arcpy.CopyFeatures_management('SGID10.TRANSPORTATION.Roads', roadsSGID)

    #----Check for statewide BlueStakes roads
    if not arcpy.Exists(roadsBS):
        arcpy.CopyFeatures_management(schemaDB + '\\TGRSSCCClkA_schema', roadsBS)
    else:
        #arcpy.DeleteFeatures_management(roadsBS)
        arcpy.TruncateTable_management(roadsBS)

    srcFlds = ['CARTOCODE', 'PREDIR', 'FULLNAME', 'POSTTYPE', 'POSTDIR', 'FROMADDR_L', 'TOADDR_L', 'FROMADDR_R', \
               'TOADDR_R', 'A1_NAME', 'A2_NAME', 'AN_NAME', 'AN_POSTDIR', 'COUNTY_L', 'DOT_HWYNAM', 'UPDATED', \
               'ADDRSYS_L', 'NAME', 'SHAPE@', 'A1_POSTTYPE', 'A2_POSTTYPE', 'COUNTY_R', 'ADDRSYS_R']

    oldRoadsSchema = ['CARTOCODE', 'PREDIR', 'FULLNAME', 'STREETTYPE', 'SUFDIR', 'L_F_ADD', 'L_T_ADD', 'R_F_ADD', 'R_T_ADD', 'ALIAS1', \
                      'ALIAS2', 'ACSALIAS', 'ACSNAME', 'COFIPS', 'HWYNAME', 'MODIFYDATE', 'ADDR_SYS', 'STREETNAME', 'SHAPE@', 'ALIAS1TYPE', 'ACSSUF', 'ALIAS2TYPE']

    tarFlds = ['FEDIRP', 'FENAME', 'FETYPE', 'FEDIRS', 'CFCC', 'FRADDL', 'TOADDL', 'FRADDR', 'TOADDR', 'CFCC1', 'CFCC2', 'FULLNAME', \
               'HASALT', 'ISALT', 'S_FIPS', 'AGRC_MDATE', 'ADDRESS_SY', 'SHAPE@']

    replaceDict = {'Sr':'SR', 'Usfs':'USFS', 'Us ':'US ', 'Usu ':'USU ', 'Rr':'RR', 'Usaf':'USAF', 'Fs':'FS', 'Blm':'BLM', 'Mvc':'MVC'} #'Us ':'Hwy ',

    print 'Start inserting rows'

    def replacePropCase(string, dict):
        for i in dict:
            if i in string:
                return string.replace(i, dict[i])
        return string

    #----Format HasAlt isAlt values----
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
            return'1'
        if srcRow[2] not in errorList and srcRow[2][:3] == 'US ':
            return '1'
        else:
            return '0'

    #----RegEx to format street avbreviations (i.e. ST RD TH --> st rd th)----
    def lowerAbrev(inRow):
        return inRow.group(0).lower()

    #---RegEx to format route directions (i.e. Nb Wb --> NB WB)
    def upperAbrev(inRow):
        return inRow.group(0).upper()



    tarRows = arcpy.da.InsertCursor(roadsBS, tarFlds)

    with arcpy.da.SearchCursor(roadsSGID, srcFlds) as srcRows:
        for srcRow in srcRows:

            #----Prefix Direction----
            FEDIRP = formatValues(srcRow[1], dirList)

            #----Sufix Direction----
            FEDIRS = formatValues(srcRow[4], dirList)

            #----Root and Full Street Name----
            # if srcRow[2] not in errorList:
            #
            #     modFULLNAME = '{} {}'.format(FEDIRP, srcRow[2].title()).strip()
            #     modFULLNAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, modFULLNAME, flags=re.IGNORECASE)
            #     modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, modFULLNAME, flags=re.IGNORECASE)
            #     modFULLNAME = replacePropCase(modFULLNAME, replaceDict)
            #
            # elif srcRow[3] == 'RAMP':
            #     modFULLNAME = srcRow[2].title()
            #     modFULLNAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, modFULLNAME, flags=re.IGNORECASE)
            #     modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, modFULLNAME, flags=re.IGNORECASE)
            #     modFULLNAME = replacePropCase(modFULLNAME, replaceDict)
            #
            # else:
            #     modFULLNAME = ''
            #
            # # modFULLNAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, FULLNAME, flags=re.IGNORECASE)
            # # modFULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, modFULLNAME, flags=re.IGNORECASE)
            # # modFULLNAME = replacePropCase(modFULLNAME, replaceDict)
            if srcRow[2] not in errorList:
                FULLNAME = '{} {}'.format(FEDIRP, srcRow[2].title()).strip()

            elif srcRow[3] == 'RAMP':
                FULLNAME = srcRow[2].title()

            else:
                FULLNAME = ''

            FULLNAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, FULLNAME, flags=re.IGNORECASE)
            FULLNAME = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, FULLNAME, flags=re.IGNORECASE)
            FULLNAME = replacePropCase(FULLNAME, replaceDict)

            if srcRow[17] != None:
                FENAME = srcRow[17].title()
                modFENAME = replacePropCase(FENAME, replaceDict)
                modFENAME = re.sub('\d+(st|nd|rd|th)\\b', lowerAbrev, modFENAME, flags=re.IGNORECASE)
                modFENAME = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, modFENAME, flags=re.IGNORECASE)
            else:
                modFENAME = ''

            #----Street Type----
            FETYPE = formatValues(srcRow[3], typeList).title()

            #----CFCC----
            CartoToCFCC = {'1':'A15', '2':'A20', '3':'A21', '4':'A25', '5':'A20', '6':'A41', '7':'A20', '8':'A31', '9':'A41', \
                           '10':'A41', '11':'A41', '12':'A41', '13':'A65', '14':'A74', '15':'A99', '16':'A41', '17':'A41', '18':'A41'}
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

            tarRows.insertRow((FEDIRP, modFENAME, FETYPE, FEDIRS, CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, FULLNAME, HASALT, \
                               ISALT, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))

            # modFULLNAME = ''
            # modFENAME = ''
            # FULLNAME = ''

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
            if srcRow[9] not in errorList:
                if srcRow[9][:7] != 'HIGHWAY':
                    alsFENAME = srcRow[9].title()
                    mod_alsFENAME = replacePropCase(alsFENAME, replaceDict)
                    mod_alsFENAME = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, mod_alsFENAME, flags=re.IGNORECASE)

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

                    modFULLNAME_a1 = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, FULLNAME_a1, flags=re.IGNORECASE).strip()
                    modFULLNAME_a1 = replacePropCase(modFULLNAME_a1, replaceDict)

                    tarRows.insertRow((FEDIRP, mod_alsFENAME, FETYPE, '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, \
                                       modFULLNAME_a1, 0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))


            #----Add Duplicate Alias2----
            if srcRow[10] not in errorList:
                if srcRow[10][:7] != 'HIGHWAY':
                    als2FENAME = srcRow[10].title()
                    modFENAME2 = replacePropCase(als2FENAME, replaceDict)
                    modFENAME2 = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, modFENAME2, flags=re.IGNORECASE)

                    if srcRow[20] != None:
                        FETYPE = srcRow[20].title()

                    if FEDIRP != None:
                        FULLNAME_a2 = '{} {}'.format(FEDIRP, modFENAME2).strip()  #FEDIRP + ' ' + modFENAME2

                    if FEDIRP != None and srcRow[12] != None:
                        FULLNAME_a2 = '{} {} {}'.format(FEDIRP, modFENAME2, srcRow[12][:1]).strip()  #FEDIRP + ' ' + modFENAME2 + ' ' + srcRow[12][:1]

                    if FEDIRP != None and FETYPE != None:
                        FULLNAME_a2 = '{} {} {}'.format(FEDIRP, modFENAME2, FETYPE).strip()  #FEDIRP + ' ' + modFENAME2 + ' ' + FETYPE

                    if FEDIRP == None and FETYPE != None:
                        FULLNAME_a2 = '{} {}'.format(modFENAME2, FETYPE)  #modFENAME2 + ' ' + FETYPE

                    modFULLNAME_a2 = re.sub('\W(nb|sb|eb|wb)\\b', upperAbrev, FULLNAME_a2, flags=re.IGNORECASE)
                    modFULLNAME_a2 = replacePropCase(modFULLNAME_a2, replaceDict)


                    tarRows.insertRow((FEDIRP, modFENAME2, FETYPE, '', CFCC, FRADDL, TOADDL, FRADDR, TOADDR, CFCC1, CFCC2, \
                                       modFULLNAME_a2, 0, 1, S_FIPS, AGRC_MDATE, ADDRESS_SY, shp))


            if srcRow[12] not in errorList:
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


roads()

