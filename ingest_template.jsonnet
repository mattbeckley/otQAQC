#Location of output log
local log_dir = '/Users/matt/ot/DataIngest/NZ16_SAuckland/logs/';
local ingestlog = log_dir+'LAS2LAZ_QAQCLog.txt';

#config for the list of lidar files to work on
{'config':{
'getLidarFiles':{
  #Path of files to work on
  getFilesDir:'/Volumes/New Volume/ToOT_HD35/2018_13_265_Feehan/_Deliverables/PCTiles',
  #Regular expression of files to grab
  getFilesWild: '.*\.las$',
  #Files are either Files ('f') or Directories ('d').  Usually only ESRI
  #Grid files will be 'd' 
  ftype: 'f',
  #set to 1 if you want to recursively search subdirectories
  recursive: 0
},

'AddCRS2Header':{
  #Directory to output an error messages.  Generally the log dir.
  log_dir: log_dir,
  #Location of PDAL pipeline that will add the metadata
  pipeline: '/Users/matt/ot/DataIngest/NZ16_SAuckland/scripts/pipeline.json',
  #directory to output files to if not overwriting
  LAZDir_out:'/volumes/OT6TB/NZ16_SAuckland/LAZ',
  #suffix if not overwriting and want to adjust name
  fsuffix: '_wCRS',
  #set this to 1 if you want to add headers in place and overwrite files
  overwrite: 0
}
}}


