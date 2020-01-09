#!/usr/bin/env python
'''
script to check today's new-scan completeness on CFMM PACS and triger the retriving/converting/processing(on graham)

This script will be run by a cron job:
*/5 8-22 * * 1-5 /home/akhan/retrieve_cfmm/cron_cmd

cron_cmd:
    /home/akhan/retrieve_cfmm/check_and_remote_retrieve.py akhanf graham.sharcnet.ca ~/.ssh/id_rsa_graham.sharcnet.ca /project/6007967/akhanf/autobids-cfmm/bin/procNewScans 2>&1 1>/dev/null | /usr/bin/logger -t "retrieve_cfmm"

algorithm:
    every 5 mins:
        pre=get PI+Today's NumberOfStudyRelatedInstances
            is pre not empty: (means there is today's new scan)
                wait 20-30 seconds
                current = get PI+Today's NumberOfStudyRelatedInstances
                if pre==current (means transfers from scanner to pacs finished!, can trigger retriving/converting/processing(on graham))
                    /usr/bin/ssh -i ~akhan/.ssh/id_rsa_graham.sharcnet.ca akhanf@graham.sharcnet.ca /project/6007967/akhanf/cfmm-bids/src/bin/procNewScans `date +'%Y%m%d'`
                    (which will retrive all today's scans, then submit jobs to convert/process)

note: findscu is dcm4che's! not dcmtk's!!
      need docker image: yinglilu/dcm4che
      (docker pull yinglilu/dcm4che:0.1)

python:2.7.13
'''

import os
import sys
import datetime
import subprocess
from os.path import expanduser
import time
import getpass

#CFMM pacs 
CONNECT='CFMM-Public@dicom.cfmm.robarts.ca:11112'
PI_MATCHING_KEY='*'


SLEEP_SEC=30 #interval checking PACS data completeness 
FNULL = open(os.devnull, 'w')

def get_today_date():
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d")

def get_NumberOfStudyRelatedInstances(username,password,matching_key):
    '''
    find StudyInstanceUID[s] by matching key

    input:
        username: UWO's username to access CFMM's PACS
        password: UWO's password to access CFMM's PACS
        matching_key: -m StudyDescription='Khan*' -m StudyDate='20171116'
        
    output:string
        StudyInstanceUID1\n
        StudyInstanceUID2\n
        ...
    '''

    #check PACS server data completeness 
    cmd = 'docker run --rm yinglilu/dcm4che:0.1 findscu'+\
          ' --bind  DEFAULT' +\
          ' --connect {}'.format(CONNECT)+\
          ' --accept-timeout 10000 '+\
          ' --tls-aes --user {} --user-pass {} '.format(username,password)+\
          ' {}'.format(matching_key) +\
          ' -r 00201208'+\
          ' |grep -i NumberOfStudyRelatedInstances |cut -d[ -f 2|cut -d] -f 1 |sed "/^$/d"'
    try:
        instances_str = subprocess.check_output(cmd,stderr=FNULL, shell=True)
    except subprocess.CalledProcessError as e:
        print 'findscu returned non-zero exit status'

    return instances_str

def have_new_scan_and_ready_for_retrieve(uwo_username,uwo_password,study_date):
    '''
    pre=get PI+Today's NumberOfStudyRelatedInstances
    if pre not empty:
        wait 20-30 seconds
        current = get PI+Today's NumberOfStudyRelatedInstances
        if pre==current (means transfer from scanner to pacs finished!)
            return True
    '''

    #get NumberOfStudyRelatedInstances
    matching_key= "-m StudyDescription='{}' -m StudyDate='{}'".format(PI_MATCHING_KEY,study_date)
    pre = get_NumberOfStudyRelatedInstances(uwo_username,uwo_password,matching_key)
    

    #print "matching key: {}".format(matching_key)
    #print "number of study related instances: {}".format(pre)

    if pre: #if not empty, means found today's study on PACS
        time.sleep(SLEEP_SEC)
        current = get_NumberOfStudyRelatedInstances(uwo_username,uwo_password,matching_key)
        if pre == current: #transfer from scanner to pacs finished, ready for retrieve
            return True
        else:
            return False
    else:
        sys.stdout.writelines('no new data to retrieve yet!\n')
        sys.stdout.flush()
        return False

