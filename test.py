import pickle
import cv2
import os

# Folder where your images are stored
image_folder = 'static/dataset/CrimeNet/Subash'

# List to store images
images = []

# Read each image and store in list
for filename in os.listdir(image_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        img_path = os.path.join(image_folder, filename)
        img = cv2.imread(img_path)
        if img is not None:
            images.append(img)

# Save the list of images to a pickle file
with open('crimenet.pkl', 'wb') as f:
    pickle.dump(images, f)

print("Images have been pickled successfully!")
