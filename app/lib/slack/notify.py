import requests
import datetime
import re

class Slack:
    token = ''
    icon_emoji = ''
    user_title = ''
    env_name = ''

    posts = {}

    def __init__(self, token, icon_emoji =False, user_title =False, env_name =False) -> None:
        if not token:
            print("Slack token required!")
            exit(1)
        self.token = token
        self.icon_emoji = icon_emoji if icon_emoji else ':kubernetes:'
        self.user_title = user_title if user_title else 'Deployment notifier'
        self.env_name = env_name if env_name else 'Staging'
        pass


    def send_message(self, channel, text):
        url = 'https://slack.com/api/chat.postMessage'

        result = requests.post(url, data={
            'token': self.token,
            'channel': channel,
            'icon_emoji': self.icon_emoji,
            'username': self.user_title,
            'text': text
        })
        if result.json() and not result.json()['ok']:
            print("Slack rejected")
            print(result.content)
        if result.status_code != 200 :
            print("Slack Non 200 response")
            print(result.content) 
        return result.json()


    def update_message(self, channel, ts, text):
        url = 'https://slack.com/api/chat.update'

        result = requests.post(url, data={
            'token': self.token,
            'ts': ts,
            'channel': channel,
            'text': text
        })
        if result.json() and not result.json()['ok']:
            print("Slack rejected")
            print(result.content)
        if result.status_code != 200 :
            print("Slack Non 200 response")
            print(result.content) 
        return result.json()
    

    def notify(self, changes, channel):       
        for name, change in changes.items():
            message = ''
            new_version = self.shorten_docker_name(change['new']['version'])
            old_version = self.shorten_docker_name(change['old']['version']) if change['old'] else False
            # image version changed
            if new_version != old_version:
                message += f"{self.env_name} `{name}` is set to `{new_version}`"
            # image stays same
            else:
                message += f"{self.env_name} `{name}` is `{new_version}`\n"
                message += f"Revision changed `{change['old']['revision']}` => `{change['new']['revision']}`"
            # send slack    
            post = self.send_message(channel, message)
            self.posts[ f"{name}/{change['new']['revision']}" ] = {
                "time": datetime.datetime.now() ,
                "change": change,
                "message": message,
                "status": False,
                "repository": False,
                "branch": False,
                "author": False,
                "id": post['ts'],
                "channel": post['channel'],
            }

        return


    # if version is a full length docker, remove repo host
    def shorten_docker_name(self, name):
        if len(name.split("/")) > 2:
            name = name.split("/")
            name.pop(0)
            name = "/".join(name)
        return name
    

    # if author is email address, strip all after '@'
    def shorten_author_name(self, name):
        i = name.index('@')
        return name[0:i] if i>0 else name


    def build_repo_link(self, repo, branch):
        link = False
        # check if repo link is valid
        if repo and repo.find('@') and repo.find(':') and repo.find('.git'):
            repo = repo[ repo.find(':')+1 : repo.find('.git') ]
        # text for slack
        if repo and branch:
            link = f"<https://github.com/{repo}/tree/{branch}|{branch}>"
        if repo and not branch:
            link = f""
        if branch and not repo:
            link = f"`{branch}`"
        return link
    

    def pods(self, pods, replicasets):
        for _, post in self.posts.items():
            # do not send updates after X minutes
            now = datetime.datetime.now()
            if (now - datetime.timedelta(minutes=40) > post['time']):
                continue
            if (now - datetime.timedelta(minutes=30) > post['time']):
                update = ""
                self.posts[_]['status'] = update
                text = self.buildText(self.posts[_])
                self.update_message(post['channel'], post['id'], text)
                continue
            # get update
            key = post['change']['new']['name']
            revision = post['change']['new']['revision']
            replicapods = []
            replicaset = ""
            for rs in replicasets[key]:
                if rs['revision'] == revision:
                    replicaset = rs['name']
                    if (rs.get('image-full') and rs['image-full'] == rs['version']):
                        repo = rs['git-repo'] if rs['git-repo'] else False 
                        branch = rs['git-branch'] if rs['git-branch'] else False
                        self.posts[_]['branch'] = self.build_repo_link(repo, branch) if branch else False
                        self.posts[_]['author'] = self.shorten_author_name(rs['gcloud-user']) if rs['gcloud-user'] else False
            for p in pods[key]:
                if p['replicaset'] == replicaset:
                    replicapods.append(p)
            # resolution
            if 0 == len(replicapods):    
                update = f":no_pods:"
            else: 
                update = f":starting:"
            all_ready = True    
            for p in replicapods:
                if not p['ready']:    
                    all_ready = False
            if all_ready and len(replicapods):
                update = f":ready:"
            # post update
            if post['status'] == update:
                continue
            self.posts[_]['status'] = update
            text = self.buildText(self.posts[_])
            self.update_message(channel=post['channel'], ts=post['id'], text=text)           
        return


    def buildText(self, post):
        message = f"{post['message']}"
        if post['status']:
            message += f" {post['status']}"
        if post['branch'] or post['author']:
            message += f"\n"
        if post['author']:
            message += f"By `{post['author']}` "
        if post['branch']:
            message += f"Branch {post['branch']}"
        return message


    def commits(self, github):
        for _, post in self.posts.items():
            # check only posts with unknonwn branches
            if not post['branch']:
                # find hash from version
                version = post['change']['new']['version']
                possible_commits = []
                for match in re.finditer(r"([a-z0-9])*", version):
                    str = match.group()
                    if(str.isalnum() and not str.isalpha() and not str.isnumeric()):
                        possible_commits.append(str)
                for hash in possible_commits:
                    print("hash search for", post['change']['new']['name'], post['change']['new']['version'], hash)
                    repo = github.whereCommit(hash)
                    branch = github.whereHead(repo, hash) if repo else False
                    if repo:
                        post['repository'] = repo
                    if repo and branch:
                        post['branch'] = f"<https://github.com/{repo}/commit/{hash}|{branch}>"
                    if repo and not branch:
                        post['branch'] = f"<https://github.com/{repo}/commit/{hash}|unknown>"
                if post['repository']:
                    self.posts[_] = post
                    text = self.buildText(self.posts[_])
                    self.update_message(channel=post['channel'], ts=post['id'], text=text)           
                    break