#!/usr/bin/python
"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: A module to Create a ZIP file on disk and transmit it in chunks of 8KB,
    without loading the whole file into memory.
"""

import os
import tempfile, zipfile
import argparse
from util import get_genus

def zipFilesFromFolders(dirName = None, multiTuple = []):
    '''
    @deprecated
    @param dirName: any folder
    '''
    temp = tempfile.TemporaryFile()
    myzip = zipfile.ZipFile(temp ,'w', zipfile.ZIP_DEFLATED)

    if (multiTuple):
        for dirName in multiTuple:
            if dirName[0] != '.': # ignore metadata
                dirName = os.path.join(multiTuple, dirName)
                filesInOutputDir = os.listdir(dirName)

                for thefolder in filesInOutputDir:
                    if thefolder[0] != '.': # ignore metadata
                        dataProdDir = os.path.join(dirName, thefolder)
                        for thefile in os.listdir(dataProdDir):
                            filename =  os.path.join(dataProdDir, thefile)
                            myzip.write(filename, thefile) # second param of write determines name output
                            print "Compressing: " + thefile
        myzip.close()
        return temp


    filesInOutputDir = os.listdir(dirName)

    for thefolder in filesInOutputDir:
        if thefolder[0] != '.': # ignore metadata
            dataProdDir = os.path.join(dirName, thefolder)
            for thefile in os.listdir(dataProdDir):
                filename =  os.path.join(dataProdDir, thefile)
                myzip.write(filename, thefile) # second param of write determines name output
                print "Compressing: " + thefile

    myzip.close()
    return temp

def zipup(directory, zip_file, todisk=None):
    '''
    Write a zipfile from a directory

    @param dir: the path to directory to be zipped
    @type dir: string

    @param zip_file: name of zip file
    @type zip_file: string

    @param todisk: specify path if you want the zip written to disk as well
    @type todisk: string
    '''
    zip_file = tempfile.TemporaryFile()

    zipf = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED)
    root_len = len(os.path.abspath(directory))
    for root, dirs, files in os.walk(directory):
        archive_root = os.path.abspath(root)[root_len:] # = archive_root = os.path.basename(root)
        for f in files:
            fullpath = os.path.join(root, f)
            archive_name = os.path.join(archive_root, f)
            print "Compressing: " + f
            zipf.write(fullpath, archive_name, zipfile.ZIP_DEFLATED) # (from, to_in_archive, format)
    zipf.close()
    return zip_file

def zipfiles(files, zip_out_fn, use_genus, todisk=None):
    '''
    Write a zipfile from a list of files

    @param zip_out_fn: the output file name
    @type dir: string

    @param zip_file: name of zip file
    @type zip_file: string

    @param use_genus: use the genus at the zipfile directory name
    @type use_genus: bool

    @param todisk: specify path if you want the zip written to disk as well
    @type todisk: string
    '''
    zip_file = tempfile.TemporaryFile()

    zipf = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED)
    for fn in files:
      print "Compressing %s ..." % fn
      archive_name = fn if not use_genus else fn[fn.rfind(get_genus(fn)):]
      zipf.write(os.path.abspath(fn), archive_name, zipfile.ZIP_DEFLATED)
    zipf.close()
    return zip_file

def unzip( zfilename, saveToDir ):
    '''
    Recursively unzip a zipped folder

    @param zfilename: full filename of the zipfile
    @type zfilename: string

    @param saveToDir: the save location
    @type saveToDir: string
    '''
    # open the zipped file
    zfile = zipfile.ZipFile( zfilename, "r" )

    # get each archived file and process the decompressed data
    for info in zfile.infolist():
        fname = info.filename
        # decompress each file's data
        if os.path.splitext(fname)[1]:
            data = zfile.read(fname)

            # save the decompressed data to a new file
            filename = os.path.join(saveToDir, fname.split('/')[-1])
            fout = open(filename, "w")
            fout.write(data)
            fout.close()
            print "New file created --> %s" % filename
        else:
           print "Folder ignored --> %s" % fname

  # Do not return file names here!


if __name__ == '__main__':
    main()

def main():

    parser = argparse.ArgumentParser(description='Zip the contents of an entire directory & place contents in single zip File')
    parser.add_argument('dirName', action='store')
    parser.add_argument('--multiTuple', action='store')

    result = parser.parse_args()

    zipFilesFromFolders(result.dirName, result.multiTuple)

if __name__ == '__main__':
    main()
