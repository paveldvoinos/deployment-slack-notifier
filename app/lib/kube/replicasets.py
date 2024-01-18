class Replicasets:

    __client: any

    def __init__(self, client) -> None:
        self.__client = client
        pass

    def list(self, namespace ="default", fieldSelector=False):
        filter = ""
        if fieldSelector:
            filter = f"fieldSelector={fieldSelector}"
        return self.__client.get(f'/apis/apps/v1/namespaces/{namespace}/replicasets?{filter}').json()
