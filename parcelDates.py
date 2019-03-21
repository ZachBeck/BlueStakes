import datetime, time
from datetime import date, datetime, timedelta
import arcpy

qParcels = r'C:\ZBECK\BlueStakes\Questar\QuestarUpdates.gdb\Property'
testParcels = r'C:\ZBECK\BlueStakes\stagingBS.gdb\QUESTAR_GEOGRAPHIC\testParcels'

today = datetime.datetime.now()
oidList = []
flds = ['OBJECTID', 'DATECREATED', 'DATEMODIFIED', 'SHAPE@', 'SUBTYPECD']
iFlds = ['DATECREATED', 'DATEMODIFIED', 'SUBTYPECD', 'SHAPE@']

iCursor = arcpy.da.InsertCursor(testParcels, iFlds)

with arcpy.da.SearchCursor(qParcels, flds) as sCursor:
   for row in sCursor:
       oid = row[0]
       dateC = row[1]
       dateM = row[2]
       propType = row[4]
       if dateC != None:
           dateC_delta = today - dateC
           if int(str(dateC_delta).split()[0]) < 366:
               dateC_subYear = int(str(dateC_delta).split()[0])
               iCursor.insertRow((dateC, None, propType, row[3]))
       if dateM != None:
           dateM_delta = today - dateM
           if int(str(dateM_delta).split()[0]) < 366:
               if oid not in oidList:
                   oidList.append(oid)
                   dateM_subYear = int(str(dateM_delta).split()[0])
                   iCursor.insertRow((None, dateM, propType, row[3]))

