# -*- coding: utf-8 -*-

"""
Given a local folder, path to remote folder, path to config and aterm files, check offline status and checksum for every file.

Change log:
v0.13.4 list problem if offline gives an IndexError and file isn't empty as expected
v0.13.3 catch IndexError exceptions with remote_crc
v0.13.2 fix counts
v0.13.1 Add --verbose flag to add full error messages to logs
v0.13.0 Add summary numbers for each error type
v0.12.2 fix bug with local file not found
v0.12.1 fix bug with crc32
v0.12 add try excepts around all os commands
v0.11 bug fix path_subtract with trailing slash. Added commands to unexpected error messages.
v0.10 add option for time since expected last backup, added appendIssue() function, made all file exceptions write to file and continue
v0.9 add checks for java, python  v2.7.5, improve error message for checksums.
v0.8.1 allow folder to be relative
v0.8 try to use rhash -c or cksum -o 3 if crc32 command is not available.
v0.7 fixed comparison of checksums of empty files, set offline status of empty files to true
v0.6.2 fixed backslash fix breaking escaping of quotes
v0.6.1 fixed escaping for backslashes in remote folder exists check
v0.6 added escaping for backslashes
v0.5 check if filename causes aterm.jar to crash, add error messages to output log, escape quotes, improve quoting of filenames
v0.4 add local files with permission issues to log
v0.3 added explicit connection test, fixed path joining for offline check command
v0.2 added explicit checks for all assumptions about inputs
  - folder starts with path subtract
  - folder exists
  - rdmp_id has a 'D' then 7 digits
  - config_path exists and contains both config.cfg and aterm.jar
  - remote folder exists
v0.1 added spaces in outputs, --path_add option

Known issues:
False positives that I can't replicate in smaller examples
   'file not found on archive'
   'filename caused data archive script to crash' 

TODO:
do sanity checking of crc results?
add Archive::Zip module for Perl option? See man crc32
add other date options?
  specific date and time?
  most recent Saturday midnight?
warn if prefix exists?
warn if prefix contains weird characters?
check dates/sizes too?
get actual error messages from aterm.jar?
"""

import subprocess
import os
import re
import sys
import platform
from datetime import timedelta
import time

def addToDic(issue, dic):
    if issue in dic:
        dic[issue] += 1
    else:
        dic[issue] = 1

def appendIssue(issue, new_files, old_files, new, new_dict, old_dict):
    short_issue = issue.split(': ', 1)[1].split('.', 1)[0]
    if new:
        new_files.append(issue)
        addToDic(short_issue, new_dict)
    else:
        old_files.append(issue)
        addToDic(short_issue, old_dict)
    return new_files, old_files

def appendMessage(verbose, log, log_message, err, err_desc):
    if verbose:
        err = '. ' + err_desc + ": {0}".format(err.output).rstrip()
        log_message += err
    log.append(log_message + '\n')
    return log

