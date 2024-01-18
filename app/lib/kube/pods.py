class Pods:

    __client: any

    def __init__(self, client) -> None:
        self.__client = client
        pass

    def list(self, namespace ="default"):
        return self.__client.get(f'/api/v1/namespaces/{namespace}/pods').json()

    def get(self, name, namespace="default"):
        return self.__client.get(f'/api/v1/namespaces/{namespace}/pods/{name}').json()
        