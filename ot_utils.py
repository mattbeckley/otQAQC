#!/usr/bin/env python
from __future__ import print_function
import json,glob,os,sys,ipdb,subprocess
import ogr,logging,datetime,re
import pandas as pd
from datetime import datetime
from osgeo import gdal,osr
from subprocess import Popen, PIPE
from progress.bar import Bar
from shutil import copyfile,move

# this allows GDAL to throw Python Exceptions
gdal.UseExceptions()



"""Name: 
   Description:  This is the prototype of code to do all the checking
   for a CRS ingest.

   Date Created: 02/11/2019

   Input(s):
   Output(s):
   Keyword(s):
   Update(s):
   Notes:
   #Test to see if git push is working....

"""

__author__      = "Matthew Beckley"

#----------------------------------------------------------------------
def initializeNullConfig():
    #Config file for Converting LAS2LAS
    config = {'log_dir':'',
              'ingestLog':'',
              'AddCRS2Header':0,
              'fsuffix':'',
              'overwrite':0,
              'ftype':'f',
              'LAS2LAZ':0,
              'getFilesWild':'',
              'getFilesDir': '',
              'recursive':0,
              'LAZDir_out':'',
              'pipeline': '',
              'CreatePDALInfo':0,
              'PDALInfoFile':'',
              'ReadPDALLog':0,
              'CheckLAZCount':0,
              'MissingHCRS':0,
              'MissingVCRS':0,
              'HCRS_Uniform':0,
              'VCRS_Uniform':0,
              'VersionCheck':0,
              'PointTypeCheck':0,
              'GlobalEncodingCheck':0,
              'PointCountCheck':0,
              'CreatePDALBoundary':0,
              'bounds_PDAL':'',
              'BufferSize':0,
              'epsg':'',
              'bounds_PDALmerge':'',
              'bounds_PDALmergeArea':'',
              'bounds_PDALKML':'',
              'CreateLASBoundary':0,
              'winePath':'',
              'bounds_LT':'',
              'randFrac':0,
              'concavity':0,
              'bounds_LTArea':'',
              'bounds_LTKML':'',
              'CheckRasMeta':0,
              'SetRasterCRS':0,
              'a_srs':'',
              'Translate2Tiff':0,
              'RasOutDir':'',
              'Warp2Tiff':0,
              'ras_xBlock':0,
              'ras_yBlock':0,
              'warp_t_srs':''}

    return config
#----------------------------------------------------------------------

#----------------------------------------------------------------------
def ElapsedTime(start_time,end_time):

    print('Program Duration: {}'.format(end_time - start_time))
#----------------------------------------------------------------------

#----------------------------------------------------------------------
def setup_logger(name, log_file,stdout=0, level=logging.INFO):
    """Function setup as many loggers as you want"""
    formatter = logging.Formatter('%(message)s')

    if stdout:
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.FileHandler(log_file)

    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
#----------------------------------------------------------------------

#----------------------------------------------------------------------
def LogHeader(log,indir):
    archived_date = str(datetime.now())
    log.info('------------------------------------------------------')    
    log.info('Program started on: '+archived_date)
    log.info('\nWorking on files from directory:\n')
    log.info(indir)
    log.info('------------------------------------------------------\n')
#----------------------------------------------------------------------

#--------------------------------------------------
def initDirs(dirBase,readme_template,
             ingest_template='ingest_template.py',
             pipeline_template='pipeline.json'):
    """"
    routine to set up a standard set of directories that I will use for
    every project
    """
    
    if len(sys.argv) <= 1:
        print("Need to specify the directory to copy files to.")
        sys.exit()
    else:
        dirBase = sys.argv[1]
        readme_template   = os.path.join(dirBase,'ingest_template.org')
        ingest_template   = os.path.join(dirBase,'ingest_template.py')
        pipeline_template = os.path.join(dirBase,'pipeline.json')


    #check if base exists
    dirCheck = CheckDir(dirBase)    
    if dirCheck is False:
        DirWarning(dirBase)

    #check if README template exists
    fcheck = CheckFile(readme_template)
    if fcheck is False:
        FileWarning(readme_template)

    #check if ingest template exists
    fcheck = CheckFile(ingest_template)
    if fcheck is False:
        FileWarning(ingest_template)

    #check if pipeline template exists
    fcheck = CheckFile(pipeline_template)
    if fcheck is False:
        FileWarning(pipeline_template)

    dirs2create= ['scripts','bounds','OTDocs','logs',
                  'testing/prod','testing/beta']

    #if you use makedirs, it will create the subdirectories.
    for dval in dirs2create:
        dirval = os.path.join(dirBase,dval)
        os.makedirs(dirval)

    #move a template of the readme so that I have
    #consistent checks and notes
    bname = os.path.basename(dirBase)
    new_template = 'ingest_'+str(bname)+'.org'
    new_readme = os.path.join(dirBase,new_template)
    move(readme_template,new_readme)

    #move over a template of the ingest script
    bname = os.path.basename(dirBase)
    new_py_template = 'ingest_'+str(bname)+'.py'
    newBase    = os.path.join(dirBase,'scripts')
    new_ingest = os.path.join(newBase,new_py_template)
    move(ingest_template,new_ingest)

    #move over a template of the PDAL pipeline
    bname = os.path.basename(pipeline_template)
    newBase    = os.path.join(dirBase,'scripts')
    new_pipe   = os.path.join(newBase,bname)
    move(pipeline_template,new_pipe)

    #move main routine, ot_utils.py to scripts
    newBase  = os.path.join(dirBase,'scripts')
    newUtils = os.path.join(newBase,'ot_utils.py')
    move('ot_utils.py',newUtils)

#--------------------------------------------------

   
#--------------------------------------------------
def DirWarning(dirName):
   print( "*******************")
   print( "WARNING!  Directory:\n")
   print( dirName+"\n")
   print( "DOES NOT EXIST!  CHECK PATH.")
   print( "*******************")
   sys.exit()
#--------------------------------------------------

#--------------------------------------------------
def FileWarning(infile):
   print( "*******************")
   print( "WARNING!  FILE:\n")
   print( infile+"\n")
   print( "DOES NOT EXIST!  CHECK PATH.")
   print( "*******************")
   sys.exit()
#--------------------------------------------------


#-----------------------------------------------------------------
def CreatePDALInfo(files,outdir,outfile,errors='errors.txt',progress=1):
    
    #check that outdir exists
    out_check = CheckDir(outdir)    

    if out_check is False:
        print("Directory does not exist:\n"+outdir)
        sys.exit()
              
    out_fpath = os.path.join(outdir,outfile)
    FileOverWrite(out_fpath,ForceOverwrite=1)

    #collect errors in a separate file...
    out_errors = os.path.join(outdir,errors)
    FileOverWrite(out_errors,ForceOverwrite=1)
    
    cmd1 = ['echo [ > '+out_fpath]
    p1   = subprocess.run(cmd1,shell=True)

    if progress:
        bar = Bar('Creating PDAL Log', max=len(files)) 
    for f in files:

        cmd2 = ['pdal info \"'+f+'\" --metadata >> '+out_fpath]
        
        p2 = subprocess.run(cmd2,shell=True,stderr=subprocess.PIPE)

        #check for errors.  Don't want to stop execution because some
        #errors could be minor?
        if (p2.returncode == 1) or (len(p2.stderr) > 0):
            cmd3 = ['echo Error creating PDAL info for '
                    +f+'.  Standard Error of: '
                    +'\"'+str(p2.stderr)+'\" >> '+out_errors]            

            #adds an extra comma for some errors, and I don't know why
            p3 = subprocess.run(cmd3,shell=True,stderr=subprocess.PIPE)

        #separate JSON files with ',' so I can read in as array
        cmd4 = ['echo "," >> '+out_fpath]
        p4 = subprocess.run(cmd4,shell=True,stderr=subprocess.PIPE)

        if progress:
            bar.next()

    #remove final comma from file...
    cmd5 = ['sed -i \'\' -e \'$ d \' '+out_fpath]
    p5 = subprocess.run(cmd5,shell=True)

    #add final bracket to complete the JSON array
    cmd6 = ['echo ] >> '+out_fpath]
    p6 = subprocess.run(cmd6,shell=True)

    if progress:    
        bar.finish()
#-----------------------------------------------------------------


#-----------------------------------------------------------------     
def CheckFile(infile):
    #check that the input file exists
    fcheck = os.path.isfile(infile)
    return fcheck
#-----------------------------------------------------------------     

#-----------------------------------------------------------------     
def CheckDir(indir):
    #check that the input file exists
    fcheck = os.path.isdir(indir)

    return fcheck
#-----------------------------------------------------------------     

#----------------------------------------------------------------------    
def absoluteFilePaths(directory):
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           yield os.path.abspath(os.path.join(dirpath, f))
#----------------------------------------------------------------------


