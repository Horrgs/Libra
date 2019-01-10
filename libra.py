from urllib.request import urlopen, urlretrieve
from urllib.error import URLError
from pathlib2 import Path
import os
import json


class Settings:

    def has_internet(self):
        try:
            urlopen('https://1.1.1.1', timeout=1)
            return True
        except URLError:
            return False

    def is_client_secret(self):
        my_file = Path("/path/to/client_secret.json")
        if my_file.is_file():
            return True
        return False

    def set_up(self):
        my_path = Path("%s/Documents/Libra/" % Path.home())
        if not my_path.exists():
            os.mkdir(my_path)
            os.mkdir("%s/cached" % my_path)
            with open("messages.json", 'r') as msg_ex:
                msg_contents = json.load(msg_ex)
            with open('%s/messages.json' % my_path, 'w') as msg_out:
                json.dump(msg_contents, msg_out, sort_keys=True, indent=4)
            with open("cache.json", 'r') as cch_ex:
                cch_contents = json.load(cch_ex)
            with open("%s/cache.json", 'w') as cch_out:
                json.dump(cch_contents, cch_out, sort_keys=True, indent=4)

    def write_cache_from_objs(self, objs_list: list):
        my_path = Path("%s/Documents/Libra/cache.json" % Path.home())
        if not my_path.exists():
            raise SystemError("Application not properly configured.")
        else:
            with open(str(my_path), 'w') as cache:
                content = {'mediaItems': []}
                content['mediaItems'] = objs_list
                json.dump(content, cache, sort_keys=True, indent=4)
        cache_path = Path("%s/Documents/Libra/cached" % Path.home())
        for the_file in os.listdir(cache_path):
            file_path = os.path.join(cache_path, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)
        for obj in objs_list:
            urlretrieve(str(obj['baseUrl'] + "=d"), "%s/%s.%s" % (cache_path, obj['id'],
                                                                  str(obj['mimeType']).split("/")[1]))

    def get_cache(self):
        path = Path("%s/Documents/Libra/cache.json" % Path.home())
        if not path.exists():
            raise SystemError("Application not properly configured. No cache found.")
        else:
            with open(str(path), 'r') as cache:
                return json.load(cache)

    def is_cached(self, photo_id):
        my_path = Path("%s/Documents/Libra/cache.json" % Path.home())
        if not my_path.exists():
            raise SystemError("Application not properly configured.")
        else:
            with open(str(my_path), 'r') as cache:
                content = json.load(cache)
            if 'mediaItems' in content:
                for media_item in content['mediaItems']:
                    if media_item['id'] == photo_id:
                        return True
                    else:
                        pass
                return False
            return False


