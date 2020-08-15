import json
import re
import zipfile
import os
import time

class FacebookArchive:
    def __init__(self, filename):
        self.filename = filename
        self.zip = zipfile.ZipFile(self.filename)

    def post_jsons(self):
        jsons = []
        for n in sorted(self.zip.namelist()):
            if re.search('^posts/your_posts_.*\.json$', n):
                jsons.append(n)
        return jsons

    def posts(self, **kwargs):
        json_files = self.post_jsons()
        json_data = []
        for jsonf in json_files:
            json_1 = json.loads(self.zip.read(jsonf))
            
            for e in json_1:
                p = Post.parse(e)
                if 'month' in kwargs and p.timestamp.tm_mon != kwargs['month']:
                    continue
                if 'day' in kwargs and p.timestamp.tm_mday != kwargs['day']:
                    continue
                json_data.append(p)
        return json_data

    def image(self, filename):
        return self.zip.read(filename)

class Post:
    def __init__(self, timestamp, text, images=[]):
        self.timestamp = timestamp
        self.text = text
        self.images = images

    def to_dict(self):
        return {'timestamp': self.timestamp, 'text': self.text, 'images': self.images}

    # @static
    def parse(data):
        ts = time.localtime(data['timestamp'])
        
        text = None
        try:
            # https://stackoverflow.com/questions/50008296/facebook-json-badly-encoded
            text = data['data'][0]['post'].encode('latin-1').decode('utf-8')
        except Exception as ex:
            pass
        
        images = []
        try:
            for a in data['attachments'][0]['data']:
                images.append(a['media']['uri'])
        except Exception as ex:
            pass

        return Post(ts, text, images)
