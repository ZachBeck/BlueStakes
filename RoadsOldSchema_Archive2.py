#---KG Version--------------------------------------------------------------------------------------------------------------------------------------------------
def roads():

    print 'Starting Roads  ' + str(datetime.datetime.now())

    env.workspace = sgid10
    arcpy.env.overwriteOutput = True

    roadsSGID = sgid10_GEO + '\\RoadsODM'
    roadsBS = stageDB + '\\TGR_StWide_lkA'
    roadSegsQuestar = stageDB + '\\QUESTAR_GEOGRAPHIC\RoadSegs_Questar'


    #----Move Roads to SGID10_GEOGRAPHIC staging area
    arcpy.CopyFeatures_management('SGID10.TRANSPORTATION.RoadsODM', roadsSGID)

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

        errorList = [None, '', ' ', '<NULL>', '<NULL> ST']

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
        if srcRow[2] not in errorList and srcRow[2][-3:] == 'FWY':
            return '1'
        if srcRow[2] not in errorList and srcRow[2][:3] == 'HWY':
            return'1'
        if srcRow[2] not in errorList and srcRow[2][:2] == 'US':
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