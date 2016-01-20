import glob
import os
import yaml


class Category(object):

    def __init__(self, category_id, name="",
                 parent_uri="", users="",
                 access_secret="", access_token="",
                 consumer_key="", consumer_secret=""):
        self.id = category_id
        self.name = name
        self.parent_uri = parent_uri
        self.users = users

        # twitter credentials
        self.access_secret = access_secret
        self.access_token = access_token
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def set_from_dict(self, d):
        self.name = d['name']
        self.parent_uri = d['parent_uri']
        self.users = d['users']
        self.access_secret = d['access_secret']
        self.access_token = d['access_token']
        self.consumer_key = d['consumer_key']
        self.consumer_secret = d['consumer_secret']

    def load(self):
        f = open(self.file_path(), "r")
        settings = yaml.safe_load(f)
        f.close()
        self.set_from_dict(settings)

    def save(self):
        settings = {
            'name': self.name,
            'parent_uri': self.parent_uri,
            'users': self.users,
            'access_secret': self.access_secret,
            'access_token': self.access_token,
            'consumer_key': self.consumer_key,
            'consumer_secret': self.consumer_secret
        }
        f = open(self.file_path(), "w")
        yaml.dump(settings, f, default_flow_style=False, encoding='utf-8')
        f.close()

    def file_path(self):
        return os.path.join('categories', 'settings{}.yaml'.format(self.id))

    @staticmethod
    def all():
        files_names = glob.glob1('categories', 'settings*.yaml')
        rtn = []
        for file_name in files_names:
            category_id = file_name[len('settings'):-len('.yaml')]
            category = Category(category_id)
            category.load()
            rtn.append(category)
        return rtn

    @staticmethod
    def find_by_id(category_id):
        file_path = os.path.join('categories', 'settings{}.yaml'.format(category_id))
        if os.path.exists(file_path):
            rtn = Category(category_id)
            rtn.load()
            return rtn
        else:
            return None

    @staticmethod
    def delete(category_id):
        file_path = os.path.join('categories', 'settings{}.yaml'.format(category_id))
        if os.path.exists(file_path):
            os.remove(file_path)