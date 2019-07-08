#!/usr/bin/env python
from __future__ import print_function
import json,glob,os,sys,ipdb,subprocess
import ogr,logging,datetime,re
import pandas as pd
from datetime import datetime
from osgeo import gdal,osr
from subprocess import Popen, PIPE
from progress.bar import Bar
from shutil import copyfile

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


"""

__author__      = "Matthew Beckley"


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
def LogHeader(log,las_dir):
    archived_date = str(datetime.utcnow())
    log.info('------------------------------------------------------')    
    log.info('Ingest started on: '+archived_date)
    log.info('\nIngesting files from directory:\n')
    log.info(las_dir)
    log.info('------------------------------------------------------\n')
#----------------------------------------------------------------------

#--------------------------------------------------
def initDirs(dirBase,readme_template,
             ingest_template='/Users/matt/ot/dev/ingest_template.py',
             pipeline_template='/Users/matt/ot/dev/pipeline.json',):

    #routine to set up a standard set of directories that I will use for
    #every project
    
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

    #copy over a template of the readme so that I have
    #consistent checks and notes
    bname = os.path.basename(dirBase)
    new_template = 'ingest_'+str(bname)+'.org'
    new_readme = os.path.join(dirBase,new_template)
    copyfile(readme_template,new_readme)

    #copy over a template of the ingest script
    bname = os.path.basename(dirBase)
    new_py_template = 'ingest_'+str(bname)+'.py'
    newBase    = os.path.join(dirBase,'scripts')
    new_ingest = os.path.join(newBase,new_py_template)
    copyfile(ingest_template,new_ingest)

    #copy over a template of the PDAL pipeline
    bname = os.path.basename(pipeline_template)
    newBase    = os.path.join(dirBase,'scripts')
    new_pipe   = os.path.join(newBase,bname)
    copyfile(pipeline_template,new_pipe)
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

        #check for errors.  Don't want to add a comma if there were problems.
        if (p2.returncode == 1) or (len(p2.stderr) > 0):
            cmd3 = ['echo Error creating PDAL info for '
                    +f+'.  Standard Error of: '
                    +'\"'+str(p2.stderr)+'\" >> '+out_errors]            

            #adds and extrac comma for some errors, and I don't know why
            p3 = subprocess.run(cmd3,shell=True,stderr=subprocess.PIPE)
        else:
            #separate JSON files with ',' so I can read in as array
            cmd4 = ['echo "," >> '+out_fpath]
            p4 = subprocess.run(cmd4,shell=True,stderr=subprocess.PIPE)

        bar.next()

    #remove final comma from file...
    cmd5 = ['sed -i \'\' -e \'$ d \' '+out_fpath]
    p5 = subprocess.run(cmd5,shell=True)

    #add final bracket to complete the JSON array
    cmd6 = ['echo ] >> '+out_fpath]
    p6 = subprocess.run(cmd6,shell=True)

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
                f2remove = glob.glob(infile[:-3]+"*")
                #f2remove = [infile]
                
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
                    f2remove = glob.glob(infile[:-3]+"*")
                    #f2remove = [infile]
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

def Translate2Tiff(files,outdir="TIFFs",xblock=128,yblock=128,
                   recursive=0,progress=1):

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
    1.  Output will be written to the outdir, or if the recursive
    keyword is set, then the tiff for each file in the list will be
    written to the same directory as the path of the inputfile in the
    list.

    Keyword(s):
    1.  outdir.  Set this to a single directory if you want all the
    output written to a single directory.  If this is what you want,
    then recursive should be set to 0.
    2.  xblock.  This is the size of the tiles that gdal will tile at in
    the X direction.  This is usually: 128, 256, or 512.  default is set
    to 128.
    3.  yblock.  This is the size of the tiles that gdal will tile at in
    the Y direction.  This is usually: 128, 256, or 512.  default is set
    to 128.
    4.  recursive.  Set this to 1 if you are feeding in a list of files
    that have different paths.  In this way, the output tiff will be
    written to the same directory as the input file.  This is useful if
    you have a directory structure with lots of subdirectories, and you
    want to do some comparisons (ex: Utah dataset).  If this is set to
    0, then all the output will go to the path specified in the 'outdir'
    keyword.  
    5.  progress.  Set this to 1 if you want to see a progress bar.  

    Update(s):
    Notes:    
    1.  Errors are written to a log in the output directory.  I may want
    to change this to write to the logs directory for the project, but
    that would require me feeding the full path of the error file, and I
    don't know if that is really necessary right now.
    """
    
    #check that output directory exists...
    if recursive == 0:
        dirCheck = CheckDir(outdir)    
        if dirCheck is False:
            DirWarning(outdir)

    if progress:
        bar = Bar('Translating rasters to Geotiff', max=len(files))
 
    for infile in files:
        
        #get basename
        outbase = os.path.basename(infile)

        #strip out suffix and add tiff suffix.
        outfile = outbase.split(".")[0]+".tif" 
        
        if recursive == 1:
            outdir = os.path.dirname(infile)
            outfile = os.path.join(outdir,outfile)
        else:
            outfile = os.path.join(outdir,outfile)
        
        errorfile = os.path.join(outdir,'Translate2Tiff_errors.txt')

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

        bar.next()

    bar.finish()
