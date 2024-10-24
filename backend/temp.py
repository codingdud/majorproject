import os

if not os.path.isfile('shape_predictor_68_face_landmarks.dat'):
    print("File not found!")
else:
    print("File found!")