#----------------------------------------------------------------------
def FileOverWrite(infile,ForceOverwrite=0):
    """
    check if file exists.  If it does prompt for overwriting...
    
    Beware in that it will remove all files with the basename, so if you
    have a csv file associated with a shapefile, it will remove that too

    MAB 03.27.2015  Adding feature to print the filename that already
    exists.  Also added the ForceOverwrite keyword.  this will just
    overwrite the file without prompting you.  Also if you are forcing
    it to overwrite, then I don't print anything to standard output.

    MAB 09.02.2015  I removed the fact that it was removing the filename
    with the wildcard*.  I only really needed this for shapefiles, and I
    fixed that by putting in the shapefile check.  So, now, it is not a
    shapefile, it just removes the infile name only.
    """

    fstat = os.path.exists(infile)
    if fstat == 1:
        if ForceOverwrite:
            #check if the file is a shapefile..
            shapecheck = CheckShape(infile)

            #if file is a shapefile, get all associated files....
            if shapecheck:
                suffs = ["shp","dbf","prj","xml","shx","sbn","sbx"]
                
                #this will get all the files associated with a shapefile
                #only!  I do this so that I don't accidentally remove a
                #*.csv or *.kml file....
                f2remove = [item for a in suffs for item in glob.glob(infile[:-3]+"*"+a)]

            else:
                #f2remove = glob.glob(infile[:-3]+"*")
                f2remove = [infile]
                
            for f in f2remove:
                #if forcing, not printing anything to standard out.
                #print "Removing: "+f
                os.remove(f)
        else:
            ansO = input("File: "+infile+ "\nAlready exists.  Do you want to overwrite? [Y/n]: ")
            ansO = ansO.lower()

            if ansO == 'n':
                print( "Program Exiting - File already exists.")
                sys.exit()
            else:
                #check if the file is a shapefile..
                shapecheck = CheckShape(infile)

                #if file is a shapefile, get all associated files....
                if shapecheck:
                    suffs = ["shp","dbf","prj","xml","shx","sbn","sbx"]

                    #this will get all the files associated with a shapefile
                    #only!  I do this so that I don't accidentally remove a
                    #*.csv or *.kml file....
                    f2remove = [item for a in suffs for item in glob.glob(infile[:-3]+"*"+a)]

                else:
                    #f2remove = glob.glob(infile[:-3]+"*")
                    f2remove = [infile]
                for f in f2remove:
                    print( "Removing: "+f)
                    os.remove(f)
#----------------------------------------------------------------------


#----------------------------------------------------------------------
def CheckShape(infile):
    """
    This module will check that the file exists, that it is a shapefile
    and that it has a shp suffix.

    It will return a 1 if the file is o.k., 0 if it is not

    """

    #return flag
    fcheck = 0

    #check that the file exists!
    in_fstat = os.path.exists(infile)
    if in_fstat == 0:
        fcheck = 0
    else:
        #file exists, but is it a shapefile???
        fsplit = infile.split('.')
        if len(fsplit) == 1:
            fcheck = 0
        else:
            #here file has a suffix, but it is not a shapefile
            suffix = fsplit[1].lower()
            if suffix != "shp":
                fcheck = 0
            else:
                fcheck = 1

    return fcheck
#----------------------------------------------------------------------

def Translate2Tiff(files,log,outdir_1="",xblock=256,yblock=256,
                   progress=0):

    """
    Description:  This module will "translate" a tif using
    gdal_translate.  Note that this doesn't do a reprojection.  This
    module is for just changing formats, and is useful if that is all
    you have to do.  I have baked in the ability to tile, and compress
    the output

    Date Created: 05/23/2019

    Input(s):
    1.  files.  this is a list of files that you want to convert.  Note
    that these files can be in different directories.
    
    Output(s):  
    1.  Output will be written to the outdir_1.  Otherwise, the tiff for
    each file in the list will be written to the same directory as the
    path of the inputfile in the list.

    Keyword(s):
    1.  outdir.  Set this to a single directory if you want all the
    output written to a single directory.  
    2.  xblock.  This is the size of the tiles that gdal will tile at in
    the X direction.  This is usually: 128, 256, or 512.  default is set
    to 128.
    3.  yblock.  This is the size of the tiles that gdal will tile at in
    the Y direction.  This is usually: 128, 256, or 512.  default is set
    to 128.
    4.  progress.  Set this to 1 if you want to see a progress bar.  

    Update(s):
    Notes:    
    1.  Errors are written to a log in the output directory.  I may want
    to change this to write to the logs directory for the project, but
    that would require me feeding the full path of the error file, and I
    don't know if that is really necessary right now.
    """

    log.info('Convert Raster to TIFF Format...')        
    log.info('------------------------------------------------------')                

    #check that output directory exists...
    if len(outdir_1) > 1:
        dirCheck = CheckDir(outdir_1)    
        if dirCheck is False:
            DirWarning(outdir_1)

    if progress:
        bar = Bar('Translating rasters to Geotiff', max=len(files))


    
    for infile in files:
        
        #get basename
        outbase = os.path.basename(infile)

        #strip out suffix and add tiff suffix.
        outfile = outbase.split(".")[0]+".tif" 

        #default is to write in same directory as input file.  If you
        #want output to another directory, you must set one.
        if len(outdir_1) > 1:
            outfile = os.path.join(outdir_1,outfile)
            errorfile = os.path.join(outdir_1,'Translate2Tiff_errors.txt')
        else:
            outdir = os.path.dirname(infile)
            outfile = os.path.join(outdir,outfile)
            errorfile = os.path.join(outdir,'Translate2Tiff_errors.txt')

        errors = []
        if outfile:
            #need double quotes for paths with spaces!
            cmd = ['gdal_translate -of GTIFF -co \"COMPRESS=LZW\"'
                   +' -co \"TILED=YES\" -co \"blockxsize='+str(xblock)+'\"'
                   +' -co \"blockysize='+str(yblock)+'\"'
                   +' \"'+infile+'\"'
                   +' '+'\"'+outfile+'\" 2>> \"'+errorfile+'\"']

            #needed the shell=True for this to work
            p = subprocess.run(cmd,shell=True,stderr=subprocess.PIPE)

            #Want to know if there is a problem...
            if (p.returncode == 1):
                print("\nProblem with the TIFF translation for file:\n"+infile)
                print("\nCHECK ERROR LOG:\n"+errorfile+"\n when completed")
                cmd2 = ['echo "error with file:" \"'+infile+'\" >> \"'+errorfile+'\"']
                p2 = subprocess.run(cmd2,shell=True,stderr=subprocess.PIPE)
                errors.append(1)
                
        if progress:
            bar.next()
    
    if progress:
        bar.finish()

    if any(errors):
        log.info("FAIL: Problem Converting Raster(s) to TIFF(s)")
        log.info("CHECK ERROR LOG:\n"+errorfile+"\n")
    else:
        log.info("PASS: Converted Raster(s) to TIFF(s)")
    log.info('------------------------------------------------------\n')

#----------------------------------------------------------------------
    
#----------------------------------------------------------------------
def Warp2Tiff(files,log,t_srs,outdir_1='',xblock=128,yblock=128,
              progress=0):
    """
    Description:  This module will "transform" a tif using
    gdalwarp.  Use this module if you want to actually do a reprojection
    of the raster. I have baked in the ability to tile, and compress
    the output.

    Date Created: 05/23/2019

    Input(s):
    1.  files.  this is a list of files that you want to convert.  Note
    that these files can be in different directories.
    2.  t_srs.  This is the EPSG code for what you want the output to
    be.  I am assuming that it can get the input CRS, so I don't have
    that as an input right now, but that may be necessary in the future?

    Output(s):  
    1.  Output will be written to the outdir.  Otherwise, the tiff for
    each file in the list will be written to the same directory as the
    path of the inputfile in the list.

    Keyword(s):
    1.  outdir.  Set this to a single directory if you want all the
    output written to a single directory.  
    2.  xblock.  This is the size of the tiles that gdal will tile at in
    the X direction.  This is usually: 128, 256, or 512.  default is set
    to 128.
    3.  yblock.  This is the size of the tiles that gdal will tile at in
    the Y direction.  This is usually: 128, 256, or 512.  default is set
    to 128.
    4.  progress.  Set this to 1 if you want to see a progress bar.  

    Update(s):

    Notes:
    1.  Errors are written to a log in the output directory.  I may want
    to change this to write to the logs directory for the project, but
    that would require me feeding the full path of the error file, and I
    don't know if that is really necessary right now.
    """

    log.info('Reprojecting TIFFs...')        
    log.info('------------------------------------------------------')            

    #check that output directory exists...
    if len(outdir_1) > 1:
        dirCheck = CheckDir(outdir_1)    
        if dirCheck is False:
            DirWarning(outdir_1)

    if progress:
        bar = Bar('Transforming rasters to Geotiff', max=len(files))

    if not t_srs:
        log.info('FAIL: Must set a target EPSG')
        print('FAIL: Must set a target EPSG')
        ipdb.set_trace()
        
    for infile in files:
        
        #get basename
        outbase = os.path.basename(infile)

        if len(outdir_1) > 1:
            #strip out suffix and add tiff suffix.
            outfile = outbase.split(".")[0]+".tif"             
            outfile = os.path.join(outdir_1,outfile)
            errorfile = os.path.join(outdir_1,'Transform2Tiff_errors.txt')
        else:
            #in GDAL, you cannot overwrite input file, so need to
            #output a new file with EPSG as suffix
            outfile = outbase.split(".")[0]+"_EPSG"+str(t_srs)+".tif" 
            outdir = os.path.dirname(infile)
            outfile = os.path.join(outdir,outfile)
            errorfile = os.path.join(outdir,'Transform2Tiff_errors.txt')            


        errors = []
        if outfile:
            #need double quotes for paths with spaces!
            cmd = ['gdalwarp -co \"COMPRESS=LZW\"'
                   +' -co \"TILED=YES\" -co \"blockxsize='+str(xblock)+'\"'
                   +' -co \"blockysize='+str(yblock)+'\"'
                   +' -t_srs \"EPSG:'+str(t_srs)+'\"'+' \"'+infile+'\"'
                   +' '+'\"'+outfile+'\" 2>> \"'+errorfile+'\"']

            #needed the shell=True for this to work
            p = subprocess.run(cmd,shell=True,stderr=subprocess.PIPE)

            #Want to know if there is a problem...
            if (p.returncode == 1):
                print("\nProblem with the TIFF transformation for file:\n"+infile)
                print("\nCHECK ERROR LOG:\n"+errorfile+"\n when completed")
                cmd2 = ['echo "error with file:" \"'+infile+'\" >> \"'+errorfile+'\"']
                p2 = subprocess.run(cmd2,shell=True,stderr=subprocess.PIPE)
                errors.append(1)
                 
        if progress:
            bar.next()

    if progress:
        bar.finish()

    if any(errors):
        log.info("FAIL: Problem Projecting Raster(s)")
        log.info("CHECK ERROR LOG:\n"+errorfile+"\n")
    else:
        log.info("PASS: Projected Raster(s) to TIFF(s)")
        
    log.info('------------------------------------------------------\n')
