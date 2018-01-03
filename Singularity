Bootstrap: docker
From: ubuntu:xenial

# dcm4che 3.3.8

#create image
#cd Dropbox/Robarts/singularites/dcm4che
#sudo singularity build ~/singularities/dcm4che.simg Singularity

#########
%setup
#########
cp ./*.sh $SINGULARITY_ROOTFS
#ln -fs /usr/share/zoneinfo/US/Pacific-New /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

#########
%post
#########
export DEBIAN_FRONTEND=noninteractive

bash 14.install_dcm4che_ubuntu.sh /opt

#remove all install scripts
#rm *.sh


#########
%environment

#export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

#anaconda2
export PATH=/opt/anaconda2/bin/:$PATH

#dcm4che
export PATH=/opt/dcm4che-3.3.8/bin:$PATH

#########
#fix error if run the image on graham:
#Error occurred during initialization of VM
#java.lang.OutOfMemoryError: unable to create new native thread

export _JAVA_OPTIONS="-Xmx4048m"
