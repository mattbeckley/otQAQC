#!/usr/bin/env python
from __future__ import print_function

import sys,os,ipdb,logging
sys.path.append('/Users/matt/ot/dev')

from datetime import datetime
import ot_utils as ot
import ElapsedTime as et   

"""Name: 
   Description: QA/QC for data ingest of 
   Notes:
"""

#inputs:
#----------------------------------------------------------------------
shortname    = 'NZ18_Marlbo'
ingestBase   = '/Users/matt/ot/DataIngest/'+shortname
dataBase     = '/volumes/OT6TB/NZ18_Marlbo/'
las_dir      = '/volumes/OT6TB/NZ18_Marlbo/LAZ'
output_dir   = '/Users/matt/ot/DataIngest/'+shortname+'/logs'
logfile      = ingestBase+'/logs/'+shortname+'_PDALInfoLog.txt'
ingestLog    = ingestBase+'/logs/'+shortname+'_ingestLog.txt'
bounds_base  = '/Users/matt/ot/DataIngest/'+shortname+'/bounds'
bounds_PDAL          = os.path.join(bounds_base,'Boundary_PDAL.shp')
bounds_PDALmerge     = os.path.join(bounds_base,'Boundary_PDALMerged.shp')
bounds_PDALmergeArea = os.path.join(bounds_base,'Boundary_PDALMergedwArea.shp')
bounds_PDALKML       = os.path.join(bounds_base,'Boundary_PDALMergedwArea.kml')
bounds_LT            = os.path.join(bounds_base,'Boundary_wLT.shp')
bounds_LTArea        = os.path.join(bounds_base,'Boundary_wLTwArea.shp')
bounds_LTKML         = os.path.join(bounds_base,'Boundary_wLTwArea.kml')
epsg                 = 2193
#----------------------------------------------------------------------


#------------------------------------------------------------
#always start a new log?  Check if one exists, and if so
#delete it.

if os.path.exists(ingestLog):
    os.remove(ingestLog)

#open log
log    = ot.setup_logger('Log1', ingestLog)

#output for standard output
stdout = ot.setup_logger('Log2', '', stdout=1) 

#Write header to Log
ot.LogHeader(log,las_dir)
#------------------------------------------------------------



#get list of files to ingest
files = ot.getFiles(las_dir, wild='.*\.laz$',recursive=0)

#create PDAL Info output from all files
#print('Creating PDAL info log...')
#ot.CreatePDALInfo(files,output_dir,logfile)


fileCount = ot.LAZCount(las_dir)
stdout.info('Checking if LAZ count matches file count in directory...')
log.info('------------------------------------------------------')    
log.info('Checking if LAZ count matches file count in directory...')
if fileCount["TotalLAZCount"] != fileCount["TotalFileCount"]:
    log.info('WARNING: LAZ count does not match Total File Count.')
    log.info('Directory contains following filetypes:')
    for f in fileCount['FileTypes']:
        log.info(str(f))
    log.info('\nCheck path:\n'+las_dir)
else:
    log.info('PASS: LAZ count matches Total File Count.')
log.info('------------------------------------------------------\n')    

#get the json data of PDAL info
json = ot.readJSONARRAY(output_dir,logfile)

#Check if CRS is missing...
#----------------------------------------------------------------------
CRS_check = ot.CountCRS(json)
htest = CRS_check.MissingHCRS.isin([1])
vtest = CRS_check.MissingVCRS.isin([1])

stdout.info('Checking for missing horizontal or vertical CRS...')
log.info('------------------------------------------------------')    
log.info('Checking for missing horizontal or vertical CRS...')
if any(htest):
    log.info("FAIL: Some of the files are missing Horizontal CRS info")
    ipdb.set_trace()
else:
    log.info("PASS:  All files have a horizontal CRS")
    
if any(vtest):
    log.info("FAIL: Some of the files are missing Vertical CRS info")
    ipdb.set_trace()
else:
    log.info("PASS:  All files have a vertical CRS")

log.info('------------------------------------------------------\n')    
#----------------------------------------------------------------------

#check if CRS is uniform...
#----------------------------------------------------------------------
stdout.info('Checking if horizontal CRS is uniform...')
log.info('------------------------------------------------------')    
log.info('Checking if horizontal CRS is uniform...')
HCRS_epsgs   = ot.getHCRS_EPSG(json)          
unique_epsgs = set(HCRS_epsgs.HCRS_EPSG)
if len(unique_epsgs) > 1:
    log.info('FAIL: More than 1 EPSG for the Horizontal CRS')
    log.info('There are '+str(len(unique_epsgs))+'different horizontal CRS epsg values')
    log.info('Dataset contains the following horizontal CRS epsg codes:')
    for val in unique_epsgs:
        log.info(str(val))

    ipdb.set_trace()
