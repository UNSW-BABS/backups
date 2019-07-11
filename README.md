# Check archived
Confirm that files are backed up to UNSW's Data Archive and offline

Not yet for general use. Please tell me if you intend to try using it.

## Requirements

* python 2.7.5+ or maybe older. Python 2.6.6 (default on old katana and old kdm) is insufficient. Could presumably be made Python3 compatible with easily.
* crc32 command or cksum -o3 (note: cksum may not have this option) or rhash (on kdm.restech)
* config.cfg must contain an appropriate password or token
* java. (Note: load using the unswdataarchive on kdm.restech.)

Note: All options will need to be configured for use on a different computer with a different RDMP project. 

A copy of aterm.jar is attached to this page (in case you don't have it already). Use config.cfg used for uploading. Alternatively, run /share/apps/unswdataarchive/2015-09-10/script.zip from KDM on any other Linux, Windows or Mac computer than KDM to get your own copies.

## Usage 

```
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
```
## Change Log

v0.13.3 catch IndexError exceptions with remote_crc<br/>
v0.13.2 fix counts<br/>
v0.13.1 Add --verbose flag to add full error messages to logs<br/>
v0.13.0 Add summary numbers for each error type<br/>
v0.12.2 fix bug with local file not found<br/>
v0.12.1 fix bug with crc32<br/>
v0.12 add try excepts around all os commands<br/>
v0.11 bug fix path_subtract with trailing slash. Added commands to unexpected error messages.<br/>
v0.10 add option for time since expected last backup, added appendIssue() function, made all file exceptions write to file and continue<br/>
v0.9 add checks for java, python  v2.7.5, improve error message for checksums.<br/>
v0.8.1 allow folder to be relative<br/>
v0.8 try to use rhash -c or cksum -o 3 if crc32 command is not available.<br/>
v0.7 fixed comparison of checksums of empty files, set offline status of empty files to true<br/>
v0.6.2 fixed backslash fix breaking escaping of quotes<br/>
v0.6.1 fixed escaping for backslashes in remote folder exists check<br/>
v0.6 added escaping for backslashes<br/>
v0.5 check if filename causes aterm.jar to crash, add error messages to output log, escape quotes, improve quoting of filenames<br/>
v0.4 add local files with permission issues to log<br/>
v0.3 added explicit connection test, fixed path joining for offline check command<br/>
v0.2 added explicit checks for all assumptions about inputs<br/>
    - folder starts with path subtract<br/>
    - folder exists<br/>
    - rdmp_id has a 'D' then 7 digits<br/>
    - config_path exists and contains both config.cfg and aterm.jar<br/>
    - remote folder exists<br/>
v0.1 added spaces in outputs, --path_add option<br/>