#----------------------------------------------------------------------
    
#----------------------------------------------------------------------
def Warp2Tiff(files,t_srs,outdir="TIFFs",xblock=128,yblock=128,
              recursive=0,progress=1):
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
    1.  Output will be written to the outdir, or if the recursive
    keyword is set, then the tiff for each file in the list will be
    written to the same directory as the path of the inputfile in the
    list.

    Keyword(s):
    1.  outdir.  Set this to a single directory if you want all the
    output written to a single directory.  If this is what you want,
    then recursive should be set to 0.
    2.  xblock.  This is the size of the tiles that gdal will tile at in
    the X direction.  This is usually: 128, 256, or 512.  default is set
    to 128.
    3.  yblock.  This is the size of the tiles that gdal will tile at in
    the Y direction.  This is usually: 128, 256, or 512.  default is set
    to 128.
    4.  recursive.  Set this to 1 if you are feeding in a list of files
    that have different paths.  In this way, the output tiff will be
    written to the same directory as the input file.  This is useful if
    you have a directory structure with lots of subdirectories, and you
    want to do some comparisons (ex: Utah dataset).  If this is set to
    0, then all the output will go to the path specified in the 'outdir'
    keyword.  
    5.  progress.  Set this to 1 if you want to see a progress bar.  

    Update(s):

    Notes:
    1.  Errors are written to a log in the output directory.  I may want
    to change this to write to the logs directory for the project, but
    that would require me feeding the full path of the error file, and I
    don't know if that is really necessary right now.
    """

    #check that output directory exists...
    if recursive == 0:
        dirCheck = CheckDir(outdir)    
        if dirCheck is False:
            DirWarning(outdir)

    if progress:
        bar = Bar('Transforming rasters to Geotiff', max=len(files))
 
    for infile in files:
        
        #get basename
        outbase = os.path.basename(infile)

        #strip out suffix and add tiff suffix.
        outfile = outbase.split(".")[0]+".tif" 
        
        if recursive == 1:
            outdir = os.path.dirname(infile)
            outfile = os.path.join(outdir,outfile)
        else:
            outfile = os.path.join(outdir,outfile)
        
        errorfile = os.path.join(outdir,'Transform2Tiff_errors.txt')

        if outfile:
            #need double quotes for paths with spaces!
            cmd = ['gdalwarp -co \"COMPRESS=LZW\"'
                   +' -co \"TILED=YES\" -co \"blockxsize='+str(xblock)+'\"'
                   +' -co \"blockysize='+str(yblock)+'\"'
                   +' -t_srs \"EPSG:'+str(t_srs)+'\"'+' \"'+infile+'\"'
                   +' '+'\"'+outfile+'\" 2>> \"'+errorfile+'\"']

            ipdb.set_trace()
            
            #needed the shell=True for this to work
            p = subprocess.run(cmd,shell=True,stderr=subprocess.PIPE)

            #Want to know if there is a problem...
            if (p.returncode == 1):
                print("\nProblem with the TIFF transformation for file:\n"+infile)
                print("\nCHECK ERROR LOG:\n"+errorfile+"\n when completed")
                cmd2 = ['echo "error with file:" \"'+infile+'\" >> \"'+errorfile+'\"']
                p2 = subprocess.run(cmd2,shell=True,stderr=subprocess.PIPE)

        bar.next()

    bar.finish()
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
        out_struct['PixelRes_EW'] = rasInfo['PixelRes_EW']
        out_struct['PixelRes_NS'] = rasInfo['PixelRes_NS']
        out_struct['DataType']    = rasInfo['DataType']
        out_struct['ColorType']   = rasInfo['ColorType']        

        output.append(out_struct)

    df = pd.DataFrame(output)

    return df

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
            print("Missing Vertical CRS info: "+fname)
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
def Convert2LAZ(files,pipeline,outdir='LAZ',recursive=0,progress=1):
    #reads in a pipline and executes it.  technically the pipeline could
    #be anything, but this one should just convert las to laz.
    #if recursive, write laz files to same directory as what las
    #files are in.  These could be different dirs that I will not
    #know ahead of time.

    #check that pipeline exists:
    fcheck = CheckFile(pipeline)
    if fcheck is False:
        FileWarning(pipeline)

    #check that output directory exists...
    if recursive == 0:
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

        #get basename
        outfile = os.path.basename(outfile)

        if recursive == 1:
            outdir = os.path.dirname(infile)
            outfile = os.path.join(outdir,outfile)
        else:
            outfile = os.path.join(outdir,outfile)
        
        errorfile = os.path.join(outdir,'LAS2LAZ_errors.txt')

        if outfile:
            #need double quotes for paths with spaces!
            #Added "forward" to preserve header values, Otherwise PDAL
            #updates them and I want to keep the file as close to
            #original as possible.
            cmd = ['pdal pipeline '+pipeline+
                   ' --readers.las.filename=\"'+infile+
                   '\" --writers.las.filename=\"'+outfile+
                   '\" --writers.las.forward=\"header\" 2>> \"'+errorfile+'\"']

            #needed the shell=True for this to work
            p = subprocess.run(cmd,shell=True,stderr=subprocess.PIPE)

            #Want to know if there is a problem...
            if (p.returncode == 1):
                print("\nProblem with the LAS conversion for file:\n"+infile)
                print("\nCHECK ERROR LOG:\n"+errorfile+"\n when completed")
                cmd2 = ['echo "error with file:" \"'+infile+'\" >> \"'+errorfile+'\"']
                p2 = subprocess.run(cmd2,shell=True,stderr=subprocess.PIPE)

        bar.next()

    bar.finish()
#----------------------------------------------------------------------        

#----------------------------------------------------------------------    
def AddCRS2Header(indir,pipeline,wild=r'.*[LlAaSsZz]$',verbose=1,
                  out_suffix='_wCRS.laz',overwrite=0):
    #reads in a pipline and executes it.  This module should add the CRS
    #info to the header of the files...

    #Additions:
    #- add specific output dir for this module?
    #- add verbose option.    
    
    #check that pipeline exists:
    fcheck = CheckFile(pipeline)
    if fcheck is False:
        FileWarning(pipeline)
       
    #check that directory exists:
    dirCheck = CheckDir(indir)    
    if dirCheck is False:
        DirWarning(indir)

    absPath = os.path.abspath(indir)

    #get absolute basepath without filename
    basePath = os.path.dirname(absPath)
    
    #find all LAS or LAZ files - account for case
    files = [f for f in os.listdir(absPath) if re.match(wild, f)]
    num_files = len(files)

    count=1
    for f in files:
        infile = os.path.join(absPath,f)

        if verbose:
            print('Adding CRS header to file #'
                  +str(count)+' of '+str(num_files))
        
        #check that it is a las file
        suffix = infile.split(".")[-1]

        if suffix  == 'las':            
            outfile = infile.replace('.las',out_suffix)
        elif suffix  == 'LAS':
            outfile = infile.replace('.LAS',out_suffix)           
        elif suffix  == 'LAZ':
            outfile = infile.replace('.LAZ',out_suffix)           
        elif suffix  == 'laz':
            outfile = infile.replace('.laz',out_suffix)
        else:
            print('Input file: \n'+infile+'\nhas a non-standard file suffix')
            ipdb.set_trace()
        
        if outfile:
            #abs_outfile = os.path.join(absPath,outfile)
            #abs_infile  = os.path.join(absPath,infile)
            #write errors to a file
            cmd = ['pdal pipeline '+pipeline+' --readers.las.filename=\"'
                   +infile+'\" --writers.las.filename=\"'
                   +outfile+'\" 2>> '+os.path.join(absPath,'CRSDefineErrors.txt')]
            
            #needed the shell=True for this to work
            p = subprocess.run(cmd,shell=True)#,stderr=subprocess.PIPE)

        if overwrite:
            in_suffix = suffix.lower()
            Over_out_suffix = outfile.split(".")[-1]
            Over_out_suffix = Over_out_suffix.lower()

            if in_suffix == Over_out_suffix:
                cmd2 = ['mv \"'+outfile+'\" \"'+infile+'\"']
                p2 = subprocess.run(cmd2,shell=True)

        count+=1
#----------------------------------------------------------------------        

#----------------------------------------------------------------------
def CreateBounds(indir,out_boundary,epsg,wild=r'.*[LlAaZz]$',
                 recursive=0,edge_size=50):
    #setting edge_size=10 gets a better approximation of the boundary.
    #Edge_size of 1 finds to many gaps.
    #Needed to escape asterisk to avoid getting weird errors....
    #Need extra "quotes" for paths with spaces...
    #regular expression is a pain in the ass.  This will match LAZ
    #files.  the .* matches ANY previous characters, and the $ indicates
    #that the text needs to end in LAZ or laz or any combo.  Change the
    #Zz to Ss if want las files.
    
    #check that directory exists:
    dirCheck = CheckDir(indir)    
    if dirCheck is False:
        DirWarning(indir)

    #get listing of files that match the reg expression and output a
    #list.  ireg will ignore case
    if recursive == 0:
        find_cmd = 'find \"'+indir+'\" -iregex '+wild+' -type f -maxdepth 1 -print'
    if recursive == 1:
        find_cmd = 'find \"'+indir+'\" -iregex '+wild+' -type f -print'


    p1 = subprocess.run(find_cmd,shell=True,stdout=PIPE)

    #do some error checking...
    if (len(p1.stdout) == 0) and (p1.returncode == 0):
        print('No files found in '+indir+' with wildcard: '+wild)
        ipdb.set_trace()
    elif (p1.returncode == 1):
        print('Error - Check if path exists:\n'+indir)
        ipdb.set_trace()        
    else:

        if edge_size == 0:
            cmd = [find_cmd+'|pdal tindex --tindex '+out_boundary
                   +' --stdin'
                   +' -f "ESRI Shapefile"'
                   +' --t_srs \"EPSG:'+str(epsg)+'\"']
        else:
            cmd = [find_cmd+'|pdal tindex --tindex '+out_boundary
               +' --stdin'
               +' -f "ESRI Shapefile"'
               +' --filters.hexbin.edge_size='+str(edge_size)
               +' --t_srs \"EPSG:'+str(epsg)+'\"']

        p = subprocess.run(cmd,shell=True,stderr=subprocess.PIPE)
        if (p.returncode == 1):
           print('Error Creating Boundary with PDAL..\n')
           print(p)
           ipdb.set_trace()           

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
def getFiles(indir, wild='.*[LlAaZz]$',recursive=1):
    
    #get listing of files that match the reg expression and output a
    #list.  ireg will ignore case
    if recursive == 0:
        find_cmd = 'find \"'+indir+'\" -iregex '+wild+' -type f -maxdepth 1 -print'
    if recursive == 1:
        find_cmd = 'find \"'+indir+'\" -iregex '+wild+' -type f -print'


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

    
if __name__ == "__main__":
    #initialize directories by running:
    #python3 ~/ot/dev/ot_utils.py $PWD

    #This will copy over all the necessary files and directories you
    #need for doing the ingest.
    
    if len(sys.argv) < 1:
        print("Need to specify the directory to copy files to.")
        sys.exit()
    else:
        dirBase = sys.argv[1]
        template = os.path.join(dirBase,'ingest_template.org')
        ingest_template   = os.path.join(dirBase,'ingest_template.py')
        pipeline_template = os.path.join(dirBase,'pipeline.json')

    #This will copy all the templates and set up the directory structure.
    initDirs(dirBase,template,ingest_template=ingest_template,
             pipeline_template=pipeline_template)


