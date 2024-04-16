from lib.kube.deployments import Deployments
from lib.kube.pods import Pods
from lib.kube.replicasets import Replicasets
import datetime

class KubernetesCollector:

    def __init__(self, client) -> None:
        self.__client = client
        pass

    def deployments(self, namespace ="default"):
        result = {}
        list = Deployments(self.__client).list(namespace)
        for d in list['items']:
            key = d['spec']['template']['spec']['containers'][0]['name']
            version = d['spec']['template']['spec']['containers'][0]['image']
            result[ key ] = {
                "name": key,
                "version": version,
                "revision": d['metadata']['annotations']['deployment.kubernetes.io/revision']
            }
        return result


    def versions(self, namespace ="default"):
        result = {}
        list = self.deployments(namespace)
        for name, d in list.items():
            result[ name ] =  d['version']
        return result


    def changes(self, old, new):
        result = {}
        for name, d in new.items():
            rec = {
                "new": d,
                "detectedAt": datetime.datetime.now().isoformat()
            }
            if not name in old:
                # added
                rec["old"] = False
            elif old[name] != new[name]:
                # changed
                rec["old"] = old[name]
                print(f"Changes found: ")
            else:
                continue
            result[ name ] = rec
        return result


    def pods(self, namespace ="default"):
        result = {}
        list = Pods(self.__client).list(namespace)
        for p in list['items']:
            key = p['spec']['containers'][0]['name']
            version = p['spec']['containers'][0]['image']
            readiness = ""
            ready = False
            if p['status'].get('conditions'):
                for condition in p['status']['conditions']:
                    if condition['status'] == 'True':
                        readiness += condition['type'] + " "
                        if condition['type'] == 'Ready':
                            ready = True
            if not key in result:
                result[key] = []
            result[ key ].append( {
                "name": key,
                "id": p['metadata']['name'],
                "version": version,
                "replicaset": p['metadata']['ownerReferences'][0]['name'] if p['metadata'].get('ownerReferences') else '',
                "phase": p['status']['phase'],
                "readiness": readiness,
                "ready": ready
            }
            )
        return result
    

    def replicasets(self, namespace ="default"):
        result = {}
        list = Replicasets(self.__client).list(namespace)
        for rs in list['items']:
            key = rs['metadata']['ownerReferences'][0]['name']
            revision = rs['metadata']['annotations']['deployment.kubernetes.io/revision']
            if not key in result:
                result[key] = []
            data = {
                "name": rs['metadata']['name'],
                "revision": revision,
                "version": rs['spec']['template']['spec']['containers'][0]['image']
            }
            for annotation in rs['metadata']['annotations']:
                prefix = "fst-"
                if str(annotation).startswith(prefix):
                    data[annotation[len(prefix):]] = rs['metadata']['annotations'][annotation]
            result[ key ].append( data )
            
        return result