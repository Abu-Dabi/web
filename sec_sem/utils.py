import face_recognition as fr
import numpy as np
from profiles.models import Profile
import re
import cv2
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'


def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_encoded_faces():
    # Retrieve all user profiles from the database
    qs = Profile.objects.all()

    # Create a dictionary to hold the encoded face for each user
    encoded = {}

    for p in qs:
        # Initialize the encoding variable with None
        encoding = None

        # Load the user's profile image
        face = fr.load_image_file(p.photo.path)

        # Encode the face (id detected)
        face_encodings = fr.face_encodings(face)
        if len(face_encodings) > 0:
            encoding = face_encodings[0]
        else:
            print("No face found in the image")

        # Add the user's encoded face to the dictionary id encoding is not None
        if encoding is not None:
            encoded[p.user.username] = encoding

    # Return the dictionary of encoded faces
    return encoded


def contains_number(image_path):
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
                        return True
            except Exception as e:
                print("Ошибка при распознавании текста:", e)
    return False


def classify_face(img):
    """
    This function takes an image as input and returns the name of the face it contains
    """
    # Load all the known faces and their encodings
    faces = get_encoded_faces()
    faces_encoded = list(faces.values())
    known_face_names = list(faces.keys())

    # Load the input image
    img = fr.load_image_file(img)

    try:
        # Find the locations of all faces in the input image
        face_locations = fr.face_locations(img)

        # Encode the faces in the input image
        unknown_face_encodings = fr.face_encodings(img, face_locations)

        # Identify the faces in the input image
        face_names = []
        for face_encoding in unknown_face_encodings:
            # Compare the encoding of the current face to the encodings of all known faces
            matches = fr.compare_faces(faces_encoded, face_encoding)

            # Find the known face with the closest encoding to the current face
            face_distances = fr.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(face_distances)

            # If the closest known face is a match for the current face, label the face with the known name
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            else:
                name = "Unknown"

            face_names.append(name)

        # Return the name of the first face in the input image
        return face_names[0]
    except:
        # If no faces are found in the input image or an error occurs, return False
        return False


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
