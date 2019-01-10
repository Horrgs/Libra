from django.http import HttpResponse
import json
from django.template import loader
from pathlib import Path
from libra import Settings
from photos.photos import PhotoConnect, Album

def index(request):
    context = {}
    home = str(Path.home())
    with open('%s/Documents/messages.json' % home, 'r+') as f:
        data = json.load(f)
        if data['had_first'] is False:
            first_vist = True
            data['had_first'] = True
            json.dump(data, f, sort_keys=True, indent=4)
            message = data['message']
            context['con'] = message
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))


def start_slide_show(request):
    if request.method == 'POST':
        settings = Settings()
        if settings.has_internet():
            photos = PhotoConnect()
            session = photos.get_authorized_session()
            album = Album(session, "Libra")
            links = []
            for media_item in album.get_media_items():
                reg = media_item['baseUrl']
                mod = str(media_item['baseUrl'] + "=w1280-h800-c")
                links.append(mod)
            context = {
                'links': json.dumps(links)
            }
            template = loader.get_template('photos.html')
            return HttpResponse(template.render(context, request))
        else:
            #use cache.
            pass
    pass


def first_visit(request):
    home = str(Path.home())
    with open('%s/Documents/messages.json' % home, 'r') as f:
        data = json.load(f)
        message = data['message']

    with open('%s/Documents/messages.json' % home, 'w') as outfile:
        d = data
        d['had_first'] = 'true'
        json.dump(d, outfile, sort_keys=True, indent=4)
    return HttpResponse(message)
