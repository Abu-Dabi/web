from django.shortcuts import redirect
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .utils import is_ajax, classify_face, contains_number, extract_number_from_image
import base64
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from profiles.models import Profile
from django.shortcuts import render
from .models import Log
from .forms import PhotoForm
import cv2
import pytesseract
import re
import os

# Устанавливаем путь к исполняемому файлу Tesseract OCR (если необходимо)
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'


def get_photo_by_id(request):
    if request.method == 'POST':
        user_id = request.POST.get('userID')
        try:
            profile = Profile.objects.get(custom_id=user_id)
            if profile.photo:
                return JsonResponse({'success': True, 'photo_url': profile.photo.url})
            else:
                return JsonResponse({'success': False, 'error': 'Photo not found for the given ID'})
        except Profile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User with the given ID not found'})

    return render(request, 'check_user.html')


def check_user_view(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        if not image:
            return JsonResponse({'success': False, 'error': 'Изображение не найдено в запросе'})

        try:
            temp_image_name = 'temp.jpg'
            temp_image_path = os.path.join(settings.MEDIA_ROOT, temp_image_name)
            with default_storage.open(temp_image_path, 'wb') as temp_image_file:
                for chunk in image.chunks():
                    temp_image_file.write(chunk)

            if contains_number(temp_image_path):
                extracted_number = extract_number_from_image(temp_image_path)
                if extracted_number:
                    profile = Profile.objects.filter(custom_id=extracted_number).first()
                    if profile:
                        user = profile.user
                        response_data = {'success': True, 'user_id': user.id, 'username': user.username}
                    else:
                        response_data = {'success': False, 'error': 'Пользователь не найден'}
                else:
                    response_data = {'success': False, 'error': 'Невозможно извлечь число с изображения'}
            else:
                response_data = {'success': False, 'error': 'На изображении не найдено число'}

        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
            response_data = {'success': False, 'error': str(e)}

        finally:
            if default_storage.exists(temp_image_path):
                default_storage.delete(temp_image_path)

        return JsonResponse(response_data)

    return render(request, 'check_user.html')

def contains_number(image_path):
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        _, thresholded = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        thresholded = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h > 50:
                roi = image[y:y + h, x:x + w]
                text = pytesseract.image_to_string(roi, config='--psm 6')
                if text.strip():
                    black_numbers = re.findall(r'\b\d{3}\b', text)
                    if black_numbers:
                        return True
    except Exception as e:
        logger.error(f"Error during text recognition: {e}")
    return False



def upload_photo(request):
    if request.method == 'POST':
        files = request.FILES.getlist('image')
        responses = []

        for file in files:
            form = PhotoForm(files={'image': file})
            if form.is_valid():
                photo_instance = form.save()
                temp_file_path = photo_instance.image.path

                if contains_number(temp_file_path):
                    destination_folder = os.path.join(settings.MEDIA_ROOT, 'success')
                    status = 'success'
                else:
                    destination_folder = os.path.join(settings.MEDIA_ROOT, 'errors')
                    status = 'error'

                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)

                saved_file_path = os.path.join(destination_folder, os.path.basename(temp_file_path))
                os.rename(temp_file_path, saved_file_path)

                responses.append({'name': file.name, 'status': status, 'url': saved_file_path})
            else:
                responses.append({'name': file.name, 'status': 'error', 'errors': form.errors.as_json()})

        return JsonResponse({'files': responses})

    form = PhotoForm()
    return render(request, 'photo.html', {'form': form})


def extract_number_from_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    _, thresholded = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thresholded = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 50 and h > 50:
            roi = image[y:y + h, x:x + w]
            try:
                text = pytesseract.image_to_string(roi, config='--psm 6')
                if text.strip():
                    black_numbers = re.findall(r'\b\d{3}\b', text)
                    if black_numbers:
                        return black_numbers[0]
            except Exception as e:
                print("Ошибка при распознавании текста:", e)
    return None


def login_view(request):
    return render(request, 'login.html', {})


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    return render(request, 'main.html', {})


def find_user_view(request):
    if is_ajax(request):
        # Получаем изображение из POST-запроса и декодируем его из base64
        photo = request.POST.get('photo')
        _, str_img = photo.split(';base64')
        decoded_file = base64.b64decode(str_img)

        # Создаем новый объект Log и сохраняем переданное изображение в нем
        x = Log()
        x.photo.save('upload.png', ContentFile(decoded_file))
        x.save()

        # Классифицируем лицо на изображении
        res = classify_face(x.photo.path)
        photo_path = x.photo.path

        # Проверяем результат классификации лица
        if res:
            # Если классификация прошла успешно и лицо не является "Unknown"
            if res != "Unknown":
                # Проверяем, существует ли пользователь с таким именем
                user_exists = User.objects.filter(username=res).exists()
                if user_exists:
                    # Получаем пользователя и его профиль из базы данных
                    user = User.objects.get(username=res)
                    profile = Profile.objects.get(user=user)
                    x.profile = profile
                    x.save()
                    if res is not None:
                        # Извлекаем число с изображения
                        extracted_number = extract_number_from_image(photo_path)
                        if extracted_number:
                            # Проверяем, существует ли пользователь с таким ID
                            user = User.objects.filter(username=extracted_number).first()
                            if user is not None:
                                login(request, user)
                                return JsonResponse({'success': True})
                            else:
                                return JsonResponse({'success': False, 'error': 'User not found'})
                        else:
                            return JsonResponse({'success': False, 'error': 'Unable to extract number from image'})
                    else:
                        return JsonResponse({'success': False, 'error': 'Unable to detect face in image'})
                else:
                    # Если лицо не распознано, возвращаем ошибку
                    return JsonResponse({'success': False, 'error': 'Unknown face'})
            else:
                # Если лицо не распознано, возвращаем ошибку
                return JsonResponse({'success': False, 'error': 'Unable to classify face'})
        # Если это не AJAX-запрос, возвращаем ошибку
        return JsonResponse({'error': 'Invalid request'})
    return JsonResponse({'error': 'Invalid request'})
