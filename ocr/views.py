from django.shortcuts import render
from django.views.generic import TemplateView
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageFilter
from tesserocr import PyTessBaseAPI
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class OcrView(TemplateView):

    def get(self, request, *args, **kwargs):
        """
        GET /ocr/
        Not allowed. Does nothing. 
        TODO: Serve form here
        """
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    def post(self, request, *args, **kwargs):
        """
        POST /ocr/
        Process an image using tesserocr and return text content
        """
        image = request.FILES.get('image', None)
        if not image:
            return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

        if not image.content_type.startswith('image/'):
            return JsonResponse({'status': 'error', 'message': 'Invalid file'}, status=400)

        utf8_text = None
        try:
            with PyTessBaseAPI() as api:
                with Image.open(image) as image_file:
                    rgb_image = image_file.convert('RGB')
                    sharpened_image = rgb_image.filter(ImageFilter.SHARPEN)
                    api.SetImage(sharpened_image)
                    utf8_text = api.GetUTF8Text()
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Server Error {}'.format(e)}, status=500)
        return JsonResponse({'status': 'ok', 'data': utf8_text}, status=200)
