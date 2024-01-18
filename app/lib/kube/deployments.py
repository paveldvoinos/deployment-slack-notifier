class Deployments:

    __client: any

    def __init__(self, client) -> None:
        self.__client = client
        pass

    def list(self, namespace ="default"):
        return self.__client.get(f'/apis/apps/v1/namespaces/{namespace}/deployments').json()

    def describe(self, name, namespace="default"):
        return self.__client.get(f'/apis/apps/v1/namespaces/{namespace}/deployments/{name}').json()
        