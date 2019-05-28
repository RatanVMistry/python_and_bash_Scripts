#!/bin/bash
#Install Helm with Bash
sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo << EOM
[google-cloud-sdk]
name=Google Cloud SDK
baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg
           https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOM

yum install google-cloud-sdk -y
yum install kubectl -y
export KUBECONFIG="/root/.kube/config"
file="key.json"

if [ -f $file ] ; then
    rm $file
fi
echo $key >> key.json
chmod 400 key.json

gcloud auth activate-service-account --key-file key.json
gcloud config set project $project_id
gcloud config set compute/zone $zone
gcloud container clusters get-credentials $cluster_name

flag=`kubectl get pod -n kube-system -l app=helm -l name=tiller  -o=jsonpath='{range .items[*]}{.status.containerStatuses[*].ready}{"\n"}{end}'`
flag=`echo $flag | tr '[:upper:]' '[:lower:]'`
echo "flag is $flag"
if [ "$flag" == "true" ]; then
        export PATH=$PATH:/usr/local/bin
        echo ""
else
        curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get > get_helm.sh
        chmod 700 get_helm.sh
        export PATH=$PATH:/usr/local/bin
        source get_helm.sh
        helm init
        kubectl create serviceaccount --namespace kube-system tiller
        kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
        kubectl patch deploy --namespace kube-system tiller-deploy -p '{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}'
fi
echo "installing prometheus start"

flag1=false

while [ "$flag1" != "true" ]
do
        sleep 30
        echo "---cheking status for tiller pod----"
        flag1=`kubectl get pod -n kube-system -l app=helm -l name=tiller  -o=jsonpath='{range .items[*]}{.status.containerStatuses[*].ready}{"\n"}{end}'`

done

helm repo add coreos https://s3-eu-west-1.amazonaws.com/coreos-charts/stable/
helm repo update
kubectl create namespace monitoring
helm install coreos/prometheus-operator --name prometheus-operator --namespace monitoring
helm install coreos/kube-prometheus --name kube-prometheus --set global.rbacEnable=true --namespace monitoring

echo "Success!!"