#----------------------------------------------------------------------
    
#----------------------------------------------------------------------
def GetRasterInfo(FileName):
    """
    Description:  This module will take in a raster and return the basic
    info about it:  

    Date Created: 05/22/2019

    Input(s):
    1.  Filename.  Full path to raster to get info on.

    Output(s):  
    1. structure with the following variables:
    NDV          - no data value
    xsize        - xsize in pixels
    ysize        - ysize in pixels
    PixelRes_EW  - Pixel resolution in EW direction
    PixelRes_NS  - Pixel resolution in NS direction
    Projection   - WKT version of projection
    DataType     - DataType of raster (ex: byte, float32, etc)
    ColorType    - colortype of raster (grayscale, RGB, etc)

    Update(s):

    Notes:
    1.  
    """

    SourceDS = gdal.Open(FileName)
    NDV      = SourceDS.GetRasterBand(1).GetNoDataValue()
    xsize    = SourceDS.RasterXSize
    ysize    = SourceDS.RasterYSize
    GeoT     = SourceDS.GetGeoTransform()
    Projection = SourceDS.GetProjection()
    DataType  = SourceDS.GetRasterBand(1).DataType
    DataType  = gdal.GetDataTypeName(DataType)

    ColorType = SourceDS.GetRasterBand(1).GetColorInterpretation() 
    ColorType = gdal.GetColorInterpretationName(ColorType)
    
    PixelRes_EW = abs(GeoT[1])
    PixelRes_NS = abs(GeoT[5])
    
    output={}
    output["NDV"]          = NDV
    output["xsize"]        = xsize
    output["ysize"]        = ysize
    output["PixelRes_EW"]  = PixelRes_EW
    output["PixelRes_NS"]  = PixelRes_NS    
    output["projection"]   = Projection
    output["DataType"]     = DataType
    output["ColorType"]    = ColorType      
    
    return output
#----------------------------------------------------------------------


#----------------------------------------------------------------------
def CheckRasterInfo(infiles):
    """
    Description:  check if list of rasters is missing CRS
    Date Created: 02/11/2019

    Input(s): list of raster files to check
    Output(s): pandas dataframe
    Update(s):
    Notes: should I put a check in if the file is a valid raster file?
    """

    output  = []    
    for f in infiles:
        #reset record to blank each time
        out_struct   = {"filename":'',"MissingCRS":0,"ActualCRS":'',
                        "PixelRes_EW":0,"PixelRes_NS":0,
                        "DataType":'',"ColorType":''}
        
        bname = os.path.basename(f)
        out_struct['filename'] = bname

        rasInfo = GetRasterInfo(f)

        if len(rasInfo['projection']) == 0:
           out_struct['MissingCRS'] = 1
            
        out_struct['ActualCRS']   = rasInfo['projection']

        #for Pixel res, want to avoid cases where the values are
        #basically the same, but do to float or rounding issues may be
        #technically different (e.g. 1.00005 vs 1.0000499999
        out_struct['PixelRes_EW'] = round(rasInfo['PixelRes_EW'],1)
        out_struct['PixelRes_NS'] = round(rasInfo['PixelRes_NS'],1)
        
        out_struct['DataType']    = rasInfo['DataType']
        out_struct['ColorType']   = rasInfo['ColorType']        

        output.append(out_struct)

    df = pd.DataFrame(output)

    return df

#----------------------------------------------------------------------

#----------------------------------------------------------------------
def SetRasterCRS(infiles,log,a_srs,progress=0):
    """
    Description:  Set the CRS info in the header of raster files.
    Date Created: 07/22/2019

    Input(s): list of raster files 
    Notes:    Adding the header values in place, so may want to add an
    option to write to a separate location?
    """

    log.info('Adding CRS Info to Header...')        
    log.info('------------------------------------------------------')            

    if progress:
        bar = Bar('Transforming rasters to Geotiff', max=len(infiles))
    
    
    for f in infiles:
        fcheck = CheckFile(f)
        if fcheck is False:
            FileWarning(f)
        
        #need double quotes for paths with spaces!
        cmd = ['gdal_edit.py -a_srs \"EPSG:'+str(a_srs)+'\" '+f]

        #needed the shell=True for this to work
        p = subprocess.run(cmd,shell=True,stderr=subprocess.PIPE)

        errors = []
        #Want to know if there is a problem...
        if (p.returncode == 1):
            print("WARNING: Problem with Adding CRS to header for file:\n"+f)            
            log.info("WARNING: Problem with Adding CRS to header for file:\n"+f)
            errors.append(1)


        if progress:
            bar.next()

    if progress:
        bar.finish()

    if any(errors):
        log.info("WARNING: Problem Adding CRS info to some Raster(s)")
    else:
        log.info("PASS: Added CRS Info to Raster(s)")
        
    log.info('------------------------------------------------------\n')        

#----------------------------------------------------------------------

    
#----------------------------------------------------------------------
def LAZCount(indir):
    #report if the files are in laz or not.  output could be:
    #{totalFileCount,totalLAZCount,totalLASCount, list of file suffixes}

    #don't think I need to worry about case?

    
    laz_files = [filename for filename in os.listdir(indir) 
                 if re.search(r'\.laz$', filename, re.IGNORECASE)]
    laz_count = len(laz_files)

    las_files = [filename for filename in os.listdir(indir) 
                 if re.search(r'\.las$', filename, re.IGNORECASE)]
    las_count = len(las_files)
    
    #just a list of ALL the files, BUT filter out directories.
    onlyfiles = [f for f in os.listdir(indir) if os.path.isfile(os.path.join(indir, f))]  
    all_count = len(onlyfiles)

    suffixes = []
    for f in onlyfiles:
        suffixes.append(f.split(".")[-1])
    
    output = {"TotalFileCount":all_count, "TotalLAZCount":laz_count,
              "TotalLASCount":las_count,"FileTypes":list(set(suffixes))}


    return output
#----------------------------------------------------------------------

#----------------------------------------------------------------------
def CreatePDALLog(script_name,las_dir,output_dir,logfile):
    #log.info('\nCreating PDAL output for all files...')
    #log.info('------------------------------------------------------')
    #createPDAL_output = script_name+' '+las_dir+' '+output_dir+' '+logfile
    #call the unix script that creates the PDAL output as an array of JSON
    #files.  

    #check that script exists.

    fcheck = CheckFile(script_name)
    if fcheck is False:
        FileWarning(script_name)
       
    dirCheck = CheckDir(las_dir)    
    if dirCheck is False:
        DirWarning(indir)

    #check that la[sz] files exist in las_dir:
    absPath = os.path.abspath(las_dir)
    
    #find all LAS or LAZ files - account for case
    files = [f for f in os.listdir(absPath) if re.match(r'.*\.[LlAaSsZz]', f)] 

    if len(files) == 0:
        print("No LA[SZ] files in: \n"+absPath+"\nQuitting!")
        sys.exit()              
    else:
        p = subprocess.Popen([script_name,las_dir,output_dir,logfile])
        p.wait()

    #log.info('\nPDAL output created successfully.')
    #log.info('\nJSON file written to: \n')
    #log.info(os.path.join(output_dir,logfile)
    #log.info('------------------------------------------------------\n')    
#----------------------------------------------------------------------

#----------------------------------------------------------------------    
def readJSONARRAY(output_dir,logfile):

    PDAL_file = os.path.join(output_dir,logfile)

    #only want to do this once...no need to keep re-do
    #read in the PDAL output for ALL the files.
    with open(PDAL_file,'r') as read_file:
        data = json.load(read_file)

    return data
#----------------------------------------------------------------------


#----------------------------------------------------------------------    
def CountCRS(json):

    #missingCRS: 0/1
    #multipleCRS: 0/1
    #missingVCRS:0/1
    #multipleVCRS:0/1
    #looping through thousands of files.  may want to know which files
    #have different CRS?  Maybe have a separate routine for that, so one
    #routine to just check if they are all the same and what they are,
    #then if there is a problem, have a different routine to isolate
    #which files have which CRS?    
    #get a count of the different CRS fields for each file

    output  = []    
    for d in json:
        #reset record to blank each time
        out_struct   = {"filename":'',"MissingHCRS":0,"MissingVCRS":0}

        fname    = d['filename']
        metadata = d['metadata']

        HCRS_1 = metadata['comp_spatialreference']
        HCRS_2 = metadata['spatialreference']
        HCRS_3 = metadata['srs']['compoundwkt']
        HCRS_4 = metadata['srs']['horizontal']
        HCRS_5 = metadata['srs']['prettycompoundwkt']
        HCRS_6 = metadata['srs']['prettywkt']
        HCRS_7 = metadata['srs']['proj4'] 

        VCRS_1 = metadata['srs']['vertical'] 
        
        #Horizontal CRS check - if ALL of the potential Horizontal CRS
        #fields are blank, then warn...
        #need to also test if it is just set to "unknown"!
        if (len(HCRS_1) == 0) and (len(HCRS_2) == 0) and (len(HCRS_3) == 0) and \
        (len(HCRS_4) == 0) and (len(HCRS_5) == 0) and (len(HCRS_6) == 0) and \
        (len(HCRS_7) == 0):
            #print("Missing Horizontal CRS info: "+fname)
            out_struct["filename"] = fname
            out_struct["MissingHCRS"] = 1

        if (len(VCRS_1) == 0):
            #print("Missing Vertical CRS Info: "+fname)
            out_struct["filename"] = fname
            out_struct["MissingVCRS"] = 1

        output.append(out_struct)


    out_pandas = pd.DataFrame(output)

    return out_pandas


