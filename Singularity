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
mkdir -p $SINGULARITY_ROOTFS/opt/retrieve_cfmm
cp ./*.py $SINGULARITY_ROOTFS/opt/retrieve_cfmm

#########
%post
#########
export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get install -y --no-install-recommends apt-utils \
    sudo \
    git \
    wget \
    curl \
    zip \
    unzip \
    python2.7 \
    python-pip \
    rsync \
    openssh-client

pip install -U pip setuptools

#install pydicom
mkdir /opt/pydicom
cd /opt/pydicom
git clone https://www.github.com/pydicom/pydicom.git
cd pydicom
python setup.py install


#needed when install dcm4che
apt-get install -y default-jre

cd /
bash 14.install_dcm4che_ubuntu.sh /opt


#########
%environment

#export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

#anaconda2
export PATH=/opt/anaconda2/bin/:$PATH

#dcm4che
export PATH=/opt/dcm4che-3.3.8/bin:$PATH

#python scripts
export PATH=/opt/retrieve_cfmm:$PATH

#########
#fix error if run the image on graham:
#Error occurred during initialization of VM
#java.lang.OutOfMemoryError: unable to create new native thread

export _JAVA_OPTIONS="-Xmx4048m"

%runscript
exec python /opt/retrieve_cfmm/retrieve_cfmm_tgz.py $@
