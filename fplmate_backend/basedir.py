import os
from django.conf import settings
from django.http import JsonResponse
from django.views import View

class BaseDirectoryView(View):
    def get(self, request):
        return JsonResponse({
            'BASE_DIR': str(settings.BASE_DIR),
            'Absolute BASE_DIR': os.path.abspath(str(settings.BASE_DIR))
        })