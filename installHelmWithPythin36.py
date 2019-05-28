#Install Helm with Python3.6


import os
import subprocess
import time

def subprocess_cmd(command):
    print("cmd to be executed = " + str(command))
    output = subprocess.check_output(command, shell=True)
    print(output)

f_loc_gcloud = r"/etc/yum.repos.d/google-cloud-sdk.repo"

#f_loc_gcloud = r"/Users/ratmistr/testVagrant/google-cloud-sdk.repo"
if not os.path.exists(f_loc_gcloud):
    open(f_loc_gcloud, 'w').close()

flag = True
if flag:
        gcloud_cont = '''[google-cloud-sdk]
name=Google Cloud SDK
baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg
       https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg'''

        f_loc_kubectl = r"/etc/yum.repos.d/kubernetes.repo"
        #f_loc_kubectl = r"/Users/ratmistr/testVagrant/kubernetes.repo"
        if not os.path.exists(f_loc_kubectl):
                open(f_loc_kubectl, 'w').close()

        f=open(f_loc_gcloud,'w')
        f.write(gcloud_cont)

        kubect_cont='''[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg'''

        f=open(f_loc_kubectl,'w')
        f.write(kubect_cont)

        subprocess_cmd("yum update -y")
        subprocess_cmd("yum install google-cloud-sdk -y")
        subprocess_cmd("yum install kubectl -y")
        #subprocess_cmd("export KUBECONFIG=/root/.kube/config")
key_loc = "/home/key.json"
#key_loc=r"/Users/ratmistr/testVagrant/key.json"
if not os.path.exists(key_loc):
        f1 = open(key_loc, 'w')
        keydata=os.environ.get('key')
        f1.write(keydata)
        f1.close()
print("Hello")
cmd = "gcloud auth activate-service-account --key-file " + str(key_loc)
subprocess_cmd(cmd)
print("Here")
os.environ["KUBECONFIG"]="/root/.kube/config"
project=os.environ.get('project')
print("project name is = " + str(project))
zone=os.environ.get('zone')
print("Zone name is = " + str(zone))
cluster=os.environ.get('cluster')
print("Cluster name is = " + str(cluster))
subprocess_cmd("gcloud config set project {}".format(str(project)))
subprocess_cmd("gcloud config set compute/zone {}".format(str(zone)))
subprocess_cmd("gcloud container clusters get-credentials {}".format(str(cluster)))
#kubeconfigpath="/root/.kube/config"

subprocess_cmd("kubectl get pod -n kube-system -l app=helm -l name=tiller  -o=jsonpath='{range .items[*]}{.status.containerStatuses[*].ready}{\"\\n\"}{end}' > /tmp/data")
#subprocess_cmd("kubectl get pod --all-namespaces > /tmp/data")
#print("Flag is = " + str(f))

if 'true' in open('/tmp/data').read():
    #subprocess_cmd("export KUBECONFIG=/root/.kube/config")
    #os.environ["KUBECONFIG"]="/root/.kube/config"
    print("Already installed")
    os.remove("/tmp/data")
else:
    subprocess_cmd("curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get > /home/get_helm.sh")
    subprocess_cmd("chmod 700 /home/get_helm.sh")
    os.environ["PATH"] = os.environ["PATH"] + ":/usr/local/bin"
    #subprocess_cmd("export PATH=$PATH:/usr/local/bin")
    #subprocess_cmd("echo 'PATH is $PATH'")
    subprocess_cmd("source /home/get_helm.sh")
    subprocess_cmd("helm init")
    subprocess_cmd("kubectl create serviceaccount --namespace kube-system tiller")
    subprocess_cmd("kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller")
    subprocess_cmd("kubectl patch deploy --namespace kube-system tiller-deploy -p '{\"spec\":{\"template\":{\"spec\":{\"serviceAccount\":\"tiller\"}}}}'")

#subprocess_cmd("export PATH=$PATH:/usr/local/bin")
f2 = "false"
while f2 != "true":
	subprocess_cmd("kubectl get pod -n kube-system -l app=helm -l name=tiller  -o=jsonpath='{range .items[*]}{.status.containerStatuses[*].ready}{\"\\n\"}{end}' > /tmp/data1")
	if 'true' not in open('/tmp/data1').read():
		time.sleep(20)
		print("Waiting for tiller to deploy")
	else:
		f2 = "true"
subprocess_cmd("helm repo add coreos https://s3-eu-west-1.amazonaws.com/coreos-charts/stable/")
subprocess_cmd("helm repo update")
subprocess_cmd("kubectl create namespace monitoring")
subprocess_cmd("helm install coreos/prometheus-operator --name prometheus-operator --namespace monitoring")
subprocess_cmd("helm install coreos/kube-prometheus --name kube-prometheus --set global.rbacEnable=true --namespace monitoring")

print("success")


