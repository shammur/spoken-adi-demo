# QMDIS Post Processor Full

An Arabic dialect identification "post processor" after full result of the kaldi-gstreamer-server

This project is a part of QMDIS "QCRI-MIT Advanced Dialect Identification" system. The purpose of the system is to identify between five Arabic dialects, namely Egyptian Arabic, Levantine Arabic, Gulf Arabic, North African Arabic and Modern Standard Arabic (or MSA). 

This project is just the post processor script that is called after the full transcript result of the ASR system. You need to install Kaldi ASR and the its Gstreamer server first before you can use it.  

Current Specs of https://dialectid.qcri.org/ Server
---------------------------------------------------

|    | Type                 | value                                     |
|----|----------------------|-------------------------------------------|
| 1  | Architecture:        | x86_64                                    |
| 2  | CPU op-mode(s):      | 32-bit, 64-bit                            |
| 3  | Byte Order:          | Little Endian                             |
| 4  | CPU(s):              | 16                                        |
| 5  | Memory:              | 64 GiB                                    |
| 6  | On-line CPU(s) list: | 0-15                                      |
| 7  | Thread(s) per core:  | 2                                         |
| 8  | Core(s) per socket:  | 8                                         |
| 9  | Socket(s):           | 1                                         |
| 10 | NUMA node(s):        | 1                                         |
| 11 | Vendor ID:           | GenuineIntel                              |
| 12 | CPU family:          | 6                                         |
| 13 | Model:               | 63                                        |
| 14 | Model name:          | Intel(R) Xeon(R) CPU E5-2673 v3 @ 2.40GHz |
| 15 | Stepping:            | 2                                         |
| 16 | CPU MHz:             | 2394.452                                  |
| 17 | BogoMIPS:            | 4788.90                                   |
| 18 | Virtualization:      | VT-x                                      |
| 19 | Hypervisor vendor:   | Microsoft                                 |
| 20 | Virtualization type: | full                                      |
| 21 | L1d cache:           | 32K                                       |
| 22 | L1i cache:           | 32K                                       |
| 23 | L2 cache:            | 256K                                      |
| 24 | L3 cache:            | 30720K                                    |
| 25 | NUMA node0 CPU(s):   | 0-15                                      |

Setting timezone
----------------
As QMDIS saves audio and json files within each session, It is usful to store the local time as well. To adjust the timezone according to the wanted place, we can do that through one of the following commands, 
```bash
tzselect
```
which opens a gui in terminal, or
```bash
sudo cp /usr/share/zoneinfo/Europe/London /etc/localtime
```

Installation
------------

### Requirment
*NB!*: Please don't use anaconda to install the ASR becasue bindings for gobject-introspection libraries will not be installed in its site-packages.

*NB!*: If you want to use virtual environment it is recommended to create it with --system-site-packages flag so that it can use Python bindings

*NB!*: The server doesn't work quite correctly with ws4py 0.3.5 because of a bug that has been reported here: https://github.com/Lawouach/WebSocket-for-Python/issues/152.
* Python 2.7
* In addition, you need Python 2.x bindings for gobject-introspection libraries, provided by the `python-gi`
package on Debian and Ubuntu.
* Tornado 4.5.2
* ws4py (0.3.0 .. 0.3.2)
* YAML
* JSON


```bash
sudo apt-get update
sudo apt install virtualenv
sudo apt install python-gobject
sudo apt install python-dbus
```

Use `sudo -H` only when you installing in the global environment. Check requirements.txt in repo for libraries versions.
```bash
virtualenv --system-site-packages <your_env_name> -p <path/to/python2.7>
source <path/to/your/env>/bin/activate

[sudo -H] pip install tornado==4.5.2
[sudo -H] pip install ws4py==0.3.2
[sudo -H] pip install pyyaml
[sudo -H] pip install numpy # numpy dropped python2 try [sudo apt-get install python-numpy]
											# scipy dropped python2 try [sudo apt-get install python-scipy]
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
or 
post-processor: /the/path/to/dialectid_post_processor.py  #depending on yaml  
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