#----------------------------------------------------------------------

#----------------------------------------------------------------------    
def getHCRS_EPSG(json):

    #Need to pull out the horizontal coordinate EPSG code.  This is
    #probably not fool proof, but worth a shot.  It could be that the
    #EPSG for the horizontal CRS is in a field that I cannot easily
    #check.  the comp_spatial reference, for example, will have VCRS
    #at the end, and there is not way to easily pick out the EPSG that
    #is unique.

    output  = []    
    for d in json:
        #reset record to blank each time
        out_struct   = {"filename":'',"HCRS_EPSG":''}

        fname    = d['filename']
        out_struct["filename"] = fname

        metadata = d['metadata']

        HCRS_1 = metadata['srs']['horizontal']
        HCRS_2 = metadata['srs']['prettywkt']
        HCRS_3 = metadata['srs']['wkt']

        if (len(HCRS_1) == 0) and (len(HCRS_2) == 0) and (len(HCRS_3) == 0):
            print("Missing Horizontal CRS info: "+fname)
            out_struct["HCRS_EPSG"] = 'None'
        else:
            #need to slice up the list
            wkt2 = HCRS_3.split(',')[-1]
            wkt3 = [val for val in wkt2 if val.isdigit()]    
            epsg = ''.join(wkt3)

            out_struct['HCRS_EPSG'] = epsg

        output.append(out_struct)

    out_pandas = pd.DataFrame(output)

    return out_pandas
#----------------------------------------------------------------------

#----------------------------------------------------------------------    
def getVCRS_EPSG(json):

    #Need to pull out the vertical coordinate EPSG code.  This is
    #probably not fool proof, but worth a shot.  It could be that the
    #EPSG for the vertical CRS is in a field that I cannot easily
    #check.  Or they just may not be a Vertical CRS

    #----------------------------------------------
    def firstNon0(inlist,startindex):
        for index in range(startindex,len(inlist)):
            if inlist[index]!=0:return index

        return None
    #----------------------------------------------

    output  = []    
    for d in json:
        #reset record to blank each time
        out_struct   = {"filename":'',"VCRS_EPSG":''}

        fname    = d['filename']
        out_struct["filename"] = fname

        metadata = d['metadata']

        #it could be buried in any of these schemas...
        #['compoundwkt', 'prettycompoundwkt', 'prettywkt', 'vertical','wkt']
        compoundwkt  = metadata['srs']['compoundwkt']
        Pcompoundwkt = metadata['srs']['prettycompoundwkt']        
        Pwkt         = metadata['srs']['prettywkt']
        vertical     = metadata['srs']['vertical']
        wkt          = metadata['srs']['wkt']

        VCRS_types = [compoundwkt,Pcompoundwkt,Pwkt,vertical,wkt]

        VCRS_vals = []
        for v in VCRS_types:
            
            #get the index of VERT_DATUM
            VCRS_i = v.find('VERT_DATUM')
            if VCRS_i != -1:
                VCRS_vals.append(v[VCRS_i:])
            else:
                VCRS_vals.append(0)
                            
        if any(VCRS_vals) is False:
            #print("Missing Vertical CRS info: "+fname)
            out_struct["VCRS_EPSG"] = 'None'
        else:
            #get the element that had a defined CRS string
            validCRS = firstNon0(VCRS_vals,0)            
            #need to slice up the list
            v    = VCRS_vals[validCRS]
            wkt2 = v.split(',')[-1] 
            wkt3 = [val for val in wkt2 if val.isdigit()]    
            epsg = ''.join(wkt3)

            out_struct['VCRS_EPSG'] = epsg

        output.append(out_struct)

    
    out_pandas = pd.DataFrame(output)

    return out_pandas
#----------------------------------------------------------------------

#----------------------------------------------------------------------    
def getGlobalEncoding(json):

    #Routine to get the point types for each of the las files, and see
    #if they are uniform.

    output  = []    
    for d in json:
        #reset record to blank each time
        out_struct   = {"filename":'',"GlobalEncoding":0}

        fname    = d['filename']
        out_struct["filename"] = fname

        metadata = d['metadata']

        GlobalE  = metadata['global_encoding']

        out_struct['GlobalEncoding'] = GlobalE

        output.append(out_struct)

    
    out_pandas = pd.DataFrame(output)

    return out_pandas
#----------------------------------------------------------------------

#----------------------------------------------------------------------    
def getPointType(json):

    #Routine to get the point types for each of the las files, and see
    #if they are uniform.

    output  = []    
    for d in json:
        #reset record to blank each time
        out_struct   = {"filename":'',"PointType":0}

        fname    = d['filename']
        out_struct["filename"] = fname

        metadata = d['metadata']

        pType  = metadata['dataformat_id']

        out_struct['PointType'] = pType

        output.append(out_struct)

    
    out_pandas = pd.DataFrame(output)

    return out_pandas
#----------------------------------------------------------------------

#----------------------------------------------------------------------    
def getPointCount(json):
    """
    Make sure the file has points.  If it is just a header, sometimes
    this will mess things up.  Want to warn if there are empty files.  

    Input:  
    1.  PDAL metadata output in JSON of all the files

    """

    output  = []    
    for d in json:
        #reset record to blank each time
        out_struct   = {"filename":'',"PointCount":0}

        fname    = d['filename']
        out_struct["filename"] = fname

        metadata = d['metadata']
        ptCount  = metadata['count']

        out_struct['PointCount'] = ptCount

        output.append(out_struct)

    
    out_pandas = pd.DataFrame(output)

    return out_pandas    
#----------------------------------------------------------------------    


#----------------------------------------------------------------------    
def checkLASVersion(json):

    output  = []    
    for d in json:
        #reset record to blank each time
        out_struct   = {"filename":'',"Version":0.0}

        fname    = d['filename']
        metadata = d['metadata']

        major = metadata["major_version"]
        minor = metadata["minor_version"]        
        las_version = float(major)+(float(minor)/10.0)


        out_struct["filename"] = fname
        out_struct["Version"]  = las_version

        output.append(out_struct)

    #convert to pandas dataframe
    out_pandas = pd.DataFrame(output)

    return out_pandas

#----------------------------------------------------------------------


#----------------------------------------------------------------------    
def Convert2LAZ(files,pipeline,outdir='',progress=1,method='pdal',
                wine_path='/Applications/LASTools/bin'):
    
    #convert from las to laz using pdal OR lastools...

    method = method.lower()
    if method not in ['lastools','pdal']:
        print('FAIL: must set method to pdal or lastools')
        ipdb.set_trace()

    #check that output directory exists...
    if len(outdir) > 1:
        dirCheck = CheckDir(outdir)    
        if dirCheck is False:
            DirWarning(outdir)

    if progress:
        bar = Bar('Converting from LAS to LAZ', max=len(files))
 
    for infile in files:
        
        #check that it is a las file
        suffix = infile.split(".")[-1]

        if suffix  == 'las':            
            outfile = infile.replace('.las','.laz')
        elif suffix  == 'LAS':
            outfile = infile.replace('.LAS','.laz')           

        #get base filename
        outfile = os.path.basename(outfile)

        if len(outdir) > 1:
            #write output to a different directory...
            outfile = os.path.join(outdir,outfile)
        else:
            #write output to same as input...
            outdir = os.path.dirname(infile)
            outfile = os.path.join(outdir,outfile)
        
        errorfile = os.path.join(outdir,'LAS2LAZ_errors.txt')

        if outfile:

            if method == 'pdal':
                #check that pipeline exists:
                fcheck = CheckFile(pipeline)
                if fcheck is False:
                    FileWarning(pipeline)

                #need double quotes for paths with spaces!
                #Added "forward" to preserve header values, Otherwise PDAL
                #updates them and I want to keep the file as close to
                #original as possible.
                #Convert using PDAL...
                cmd = ['pdal pipeline '+pipeline+
                       ' --readers.las.filename=\"'+infile+
                       '\" --writers.las.filename=\"'+outfile+
                       '\" --writers.las.forward=\"header\" 2>> \"'+errorfile+'\"']

            if method == 'lastools':
                wineCheck = CheckDir(wine_path)
                if wineCheck is False:
                    DirWarning(wine_path)

                #Convert using LASTools...
                cmd = ['wine '+os.path.join(wine_path,'las2las.exe')
                       +' -i \"'+infile+'\" -o \"'+outfile+'\" 2>/dev/null']

                
            #needed the shell=True for this to work
            p = subprocess.run(cmd,shell=True,stderr=subprocess.PIPE)

            #Want to know if there is a problem...
            if (p.returncode == 1):
                print("\nProblem with the LAS conversion for file:\n"+infile)
                print("\nCHECK ERROR LOG:\n"+errorfile+"\n when completed")
                cmd2 = ['echo "error with file:" \"'+infile+'\" >> \"'+errorfile+'\"']
                p2 = subprocess.run(cmd2,shell=True,stderr=subprocess.PIPE)
                ipdb.set_trace()
    
        if progress:        
            bar.next()

    if progress:
        bar.finish()

