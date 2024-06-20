import base64
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from urllib.parse import parse_qs
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import os
from deepface import DeepFace
import pandas as pd

# Create your views here.


@csrf_exempt
@require_http_methods(["GET"])
def get_books(request):
    books = [
        {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "year": 1925
        },
        {
            "title": "One Hundred Years of Solitude",
            "author": "Gabriel Garcia Marquez",
            "year": 1967
        },
        {
            "title": "A Passage to India",
            "author": "E.M. Forster",
            "year": 1924
        }
    ]
    return JsonResponse(books, safe=False)



@csrf_exempt
@require_http_methods(["POST"])
def get_demo(request):
    try:
        data = request.body.decode('utf-8')
        data = json.loads(data)
    except json.JSONDecodeError:
        data = dict(request.POST)
    
    return JsonResponse({"message": "This is a POST request","data":data})




@csrf_exempt
@require_http_methods(["POST"])
def get_image(request):
    if request.FILES:
        # Assuming the form field name for the file is 'image'
        uploaded_file = request.FILES['image']
        image = Image.open(uploaded_file)
        
        # Convert the PIL image to a NumPy array
        image_np = np.array(image)
        
        max_width = 800
        max_height = 600
        ratio = min(max_width / image.width, max_height / image.height)
        
        # Resize the image using OpenCV
        resized_image = cv2.resize(image_np, (int(image.width * ratio), int(image.height * ratio)))
        
        # Convert the color format from BGR to RGB (required for PIL)
        resized_image_rgb = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
        
        # Display the resized image
        cv2.imshow('Uploaded Image', resized_image_rgb)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return JsonResponse({"message": "Image received"})
    else:
        return JsonResponse({"message": "No image received"})
    


@csrf_exempt
@require_http_methods(["POST"])
def play_video(request):
    # Check if a file named 'video' was uploaded
    if 'video' in request.FILES:
        # Get the uploaded video file
        uploaded_video = request.FILES['video']
        
        # Create a unique temporary file path
        temp_video_path = 'temp_video.mp4'  # You can generate a unique filename if needed
        
        # Write the uploaded video data to the temporary file
        with open(temp_video_path, 'wb') as temp_video:
            for chunk in uploaded_video.chunks():
                temp_video.write(chunk)
        
        # Create a VideoCapture object to read the video file from disk
        cap = cv2.VideoCapture(temp_video_path)
        
        # Check if the VideoCapture object was initialized successfully
        if not cap.isOpened():
            return JsonResponse({"error": "Failed to open video file"})
        
        # Loop through the frames of the video
        while True:
            # Read a frame from the video
            ret, frame = cap.read()
            
            # Check if frame reading was successful
            if not ret:
                break  # Break the loop if no more frames are available
            
            # Display the frame
            cv2.imshow('Video', frame)
            
            # Check for key press (wait for 25 milliseconds)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break  # Break the loop if 'q' key is pressed
        
        # Release the VideoCapture object, delete the temporary file, and close all OpenCV windows
        cap.release()
        os.remove(temp_video_path)
        cv2.destroyAllWindows()
        
        return JsonResponse({"message": "Video playback completed"})
    else:
        return JsonResponse({"error": "No video file uploaded"})
    
def hello_world(request):
    return render(request, 'helloworld.html')


def webcam(request):
    return render(request, 'webcam.html')

def register(request):
    return render(request, 'register.html')


@csrf_exempt
@require_http_methods(["POST"])
def capture_image(request):
    if request.method == 'POST':
        try:
            # Parse JSON request body
            data = json.loads(request.body.decode('utf-8'))
            image_data = data.get('image_data')

            if image_data:
                # Decode the base64 encoded image data
                decoded_data = base64.b64decode(image_data.split(',')[1])

                # Process the image using cv2 (optional)
                np_arr = np.frombuffer(decoded_data, np.uint8)
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                # Resize the image (optional)
                width, height = 640, 480
                resized_img = cv2.resize(img, (width, height))

                # Save the resized image
                cv2.imwrite("fetched_image.jpg", resized_img)

                # Load images from folders
                known_folder = "known"
                unknown_folder = "unknown"

                # Perform face recognition
                try:
                    recognition = DeepFace.find(img_path="fetched_image.jpg", db_path="Data", model_name="VGG-Face", distance_metric="euclidean_l2",enforce_detection=True)
                    print(recognition)
                    # Handle recognition result
                    if recognition:
                        try:
                            identity = remove_data_jpg(recognition[0]['identity'][0])
                            return JsonResponse({'message': 'Image received successfully!', 'processed_data': None, 'recognition': identity})
                        except KeyError as e:
                            return JsonResponse({'message': 'Image received successfully!',"error":str(e), 'processed_data': None, 'recognition': 'Unknown'})
                    else:
                        return JsonResponse({'message': 'Image received successfully!', 'processed_data': None, 'recognition': 'Unknown'})
                except ValueError as e:
                    return JsonResponse({'message': 'Image received successfully!','error':str(e), 'processed_data': None, 'recognition': 'Unknown'})
            else:
                return JsonResponse({'error': 'Missing image data in request body','recognition': 'Unknown'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON','recognition': 'Unknown'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method (POST required)','recognition': 'Unknown'}, status=405)
    

def remove_data_jpg(string):

  start_index = string.find("\\") + 1  # Skip past leading "Data/"
  end_index = string.rfind(".")  # Find the last occurrence of "."
  if start_index != -1 and end_index != -1:
    return string[start_index:end_index]
  else:
    # Handle cases where "Data/" or ".jpg" is not present
    return string
  
@require_http_methods(["POST"])
def registerAPI(request):
    if request.method == 'POST':
        roll_no = request.POST.get('text-input', '')
        image_file = request.FILES.get('image-input', None)

        if roll_no and image_file:
            with open(f'Data/{roll_no}.jpg', 'wb') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)
            return JsonResponse({'message': 'Image received successfully!', 'recognition': 'Unknown'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid request data', 'recognition': 'Unknown'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed', 'recognition': 'Unknown'}, status=405)