def main(prefix, folder, rdmp_id, config_path, path_subtract, path_add, days_since_backup, verbose):
    ## Check output file can be written to
    try:
        with open(prefix + '.tdt', 'w') as f:
            f.write('')
    except IOError as err:
        print("Error: {0}".format(err))
        exit()
    ## Check python version
    if sys.version_info[0] == 2:
        if sys.version_info[1] < 7 or (sys.version_info[1] == 7 and sys.version_info[2] < 5):
            err = 'Error: Your python version needs to be at least v2.7.5. It is only: v' + platform.python_version() + '. If you are trying to run this on kdm.science.unsw.edu.au, try kdm.restech.unsw.edu.au instead.'
            print(err)
            with open(prefix + '.tdt', 'w') as f:
                f.write(err + '\n')
            exit()
    ## Check java installation
    cmd = 'java -version'
    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        err = 'Error: Java is not installed. If running on kdm.restech.unsw.edu.au, try running "module add unswdataarchive"'
        print(err)
        with open(prefix + '.tdt', 'w') as f:
            f.write(err + '\n')
        exit()
    ## Check folder exists
    if not os.path.isdir(folder):
        err = 'Error: "' + folder + '" is not an existing folder'
        print(err)
        with open(prefix + '.tdt', 'w') as f:
            f.write(err + '\n')
        exit()
    ##Check path_subtract is a prefix of folder
    ##Add a trailing slash so a trailing slash in path_subtract doesn't cause an issue
    folder_abs = os.path.join(os.path.abspath(folder), '')
    if not folder_abs.startswith(path_subtract):
        err = 'Error: --path_subtract value "' + path_subtract + '" is not a prefix of folder "' + folder_abs + '"'
        print(err)
        with open(prefix + '.tdt', 'w') as f:
            f.write(err + '\n')
            exit()
    ##Check RDMP ID is well formed
    if not re.match('D\d{7}', rdmp_id) != None:
        err = 'Error: "' + rdmp_id + '" is not a well formed RDMP ID. It needs to be a "D" followed by seven digits.'
        print(err)
        with open(prefix + '.tdt', 'w') as f:
            f.write(err + '\n')
            exit()
    ## Check config_path exists
    if not os.path.isdir(config_path):
        err = 'Error: "' + config_path + '" is not an existing folder'
        print(err)
        with open(prefix + '.tdt', 'w') as f:
            f.write(err + '\n')
        exit()
    ## Check aterm.jar is in config_path
    if not os.path.isfile(os.path.join(config_path, 'aterm.jar')):
        err = 'Error: the required aterm.jar file is not present in the folder "' + config_path + '"'
        print(err)
        with open(prefix + '.tdt', 'w') as f:
            f.write(err + '\n')
        exit()
    ## Check config.cfg is in config_path
    if not os.path.isfile(os.path.join(config_path, 'config.cfg')):
        err = 'Error: the required config.cfg file is not present in the folder "' + config_path + '"'
        print(err)
        with open(prefix + '.tdt', 'w') as f:
            f.write(err + '\n')
        exit()
    ## Check aterm.jar permissions
    if not os.access(os.path.join(config_path, 'aterm.jar'), os.R_OK):
        err = 'Error: permission denied to read required aterm.jar file'
        print(err)
        with open(prefix + '.tdt', 'w') as f:
            f.write(err + '\n')
        exit()
    ## Check config.cfg permissions
    if not os.access(os.path.join(config_path, 'config.cfg'), os.R_OK):
        err = 'Error: permission denied to read required config.cfg file'
        print(err)
        with open(prefix + '.tdt', 'w') as f:
            f.write(err + '\n')
        exit()
    ## Check crc32 or equivalent works
    crc_command = 'crc32'
    cmd = crc_command + ' "' + os.path.join(config_path, 'config.cfg') + '"'
    try:
        local_crc = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError:
        crc_command = 'rhash -C'
        cmd = crc_command + ' "' + os.path.join(config_path, 'config.cfg') + '"'
        try:
            local_crc = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            crc_command = 'cksum -o 3'
            cmd = crc_command + ' "' + os.path.join(config_path, 'config.cfg') + '"'
            try:
                local_crc = subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError:
                err = 'Error: "crc32", "rhash -C" and "cksum -o 3" commands all return non-zero exit status. If running on katana, try kdm.restech.unsw.edu.au instead.'
                print(err)
                with open(prefix + '.tdt', 'w') as f:
                    f.write(err + '\n')
                exit()
    ## Check remote connection
    cmd = 'java -Dmf.cfg=' + os.path.join(config_path, 'config.cfg') + ' -jar ' + os.path.join(config_path, 'aterm.jar') + ' nogui asset.namespace.exists :namespace "/"'
    try:
        connected = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).rsplit(' ', 1)[1].rstrip()
    except subprocess.CalledProcessError:
        connected = '"false"'
    if connected != '"true"':
        err = 'Error: Could not connect to UNSW Research Data Store. config.cfg must contain the appropriate password or token. Try running: \'' + cmd + '\''
        print(err)
        with open(prefix + '.tdt', 'w') as f:
            f.write(err + '\n')
        exit()
    ## Check remote folder exists
    remote_path = '/UNSW_RDS/' + rdmp_id + '/' + path_add + '/' + folder_abs.replace(path_subtract, '')
    remote_path = remote_path.replace('\\', '\\\\').replace('"', '\\"').replace("'", "'\"'\"'")
    cmd = 'java -Dmf.cfg=' + os.path.join(config_path, 'config.cfg') + ' -jar ' + os.path.join(config_path, 'aterm.jar') + ' nogui asset.namespace.exists :namespace \'' + remote_path + '\''
    try:
        exists = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).rsplit(' ', 1)[1].rstrip()
    except subprocess.CalledProcessError:
        exists = '"false"'
    if exists != '"true"':
        err = 'Error: The namespace "' + remote_path + '" does not exist on UNSW Research Data Store. You may need to check your settings of --rdmp_id, --path_subtract and --path_add. Alternatively, this folder may not have been backed up at all yet.'
        print(err)
        with open(prefix + '.tdt', 'w') as f:
            f.write(err + '\n')
        exit()
    ## Check days_since_backup isn't too big
    try:
        timedelta(days_since_backup)
    except OverflowError as err:
        err = "Error: Problem with --days_since_backup: {0}".format(err)
        print(err)
        with open(prefix + '.tdt', 'w') as f:
            f.write(err + '\n')
        exit()
    ## Check files
    passed_counter = 0
    fail_counter = 0
    new_files = []
    old_files = []
    problem_files = []
    new_dict = {}
    old_dict = {}
    problem_dict = {}
    for root, subfolders, files in os.walk(folder_abs):
        path = root.replace(path_subtract, '')
        for filename in files:
            remote_path = '/UNSW_RDS/' + rdmp_id + '/' + path_add + '/' + path + '/' + filename
            remote_path = remote_path.replace('\\', '\\\\').replace('"', '\\"').replace("'", "'\"'\"'")
            ##Note: asset.namespace.exists should technically only be used on folders
            cmd = 'java -Dmf.cfg=' + os.path.join(config_path, 'config.cfg') + ' -jar ' + os.path.join(config_path, 'aterm.jar') + ' nogui asset.namespace.exists :namespace \'' + remote_path + '\''
            #print(cmd)
            try:
                exists = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as err1:
                fail_counter += 1
                local_path = os.path.join(root, filename)
                err2 = ''
                try:
                    file_age = time.ctime(os.path.getmtime(local_path))
                except OSError as err2:
                    err2 = "Error with local file: {0}".format(err2)
                    print(err2)
                    file_age = 'unknown'
                log_message = local_path + ': filename caused data archive script to crash. Does it contain non-standard characters? Try running ' + cmd + ' File was last modified on: ' + file_age + err2
                problem_files = appendMessage(verbose, problem_files, log_message, err1, "Remote file error")
                addToDic("filename caused data archive script to crash", problem_dict)
            else:
                local_path = os.path.join(root, filename)
                try:
                    new = timedelta(seconds=time.time() - os.path.getmtime(local_path)) < timedelta(days_since_backup)
                    file_age = time.ctime(os.path.getmtime(local_path))
                except OSError as err:
                    fail_counter += 1
                    err = "Error with local file: {0}".format(err)
                    print(err)
                    file_age = 'unknown'
                    problem_files.append(local_path + ': ' + err + ' File was last modified on: unknown.\n')
                    addToDic("checking age of local file failed", problem_dict)
                else:
                    cmd = 'java -Dmf.cfg=' + os.path.join(config_path, 'config.cfg') + ' -jar ' + os.path.join(config_path, 'aterm.jar') + ' nogui asset.get :id path=\'' + remote_path + '\' :xpath "content/csum"'
                    try:
                        remote_crc_output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                        remote_crc = remote_crc_output.split('"')[1].upper()
                    except subprocess.CalledProcessError as err:
                        fail_counter += 1
                        log_message = local_path + ': file not found on archive. File was last modified on: ' + file_age
                        if verbose:
                            err = ". Remote file error: {0}".format(err.output).rstrip()
                            log_message += err
                        new_files, old_files = appendIssue(log_message + '. \n', new_files, old_files, new, new_dict, old_dict)
                    except IndexError as err:
                        fail_counter += 1
                        log_message = local_path + ': unexpected output for remote checksum. File was last modified on: ' + file_age
                        problem_files = appendMessage(verbose, problem_files, log_message, err + ' ' + remote_crc_output, "Remote checksum processing error")
                        addToDic("unexpected output for remote checksum", problem_dict)
                    else:
                        if not os.access(local_path, os.R_OK):
                            fail_counter += 1
                            problem_files.append(local_path + ': permission denied for local copy. File was last modified on: ' + file_age + '\n')
                            addToDic("permission denied for local copy", problem_dict)
                        else:
                            #print('remote_crc = ', remote_crc)
                            cmd = crc_command + ' \'' + local_path.replace("'", "'\"'\"'") + '\''
                            try:
                                if crc_command == 'cksum -o 3':
                                    local_crc = hex(int(subprocess.check_output(cmd, shell=True).split(' ')[0])).rsplit('x')[-1].upper()
                                elif crc_command == 'crc32':
                                    local_crc = subprocess.check_output(cmd, shell=True).rstrip().upper().split('\t', 1)[0]
                                else:
                                    local_crc = subprocess.check_output(cmd, shell=True).rstrip().upper().rsplit(' ', 1)[-1]
                            except subprocess.CalledProcessError as err:
                                ## Checks should prevent this occuring
                                fail_counter += 1
                                issue = "calling " + crc_command + " on " + local_path + " failed. Try running: " + cmd
                                print("Warning: " + issue)
                                log_message = issue + ' File was last modified on: ' + file_age
                                problem_files = appendMessage(verbose, problem_files, log_message, err, "Local checksum error")
                                addToDic("calling " + crc_command + " failed", problem_dict)
                            else:
                                #print('local_crc = ', local_crc)
                                if remote_crc != local_crc and remote_crc != local_crc.lstrip('0') and remote_crc != '0' + local_crc.lstrip('0'):
                                    fail_counter += 1
                                    new_files, old_files = appendIssue(local_path + ': file checksum does not match. File was last modified on: ' + file_age + '\n', new_files, old_files, new, new_dict, old_dict)
                                else:
                                    cmd = 'java -Dmf.cfg=' + os.path.join(config_path, 'config.cfg') + ' -jar ' + os.path.join(config_path, 'aterm.jar') + ' nogui asset.get :id path=\'' + remote_path + '\''
                                    #print('cmd =', cmd)
                                    try:
                                        offline_output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                                        offline = offline_output.split('committed-to-tape')[1].strip(' "\n')
                                    except subprocess.CalledProcessError as err:
                                        ## Checks should prevent this occuring
                                        fail_counter += 1
                                        issue = "checking offline status of " + local_path + " failed. Try running: " + cmd
                                        print("Warning: " + issue)
                                        log_message = issue + ' File was last modified on: ' + file_age
                                        problem_files = appendMessage(verbose, problem_files, log_message, err, "Remote file error")
                                        addToDic("checking offline status failed", problem_dict)
                                        continue
                                    except IndexError as err:
                                        ## Empty files are never committed to tape and do not have a committed-to-tape label in their metadata
                                        if remote_crc == '0':
                                            offline = 'true'
                                        else:
                                            ## No known reason for this to occur
                                            fail_counter += 1
                                            issue = "processing offline status of " + local_path + " failed. Try running: " + cmd
                                            print("Warning: " + issue)
                                            log_message = issue + ' File was last modified on: ' + file_age
                                            problem_files = appendMessage(verbose, problem_files, log_message, err + ' ' + offline_output, "Error processing offline status")
                                            addToDic("processing offline status failed", problem_dict)
                                            continue
                                    #print('offline =', offline)
                                    if offline == 'true':
                                        passed_counter += 1
                                    else:
                                        fail_counter += 1
                                        new_files, old_files = appendIssue(local_path + ': file not offline. File was last modified on: ' + file_age + '\n', new_files, old_files, new, new_dict, old_dict)
    with open(prefix + '.tdt', 'w') as f:
        f.write('### Files that might have been created or changed since last backup ###\n')
        for issue in new_files:
            f.write(issue)
        f.write('\n### Files that should be backed up based on age since last change ###\n')
        for issue in old_files:
            f.write(issue)
        f.write('\n### Files with other issues ###\n')
        for issue in problem_files:
            f.write(issue)
        f.write('\n### Summary ###\n')
        f.write(str(passed_counter) + ' files are backed up offline and OK to delete.\n')
        f.write(str(fail_counter) + ' files are NOT backed up offline and NOT OK to delete.\n')
        if len(new_dict) >= 1:
            f.write('\tRecently changed files:\n')
            for issue in new_dict:
                f.write('\t\t' + issue + ': ' + str(new_dict[issue]) + '\n')
        if len(old_dict) >= 1:
            f.write('\tOlder files:\n')
            for issue in old_dict:
                f.write('\t\t' + issue + ': ' + str(old_dict[issue]) + '\n')
        if len(problem_dict) >= 1:
            f.write('\tProblem files:\n')
            for issue in problem_dict:
                f.write('\t\t' + issue + ': ' + str(problem_dict[issue]) + '\n')
        if fail_counter == 0:
            f.write('Folder ' + folder_abs + ' is backed up and safe to delete.\n')
        else:
            f.write('Folder ' + folder_abs + ' is NOT backed up and NOT safe to delete.\n')

