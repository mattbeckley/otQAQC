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


#Config file for Checking Original Rasters for Metadata
#----------------------------------------------------------------------
#module to initialize the config file to all null values?
config1 = ot.initializeNullConfig()

config1['CheckRasMeta'] = 1
config1['log_dir'] = log_dir
config1['ingestLog'] = os.path.join(log_dir,shortname+'_TEST_QAQCLog.txt')
config1['getFilesDir'] =  '/volumes/OT6TB/CA17_Dietrich/2017_ESRI_50cm'
config1['getFilesWild'] = '.*\.flt$'
config1['recursive'] = 1

#Run module to convert rasters to tiffs
ot.RunQAQC(config1)
#----------------------------------------------------------------------


#Config file for reprojecting and converting to tiffs.
#----------------------------------------------------------------------
##module to initialize the config file to all null values
config2 = ot.initializeNullConfig()

config2['log_dir'] = log_dir
config2['ingestLog'] = os.path.join(log_dir,shortname+'_TEST_QAQCLog.txt')
config2['getFilesDir'] =  '/volumes/OT6TB/CA17_Dietrich/2017_ESRI_50cm'
config2['getFilesWild'] = '.*\.flt$'
config2['recursive'] = 1
config2['Warp2Tiff'] = 1
config2['ras_xBlock'] = 256
config2['ras_yBlock'] = 256
config2['warp_t_srs'] = '6339'

#Run module to reproject rasters...
ot.RunQAQC(config2)
#----------------------------------------------------------------------


#Make sure the proper CRS info is in the header.
#----------------------------------------------------------------------
#module to initialize the config file to all null values?
config3 = ot.initializeNullConfig()
config3['SetRasterCRS'] = 1
config3['log_dir'] = log_dir
config3['ingestLog'] = os.path.join(log_dir,shortname+'_TEST_QAQCLog.txt')
config3['getFilesDir'] =  '/volumes/OT6TB/CA17_Dietrich/2017_ESRI_50cm'
config3['getFilesWild'] = '.*\.tif$'
config3['recursive'] = 1
config3['a_srs']='6339+5703'

#Run module to re-check the raster metadata
ot.RunQAQC(config3)
#----------------------------------------------------------------------

    



