# QMDIS Post Processor Full

An Arabic dialect identification "post processor" after full result of the kaldi-gstreamer-server

This project is a part of QMDIS "QCRI-MIT Advanced Dialect Identification" system. The purpose of the system is to identify between five Arabic dialects, namely Egyptian Arabic, Levantine Arabic, Gulf Arabic, North African Arabic and Modern Standard Arabic (or MSA). 

This project is just the post processor script that is called after the full transcript result of the ASR system. You need to install Kaldi ASR and the its Gstreamer server first before you can use it.  



Installation
------------

### Requirment
*NB!*: Please don't use anaconda to install the ASR becasue bindings for gobject-introspection libraries will not be installed in its site-packages.

*NB!*: If you want to use virtual environment it is recommended to create it with --system-site-packages flag so that it can use Python bindings

*NB!*: The server doesn't work quite correctly with ws4py 0.3.5 because of a bug I reported here: https://github.com/Lawouach/WebSocket-for-Python/issues/152.
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

sudo -H pip install tornado
sudo -H pip install ws4py==0.3.2
sudo -H pip install pyyaml
```
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



