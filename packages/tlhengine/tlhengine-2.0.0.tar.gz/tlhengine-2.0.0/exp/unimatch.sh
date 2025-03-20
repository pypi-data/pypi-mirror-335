set -x
if [ -d "/kaggle" ]; then
    echo "you are in kaggle"
    kaggle=true
fi


apt install tree
cd /root
mkdir exp
cd exp
mkdir unimatch
cd unimatch
git clone https://github.com/tianlianghai/UniMatch.git unimatch-code
cd unimatch-code
git pull
mkdir /root/data
cd /root/data
mkdir voc
cd voc
apt install axel
axel -c -n 8 http://host.robots.ox.ac.uk/pascal/VOC/voc2012/VOCtrainval_11-May-2012.tar -o voc.tar
extracted_file="VOCdevkit"
if [ -d "$extracted_file" ]; then
    echo "Destination directory $destination_dir already exists. Skipping extraction."
else
    tar -xf voc.tar 
fi
pip install gdown
gdown -O cls.zip 1ikrDlsai5QSf2GiSUR3f8PZUzyTubcuF
extracted_file="SegmentationClass"
if [ -d "$extracted_file" ]; then
    echo "Destination directory $destination_dir already exists. Skipping extraction."
else
    unzip -qn cls.zip
fi

ln -s /root/data/voc/VOCdevkit/VOC2012 /root/data/
cd /root/data/VOC2012
mv SegmentationClass SegmentationClassBackup
mv /root/data/voc/SegmentationClass .
cd /root/exp/unimatch/unimatch-code
pip install -r requirements.txt
mkdir pretrained
cd pretrained
gdown 1Rx0legsMolCWENpfvE2jUScT3ogalMO8
cd ..
# Use the 'kaggle' variable
if [ "$kaggle" = true ]; then
    save_prefix="/kaggle/working"
    # Add your kaggle-related commands here
    batch_size=4
else
    save_prefix=""
    batch_size=8
fi
bash scripts/dist_train.sh $save_prefix --eval-interval 10 --batch-size ${batch_size}
