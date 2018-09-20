#!/bin/bash -e

BASEDIR=$(dirname $0)

screen -dmS kgserver sh
screen -S kgserver -p 0 -X stuff ". ~/kgs_env/bin/activate
"
screen -S kgserver -p 0 -X stuff "cd kaldi-gstreamer-server/
"
screen -S kgserver -p 0 -X stuff "python kaldigstserver/master_server.py --port=8888 --certfile=/etc/ssl/qcri-cert-20180914/qcri_certificate.pem --keyfile=/etc/ssl/qcri-cert-20180914/qcri_key.pem
"

sleep 2


counter=1
while [ $counter -le 11 ]
do
echo  running worker w$counter
screen -dmS w$counter sh
screen -S w$counter -p 0 -X stuff ". ~/kgs_env/bin/activate
"
screen -S w$counter -p 0 -X stuff "export GST_PLUGIN_PATH=~/gst-kaldi-nnet2-online/src
"
screen -S kgserver -p 0 -X stuff "cd kaldi-gstreamer-server/
"
screen -S w$counter -p 0 -X stuff "python kaldigstserver/worker.py -u wss://localhost:8888/worker/ws/speech -c /opt/model/model.yaml
"
sleep 2
((counter++))
done

