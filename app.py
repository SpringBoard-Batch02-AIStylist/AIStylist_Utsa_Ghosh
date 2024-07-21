import numpy as np
import os
from PIL import Image
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import GlobalMaxPooling2D
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from numpy.linalg import norm
from sklearn.neighbors import NearestNeighbors
import pickle
import streamlit as st

# Custom CSS
custom_css = """
<style>
h1, h2, h3, h4, h5, h6 {
    color: #C8ACD6; 
}
</style>
"""

# Injecting custom CSS
st.markdown(custom_css, unsafe_allow_html=True)


# Loading features and filenames
feature_list = np.array(pickle.load(open('features.pkl', 'rb')))
filenames = pickle.load(open('images.pkl', 'rb'))


# model resnet50
model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
model.trainable = False

model = tf.keras.Sequential([
    model,
    GlobalMaxPooling2D()
])


st.title('AI Stylist Recommendation System')


def save_uploaded_file(uploaded_file):
    try:
        with open(os.path.join('upload', uploaded_file.name), 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return 1
    except:
        return 0

    
# feature extraction
def feature_extraction(img_path, model):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    result = model.predict(preprocessed_img, verbose=0).flatten()
    normalized_result = result / norm(result)
    return normalized_result


# finding nearest neighbours
def recommend(features, feature_list):
    neighbors = NearestNeighbors(n_neighbors=6, algorithm='brute', metric='euclidean')
    neighbors.fit(feature_list)
    distances, indices = neighbors.kneighbors([features])
    return indices


#Uploading and recommending
uploaded_file = st.file_uploader("Choose an image")

if uploaded_file is not None:
    if save_uploaded_file(uploaded_file):
        display_image = Image.open(uploaded_file)
        st.title('Uploaded Image')
        st.image(display_image,width=200)
        
        features = feature_extraction(os.path.join('upload', uploaded_file.name), model)
        
        indices = recommend(features, feature_list)
        
        st.title('Recommended Images')
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.image(filenames[indices[0][0]])
        with col2:
            st.image(filenames[indices[0][1]])
        with col3:
            st.image(filenames[indices[0][2]])
        with col4:
            st.image(filenames[indices[0][3]])
        with col5:
            st.image(filenames[indices[0][4]])
    else:
        st.header("Some error occurred in file upload")