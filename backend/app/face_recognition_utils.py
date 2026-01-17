import cv2
import face_recognition
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import json

class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        
    def encode_face_from_base64(self, base64_image):
        try:
            image_data = base64.b64decode(base64_image.split(',')[1])
            image = Image.open(BytesIO(image_data))
            image_array = np.array(image)
            
            face_locations = face_recognition.face_locations(image_array)
            if not face_locations:
                return None
                
            face_encodings = face_recognition.face_encodings(image_array, face_locations)
            if face_encodings:
                return face_encodings[0].tolist()
            return None
        except Exception as e:
            print(f"Error encoding face: {e}")
            return None
    
    def compare_faces(self, known_encoding, unknown_encoding, tolerance=0.6):
        if isinstance(known_encoding, str):
            known_encoding = json.loads(known_encoding)
        if isinstance(unknown_encoding, str):
            unknown_encoding = json.loads(unknown_encoding)
            
        known_encoding = np.array(known_encoding)
        unknown_encoding = np.array(unknown_encoding)
        
        distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
        confidence = 1 - distance
        
        return distance <= tolerance, confidence
    
    def detect_face_in_image(self, base64_image):
        try:
            image_data = base64.b64decode(base64_image.split(',')[1])
            image = Image.open(BytesIO(image_data))
            image_array = np.array(image)
            
            face_locations = face_recognition.face_locations(image_array)
            return len(face_locations) > 0, len(face_locations)
        except Exception as e:
            print(f"Error detecting face: {e}")
            return False, 0

face_system = FaceRecognitionSystem()