if __name__ == "__main__":
    from optparse import OptionParser
    usage = "usage: python check_archived.py prefix folder"
    parser = OptionParser(usage)
    parser.add_option("--rdmp_id", action="store", type="str", dest="rdmp_id", help="Research Data Management Plan ID, default='D0235810'", default='D0235810')
    parser.add_option("--config_path", action="store", type="str", dest="config_path", help="Location of config.cfg and aterm.jar, default='/Users/rna/PROGRAMS/RDS_SYNC/2017-02-06/'", default='/Users/rna/PROGRAMS/RDS_SYNC/2017-02-06/')
    parser.add_option("--path_subtract", action="store", type="str", dest="path_subtract", help="Prefix of local path to subtract from remote path, default='/Volumes/Data1/'", default='/Volumes/Data1/')
    parser.add_option("--path_add", action="store", type="str", dest="path_add", help="Infix to add to remote path after RDMP ID e.g. 'projects', default=''", default='')
    parser.add_option("--days_since_backup", action="store", type="float", dest="days_since_backup", help="Estimate of the number of days since last back up, default=7", default=7)
    parser.add_option("--verbose", action="store_true", dest="verbose", help="Add full error messages to output", default=False)
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error(usage)
    main(args[0], args[1], options.rdmp_id, options.config_path, options.path_subtract, options.path_add, options.days_since_backup, options.verbose)
