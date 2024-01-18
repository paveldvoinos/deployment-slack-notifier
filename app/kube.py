import requests

# # Point to the internal API server hostname
# export APISERVER=https://kubernetes.default.svc
#
# # Path to ServiceAccount token
# export SERVICEACCOUNT=/var/run/secrets/kubernetes.io/serviceaccount
#
# # Read this Pod's namespace
# export NAMESPACE=$(cat ${SERVICEACCOUNT}/namespace)
#
# # Read the ServiceAccount bearer token
# export TOKEN=$(cat ${SERVICEACCOUNT}/token)
#
# # Reference the internal certificate authority (CA)
# export CACERT=${SERVICEACCOUNT}/ca.crt
#
# # Explore the API with TOKEN
# curl --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" -X GET ${APISERVER}/api