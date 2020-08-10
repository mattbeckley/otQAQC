#!/usr/bin/env python
from __future__ import print_function

import sys,os,pdb
import ot_utils as ot

"""Name: 
   Description: config file to run QA/QC of datasets
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

config1['log_dir']        = log_dir
config1['ingestLog']      = os.path.join(log_dir,shortname+'_LAS2LAZ_QAQCLog.txt')
config1['LAS2LAZ']        = 1
config1['LAS2LAZ_method'] = 'pdal'
config1['getFilesWild']   = '.*\.las$'
config1['getFilesDir']    = '/Volumes/OT6TB/Shortname/LAS'
config1['ftype']          = 'f'
config1['recursive']      = 0
config1['LAZDir_out']     = '/volumes/OT6TB/Shortname/forbetaupload/LAZ'
config1['pipeline']       = os.path.join(scripts_dir,'pipeline.json')

#Run Module to Convert LAS2LAS...
#ot.RunQAQC(config1)
#----------------------------------------------------------------------

#Config file for initial check of LAS files....
#----------------------------------------------------------------------
#module to initialize the config file to all null values
config2 = ot.initializeNullConfig()

config2['log_dir'] = log_dir
config2['ingestLog'] = os.path.join(log_dir,shortname+'_initialCheck_QAQCLog.txt')
config2['recursive'] = 0
config2['getFilesDir'] =  '/volumes/OT6TB/Shortname/LAS'
config2['getFilesWild'] = '.*\.las$'
config2['ftype'] = 'f'
config2['CreatePDALInfo'] = 1
config2['PDALInfoFile'] = shortname+'_PDALInfoLog_initial.txt'
config2['ReadPDALLog'] = 1
config2['CheckLAZCount'] = 1
config2['MissingHCRS'] = 1
config2['MissingVCRS'] = 1
config2['HCRS_Uniform'] = 1
config2['VCRS_Uniform'] = 1
config2['VersionCheck'] = 1
config2['PointTypeCheck'] = 1
config2['GlobalEncodingCheck'] = 1
config2['PointCountCheck'] = 1
config2['CreatePDALBoundary'] = 1
config2['bounds_PDAL'] = os.path.join(bounds_base,'PDAL.shp')
config2['BufferSize'] = 1
config2['epsg'] = 6339
config2['bounds_PDALmerge'] = os.path.join(bounds_base,'PDALMerged.shp')
config2['bounds_PDALmergeArea'] = os.path.join(bounds_base,'PDALMergedwArea.shp')
config2['bounds_PDALKML'] = os.path.join(bounds_base,'PDALMergedwArea.kml')
config2['winePath'] = '/Applications/Wine\ Stable.app/Contents/Resources/wine/bin/wine /Applications/LASTools/bin'
config2['CreateLASBoundary'] = 1
config2['bounds_LT'] = os.path.join(bounds_base,'LTBounds.shp')
config2['randFrac'] = 0.25
config2['concavity'] = 75
config2['bounds_LTArea'] = os.path.join(bounds_base,'LTBoundswArea.shp')
config2['bounds_LTKML'] = os.path.join(bounds_base,'LTBoundswArea.kml')

#Run Module to do initial check of LAS files.
#ot.RunQAQC(config2)
#----------------------------------------------------------------------


#Config file for adding CRS to files...
#----------------------------------------------------------------------
#module to initialize the config file to all null values.
config3 = ot.initializeNullConfig()

config3['log_dir']      = log_dir
config3['ingestLog']    = os.path.join(log_dir,shortname+'_ADDCRS_QAQCLog.txt')
config3['AddCRS2Header']= 1
config3['getFilesWild'] = '.*\.las$'
config3['getFilesDir']  = '/volumes/OT6TB/Shortname/LAS'
config3['ftype']        = 'f'
config3['recursive']    = 0
config3['fsuffix']      = '_EPSG6339'
config3['overwrite']    = 0
config3['LAZDir_out']   = '/volumes/OT6TB/Shortname/forbetaupload/LAZ'
config3['pipeline']     = os.path.join(scripts_dir,'pipeline.json')
config3['LAS2LAZ_method'] = 'pdal'

#Run Module to add CRS to lidar files (LAS or LAZ)
#ot.RunQAQC(config3)
#----------------------------------------------------------------------



#Config file for Checking Original Rasters for Metadata
#----------------------------------------------------------------------
#module to initialize the config file to all null values?
config4 = ot.initializeNullConfig()

config4['CheckRasMeta'] = 1
config4['log_dir'] = log_dir
config4['ingestLog'] = os.path.join(log_dir,shortname+'_InitialRasterCheck_QAQCLog.txt')
config4['getFilesDir'] =  '/volumes/OT6TB/Shortname/rasters'
config4['getFilesWild'] = '.*\.flt$'
config4['ftype']        = 'f'
config4['recursive'] = 1

#Run module to convert rasters to tiffs
#ot.RunQAQC(config4)
#----------------------------------------------------------------------


#Config file for reprojecting and converting to tiffs.
#----------------------------------------------------------------------
##module to initialize the config file to all null values
config5 = ot.initializeNullConfig()

config5['log_dir'] = log_dir
config5['ingestLog'] = os.path.join(log_dir,shortname+'_WarpRasters_QAQCLog.txt')
config5['getFilesDir'] =  '/volumes/OT6TB/Shortname/rasters'
config5['getFilesWild'] = '.*\.flt$'
config5['ftype']     = 'f'
config5['recursive'] = 1
config5['Warp2Tiff'] = 1
config5['ras_xBlock'] = 256
config5['ras_yBlock'] = 256
config5['warp_t_srs'] = '6339'
config5['RasOutDir'] = '/path/to/output/rasters'

#Run module to reproject rasters...
#ot.RunQAQC(config5)
#----------------------------------------------------------------------

#Config file for ONLY converting to tiffs.
#----------------------------------------------------------------------
##module to initialize the config file to all null values
config6 = ot.initializeNullConfig()

config6['log_dir'] = log_dir
config6['ingestLog'] = os.path.join(log_dir,shortname+'_FLT2TIF_QAQCLog.txt')
config6['getFilesDir'] =  '/Volumes/OT6TB/Shortname/rasters'
config6['getFilesWild'] = '.*\.flt$'
config6['ftype']     = 'f'
config6['recursive'] = 1
config6['Translate2Tiff'] = 1
config6['ras_xBlock'] = 256
config6['ras_yBlock'] = 256
config6['RasOutDir'] = '/path/to/output/rasters'

#Run module to reproject rasters...
#ot.RunQAQC(config6)
#----------------------------------------------------------------------


#Make sure the proper CRS info is in the header.
#----------------------------------------------------------------------
#module to initialize the config file to all null values?
config7 = ot.initializeNullConfig()
config7['SetRasterCRS'] = 1
config7['log_dir'] = log_dir
config7['ingestLog'] = os.path.join(log_dir,shortname+'_RasterCRSCheck_QAQCLog.txt')
config7['getFilesDir'] =  '/volumes/OT6TB/Shortname/rasters'
config7['getFilesWild'] = '.*\.tif$'
config7['ftype']     = 'f'
config7['recursive'] = 1
config7['a_srs']='6339+5703'

#Run module to re-check the raster metadata
#ot.RunQAQC(config7)
#----------------------------------------------------------------------


#Create Tile Index of Lidar files
#----------------------------------------------------------------------
#module to initialize the config file to all null values?
config8 = ot.initializeNullConfig()
config8['CreateTileIndex'] = 1
config8['log_dir'] = log_dir
config8['ingestLog'] = os.path.join(log_dir,shortname+'_TileIndex_QAQCLog.txt')
config8['getFilesDir'] =  '/volumes/OT6TB/Shortname/LAZ'
config8['getFilesWild'] = '.*\.laz$'
config8['ftype']     = 'f'
config8['recursive'] = 0
config8['Tileftype'] = 'LAZ'
config8['OutputTileFile'] = os.path.join(bounds_base,'Shortname_TileIndex.shp')

#Run module to re-check the raster metadata
#ot.RunQAQC(config8)
#----------------------------------------------------------------------

#Create Tile Index of rasters
#----------------------------------------------------------------------
#module to initialize the config file to all null values?
config9 = ot.initializeNullConfig()
config9['CreateTileIndex'] = 1
config9['log_dir'] = log_dir
config9['ingestLog'] = os.path.join(log_dir,shortname+'_OrthoTileIndex_QAQCLog.txt')
config9['getFilesDir'] =  '/volumes/OT6TB/Shortname/DSM'
config9['getFilesWild'] = '.*\.tif$'
config9['ftype']     = 'f'
config9['recursive'] = 0
config9['OutputTileFile'] = os.path.join(bounds_base,'Shortname_DSMTileIndex.shp')
config9['Tileftype'] = 'RASTER'

#Run module to re-check the raster metadata
#ot.RunQAQC(config9)
#----------------------------------------------------------------------

    