def main(ssh_key_file,ssh_username,uwo_cred_id,ssh_server,ssh_script,study_date):
    
    '''
    check today's new-scan completeness(all dicoms has been sent to dicom server from scanner) on CFMM PACS and
    triger the retriving/converting/processing(on graham)

    '''

    uwo_cred_file=os.path.join(expanduser("~"), ".uwo_credentials.{}".format(uwo_cred_id))

    #print "using cred file {}".format(uwo_cred_file)
    #read uwo username and password(needed to login cfmm dicom server)

    if not os.path.exists(uwo_cred_file):
        print "credential file {} does not exist, failing..".format(uwo_cred_file)
        sys.exit(1)

    with open(uwo_cred_file) as f:
        #lines = f.readlines() #with '\n'
        lines=f.read().splitlines() #without '\n'
        
    uwo_username=lines[0]
    uwo_password=lines[1]

    #triger the retriving/converting/processing(on graham) if has todday's new scan and ready for retrieve
    if have_new_scan_and_ready_for_retrieve(uwo_username,uwo_password,study_date):
        cmd="ssh -i {} {}@{} {} {} {}".format(ssh_key_file,ssh_username,ssh_server,ssh_script,study_date,uwo_cred_id)
        #print cmd
        try:
            stdout_stderr = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            print stdout_stderr
        except subprocess.CalledProcessError as e:
            print 'findscu returned non-zero exit status'
            
    
if __name__=="__main__":

    #print ("number of args is {}".format(len(sys.argv)))
    if len(sys.argv) == 6:
        ssh_username=sys.argv[1]
        ssh_server=sys.argv[2]
	ssh_key_file=sys.argv[3]
	uwo_cred_id=sys.argv[4]
        ssh_script=sys.argv[5]
        study_date=get_today_date()
    elif len(sys.argv) == 7:
        ssh_username=sys.argv[1]
        ssh_server=sys.argv[2]
	ssh_key_file=sys.argv[3]
	uwo_cred_id=sys.argv[4]
        ssh_script=sys.argv[5]
        study_date=sys.argv[6]
    else:
        print ("Usage: python " + os.path.basename(__file__)+ " <remote user> <remote server> <ssh key> < uwo credential id > <remote script path>  [date (optional, default: today)]")
        print ("Example: python check_and_remote_retrieve.py yinglilu graham.sharcnet.ca ~/.ssh/id_rsa_graham.sharcnet.ca /project/6007967/yinglilu/autobids/bin/procNewScans 20171116")
        sys.exit(1)

    
    main(ssh_key_file,ssh_username,uwo_cred_id,ssh_server,ssh_script,study_date)
 
    ##info for test

    # #yingli's
    # ssh_username='yinglilu'
    # ssh_key_file="~/.ssh/id_rsa_graham.sharcnet.ca"

    # #ali's
    # ssh_username='akhanf'
    # ssh_key_file="~akhan/id_rsa_graham.sharcnet.ca"
      
    #-----test code
    #test proNewScans
    #ssh -i ~/.ssh/id_rsa_graham.sharcnet.ca yinglilu@graham.sharcnet.ca /project/6007967/yinglilu/autobids/bin/procNewScans 20171116

    ##test script

    #20171116 's scan
    #python check_and_remote_retrieve.py yinglilu graham.sharcnet.ca ~/.ssh/id_rsa_graham.sharcnet.ca default /project/6007967/yinglilu/autobids/bin/procNewScans 20171116

    #today's new scan - using ~/.uwo_credentials.bd 
    #python check_and_remote_retrieve.py yinglilu graham.sharcnet.ca ~/.ssh/id_rsa_graham.sharcnet.ca bd /project/6007967/yinglilu/autobids/bin/procNewScans


