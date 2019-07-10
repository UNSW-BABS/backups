# Check archived
Confirm that files are backed up to UNSW's Data Archive and offline

Not yet for general use. Please tell me if you intend to try using it.

##Requirements

python 2.7.5+ or maybe older. Python 2.6.6 (default on old katana and old kdm) is insufficient. Could presumably be made Python3 compatible with easily.
crc32 command or cksum -o3 (note: cksum may not have this option) or rhash (on kdm.restech)
config.cfg must contain an appropriate password or token
java. (Note: load using the unswdataarchive on kdm.restech.)
Note: All options will need to be configured for use on a different computer with a different RDMP project. 

A copy of aterm.jar is attached to this page (in case you don't have it already). Use config.cfg used for uploading. Alternatively, run /share/apps/unswdataarchive/2015-09-10/script.zip from KDM on any other Linux, Windows or Mac computer than KDM to get your own copies.

##Usage 

python check_archived.py prefix folder

Options:
 -h, --help            show this help message and exit
 --rdmp_id=RDMP_ID     Research Data Management Plan ID, default='D0235810'
 --config_path=CONFIG_PATH
                       Location of config.cfg and aterm.jar,
                       default='/Users/rna/PROGRAMS/RDS_SYNC/2017-02-06/'
 --path_subtract=PATH_SUBTRACT
                       Prefix of local path to subtract from remote path,
                       default='/Volumes/Data1/'
 --path_add=PATH_ADD   Infix to add to remote path after RDMP ID e.g.
                       'projects', default=''
 --days_since_backup=DAYS_SINCE_BACKUP
                       Estimate of the number of days since last back up,
                       default=7
--verbose             Add full error messages to output
