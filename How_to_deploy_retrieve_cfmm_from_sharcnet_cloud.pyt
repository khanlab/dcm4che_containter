deploy retrieve_cfmm_from_sharcnet_cloud.py

	0.check timezone, if not consisitent with cfmm:
		sudo timedatectl set-timezone EST
	1.docker pull yinglilu/dcm4che:0.1
	2.copy retrieve_cfmm_from_sharcnet_cloud.py to ~ (or to /usr/local/bin)
	3.create ~/.uwo_credentials(two lines):
		username
		password
	4.create password-less ssh login to graham (for instance,akhanf@graham.sharcnet.ca)
	5.create cron 
	   */5 * * * * /usr/bin/python /usr/local/bin/retrieve_cfmm_from_sharcnet_cloud.py yinglilu '~/.ssh/id_rsa_graham.sharcnet.ca' 2>&1 1>/dev/null | /usr/bin/logger -t "retrieve_cfmm"
	