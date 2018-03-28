import ftplib
import os
import argparse
from socket import error as socket_error

"""
MIT license: 2017 - Jwely
Example usage:
``` python
import ftplib
ftp = ftplib.FTP(mysite, username, password)
download_ftp_tree(ftp, remote_dir, local_dir)
```
The code above will look for a directory called "remote_dir" on the ftp host, and then duplicate the
directory and its entire contents into the "local_dir"
"""
def escapechars(seqchar):
    return seqchar.replace("[","\\[").replace("]","\\]")
    

def _is_ftp_dir(ftp_handle, name, guess_by_extension=True):
    """ simply determines if an item listed on the ftp server is a valid directory or not """

    # if the name has a "." in the fourth to last position, its probably a file extension
    # this is MUCH faster than trying to set every file to a working directory, and will work 99% of time.
    if guess_by_extension is True:
        if len(name) >= 4:
            if name[-4] == '.':
                return False

    original_cwd = ftp_handle.pwd()     # remember the current working directory
    try:
        ftp_handle.cwd(name)            # try to set directory to new name
        ftp_handle.cwd(original_cwd)    # set it back to what it was
        return True
    except:
        return False

def _make_parent_dir(fpath):
    """ ensures the parent directory of a filepath exists """
    dirname = os.path.dirname(fpath)
    #print '_make_parent_dir fpath=' + fpath
    #while not os.path.exists(dirname):
    try:
        os.makedirs(dirname)
        print("created {0}".format(dirname))
    except:
        #print "_make_parent_dir exception dirname="+dirname
        return
            #_make_parent_dir(dirname)



def _download_ftp_file(ftp_handle, name, dest, overwrite):
    """ downloads a single file from an ftp server """
    _make_parent_dir(dest.lstrip("/"))
    if not os.path.exists(dest) or overwrite is True:
        print '_download_ftp_file name=' + name + ' to dest=' + dest 
        try:
            with open(dest, 'wb') as f:
                ftp_handle.retrbinary("RETR {0}".format(name), f.write)
            print("downloaded: {0}".format(dest))
        except:
            print("FAILED: {0}".format(dest))
    else:
        print("already exists: {0}".format(dest))


def _mirror_ftp_dir(ftp_handle, path, overwrite, guess_by_extension):
    """ replicates a directory on an ftp server recursively """
    #print 'current dir ' + path
    items=ftp_handle.nlst(escapechars(path))[2:]
    if len(items)==0:
        print "WARN folder",path,"is empty"
    for item in items:
        try:
            item = os.path.join(path,item)
            if _is_ftp_dir(ftp_handle, item, guess_by_extension):
                _mirror_ftp_dir(ftp_handle, item, overwrite, guess_by_extension)
            else:
                _download_ftp_file(ftp_handle, item, item, overwrite)
        except socket_error as se:
            print "ERROR Socket error exception caught:",se,"=> Retry",item


def download_ftp_tree(ftp_handle, path, destination, overwrite=False, guess_by_extension=True):
    """
    Downloads an entire directory tree from an ftp server to the local destination
    :param ftp_handle: an authenticated ftplib.FTP instance
    :param path: the folder on the ftp server to download
    :param destination: the local directory to store the copied folder
    :param overwrite: set to True to force re-download of all files, even if they appear to exist already
    :param guess_by_extension: It takes a while to explicitly check if every item is a directory or a file.
        if this flag is set to True, it will assume any file ending with a three character extension ".???" is
        a file and not a directory. Set to False if some folders may have a "." in their names -4th position.
    """

    #path = path.lstrip("/")

    ftppath , startfolder = os.path.split(path)
    original_directory = os.getcwd()    # remember working directory before function is executed
    os.chdir(destination)               # change working directory to ftp mirror directory
    ftp_handle.cwd(ftppath);
    _mirror_ftp_dir(ftp_handle, startfolder, overwrite, guess_by_extension)
    os.chdir(original_directory)        # reset working directory to what it was before function exec



# play around here
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="ftpmirror")
    parser.add_argument("-s","--server",help="ftp server host name or ip", required=True)
    parser.add_argument("-r","--remote",help="remote folder source path", required=True)
    parser.add_argument("-l","--local",help="local destination path", required=True)
    parser.add_argument("-u","--user",help="ftp user", required=True)
    parser.add_argument("-p","--password",help="ftp password", required=True)
    parser.add_argument("-o","--override",help="force override folders/files")
    parser.add_argument("-g","--guessbyext",help="guess if folder or file with extension")
    
    cmdargs = parser.parse_args()
    mysite = cmdargs.server
    username = cmdargs.user
    password = cmdargs.password
    remote_dir = cmdargs.remote
    local_dir = cmdargs.local
    override=cmdargs.override is not None 
    guessbyext=cmdargs.guessbyext is not None
    ftp = ftplib.FTP(mysite, username, password)
    ftp.encoding='utf-8'
    download_ftp_tree(ftp, remote_dir, local_dir,override,guessbyext)