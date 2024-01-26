import requests

class GithubClient:

    __token = ""
    __org = ""

    def __init__(self, token, organization =False) -> None:
        self.__token = token
        self.__org = organization
        pass
    
    def get(self, url):
        headers = { 'Authorization': 'token '+self.__token }
        r = requests.get(url, headers=headers)
        if r.status_code != 200 :
            print("Github api non 200 response")
            print(r.content)
        return r

    def recentRepositories(self):
        url = "https://api.github.com/user/repos?sort=pushed"
        r = self.get(url)
        recent = []
        for repo in r.json().items():
            recent.append( repo['full_name'] )
        return recent

    def whereHead(self, commit_hash):
        result = False
        for repo in self.recentRepositories():
            url = f"https://api.github.com/repos/{repo}/commits/{commit_hash}/branches-where-head"
            r = self.get(url)
            if len(r.json()):
                branch = r.json()[0]['name']
                result[ repo ] = branch
                return result