#
#config1['log_dir']        = log_dir
#config1['ingestLog']      = os.path.join(log_dir,shortname+'_
#config1['LAS2LAZ']        = 1
#config1['LAS2LAZ_method'] = 'pdal'
#config1[
#config1[
#config1['ftype']          = 'f'
#config1['
#config1['LAZDir_out']     = 
#config1['pipeline']       = os.path.join(scripts_dir,'pipeline.json')
#
##Run Module to Convert LAS2LAS...
##ot.RunQAQC(config1)
##----------------------------------------------------------------------
#
##Config file for initial check of LAS files....
##----------------------------------------------------------------------
##module to initialize the config file to all null values
#config2 = ot.initializeNullConfig()
#
#config2['log_dir'] = log_dir
#config2['ingestLog'] = os.path.join(log_dir,shortname+'_initialCheck_QAQCLog.txt')
#config2['recursive'] = 0
#config2['getFilesDir'] =  '/volumes/OT6TB/CA17_Dietrich/2017_LAS_Tiles'
#config2['getFilesWild'] = '.*\.las$'
#config2['ftype'] = 'f'
#config2['CreatePDALInfo'] = 1
#config2['PDALInfoFile'] = shortname+'_PDALInfoLog_initial.txt'
#config2['ReadPDALLog'] = 1
#config2['CheckLAZCount'] = 1
#config2['MissingHCRS'] = 1
#config2['MissingVCRS'] = 1
#config2['HCRS_Uniform'] = 1
#config2['VCRS_Uniform'] = 1
#config2['VersionCheck'] = 1
#config2['PointTypeCheck'] = 1
#config2['GlobalEncodingCheck'] = 1
#config2['PointCountCheck'] = 1
#config2['CreatePDALBoundary'] = 1
#config2['bounds_PDAL'] = os.path.join(bounds_base,'PDAL.shp')
#config2['BufferSize'] = 1
#config2['epsg'] = 6339
#config2['bounds_PDALmerge'] = os.path.join(bounds_base,'PDALMerged.shp')
#config2['bounds_PDALmergeArea'] = os.path.join(bounds_base,'PDALMergedwArea.shp')
#config2['bounds_PDALKML'] = os.path.join(bounds_base,'PDALMergedwArea.kml')
#config2['winePath'] = '/Applications/LASTools/bin'
#config2['CreateLASBoundary'] = 1
#config2['bounds_LT'] = os.path.join(bounds_base,'LTBounds.shp')
#config2['randFrac'] = 0.25
#config2['concavity'] = 100
#config2['bounds_LTArea'] = os.path.join(bounds_base,'LTBoundswArea.shp')
#config2['bounds_LTKML'] = os.path.join(bounds_base,'LTBoundswArea.kml')
#
##Run Module to do initial check of LAS files.
##ot.RunQAQC(config2)
##----------------------------------------------------------------------
#
#
##Config file for adding CRS to files...
##----------------------------------------------------------------------
##module to initialize the config file to all null values.
#config3 = ot.initializeNullConfig()
#
#config3['log_dir']      = log_dir
#config3['ingestLog']    = os.path.join(log_dir,shortname+'_ADDCRS_QAQCLog.txt')
#config3['AddCRS2Header']= 1
#config3['getFilesWild'] = '.*\.las$'
#config3['getFilesDir']  = '/volumes/OT6TB/CA17_Dietrich/2017_LAS_Tiles'
#config3['ftype']        = 'f'
#config3['recursive']    = 0
#config3['fsuffix']      = '_EPSG6339'
#config3['overwrite']    = 0
#config3['LAZDir_out']   = '/volumes/OT6TB/CA17_Dietrich/LAZ'
#config3['pipeline']     = os.path.join(scripts_dir,'pipeline.json')
#config3['LAS2LAZ_method'] = 'pdal'
#
##Run Module to add CRS to lidar files (LAS or LAZ)
##ot.RunQAQC(config3)
##----------------------------------------------------------------------
#
#
#
##Config file for QA/QC of LAZ and Create Boundaries
##----------------------------------------------------------------------
##module to initialize the config file to all null values
#config4 = ot.initializeNullConfig()
#
#config4['log_dir'] = log_dir
#config4['ingestLog'] = os.path.join(log_dir,shortname+'_QAQCLog.txt')
#config4['recursive'] = 0
#config4['getFilesDir'] =  '/volumes/OT6TB/CA17_Dietrich/LAZ'
#config4['getFilesWild'] = '.*\.laz$'
#config4['ftype']        = 'f'
#config4['CreatePDALInfo'] = 1
#config4['PDALInfoFile'] = shortname+'_PDALInfoLog.txt'
#config4['ReadPDALLog'] = 1
#config4['CheckLAZCount'] = 1
#config4['MissingHCRS'] = 1
#config4['MissingVCRS'] = 1
#config4['HCRS_Uniform'] = 1
#config4['VCRS_Uniform'] = 1
#config4['VersionCheck'] = 1
#config4['PointTypeCheck'] = 1
#config4['GlobalEncodingCheck'] = 1
#config4['CreatePDALBoundary'] = 1
#config4['bounds_PDAL'] = os.path.join(bounds_base,'PDAL.shp')
#config4['BufferSize'] = 1
#config4['epsg'] = 6339
#config4['bounds_PDALmerge'] = os.path.join(bounds_base,'PDALMerged.shp')
#config4['bounds_PDALmergeArea'] = os.path.join(bounds_base,'PDALMergedwArea.shp')
#config4['bounds_PDALKML'] = os.path.join(bounds_base,'PDALMergedwArea.kml')
#config4['winePath'] = '/Applications/LASTools/bin'
#config4['CreateLASBoundary'] = 1
#config4['bounds_LT'] = os.path.join(bounds_base,'LTBounds.shp')
#config4['randFrac'] = 0.25
#config4['concavity'] = 100
#config4['bounds_LTArea'] = os.path.join(bounds_base,'LTBoundswArea.shp')
#config4['bounds_LTKML'] = os.path.join(bounds_base,'LTBoundswArea.kml')
#
##Run Module to Ingest LAZ, Create Boundaries
##ot.RunQAQC(config4)
##----------------------------------------------------------------------
#
#
#
##Config file for Checking Original Rasters for Metadata
##----------------------------------------------------------------------
##module to initialize the config file to all null values?
#config5 = ot.initializeNullConfig()
#
#config5['CheckRasMeta'] = 1
#config5['log_dir'] = log_dir
#config5['ingestLog'] = os.path.join(log_dir,shortname+'_TEST_QAQCLog.txt')
#config5['getFilesDir'] =  '/volumes/OT6TB/CA17_Dietrich/2017_ESRI_50cm'
#config5['getFilesWild'] = '.*\.flt$'
#config5['ftype']        = 'f'
#config5['recursive'] = 1
#
##Run module to convert rasters to tiffs
##ot.RunQAQC(config5)
##----------------------------------------------------------------------
#
#
##Config file for reprojecting and converting to tiffs.
##----------------------------------------------------------------------
###module to initialize the config file to all null values
#config6 = ot.initializeNullConfig()
#
#config6['log_dir'] = log_dir
#config6['ingestLog'] = os.path.join(log_dir,shortname+'_TEST_QAQCLog.txt')
#config6['getFilesDir'] =  '/volumes/OT6TB/CA17_Dietrich/2017_ESRI_50cm'
#config6['getFilesWild'] = '.*\.flt$'
#config6['ftype']     = 'f'
#config6['recursive'] = 1
#config6['Warp2Tiff'] = 1
#config6['ras_xBlock'] = 256
#config6['ras_yBlock'] = 256
#config6['warp_t_srs'] = '6339'
#config6['RasOutDir'] = '/path/to/output/rasters'
#
##Run module to reproject rasters...
##ot.RunQAQC(config6)
##----------------------------------------------------------------------
#
##Config file for ONLY converting to tiffs.
##----------------------------------------------------------------------
###module to initialize the config file to all null values
#config6 = ot.initializeNullConfig()
#
#config6['log_dir'] = log_dir
#config6['ingestLog'] = os.path.join(log_dir,shortname+'_FLT2TIF_QAQCLog.txt')
#config6['getFilesDir'] =  '/Volumes/New Volume/ToOT_HD35/2018_13_265_Feehan/_Deliverables/Rasters'
#config6['getFilesWild'] = '.*\.flt$'
#config6['ftype']     = 'f'
#config6['recursive'] = 1
#config6['Translate2Tiff'] = 1
#config6['ras_xBlock'] = 256
#config6['ras_yBlock'] = 256
#config6['RasOutDir'] = '/volumes/OT6TB/CA18_Feehan/Rasters'
#
##Run module to reproject rasters...
##ot.RunQAQC(config6)
##----------------------------------------------------------------------
#
#
##Make sure the proper CRS info is in the header.
##----------------------------------------------------------------------
##module to initialize the config file to all null values?
#config7 = ot.initializeNullConfig()
#config7['SetRasterCRS'] = 1
#config7['log_dir'] = log_dir
#config7['ingestLog'] = os.path.join(log_dir,shortname+'_TEST_QAQCLog.txt')
#config7['getFilesDir'] =  '/volumes/OT6TB/CA17_Dietrich/2017_ESRI_50cm'
#config7['getFilesWild'] = '.*\.tif$'
#config7['ftype']     = 'f'
#config7['recursive'] = 1
#config7['a_srs']='6339+5703'
#
##Run module to re-check the raster metadata
##ot.RunQAQC(config7)
##----------------------------------------------------------------------

    