#end of Convert2LAZ
#----------------------------------------------------------------------        

#----------------------------------------------------------------------    
def AddCRS2Header(files,log_dir,pipeline,outdir='',
                  out_suffix='_wCRS',overwrite=0,progress=1):

    #Add CRS to lidar file header...
    
    #test for a blank string as suffix.  if so, make one so that it
    #doesn't bomb if overwriting.  
    if not out_suffix.strip():
        out_suffix = '_wCRS'
        
    if progress:
        bar = Bar('Adding CRS to Lidar files:', max=len(files))

    #reads in a pipline and executes it.  This module should add the CRS
    #info to the header of the files...

    #check that pipeline exists:
    fcheck = CheckFile(pipeline)
    if fcheck is False:
        FileWarning(pipeline)

    #check that output directory exists...
    if len(outdir) > 1:
        dirCheck = CheckDir(outdir)    
        if dirCheck is False:
            DirWarning(outdir)
    
    for infile in files:

        #isolate filename
        outfile = os.path.basename(infile)

        #add suffix to output - not overwriting files....
        outfile  = outfile.replace('.',out_suffix+'.')

        if len(outdir) > 1:
            outfile = os.path.join(outdir,outfile)
        else:
            outdir = os.path.dirname(infile)
            outfile = os.path.join(outdir,outfile)
                
        if outfile:
            #abs_outfile = os.path.join(absPath,outfile)
            #abs_infile  = os.path.join(absPath,infile)
            #write errors to a file
            cmd = ['pdal pipeline '+pipeline+' --readers.las.filename=\"'
                   +infile+'\" --writers.las.filename=\"'+outfile+'\"'
                   +' --writers.las.forward=\"header\" + 2>> '
                   +os.path.join(log_dir,'CRSDefineErrors.txt')]

            #needed the shell=True for this to work
            p = subprocess.run(cmd,shell=True)#,stderr=subprocess.PIPE)

        if overwrite:
            #in_suffix = suffix.lower()
            #Over_out_suffix = outfile.split(".")[-1]
            #Over_out_suffix = Over_out_suffix.lower()

            #if in_suffix == Over_out_suffix:
            cmd2 = ['mv \"'+outfile+'\" \"'+infile+'\"']
            p2 = subprocess.run(cmd2,shell=True)

        if progress:        
            bar.next()

    if progress:
        bar.finish()

#----------------------------------------------------------------------        

#----------------------------------------------------------------------
def CreateBounds(infiles,out_boundary,epsg,edge_size=50):
    #setting edge_size=10 gets a better approximation of the boundary.
    #Edge_size of 1 finds to many gaps.
    #Needed to escape asterisk to avoid getting weird errors....
    #Need extra "quotes" for paths with spaces...
    #regular expression is a pain in the ass.  This will match LAZ
    #files.  the .* matches ANY previous characters, and the $ indicates
    #that the text needs to end in LAZ or laz or any combo.  Change the
    #Zz to Ss if want las files.

    indir = os.getcwd()
    CreateTempFile(infiles,indir)
    
    cat_cmd = 'cat tmp.txt'

    if edge_size == 0:
        cmd = [cat_cmd+'|pdal tindex --tindex '+out_boundary
               +' --stdin'
               +' -f "ESRI Shapefile"'
               +' --t_srs \"EPSG:'+str(epsg)+'\"']
    else:
        cmd = [cat_cmd+'|pdal tindex --tindex '+out_boundary
           +' --stdin'
           +' -f "ESRI Shapefile"'
           +' --filters.hexbin.edge_size='+str(edge_size)
           +' --t_srs \"EPSG:'+str(epsg)+'\"']

    p = subprocess.run(cmd,shell=True,stderr=subprocess.PIPE)
    if (p.returncode == 1):
       print('Error Creating Boundary with PDAL..\n')
       print(p)
       ipdb.set_trace()           

    #remove the file tmp.txt that contains the list of files...
    p2 = subprocess.run('rm -f tmp.txt',shell=True)
#----------------------------------------------------------------------

#----------------------------------------------------------------------
def DissolveBounds(inbounds, outbounds,buffer=0):
    """
    Name: 
    Description: Dissolves a boundary so that you have a single polygon.
    You can add a buffer so that it will remove slivers if you have them.   

    Date Created: 02/11/2019

    Input(s):
    inbounds.  This is the shapefile that you want to dissolve
 
    Output(s):
    outbounds. This is the output shapefile that will be dissolved

    Keyword(s):
    buffer.  Set this to remove tiny slivers that sometimes pop up.
    Default is 0, but if you set it to 1 or a low number, it will take
    care of the slivers without altering the boundary too much.

    Update(s):

    Notes:
    """
    
    #check that boundary exists:
    fcheck = CheckFile(inbounds)
    if fcheck is False:
        FileWarning(inbounds)

    #this will dissolve the file

    bname = os.path.basename(inbounds)
    bname_nosuffix = bname.split('.')[0]
    
    if buffer == 0:
        cmd = ['ogr2ogr \"'+outbounds+'\" \"'+inbounds
               +'\" -dialect sqlite -sql \"SELECT ST_UNION(geometry) FROM \''
               +bname_nosuffix+'\'\"']
    else:
        #if you get slivers, use a small buffer:
        cmd = ['ogr2ogr \"'+outbounds+'\" \"'+inbounds
               +'\" -dialect sqlite -sql \"SELECT '
               +'ST_UNION(ST_BUFFER(geometry,'+str(buffer)+')) FROM \''+bname_nosuffix+'\'\"']

    p = subprocess.run(cmd,shell=True,stdout=PIPE)
    if (p.returncode == 1):
       print('Error Dissolving Boundary with OGR..\n')
       print(p)
       ipdb.set_trace()           
#----------------------------------------------------------------------

#----------------------------------------------------------------------
def LASBoundary(files,out_boundary,rand_fract=0.2,concavity=100,
                wine_path='/Users/beckley/Documents/LAStools/bin'):

    #Create a Boundary using the lastools lasboundary.exe 

    wineCheck = CheckDir(wine_path)
    if wineCheck is False:
        DirWarning(wine_path)
    
    numfiles = len(files)
    if numfiles == 0:
        print('Cannot make boundary - file list is empty')
        sys.exit()
        
    print('Creating LAS boundary for: '+str(numfiles)+' files...')


    bounds_base = os.path.dirname(out_boundary)

    baseCheck = CheckDir(bounds_base)
    if baseCheck is False:
        DirWarning(bounds_base)
    
    #need to output a temporary file
    tmpfile = CreateTempFile(files,bounds_base)

    #disjoint prevents connecting lines between polygons that are
    #separate.
    #holes will create a separate polygon for where there are holes in
    #the data.
    cmd = ['wine '+os.path.join(wine_path,'lasboundary.exe')
           +' -lof '+tmpfile+' -merged -keep_random_fraction '
           +str(rand_fract)+' -disjoint -holes -concavity '+str(concavity)+' -o '
           +out_boundary+' 2>/dev/null']

    p2 = subprocess.run(cmd,shell=True,stdout=PIPE)
    p3 = subprocess.run('rm -f '+tmpfile,shell=True)

    if (p2.returncode == 1):
       print('Error Creating Boundary with LASTools..\n')
       print(p2)
       ipdb.set_trace()           

#----------------------------------------------------------------------

#----------------------------------------------------------------------
def CreateTempFile(files,indir):
    outfile = os.path.join(indir,'tmp.txt')
    fopen = open(outfile,'w')

    for f in files:
        fopen.write(str(f)+'\n')

    fopen.close()

    return outfile
#----------------------------------------------------------------------


#----------------------------------------------------------------------
def getFiles(indir, wild='.*[LlAaZz]$',ftype='f',recursive=1):

    """
    Description: main routine to get all the files you want to work on.
    Use Regular Expressions to get what you want.  This routine produces
    the files that are fed into all the other routines.

    Input(s): 
    indir.  The directory that you want to search on.  I add
    "" around it within this module, so it should be able to handle
    directories with spaces or other weird characters.
    
    wild.  This is the regular expression that you want to use to filter
    the results.

    ftype.  This will almost always be 'f'.  This is what gets fed into
    the unix find command (-type).  In rare cases where you want to
    convert ESRI grids, you need to set this to 'd' so that it will just
    find the ESRI grid directory and convert it properly.  

    recursive.  Set this if you want to drill down to all directories.
    Note that if you do this, then when doing conversions, if you do not
    set an output directory, the modules will write the output to the
    same directory as the input.

    Output(s): list of filenames that match the Reg expression.

    Update(s):
    Notes:

    """

    
    #type is needed because if they are ESRI GRID files, it will be a
    #directory of files that needs to be converted.
    ftype = ftype.lower()
    ftype = ftype.strip()
    if ftype not in ['f','d']:
        print('ftype for find command must be: f or d')
        ipdb.set_trace()
    
    #get listing of files that match the reg expression and output a
    #list.  ireg will ignore case
    if recursive == 0:
        find_cmd = 'find \"'+indir+'\" -iregex '+wild+' -type '+ftype+' -maxdepth 1 -print'
    if recursive == 1:
        find_cmd = 'find \"'+indir+'\" -iregex '+wild+' -type '+ftype+' -print'


    p1 = subprocess.run(find_cmd,shell=True,stdout=PIPE)

    #do some error checking...
    if (p1.returncode == 0) and (len(p1.stdout) != 0):
        out = p1.stdout
    
        #convert from bytes to string
        out_str = out.decode()

        #remove blank areas
        out_str = out_str.strip()

        out = out_str.split('\n')
    elif (len(p1.stdout) == 0) and (p1.returncode == 0):
        print('No files found in '+indir+' with wildcard: '+wild)
        sys.exit()
    elif (p1.returncode == 1):
        print('Error - Check if path exists:\n'+indir)
        sys.exit()
        
    
    return out