else:
    log.info("PASS: All files in same HCRS: "+str(unique_epsgs))

stdout.info('Checking if vertical CRS is uniform...')
log.info('Checking if vertical CRS is uniform...')
VCRS_epsgs    = ot.getVCRS_EPSG(json)          
unique_Vepsgs = set(VCRS_epsgs.VCRS_EPSG)
if len(unique_Vepsgs) > 1:
    log.info('FAIL: More than 1 EPSG for the Vertical CRS')
    log.info('There are '+str(len(unique_Vepsgs))+'different vertical CRS epsg values')
    log.info('Dataset contains the following vertical CRS epsg codes:')
    for val in unique_Vepsgs:
        log.info(str(val))
        
    ipdb.set_trace()
else:
    log.info("PASS: All files in same VCRS: "+str(unique_Vepsgs))

log.info('------------------------------------------------------\n')    
#----------------------------------------------------------------------
    
#Make sure the files are all in the same LAS version...
#----------------------------------------------------------------------    
Version_check = ot.checkLASVersion(json)
NumVersions = len(Version_check.Version.unique())
stdout.info('Checking the version of the las and if it is uniform...')
log.info('------------------------------------------------------')    
log.info('Checking the version of the las and if it is uniform...')
if NumVersions > 1:
    log.info("FAIL: Files are in more than one LAS version")
    ipdb.set_trace()
else:
    log.info("PASS: All files are in version: "+str(Version_check.Version.unique()))

log.info('------------------------------------------------------\n')    
#----------------------------------------------------------------------

#Check the point type of all files, and if they are uniform
#----------------------------------------------------------------------
stdout.info('Checking if Point Type is uniform...')
log.info('------------------------------------------------------')    
log.info('Checking if Point Type is uniform...')
pType        = ot.getPointType(json)          
unique_pType = set(pType.PointType)
if len(unique_pType) > 1:
    log.info('WARNING: More than 1 Point Types for the lidar files')
    log.info('There are '+str(len(unique_pType))+' different Point Type values')
    log.info('Dataset contains files with Point Types: ')
    for val in unique_pType:
        log.info(str(val))
else:
    log.info("PASS: All files have the same Point Type: "+str(unique_pType))

log.info('------------------------------------------------------\n')        
#----------------------------------------------------------------------    

#Check the global encoding of all files, and if they are uniform
#----------------------------------------------------------------------
stdout.info('Checking if Global Encoding is uniform...')
log.info('------------------------------------------------------')    
log.info('Checking if Global Encoding is uniform...')
GE        = ot.getGlobalEncoding(json)          
unique_GE = set(GE.GlobalEncoding)
if len(unique_GE) > 1:
    log.info('WARNING: More than 1 Global Encoding for the lidar files')
    log.info('There are '+str(len(unique_GE))+' different Global Encoding values')
    log.info('Dataset contains files with Global Encoding Values of: ')
    for val in unique_GE:
        log.info(str(val))
else:
    log.info("PASS: All files have the same Global Encoding Value: "+str(unique_GE))

log.info('------------------------------------------------------\n')        
#----------------------------------------------------------------------    


"""
#Create Boundary via PDAL
#----------------------------------------------------------------------
start_PDAL = datetime.now()
print("Create boundary with PDAL...")
ot.CreateBounds(las_dir,bounds_PDAL,epsg)
print("Dissolve boundary with PDAL...")
ot.DissolveBounds(bounds_PDAL, bounds_PDALmerge,buffer=2)
end_PDAL = datetime.now()
print("Get Area with PDAL...")
ot.getArea(bounds_PDALmerge,bounds_PDALmergeArea)
print("Convert PDAL-derived boundary to KML")
ot.shape2KML(bounds_PDALmergeArea,bounds_PDALKML)  
#----------------------------------------------------------------------


#----------------------------------------------------------------------    
print("Create boundary with LAS...")
start_LAS = datetime.now()
ot.LASBoundary(files,bounds_LT,rand_fract=0.2,concavity=100,wine_path='/Applications/LAStools/bin')
end_LAS = datetime.now()
print("Get Area for LAS boundary...")

ot.getArea(bounds_LT,bounds_LTArea)
print("Convert LAS-derived boundary to KML")
ot.shape2KML(bounds_LTArea,bounds_LTKML)

print("LAS Boundary Creation took:\n")
et.ElapsedTime(start_LAS,end_LAS)
#----------------------------------------------------------------------
"""


log.info("Program finished successfully!")

# remember to close the handlers. This will close the log.
for handler in log.handlers.copy():
    log.removeFilter(handler)
    log.removeHandler(handler)
    handler.flush()
    handler.close()

for handler in stdout.handlers.copy():
    stdout.removeFilter(handler)
    stdout.removeHandler(handler)
    handler.flush()
    handler.close()
    



