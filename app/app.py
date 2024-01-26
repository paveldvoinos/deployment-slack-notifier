from http.server import HTTPServer, BaseHTTPRequestHandler
from lib.kube.client import KubeClient
from lib.collector.kubernetes import KubernetesCollector
from lib.slack.notify import Slack
from lib.webserver.webserver import Webserver
from lib.github.client import GithubClient
import threading
import time
import os

PORT = int(os.environ.get("PORT", 8080))
PERIOD = int(os.environ.get("PERIOD", 10))
CLUSTER_NAME = os.environ.get("CLUSTER_NAME")
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL")
SLACK_ICON = os.environ.get("SLACK_ICON", ":kubernetes:")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")


k = KubeClient()
if CLUSTER_NAME:
    k.initFromConf(CLUSTER_NAME)
else:
    k.initFromCluster()


collector = KubernetesCollector(k)
slack = Slack(token=SLACK_TOKEN, icon_emoji=SLACK_ICON)
github = GithubClient(GITHUB_TOKEN)

mainThread = threading.currentThread()
Webserver(mainThread).start(PORT)

deployments = {}
messages = {}
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
    slack.commits(github)
    time.sleep(PERIOD)
