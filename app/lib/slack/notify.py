import requests
import datetime

class Slack:
    token = ''
    icon_emoji = ''
    user_title = ''

    posts = {}

    def __init__(self, token, icon_emoji =False, user_title =False) -> None:
        if not token:
            print("Slack token required!")
            exit(1)
        self.token = token
        self.icon_emoji = icon_emoji if icon_emoji else ':kubernetes:'
        self.user_title = user_title if user_title else 'Deployment notifier'
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
            old_version = self.shorten_docker_name(change['old']['version'])
            # image version changed
            if new_version != old_version:
                message += f"Staging `{name}` is set to `{new_version}`"
            # image stays same
            else:
                message += f"Staging `{name}` is `{new_version}`\n"
                message += f"Revision changed `{change['old']['revision']}` => `{change['new']['revision']}`"
            # send slack    
            post = self.send_message(channel, message)
            self.posts[ f"{name}/{change['new']['revision']}" ] = {
                "time": datetime.datetime.now() ,
                "change": change,
                "message": message,
                "id": post['ts'],
                "channel": post['channel']
            }

        return


    # if version is a full length docker, remove repo host
    def shorten_docker_name(self, name):
        if len(name.split("/")) > 2:
            name = name.split("/")
            name.pop(0)
            name = "/".join(name)
        return name


    def pods(self, pods, replicasets):
        for _, post in self.posts.items():
            # do not send updates after X minutes
            now = datetime.datetime.now()
            if (now - datetime.timedelta(minutes=40) > post['time']):
                continue
            if (now - datetime.timedelta(minutes=30) > post['time']):
                update = ""
                self.update_message(post['channel'], post['id'], post['message'])
                self.posts[_]['update'] = update
                continue
            # get update
            key = post['change']['new']['name']
            revision = post['change']['new']['revision']
            replicapods = []
            replicaset = ""
            for rs in replicasets[key]:
                if rs['revision'] == revision:
                    replicaset = rs['name']
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
            text = post['message'] + f" {update}"
            # post update
            if 'update' in post and post['update'] == update:
                continue
            self.update_message(channel=post['channel'], ts=post['id'], text=text)
            self.posts[_]['update'] = update
        return