#----------------------------------------------------------------------



#----------------------------------------------------------------------
def getArea(inpolygon,outpolygon,conv_factor=1.0e6,colName='AREA'):
    #default conversion is to convert m^2 to km^2
    #may need to put in checks for spaces as well...
    #default column name is "AREA"

    
    #verify that in/out are shapefiles.
    inpoly_check  = CheckShape(inpolygon)
    #out doesn't exist yet, so check that it ends in '.shp'
    outpoly_check = outpolygon.split('.')[1]

    if (inpoly_check == 0) or (outpoly_check.lower() != 'shp'):
        print('input and output must be shapefiles.  Quitting')
        ipdb.set_trace()
        sys.exit()

    #check for dashes in names - messes with the sql queries.
    if '-' in inpolygon:
        print("Filenames with dashes mess up the SQL query\nReplace: "
              +inpolygon+" with underscores...")
        sys.exit()
    
    #don't want "-" in names, it makes it a pain to work with in SQL
    #Also, only want to replace dashes in filename, and not full path...
    if '-' in os.path.basename(outpolygon):
        print("Replacing dashes with underscores..")
        out_new = os.path.basename(outpolygon).replace('-','_')
        outpolygon = os.path.join(os.path.dirname(outpolygon),out_new)
        print("New output file: "+outpolygon)

    #get basename of input table..
    bname = os.path.basename(inpolygon.split('.')[0])
    
    #get the area.  again must be run from OSGEO shell.  Also, shapefile
    #needs to be projected!
    cmd1 = ['ogr2ogr \"'+outpolygon+'\" \"'+inpolygon
            +'\" -sql "select OGR_GEOM_AREA/'+str(conv_factor)
            +' AS '+colName+' from '
            +bname+'\"']

    p = subprocess.run(cmd1,shell=True)
    if (p.returncode == 1):
       print('Error Calculating Area with OGR..\n')
       print(p)
       ipdb.set_trace()           
    
    #need to remove the FID from the shapefile, so that when you convert it
    #to kml, it won't be in there.
    #ogrinfo PDALmerged.shp -sql "alter table NZ16_Otago drop column FID"

    #to put it into KMZ:
    #zip -r FINAL_Bounds.kmz FINAL_Bounds.kml
#----------------------------------------------------------------------

#-----------------------------------------------------------------     
def shape2KML(infile,outfile):
    """Shape2KML function will make a call to ogr2ogr and convert an
    ESRI shapefile to a kml.  It shouldn't matter if it is a line or point
    file.
    To Call you need to supply the filename to convert.
    
    Ex:
    from mab_utils import Shape2KML
    Shape2KML("RefGround_Sep24to30_2013_Line.shp")

    Quirks:  
    1.  code will put output file in current directory.
    2.  Point shapefile come up with the default "ThumbTack" Icon.
    3.  Attributes are there, but there are in a ugly table.

    NOTES:
    1.  MAB 10/27/2014.  Now need to supply outfile name.
    2.  #to get into a kml format:
        ogr2ogr -f "KML" FINAL_Bounds.kml PDALmerged.shp

    """
    #check for input file
    in_fstat = os.path.exists(infile)
    if in_fstat == 0:
        print("File:\n"+infile+"\n does not exist.  Provide a valid input filename!")
        sys.exit()

    #check if file exists.  If it does prompt for overwriting...
    FileOverWrite(outfile)

    #Make sure input is a shape, and output is a kml file
    inShape_check  = CheckShape(infile)
    if inShape_check == 0:
        print("Problem with:"+infile+
              "\nIt either does not exist, or is not a shapefile")
        sys.exit()

    #make sure output file is a kml...
    outkml = outfile.split('.')[-1] 
    if outkml.lower() != 'kml':
        print('Output file is not a kml!')
        sys.exit()
    
    #this calls the OGR utility from UNIX to do the conversion.
    cmd=['ogr2ogr -f "KML" \"'+outfile+'\" \"'+infile+'\"']        
    p = subprocess.run(cmd,shell=True)


    if (p.returncode == 1):
       print('Error Creating KML with OGR..\n')
       print(p)
       ipdb.set_trace()           
    
    
#End of shape2KML
#----------------------------------------------------------------- 

#-----------------------------------------------------------------    
def RemoveFields(file,fields2delete=[],OnlyKeep=[]):
    """
    Description:  Remove a list of fields or keep only a subset.

    Date Created: Decmeber 18th 2015

    Input(s):
    1.  file.  The file that you want to remove columns from.  It needs to be
    a shapefile.  It has only been tested on a line file.

    2.  fields2delete.  List of field names you want to delete.  Must be
    a list of strings.  This is optional.

    3.  OnlyKeep.  List of fields that you want to keep.  Must be a list
    of strings.  If this is set, it will remove ALL other field names.

    Notes: This code will alter the file, so be cautious.  I have not
    done extensive testing on this yet.  It worked on a bunch of line
    trajectories. 

 
    Examples:
        file = "traj57291_LVIS.shp"
        dropFields = ["Id","FID","Region","Length_km","garbage"]
        Fields2Keep   = ["MJD", "Date", "Platform"]
        mb.RemoveFields(file,OnlyKeep=Fields2Keep)

    """

    __author__      = "Matthew Beckley"

    
    if (len(OnlyKeep) > 0) & (len(fields2delete) > 0):
        print( "You cannot set both 'OnlyKeep' AND 'Fields2Keep'\n")
        print( "Quitting!")
        sys.exit

    
    #check that file exists...
    fcheck = CheckFile(file)
    if fcheck is False:
        FileWarning(file)
    
    driver     = ogr.GetDriverByName('ESRI Shapefile')
    
    #set to 0 if want read-only,1 if you want to write/edit
    datasource = driver.Open(file, 1)
    layer      = datasource.GetLayer()
    ldef       = layer.GetLayerDefn()

    
    if len(OnlyKeep) > 0:
        
        numfields = ldef.GetFieldCount()
        count=0
        while (numfields != len(OnlyKeep)):
            field = ldef.GetFieldDefn(count).GetName()
            #print "count: ",str(count)
            #print field
            #print numfields, len(OnlyKeep)
            if field not in OnlyKeep:
                count = 0 
                #print "Searching for: ",field
                findex = layer.FindFieldIndex(field,1)
                if findex == -1:
                   print( "Field: "+field+" not found!")
                   print( "Not removing: "+field)

                else:
                    layer.DeleteField(findex)
            else:
                count+=1

            numfields = ldef.GetFieldCount()

                
    elif len(fields2delete) > 0:
        
        for field in fields2delete:
            print( "Searching for: ",field)
            findex = layer.FindFieldIndex(field,1)
            if findex == -1:
                print( "Field: "+field+" not found!")
                print( "Not removing: "+field)

            else:
                layer.DeleteField(findex)

        else:
            print( "you must set either 'fields2delete' OR 'OnlyKeep'\n")
            print( "Exiting!")
            sys.exit()
    
    # close the data source and text file
    datasource.Destroy()

#End of RemoveFields
#-----------------------------------------------------------------

