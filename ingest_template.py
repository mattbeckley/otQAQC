#!/usr/bin/env python
from __future__ import print_function

import sys,os,ipdb
import ot_utils as ot

"""Name: 
   Description: config file to run the QA/QC of WA18_Wall 
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


#Config file for Converting LAS files to LAZ
#----------------------------------------------------------------------
#module to initialize the config file to all null values.
config1 = ot.initializeNullConfig()

config1['log_dir']      = log_dir
config1['ingestLog']    = os.path.join(log_dir,shortname+'_LAS2LAZ_QAQCLog.txt')
config1['LAS2LAZ']      = 1
config1['getFilesWild'] = '.*\.las$'
config1['getFilesDir']  = '/Volumes/New Volume/toOT_HD34/2018_09_Wall_Seed_12August2019/_Deliverables/PointClouds'
config1['recursive']    = 0
config1['LAZDir_out']   = '/volumes/OT6TB/WALL_TEST/LAZ'
config1['pipeline']     = os.path.join(scripts_dir,'pipeline.json')

#Run Module to Convert LAS2LAS...
ot.RunQAQC(config1)
#----------------------------------------------------------------------


#Config file for QA/QC of LAZ and Create Boundaries
#----------------------------------------------------------------------
#module to initialize the config file to all null values
config2 = ot.initializeNullConfig()

config2['log_dir'] = log_dir
config2['ingestLog'] = os.path.join(log_dir,shortname+'_CheckLAZ_QAQCLog.txt')
config2['recursive'] = 0
config2['getFilesDir'] =  '/volumes/OT6TB/WALL_TEST/LAZ'
config2['getFilesWild'] = '.*\.laz$'
config2['CreatePDALInfo'] = 1
config2['PDALInfoFile'] = shortname+'_PDALInfoLog_Jul12.txt'
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
config2['bounds_PDAL'] = os.path.join(bounds_base,'PDAL_Jul12.shp')
config2['BufferSize'] = 1
config2['epsg'] = 6339
config2['bounds_PDALmerge'] = os.path.join(bounds_base,'PDALMerged_Jul12.shp')
config2['bounds_PDALmergeArea'] = os.path.join(bounds_base,'PDALMergedwArea_Jul12.shp')
config2['bounds_PDALKML'] = os.path.join(bounds_base,'PDALMergedwArea_Jul12.kml')
config2['winePath'] = '/Applications/LASTools/bin'
config2['CreateLASBoundary'] = 1
config2['bounds_LT'] = os.path.join(bounds_base,'LTBounds_Jul12.shp')
config2['randFrac'] = 0.25
config2['concavity'] = 100
config2['bounds_LTArea'] = os.path.join(bounds_base,'LTBoundswArea_Jul12.shp')
config2['bounds_LTKML'] = os.path.join(bounds_base,'LTBoundswArea_Jul12.kml')

#Run Module to Ingest LAZ, Create Boundaries
ot.RunQAQC(config2)
#----------------------------------------------------------------------

#Config file for Checking Original Rasters for Metadata
#----------------------------------------------------------------------
#module to initialize the config file to all null values?
config3 = ot.initializeNullConfig()

config3['CheckRasMeta'] = 1
config3['log_dir'] = log_dir
config3['ingestLog'] = os.path.join(log_dir,shortname+'_CheckRasterMeta_QAQCLog.txt')
config3['getFilesDir'] =  '/volumes/OT6TB/WALL_TEST/rasters'
config3['getFilesWild'] = '.*\.flt$'
config3['recursive'] = 1

#Run module to convert rasters to tiffs
ot.RunQAQC(config3)
#----------------------------------------------------------------------


#Config file for converting rasters to tiffs
#----------------------------------------------------------------------
#module to initialize the config file to all null values?
config4 = ot.initializeNullConfig()


config4['log_dir'] = log_dir
config4['ingestLog'] = os.path.join(log_dir,shortname+'TranslateRasters_QAQCLog.txt')
config4['recursive'] = 1
config4['getFilesDir'] =  '/volumes/OT6TB/WALL_TEST/rasters'
config4['getFilesWild'] = '.*\.flt$'
config4['Translate2Tiff'] = 1
config4['RasOutDir'] = ''

#Run module to convert rasters to tiffs
ot.RunQAQC(config4)
#----------------------------------------------------------------------


#Config file for reprojecting tiffs
#----------------------------------------------------------------------
#module to initialize the config file to all null values
config5 = ot.initializeNullConfig()

config5['log_dir'] = log_dir
config5['ingestLog'] = os.path.join(log_dir,shortname+'ReProjectRasters_QAQCLog.txt')
config5['getFilesDir'] =  '/volumes/OT6TB/WALL_TEST/rasters'
config5['getFilesWild'] = '.*\.tif$'
config4['recursive'] = 1
config5['Warp2Tiff'] = 1
config5['ras_xBlock'] = 256
config5['ras_yBlock'] = 256
config5['warp_t_srs'] = 6339
ot.RunQAQC(config5)
#----------------------------------------------------------------------



#----------------------------------------------------------------------
#module to initialize the config file to all null values?
config6 = ot.initializeNullConfig()

config6['CheckRasMeta'] = 1
config6['log_dir'] = log_dir
config6['ingestLog'] = os.path.join(log_dir,shortname+'CheckRasterMetaFinal_QAQCLog.txt')
config6['getFilesDir'] =  '/volumes/OT6TB/WALL_TEST/rasters'
config6['getFilesWild'] = '.*\.tif$'

#Run module to convert rasters to tiffs
ot.RunQAQC(config6)
#----------------------------------------------------------------------

    



