import streamlit as st
import pickle
import pandas as pd
import requests
import os
import gdown  # Import gdown to download from Google Drive

# 🔹 Google Drive link for similarity.pkl
GDRIVE_FILE_ID = "1z1Bg00HOpfmXnGaZ0zkJrJqLOevvoU59"
GDRIVE_URL = f"https://drive.google.com/uc?export=download&id={GDRIVE_FILE_ID}"

# 🔹 Download similarity.pkl if not already present
SIMILARITY_FILE = "similarity.pkl"

if not os.path.exists(SIMILARITY_FILE):
    st.info("Downloading similarity.pkl from Google Drive...")
    gdown.download(GDRIVE_URL, SIMILARITY_FILE, quiet=False)

# 🔹 Load movie data
try:
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open(SIMILARITY_FILE, 'rb'))
except Exception as e:
    st.error(f"Error loading movie data: {e}")
    st.stop()

# 🔹 Function to fetch movie poster
api = os.getenv("TMDB_API_KEY", "50a6e096ab32b0c22fd46acf52d9578c")

def fetch_poster(movie_id):
    try:
        # Fetch the TMDB API for movie poster and details
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api}&language=en-US"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return "https://via.placeholder.com/500x750?text=No+Image"
        data = response.json()
        return f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else "https://via.placeholder.com/500x750?text=No+Image"
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750?text=No+Image"

# 🔹 Recommendation Function
def recommend(movie):
    if movie not in movies['title'].values:
        return [], []

    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        
        recommended_movies = []
        recommended_movies_posters = []
        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(fetch_poster(movie_id))

        return recommended_movies, recommended_movies_posters
    except Exception as e:
        st.error(f"Error: {e}")
        return [], []

# 🔹 Streamlit UI
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox("Which movie's recommendation do you want?", movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    if names:
        cols = st.columns(len(names))
        for i in range(len(names)):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])
    else:
        st.warning("No recommendations found. Try another movie.")
