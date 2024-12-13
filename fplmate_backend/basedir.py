import os
from django.conf import settings
from django.http import JsonResponse
from django.views import View

class BaseDirectoryView(View):
    def get(self, request):
        return JsonResponse({
            'BASE_DIR': str(settings.BASE_DIR),
            'Absolute BASE_DIR': os.path.abspath(str(settings.BASE_DIR)),
            'Current Directory': os.getcwd(),
            'Directory Contents': os.listdir(settings.BASE_DIR),
            'Full Path Details': {
                'contents': [
                    {
                        'name': item,
                        'is_dir': os.path.isdir(os.path.join(settings.BASE_DIR, item)),
                        'is_file': os.path.isfile(os.path.join(settings.BASE_DIR, item))
                    } for item in os.listdir(settings.BASE_DIR)
                ]
            }
        })