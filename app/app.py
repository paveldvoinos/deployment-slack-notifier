from http.server import HTTPServer, BaseHTTPRequestHandler
from lib.kube.client import KubeClient
from lib.collector.collector import Collector
from lib.slack.notify import Slack
from lib.webserver.webserver import Webserver
import json
import time
import os

PORT = os.environ.get("PORT", 8080)
CLUSTER_NAME = os.environ.get("CLUSTER_NAME")
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL")
SLACK_ICON = os.environ.get("SLACK_ICON", ":kubernetes:")


k = KubeClient()
if CLUSTER_NAME:
    k.initFromConf(CLUSTER_NAME)
else:
    k.initFromCluster()

collector = Collector(k)
slack = Slack(token=SLACK_TOKEN, icon_emoji=SLACK_ICON)
Webserver(collector).start(PORT)

deployments = {}
while(True):
    new_deployments = collector.deployments()
    changes = collector.changes(deployments, new_deployments)
    print(f"Found {len(changes)}")
    if(len(deployments) and len(changes)):
        print(changes)
        slack.notify(changes, SLACK_CHANNEL)
    deployments = new_deployments
    pods = collector.pods()
    replicasets = collector.replicasets()
    slack.pods(pods, replicasets)
    time.sleep(10)
