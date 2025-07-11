import os
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import ImageUploadForm

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'covers')

def cover_upload_view(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('preview_cover')
    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {'form': form})


##############################################################


from django.http import JsonResponse
from .models import CoverImage
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def upload_cover_api(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = CoverImage(final_image=request.FILES['image'])
        image.save()
        return JsonResponse({
            "success": True,
            "image_url": image.final_image.url
        })
    return JsonResponse({"success": False, "error": "Invalid request"})


##############################################################

from django.shortcuts import get_object_or_404

def preview_cover(request):
    latest_cover = CoverImage.objects.order_by('-id').first()
    return render(request, 'preview.html', {'cover_image': latest_cover.final_image.url if latest_cover else None})