# QMDIS Post Processor Full

An Arabic dialect identification "post processor" after full result of the kaldi-gstreamer-server

This project is a part of QMDIS "QCRI-MIT Advanced Dialect Identification" system. The purpose of the system is to identify between five Arabic dialects, namely Egyptian Arabic, Levantine Arabic, Gulf Arabic, North African Arabic and Modern Standard Arabic (or MSA). 

This project is just the post processor script that is called after the full transcript result of the ASR system. You need to install Kaldi ASR and the its Gstreamer server first before you can use it.  

Server Hardware Specs of https://dialectid.qcri.org/
---------------------
Architecture:          x86_64  
CPU op-mode(s):        32-bit, 64-bit  
Byte Order:            Little Endian  
CPU(s):                16  
Memory:                64 GiB   
On-line CPU(s) list:   0-15  
Thread(s) per core:    2  
Core(s) per socket:    8  
Socket(s):             1  
NUMA node(s):          1  
Vendor ID:             GenuineIntel  
CPU family:            6  
Model:                 63  
Model name:            Intel(R) Xeon(R) CPU E5-2673 v3 @ 2.40GHz  
Stepping:              2  
CPU MHz:               2394.452  
BogoMIPS:              4788.90  
Virtualization:        VT-x  
Hypervisor vendor:     Microsoft  
Virtualization type:   full  
L1d cache:             32K  
L1i cache:             32K  
L2 cache:              256K  
L3 cache:              30720K  
NUMA node0 CPU(s):     0-15  
Flags:                 fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx pdpe1gb rdtscp lm constant_tsc rep_good nopl xtopology cpuid pni pclmulqdq vmx ssse3 fma cx16 sse4_1 sse4_2 movbe popcnt aes xsave avx f16c rdrand hypervisor lahf_lm abm pti tpr_shadow vnmi ept vpid fsgsbase bmi1 avx2 smep bmi2 erms xsaveopt


Installation
------------

### Requirment
*NB!*: Please don't use anaconda to install the ASR becasue bindings for gobject-introspection libraries will not be installed in its site-packages.

*NB!*: If you want to use virtual environment it is recommended to create it with --system-site-packages flag so that it can use Python bindings

*NB!*: The server doesn't work quite correctly with ws4py 0.3.5 because of a bug that has been reported here: https://github.com/Lawouach/WebSocket-for-Python/issues/152.
* Python 2.7
* In addition, you need Python 2.x bindings for gobject-introspection libraries, provided by the `python-gi`
package on Debian and Ubuntu.
* Tornado 
* ws4py (0.3.0 .. 0.3.2)
* YAML
* JSON


```bash
sudo apt-get update
sudo apt install python-pip
sudo -H pip install -U pip
sudo -H pip install virtualenv
sudo apt install python-gobject
sudo apt install python-dbus
```

```bash
virtualenv --system-site-packages <your_env_name> -p <path/to/python2.7>
source <path/to/your/env>/bin/activate

[sudo -H] pip install tornado
[sudo -H] pip install ws4py==0.3.2
[sudo -H] pip install pyyaml
[sudo -H] pip install numpy
[sudo -H] pip install tensorflow
[sudo -H] pip install soundfile
[sudo -H] pip install librosa
```
### Kaldi Installation
Clone the Kaldi as follows:
```bash
git clone https://github.com/kaldi-asr/kaldi.git
```
Change directory to
```bash
cd kaldi/tools/
```
and then run the following line to check the requirments to install Kaldi tools are all available
```bash
extras/check_dependencies.sh
```
.. and install them if needed

run make; IT WILL TAKE TIME 
```bash
make [-j n]  # please change n to the number of cores you want to use
```
After building kaldi tools, change directory to `kaldi/src/` and do the same thing. Note that kaldi tools need to be built first
```bash
cd kaldi/src/
./configure --shared
make clean [-j n] 
make depend [-j n] 
make [-j n]  # please change n to the number of cores you want to use
```
### Gst-kaldi-nnet2-online Installation
The DNN-based online decoder requires a newer GStreamer plugin that is not in the Kaldi codebase and has to be compiled seperately. It's available at https://github.com/alumae/gst-kaldi-nnet2-online. 

Clone it and then change directory to the `src` directory under the cloned directory
```bash
git clone https://github.com/alumae/gst-kaldi-nnet2-online.git
cd gst-kaldi-nnet2-online/src
```

Install the following
```bash
sudo apt-get install gstreamer1.0-plugins-bad  gstreamer1.0-plugins-base gstreamer1.0-plugins-good  gstreamer1.0-pulseaudio  gstreamer1.0-plugins-ugly  gstreamer1.0-tools libgstreamer1.0-dev
sudo apt-get install libjansson-dev
```

Edit the `Makefile` in the directory and change the variable `KALDI_ROOT?=` poinring to the kaldi home directory as follows
```bash
vim Makefile
KALDI_ROOT?=/path/to/kaldi/home/directory
```

and then save and run
```bash
make depend
KALDI_ROOT=/home/disooqi/kaldi make # IT WILL TAKE TIME 
```
### Setting up the Model
Download the model as
```bash
wget -O /tmp/model.tar.gz  crowdsource.cloudapp.net/models/Arabic/20180304/nnet3sac.tar.gz
wget -O /tmp/model.tar.gz  https://qcristore.blob.core.windows.net/public/asrlive/models/arabic/nnet3sac.tar.gz
```

and then untar it to `/opt/model`
```bash
sudo mkdir -m 777 /opt/model
tar xzvf /tmp/model.tar.gz -C /opt/model
```
create the following dir
```bash
sudo mkdir -p -m 777 /var/spool/asr/nnet3sac
```

### Setting up Full Post Processor (this repo)
0) Before cloning this repo please make sure `Git LFS` is insalled, use the following command to install it
```bash
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs
```
1) clone this repo
```bash
git clone https://github.com/disooqi/qmdis-post-processor-full.git
```
2) make sure that `dialectid_post_processor.py` module and its parent directories have execution permissions
3) edit `/opt/model/model.yaml` and assign the path to `dialectid_post_processor.py` to the variable `full-post-processor:` as
    follows and append it to the file:
```yaml
full-post-processor: /the/path/to/dialectid_post_processor.py
```
### Setting up Kaldi Gstreamer Server
clone 
```bash
git clone https://github.com/alumae/kaldi-gstreamer-server.git
```
change directory to the directory you just cloned, and the run server as follows:
```bash
python kaldigstserver/master_server.py --port=8888 [--certfile=] [--keyfile=]
sudo python kaldigstserver/master_server.py --port=8888 --certfile=/home/disooqi/qcri_certificate.pem --keyfile=/home/disooqi/qcri_key.pem
```
### Runnning
```bash
export GST_PLUGIN_PATH=~/gst-kaldi-nnet2-online/src
cd kaldi-gstreamer-server
python kaldigstserver/worker.py -u ws://localhost:8888/worker/ws/speech -c /opt/model/model.yaml
````
Running Using SSL
----------------
1) pass server parameters
2) run worker with `wss://` instead of `ws://`
3) run client with `wss://` instead of `ws://`

sudo python manage.py runserver --insecure 0.0.0.0:80
```bash
git clone https://github.com/Kaljurand/dictate.js.git
```
