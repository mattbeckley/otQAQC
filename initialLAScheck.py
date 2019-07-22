#!/usr/bin/env python
from __future__ import print_function

import sys,os,ipdb
import ot_utils as ot

"""Name: 
   Description: config file to run the QA/QC of 
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
#----------------------------------------------------------------------


#Config file for initial check of LAS files....
#----------------------------------------------------------------------
#module to initialize the config file to all null values
config1 = ot.initializeNullConfig()

config1['log_dir'] = log_dir
config1['ingestLog'] = os.path.join(log_dir,shortname+'_initialCheck_QAQCLog.txt')
config1['recursive'] = 0
config1['getFilesDir'] =  '/volumes/OT6TB/CA17_Dietrich/2017_LAS_Tiles'
config1['getFilesWild'] = '.*\.las$'
config1['CreatePDALInfo'] = 1
config1['PDALInfoFile'] = shortname+'_PDALInfoLog_initial.txt'
config1['ReadPDALLog'] = 1
config1['CheckLAZCount'] = 1
config1['MissingHCRS'] = 1
config1['MissingVCRS'] = 1
config1['HCRS_Uniform'] = 1
config1['VCRS_Uniform'] = 1
config1['VersionCheck'] = 1
config1['PointTypeCheck'] = 1
config1['GlobalEncodingCheck'] = 1
config1['CreatePDALBoundary'] = 0
config1['bounds_PDAL'] = os.path.join(bounds_base,'PDAL_Jul12.shp')
config1['BufferSize'] = 1
config1['epsg'] = 6339
config1['bounds_PDALmerge'] = os.path.join(bounds_base,'PDALMerged_Jul12.shp')
config1['bounds_PDALmergeArea'] = os.path.join(bounds_base,'PDALMergedwArea_Jul12.shp')
config1['bounds_PDALKML'] = os.path.join(bounds_base,'PDALMergedwArea_Jul12.kml')
config1['winePath'] = '/Applications/LASTools/bin'
config1['CreateLASBoundary'] = 0
config1['bounds_LT'] = os.path.join(bounds_base,'LTBounds_Jul12.shp')
config1['randFrac'] = 0.25
config1['concavity'] = 100
config1['bounds_LTArea'] = os.path.join(bounds_base,'LTBoundswArea_Jul12.shp')
config1['bounds_LTKML'] = os.path.join(bounds_base,'LTBoundswArea_Jul12.kml')

#Run Module to do initial check of LAS files.
#ot.RunQAQC(config1)
#----------------------------------------------------------------------


#Config file for adding CRS to files...
#----------------------------------------------------------------------
#module to initialize the config file to all null values.
config2 = ot.initializeNullConfig()

config2['log_dir']      = log_dir
config2['ingestLog']    = os.path.join(log_dir,shortname+'_ADDCRS_QAQCLog.txt')
config2['AddCRS2Header']= 1
config2['getFilesWild'] = '.*\.las$'
config2['getFilesDir']  = '/volumes/OT6TB/CA17_Dietrich/2017_LAS_Tiles'
config2['recursive']    = 0
config2['fsuffix']      = '_EPSG6339'
config2['overwrite']    = 0
config2['LAZDir_out']   = '/volumes/OT6TB/CA17_Dietrich/LAZ'
config2['pipeline']     = os.path.join(scripts_dir,'pipeline.json')

#Run Module to add CRS to lidar files (LAS or LAZ)
#ot.RunQAQC(config2)
#----------------------------------------------------------------------


#Config file for Converting LAS files to LAZ
#----------------------------------------------------------------------
#module to initialize the config file to all null values.
config3 = ot.initializeNullConfig()

config3['log_dir']      = log_dir
config3['ingestLog']    = os.path.join(log_dir,shortname+'_LAS2LAZ_QAQCLog.txt')
config3['LAS2LAZ']      = 1
config3['getFilesWild'] = '.*\.las$'
config3['getFilesDir']  = '/Volumes/New Volume/toOT_HD34/2018_09_Wall_Seed_12August2019/_Deliverables/PointClouds'
config3['recursive']    = 0
config3['LAZDir_out']   = '/volumes/OT6TB/WALL_TEST/LAZ'
config3['pipeline']     = os.path.join(scripts_dir,'pipeline.json')

#Run Module to Convert LAS2LAS...
#ot.RunQAQC(config3)
#----------------------------------------------------------------------


#Config file for QA/QC of LAZ and Create Boundaries
#----------------------------------------------------------------------
#module to initialize the config file to all null values
config4 = ot.initializeNullConfig()

config4['log_dir'] = log_dir
config4['ingestLog'] = os.path.join(log_dir,shortname+'_QAQCLog.txt')
config4['recursive'] = 0
config4['getFilesDir'] =  '/volumes/OT6TB/CA17_Dietrich/LAZ'
config4['getFilesWild'] = '.*\.laz$'
config4['CreatePDALInfo'] = 1
config4['PDALInfoFile'] = shortname+'_PDALInfoLog.txt'
config4['ReadPDALLog'] = 1
config4['CheckLAZCount'] = 1
config4['MissingHCRS'] = 1
config4['MissingVCRS'] = 1
config4['HCRS_Uniform'] = 1
config4['VCRS_Uniform'] = 1
config4['VersionCheck'] = 1
config4['PointTypeCheck'] = 1
config4['GlobalEncodingCheck'] = 1
config4['CreatePDALBoundary'] = 1
config4['bounds_PDAL'] = os.path.join(bounds_base,'PDAL.shp')
config4['BufferSize'] = 1
config4['epsg'] = 6339
config4['bounds_PDALmerge'] = os.path.join(bounds_base,'PDALMerged.shp')
config4['bounds_PDALmergeArea'] = os.path.join(bounds_base,'PDALMergedwArea.shp')
config4['bounds_PDALKML'] = os.path.join(bounds_base,'PDALMergedwArea.kml')
config4['winePath'] = '/Applications/LASTools/bin'
config4['CreateLASBoundary'] = 1
config4['bounds_LT'] = os.path.join(bounds_base,'LTBounds.shp')
config4['randFrac'] = 0.25
config4['concavity'] = 100
config4['bounds_LTArea'] = os.path.join(bounds_base,'LTBoundswArea.shp')
config4['bounds_LTKML'] = os.path.join(bounds_base,'LTBoundswArea.kml')

#Run Module to Ingest LAZ, Create Boundaries
#ot.RunQAQC(config4)
#----------------------------------------------------------------------


    



