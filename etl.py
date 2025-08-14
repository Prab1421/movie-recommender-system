import pandas as pd
import requests
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ===================== CONFIG =====================
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "50a6e096ab32b0c22fd46acf52d9578c")  # API key from environment
BASE_URL = "https://api.themoviedb.org/3/movie"
KAGGLE_DATA_PATH = "movies.csv"  # Kaggle dataset file
OUTPUT_CLEAN_DATA = "movies_clean.csv"
OUTPUT_SIM_MATRIX = "similarity_matrix.pkl"
LIMIT_MOVIES = 100  # for demo / avoid API rate limits
# ===================================================

def extract_data():
    """Extract from Kaggle CSV and TMDb API"""
    print("Reading Kaggle dataset...")
    df = pd.read_csv(KAGGLE_DATA_PATH)

    print("Fetching extra data from TMDb API...")
    extra_genres = {}
    count = 0
    for movie_id in df['id']:
        if count >= LIMIT_MOVIES:
            break
        url = f"{BASE_URL}/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        try:
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                genres = [g['name'] for g in data.get('genres', [])]
                extra_genres[movie_id] = " ".join(genres)
            else:
                extra_genres[movie_id] = ""
        except Exception as e:
            print(f"Error fetching {movie_id}: {e}")
            extra_genres[movie_id] = ""
        count += 1

    # Add genres column to DataFrame
    df['genres'] = df['id'].map(extra_genres)
    return df

def transform_data(df):
    """Clean, combine features, and compute similarity"""
    print("Cleaning data...")
    df['overview'] = df['overview'].fillna("")
    df['genres'] = df['genres'].fillna("")

    # Combine into single feature string
    df['combined_features'] = df['overview'] + " " + df['genres']

    print("Vectorizing with TF-IDF...")
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['combined_features'])

    print("Computing cosine similarity...")
    sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    return df, sim_matrix

def load_data(df, sim_matrix):
    """Save cleaned data and similarity matrix"""
    print("Saving cleaned data and similarity matrix...")
    df.to_csv(OUTPUT_CLEAN_DATA, index=False)
    pd.to_pickle(sim_matrix, OUTPUT_SIM_MATRIX)
    print(f"Data saved to {OUTPUT_CLEAN_DATA} and {OUTPUT_SIM_MATRIX}")

def run_etl():
    """Run the full ETL pipeline"""
    print("ETL started...")
    df = extract_data()
    df_clean, sim_matrix = transform_data(df)
    load_data(df_clean, sim_matrix)
    print("ETL finished.")

if __name__ == "__main__":
    run_etl()
