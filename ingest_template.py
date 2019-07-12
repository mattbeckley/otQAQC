#!/usr/bin/env python
from __future__ import print_function

import sys,os,ipdb
import ot_utils as ot

"""Name: 
   Description: config file to run the QA/QC for data ingest of WA18_Wall 
   Notes:
"""

#inputs:
#----------------------------------------------------------------------
#Best to name working directory as an OT shortname.  Assumes you are
#running this from the scripts directory..
ingestBase   = os.path.dirname(os.getcwd())
shortname    = os.path.basename(ingestBase)
bounds_base  = os.path.join(ingestBase,'bounds')
log_dir      = os.path.join(ingestBase,'logs')
scripts_dir  = os.path.join(ingestBase,'scripts')

#module to initialize the config file to all null values?
config1 = ot.initializeNullConfig()

#Config file for Converting LAS2LAS
config1['log_dir']      = log_dir
config1['ingestLog']    = os.path.join(log_dir,shortname+'_RecursiveTest_LAS2LAZ_ingestLog.txt')
config1['LAS2LAZ']      = 1
config1['getFilesWild'] = '.*\.las$'
config1['getFilesDir']  = '/volumes/OT6TB/WA18_Wall/test'
config1['recursive']    = 1
config1['laz_dir']      = ''
config1['pipeline']     = os.path.join(scripts_dir,'pipeline.json')


#module to initialize the config file to all null values?
config2 = ot.initializeNullConfig()

#Config file for Ingest LAZ, Create Boundaries
config2['log_dir'] = log_dir
config2['ingestLog'] = os.path.join(log_dir,shortname+'_RecursiveTest_IngestLAZ_ingestLog.txt')
config2['recursive'] = 1
config2['getFilesDir'] =  '/volumes/OT6TB/WA18_Wall/test'
config2['getFilesWild'] = '.*\.laz$'
config2['CreatePDALInfo'] = 1
config2['PDALInfoFile'] = shortname+'_RecursiveTest_PDALInfoLog.txt'
config2['ReadPDALLog'] = 1
config2['CheckLAZCount'] = 1
config2['MissingHCRS'] = 1
config2['MissingVCRS'] = 1
config2['HCRS_Uniform'] = 1
config2['VCRS_Uniform'] = 1
config2['VersionCheck'] = 1
config2['PointTypeCheck'] = 1
config2['GlobalEncodingCheck'] = 1
config2['CreatePDALBoundary'] = 1
config2['bounds_PDAL'] = os.path.join(bounds_base,'PDALB1_test.shp')
config2['BufferSize'] = 1
config2['epsg'] = 6339
config2['bounds_PDALmerge'] = os.path.join(bounds_base,'PDALMergedB1_test.shp')
config2['bounds_PDALmergeArea'] = os.path.join(bounds_base,'PDALMergedwAreaB1_test.shp')
config2['bounds_PDALKML'] = os.path.join(bounds_base,'PDALMergedwAreaB1_test.kml')
config2['winePath'] = '/Applications/LASTools/bin'
config2['CreateLASBoundary'] = 1
config2['bounds_LT'] = os.path.join(bounds_base,'LTB1_test.shp')
config2['randFrac'] = 0.25
config2['concavity'] = 100
config2['bounds_LTArea'] = os.path.join(bounds_base,'LTwAreaB1_test.shp')
config2['bounds_LTKML'] = os.path.join(bounds_base,'LTwAreaB1_test.kml')


#module to initialize the config file to all null values?
config3 = ot.initializeNullConfig()

#Config file for converting rasters to tiffs
config3['log_dir'] = log_dir
config3['ingestLog'] = os.path.join(log_dir,shortname+'_RecursiveTest_TranslateRasters_ingestLog.txt')
config3['recursive'] = 1
config3['getFilesDir'] =  '/volumes/OT6TB/WA18_Wall/rasters'
config3['getFilesWild'] = '.*\.flt$'
config3['Translate2Tiff'] = 1
config3['RasOutDir'] = '/volumes/OT6TB/WA18_Wall/rasters/test'
config3['Warp2Tiff'] = 0
config3['ras_xBlock'] = 128
config3['ras_yBlock'] = 128
config3['warp_t_srs'] = 6339
#----------------------------------------------------------------------

#Convert LAS2LAS
#ot.RunIngest(config1)

#Ingest LAZ, Create Boundaries
ot.RunIngest(config2)

#convert rasters to tiffs
ot.RunIngest(config3)
    



