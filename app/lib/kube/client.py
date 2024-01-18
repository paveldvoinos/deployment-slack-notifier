import yaml
import json
import os
import requests
import string
import random
import base64

class KubeClient:

    __hostname = 'localhost'
    __token    = 'xxx'
    __cert     = False

    def __init__(self) -> None:
        pass

    def initFromConf(self, cluster_name, file ='~/.kube/config'):
        print("Started kube init from local config")
        file = os.path.expanduser(file)
        with open(file, 'r') as f:
            y = yaml.safe_load(f)
        for cluster in y['clusters']:
            if cluster['name'] == cluster_name:
                self.__hostname = cluster['cluster']['server']
                certificate_data = cluster['cluster']['certificate-authority-data']
                break
        if not self.__hostname:
            print("Cluster config not found")
            exit(1)
        if certificate_data:
            filename = '/tmp/' + ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(7))
            with open(filename, 'wb') as f:
                f.write( base64.b64decode(certificate_data) )
                f.close
            self.__cert = filename

        auth_command = False
        for user in y['users']:
            if user['name'] == cluster_name:
                auth_command = user['user']['exec']['command']
        if not auth_command:
            print("Kube auth cmd failed")
            exit(1)        
        auth_result = os.popen(auth_command).read()
        auth = json.loads(auth_result)
        self.__token = auth['status']['token']

        return
    
    def initFromCluster(self):
        print("Started kube init from serviceaccount")
        self.__hostname = "https://kubernetes.default.svc"
        token_file = "/var/run/secrets/kubernetes.io/serviceaccount/token"
        cert_file = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
        with open(token_file, 'r') as f:
            token = f.read()
        f.close()
        if not token:
            print("Reading service account token failed")
            exit(1)
        self.__token = token
        if os.path.isfile(cert_file):
            self.__cert = cert_file
        return
    
    def initManual(self, hostname, token, cert =False):
        self.__hostname = hostname
        self.__token = token
        self.__cert = cert

    def get(self, endpoint):
        url = self.__hostname + endpoint
        headers = { 'Authorization': 'Bearer '+self.__token }
        r = requests.get(url, headers=headers, verify=self.__cert )
        if r.status_code != 200 :
            print("Kube api non 200 response")
            print(r.content)
        return r