def RunQAQC(config):
    """
    Description:  This is the module that reads in the config file and
    runs the modules to do the actual QAQC.  Users can set which modules
    they want to run, and the parameters to use in their config file.
    It's probably easiest to set up multiple config files and run
    multiple times to do specific tasks.

    Date Created: Jul 12 2019
    Input(s): Config file in form of dictionary.  Refer to module,
    initializeNullConfig in this file to see the list of parameters to
    set.  

    Update(s):
    Notes:

    """
    
    ingest_start_time = datetime.now()
    
    #For now, always create std out and file logs...
    #------------------------------------------------------------
    #always start a new log?  Check if one exists, and if so
    #delete it.

    if os.path.exists(config['ingestLog']):
        os.remove(config['ingestLog'])

    #open log
    log    = setup_logger('Log1', config['ingestLog'])

    #Write header to Log
    LogHeader(log,config['getFilesDir'])

    stdout = setup_logger('Log2', '', stdout=1) 
    #------------------------------------------------------------

    #There could be a case where you just want to read an existing PDAL
    #log file, and not have to find files?
    if config['getFilesDir']:
        #This is the list of files that you will work on.  To do multiple
        #operations, you will need to run RunIngest multiple times with
        #different configs.
        infiles = getFiles(config['getFilesDir'],wild=config['getFilesWild'],
                           ftype=config['ftype'],recursive=config['recursive'])

        stdout.info('Working on: '+str(len(infiles))+' files...')
        log.info('\nWorking on: '+str(len(infiles))+' files...\n')    

        
    if config['AddCRS2Header']:
        stdout.info('Adding CRS to header of lidar files...')
        log.info('------------------------------------------------------')    
        log.info('Adding CRS to header of lidar files...')
        AddCRS2Header(infiles,config['log_dir'],config['pipeline'],
                      outdir=config['LAZDir_out'],
                      out_suffix=config['fsuffix'],
                      overwrite=config['overwrite'])

        log.info('------------------------------------------------------\n')
    
    if config['LAS2LAZ']:
        stdout.info('Converting files from LAS to LAZ...\n')
        log.info('------------------------------------------------------')    
        log.info('Converting files from LAS to LAZ...')
        log.info('LAZ files will be in:\n')

        if len(config['LAZDir_out']) > 1:
            log.info(config['LAZDir_out'])
        else:
            log.info('Same directory as input files')
            
        Convert2LAZ(infiles,config['pipeline'],outdir=config['LAZDir_out'],
                    method=config['LAS2LAZ_method'],progress=1)
        log.info('------------------------------------------------------\n')

    if config['CreatePDALInfo']:
        #create PDAL Info output from all files
        log.info('------------------------------------------------------')    
        CreatePDALInfo(infiles,config['log_dir'],config['PDALInfoFile'])
        stdout.info('PASS: Created PDAL info log...')
        log.info('PASS: Created PDAL info log...')
        log.info('------------------------------------------------------\n')
        
    if config['CheckLAZCount']:
        fileCount = LAZCount(config['getFilesDir'])
        stdout.info('Checking if LAZ count matches file count in directory...')
        log.info('------------------------------------------------------')    
        log.info('Checking if LAZ count matches file count in directory...')
        if fileCount["TotalLAZCount"] != fileCount["TotalFileCount"]:
            log.info('WARNING: LAZ count does not match Total File Count.')
            log.info('Directory contains following filetypes:')
            for f in fileCount['FileTypes']:
                log.info(str(f))
            log.info('\nCheck path:\n'+config['getFilesDir'])
        else:
            log.info('PASS: LAZ count matches Total File Count.')
        log.info('------------------------------------------------------\n')    

    if config['ReadPDALLog']:
        #Get the json data of PDAL info
        json = readJSONARRAY(config['log_dir'],config['PDALInfoFile'])

    #Check if Horizontal or Vertical CRS is missing on any of the files...
    #----------------------------------------------------------------------    
    if config['MissingHCRS']:

        if not config['ReadPDALLog']:
            print("FAIL: You must set config['ReadPDALLog']=1")
            
        CRS_check = CountCRS(json)
        
        htest = CRS_check.MissingHCRS.isin([1])

        stdout.info('Checking for missing horizontal CRS...')
        log.info('------------------------------------------------------')    
        log.info('Checking for missing horizontal CRS...')
        if any(htest):
            stdout.info("FAIL: Some of the files are missing Horizontal CRS info")            
            log.info("FAIL: Some of the files are missing Horizontal CRS info")

            fname = CRS_check[CRS_check.MissingHCRS == 1]['filename']
            fname_L = fname.to_list()

            log.info("The following files are missing Horizontal CRS info:\n")
            for f in fname_L:
                 log.info(f)

            
            ipdb.set_trace()
        else:
            stdout.info("PASS:  All files have a horizontal CRS")            
            log.info("PASS:  All files have a horizontal CRS")
        log.info('------------------------------------------------------\n')
        
    if config['MissingVCRS']:
        if not config['ReadPDALLog']:
            print("FAIL: You must set config['ReadPDALLog']=1")

        CRS_check = CountCRS(json)
        
        vtest = CRS_check.MissingVCRS.isin([1])
        stdout.info('Checking for missing vertical CRS...')
        log.info('------------------------------------------------------')    
        log.info('Checking for missing vertical CRS...')
        
        if any(vtest):
            stdout.info("WARNING: Some (or ALL) of the files are missing Vertical CRS info")
            log.info("WARNING: Some (or ALL) of the files are missing Vertical CRS info")

            fname = CRS_check[CRS_check.MissingVCRS == 1]['filename']
            fname_L = fname.tolist()

            log.info("The following files are missing Vertical CRS info:\n")
            
            for f in fname_L:
                 log.info(f)

        else:
            stdout.info("PASS:  All files have a vertical CRS")
            log.info("PASS:  All files have a vertical CRS")

        log.info('------------------------------------------------------\n')    
    #----------------------------------------------------------------------

    #check if CRS is uniform...
    #----------------------------------------------------------------------
    if config['HCRS_Uniform']:
        stdout.info('Checking if horizontal CRS is uniform...')
        log.info('------------------------------------------------------')    
        log.info('Checking if horizontal CRS is uniform...')

        if not config['ReadPDALLog']:
            print("FAIL: You must set config['ReadPDALLog']=1")

        HCRS_epsgs   = getHCRS_EPSG(json)          
        unique_epsgs = set(HCRS_epsgs.HCRS_EPSG)
        if len(unique_epsgs) > 1:
            log.info('FAIL: More than 1 EPSG for the Horizontal CRS')
            log.info('There are '+str(len(unique_epsgs))+'different horizontal CRS epsg values')
            log.info('Dataset contains the following horizontal CRS epsg codes:')
            for val in unique_epsgs:
                log.info(str(val))

            ipdb.set_trace()
        else:
            stdout.info("PASS: All files in same HCRS: "+str(unique_epsgs))            
            log.info("PASS: All files in same HCRS: "+str(unique_epsgs))
        log.info('------------------------------------------------------\n')

    if config['VCRS_Uniform']:    
        stdout.info('Checking if vertical CRS is uniform...')
        log.info('------------------------------------------------------')            
        log.info('Checking if vertical CRS is uniform...')

        if not config['ReadPDALLog']:
            print("FAIL: You must set config['ReadPDALLog']=1")

        VCRS_epsgs    = getVCRS_EPSG(json)          
        unique_Vepsgs = set(VCRS_epsgs.VCRS_EPSG)
        if len(unique_Vepsgs) > 1:
            log.info('FAIL: More than 1 EPSG for the Vertical CRS')
            log.info('There are '+str(len(unique_Vepsgs))+'different vertical CRS epsg values')
            log.info('Dataset contains the following vertical CRS epsg codes:')
            for val in unique_Vepsgs:
                log.info(str(val))

            ipdb.set_trace()
        else:
            stdout.info("PASS: All files in same VCRS: "+str(unique_Vepsgs))            
            log.info("PASS: All files in same VCRS: "+str(unique_Vepsgs))

        log.info('------------------------------------------------------\n')    
    #----------------------------------------------------------------------

    #Make sure the files are all in the same LAS version...
    #----------------------------------------------------------------------    
    if config['VersionCheck']:
        if not config['ReadPDALLog']:
            print("FAIL: You must set config['ReadPDALLog']=1")

        Version_check = checkLASVersion(json)
        NumVersions = len(Version_check.Version.unique())
        stdout.info('Checking the version of the las and if it is uniform...')
        log.info('------------------------------------------------------')    
        log.info('Checking the version of the las and if it is uniform...')
        if NumVersions > 1:
            log.info("FAIL: Files are in more than one LAS version")
            ipdb.set_trace()
        else:
            stdout.info("PASS: All files are in version: "+str(Version_check.Version.unique()))
            log.info("PASS: All files are in version: "+str(Version_check.Version.unique()))

        log.info('------------------------------------------------------\n')    
    #----------------------------------------------------------------------

    #Check the point type of all files, and if they are uniform
    #----------------------------------------------------------------------
    if config['PointTypeCheck']:
        stdout.info('Checking if Point Type is uniform...')
        log.info('------------------------------------------------------')    
        log.info('Checking if Point Type is uniform...')

        if not config['ReadPDALLog']:
            print("FAIL: You must set config['ReadPDALLog']=1")

        pType        = getPointType(json)          
        unique_pType = set(pType.PointType)
        if len(unique_pType) > 1:
            log.info('WARNING: More than 1 Point Types for the lidar files')
            log.info('There are '+str(len(unique_pType))+' different Point Type values')
            log.info('Dataset contains files with Point Types: ')
            for val in unique_pType:
                log.info(str(val))
        else:
            stdout.info("PASS: All files have the same Point Type: "+str(unique_pType))
            log.info("PASS: All files have the same Point Type: "+str(unique_pType))

        log.info('------------------------------------------------------\n')        
    #----------------------------------------------------------------------    

    #Check the global encoding of all files, and if they are uniform
    #----------------------------------------------------------------------
    if config['GlobalEncodingCheck']:
        stdout.info('Checking if Global Encoding is uniform...')
        log.info('------------------------------------------------------')    
        log.info('Checking if Global Encoding is uniform...')

        if not config['ReadPDALLog']:
            print("FAIL: You must set config['ReadPDALLog']=1")

        GE        = getGlobalEncoding(json)          
        unique_GE = set(GE.GlobalEncoding)
        if len(unique_GE) > 1:
            log.info('WARNING: More than 1 Global Encoding for the lidar files')
            log.info('There are '+str(len(unique_GE))+' different Global Encoding values')
            log.info('Dataset contains files with Global Encoding Values of: ')
            for val in unique_GE:
                log.info(str(val))
        else:
            stdout.info("PASS: All files have the same Global Encoding Value: "+str(unique_GE))
            log.info("PASS: All files have the same Global Encoding Value: "+str(unique_GE))

        log.info('------------------------------------------------------\n')        
    #----------------------------------------------------------------------    

    #Check if any of the files have a point count of 0
    #----------------------------------------------------------------------
    if config['PointCountCheck']:
        stdout.info('Checking if Point Count is 0')
        log.info('------------------------------------------------------')    
        log.info('Checking if Point Count is 0')

        if not config['ReadPDALLog']:
            print("FAIL: You must set config['ReadPDALLog']=1")

        ptCount_str = getPointCount(json)          
        zero_vals = ptCount_str[ptCount_str['PointCount'] == 0] 

        if len(zero_vals) > 1:
            log.info('WARNING: Some files are empty')
            log.info('There are '+str(len(zero_vals))+' empty files')
            log.info('Following files are empty: ')
            for fname in zero_vals['filename']:
                log.info(fname)
                ipdb.set_trace()
        else:
            stdout.info("PASS: No empty files")
            log.info("PASS: No empty files")

        log.info('------------------------------------------------------\n')        
    #----------------------------------------------------------------------    
        
    #Create Boundary via PDAL
    #----------------------------------------------------------------------
    if config['CreatePDALBoundary']:
        start_PDAL = datetime.now()
        stdout.info('Creating Data Boundary with PDAL...')
        log.info('Creating Data Boundary with PDAL...')        
        log.info('------------------------------------------------------')    
        CreateBounds(infiles,config['bounds_PDAL'],
                     config['epsg'])
        stdout.info("PASS: Created initial boundary with PDAL...")
        log.info('PASS:Created initial boundary with PDAL...')
        
        DissolveBounds(config['bounds_PDAL'],config['bounds_PDALmerge'],
                       buffer=config['BufferSize'])
        stdout.info('PASS: Dissolved boundary with PDAL...')
        log.info('PASS: Dissolved boundary with PDAL...')
        
        end_PDAL = datetime.now()
        log.info('PASS: PDAL Boundary Creation took:\n')
        log.info('{}\n'.format(end_PDAL - start_PDAL))

        getArea(config['bounds_PDALmerge'],config['bounds_PDALmergeArea'])
        stdout.info('PASS: Calculated Boundary Area with PDAL...')
        log.info('PASS: Calculated Boundary Area with PDAL...')

        shape2KML(config['bounds_PDALmergeArea'],config['bounds_PDALKML'])
        stdout.info("PASS: Converted PDAL-derived boundary to KML")        
        log.info("PASS: Converted PDAL-derived boundary to KML")
        log.info('------------------------------------------------------\n')        
    #----------------------------------------------------------------------


    #----------------------------------------------------------------------    
    if config['CreateLASBoundary']:
        start_LAS = datetime.now()
        stdout.info('Creating Data Boundary with LASTools...')
        log.info('Creating Data Boundary with LASTools...')        
        log.info('------------------------------------------------------')            
        LASBoundary(infiles,config['bounds_LT'],
                    rand_fract=config['randFrac'],
                    concavity=config['concavity'],
                    wine_path=config['winePath'])
        end_LAS = datetime.now()

        stdout.info("PASS: Created boundary with LASTools...")
        log.info('PASS:Created boundary with LASTools...')
        log.info('PASS: LASTools Boundary Creation took:\n')
        log.info('{}\n'.format(end_LAS - start_LAS))

        getArea(config['bounds_LT'],config['bounds_LTArea'])
        stdout.info('PASS: Calculated Boundary Area with LASTools...')
        log.info('PASS: Calculated Boundary Area with LASTools...')

        shape2KML(config['bounds_LTArea'],config['bounds_LTKML'])
        stdout.info("PASS: Converted LASTools-derived boundary to KML")        
        log.info("PASS: Converted LASTools-derived boundary to KML")
        log.info('------------------------------------------------------\n')        
    #----------------------------------------------------------------------

    #Overall check of raster metadata...
    #----------------------------------------------------------------------
    if config['CheckRasMeta']:
        stdout.info('Checking Raster Metadata...')
        log.info('Checking Raster Metadata...')                 
        log.info('------------------------------------------------------')

        ras_meta = CheckRasterInfo(infiles)

        #--------------------------------------------------
        CRStest = ras_meta.MissingCRS.isin([1])

        stdout.info('Checking for missing CRS...')
        log.info('--------------------------------')    
        log.info('Checking for missing CRS...')
        if any(CRStest):
            print("FAIL: Some of the rasters are missing CRS info")            
            log.info("FAIL: Some of the rasters are missing CRS info")

            #get data frame of filenames that are missing CRS info.
            fname = ras_meta[ras_meta.MissingCRS == 1]['filename']
            fname_L = fname.to_list()

            log.info("The following rasters are missing CRS info:\n")
            for f in fname_L:
                 log.info(f)

            ipdb.set_trace()
                 
        else:
            stdout.info("PASS:  All rasters have a CRS")            
            log.info("PASS:  All rasters have a CRS")
        log.info('--------------------------------\n')    
        #--------------------------------------------------

        #--------------------------------------------------        
        stdout.info('Checking if CRS is uniform for all rasters...')
        log.info('------------------------------------------------------')    
        log.info('Checking if CRS is uniform for all rasters...')

        unique_WKT = set(ras_meta.ActualCRS)
        if len(unique_WKT) > 1:
            print('FAIL: More than 1 WKT format for the CRS')            
            log.info('FAIL: More than 1 WKT format for the CRS')
            log.info('There are '+str(len(unique_WKT))+'different CRS values')
            log.info('Dataset contains the following CRS WKT values:')
            for val in unique_WKT:
                log.info(str(val))

            #ipdb.set_trace()
        else:
            stdout.info("PASS: All files in same CRS: \n"+str(unique_WKT))            
            log.info("PASS: All files in same CRS: \n"+str(unique_WKT))
        log.info('------------------------------------------------------\n')
        #--------------------------------------------------

                 
        #--------------------------------------------------        
        stdout.info('Checking if Color Type is uniform for all rasters...')
        log.info('------------------------------------------------------')    
        log.info('Checking if Color Type is uniform for all rasters...')

        colortype = set(ras_meta.ColorType)
        if len(colortype) > 1:
            print('FAIL: More than 1 Color Type for the rasters')            
            log.info('FAIL: More than 1 Color Type for the rasters')
            log.info('There are '+str(len(colortype))+'different color types')
            log.info('Dataset contains the following color type values:')
            for val in colortype:
                log.info(str(val))

            ipdb.set_trace()
        else:
            stdout.info("PASS: All files have same color type: "+str(colortype))
            log.info("PASS: All files have same color type: "+str(colortype))
        log.info('------------------------------------------------------\n')
        #--------------------------------------------------

        #--------------------------------------------------        
        stdout.info('Checking if Data Type is uniform for all rasters...')
        log.info('------------------------------------------------------')    
        log.info('Checking if Data Type is uniform for all rasters...')

        datatype = set(ras_meta.DataType)
        if len(datatype) > 1:
            print('FAIL: More than 1 Data Type for the rasters')            
            log.info('FAIL: More than 1 Data Type for the rasters')
            log.info('There are '+str(len(datatype))+'different data types')
            log.info('Dataset contains the following data type values:')
            for val in datatype:
                log.info(str(val))

            ipdb.set_trace()
        else:
            stdout.info("PASS: All files have same data type: "+str(datatype))
            log.info("PASS: All files have same data type: "+str(datatype))
        log.info('------------------------------------------------------\n')
        #--------------------------------------------------
                 
        #--------------------------------------------------        
        stdout.info('Checking if Pixel Size is uniform for all rasters...')
        log.info('------------------------------------------------------')    
        log.info('Checking if Pixel Size is uniform for all rasters...')

        #check both pixel res in NS and EW directions.  These should
        #always be the same, but GDAL breaks it up like this....
        pix = pd.concat([ras_meta.PixelRes_EW,ras_meta.PixelRes_NS])
                 
        pix_res = set(pix)
        if len(pix_res) > 1:
            print('FAIL: More than 1 pixel size for the rasters')            
            log.info('FAIL: More than 1 pixel size for the rasters')
            log.info('There are '+str(len(pix_res))+'different pixel sizes')
            log.info('Dataset contains the following pixel sizes:')
            for val in pix_res:
                log.info(str(val))

            ipdb.set_trace()
        else:
            stdout.info("PASS: All files have same pixel size: "+str(pix_res))
            log.info("PASS: All files have same pixel size: "+str(pix_res))
        log.info('------------------------------------------------------\n')
        #--------------------------------------------------


        stdout.info("PASS: Checked Raster Metadata")
        log.info("PASS: Checked Raster Metadata")                         
        log.info('------------------------------------------------------\n')        

    #End checking Raster metadata
    #----------------------------------------------------------------------                 

    #Setting CRS info in header of a raster
    #----------------------------------------------------------------------
    if config['SetRasterCRS']:
        stdout.info('Adding CRS Info to Raster...')        
        SetRasterCRS(infiles,log,config['a_srs'],progress=1)

        stdout.info('PASS: Added CRS Info to Raster...')        
    #----------------------------------------------------------------------

    #Converting a raster from a Non-TIFF to a tiff.
    #----------------------------------------------------------------------        
    if config['Translate2Tiff']:
        stdout.info('Convert Raster to TIFF Format...')

        Translate2Tiff(infiles,log,outdir_1=config['RasOutDir'],
                       xblock=config['ras_xBlock'],
                       yblock=config['ras_yBlock'],
                       progress=0)
        stdout.info("PASS: Converted Raster(s) to TIFF(s)")
    #----------------------------------------------------------------------        

    #RE-Projecting a raster into a different Projection...
    #----------------------------------------------------------------------
    if config['Warp2Tiff']:
        stdout.info('Reprojecting TIFFs...')

        Warp2Tiff(infiles,log,config['warp_t_srs'],
                  outdir_1=config['RasOutDir'],xblock=config['ras_xBlock'],
                  yblock=config['ras_yBlock'],
                  progress=0)

        stdout.info("PASS: Reprojected TIFFs")        
    #----------------------------------------------------------------------

        
    ingest_end_time = datetime.now()
    log.info('Total Time:\n')
    log.info('{}\n'.format(ingest_end_time - ingest_start_time))
    log.info("\nProgram finished successfully!")
    log.info('------------------------------------------------------\n')
    
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
        
    
    stdout.info("Program finished successfully!")
    
#End runQAQC module
#-----------------------------------------------------------------    
    
if __name__ == "__main__":
    #initialize directories by running:
    #python3 ~/ot/dev/ot_utils.py $PWD

    #This will copy over all the necessary files and directories you
    #need for doing the ingest.

    #set up directories
    initDirs()


 
