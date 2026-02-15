import streamlit as st
import pickle
import pandas as pd
import requests

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

# ---------------- API FUNCTIONS ----------------
def fetch_poster(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}",
        params={
            "api_key": "4a67736c0e04819457ec5e9b7bd576e0",
            "language": "en-US"
        }
    )
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]


def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": "4a67736c0e04819457ec5e9b7bd576e0",
        "language": "en-US",
        "append_to_response": "credits"
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None
    return response.json()

# ---------------- RECOMMENDATION ----------------
def recommend(movie):
    movie_idx = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_idx]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    names, posters, movie_ids = [], [], []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        names.append(movies.iloc[i[0]]["title"])
        posters.append(fetch_poster(movie_id))
        movie_ids.append(movie_id)

    return names, posters, movie_ids

# ---------------- LOAD DATA ----------------
similarity = pickle.load(open("similarity.pkl", "rb"))
movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

# ================= HOME PAGE =================
if st.session_state.page == "home":

    st.title("Movie Recommender System")

    selected_movie_name = st.selectbox(
        "What is your favorite movie?",
        movies["title"].values
    )

    if st.button("Recommend"):
        st.session_state.recommendations = recommend(selected_movie_name)

    if st.session_state.recommendations:
        names, posters, movie_ids = st.session_state.recommendations
        cols = st.columns(5)

        for i in range(5):
            with cols[i]:
                st.image(posters[i])
                if st.button(names[i], key=movie_ids[i]):
                    st.session_state.movie_id = movie_ids[i]
                    st.session_state.page = "details"

# ================= DETAIL PAGE =================
if st.session_state.page == "details":

    data = fetch_movie_details(st.session_state.movie_id)

    if data:
        st.image("https://image.tmdb.org/t/p/w500/" + data["poster_path"])
        st.title(data["title"])

        st.write("⭐ Rating:", data["vote_average"])
        st.write("📅 Release Date:", data["release_date"])
        st.write("⏱ Runtime:", data["runtime"], "minutes")

        st.subheader("Overview")
        st.write(data["overview"])

        st.subheader("Top Cast")
        for cast in data["credits"]["cast"][:5]:
            st.write(f"{cast['name']} as {cast['character']}")
    else:
        st.error("Movie details not found.")

    if st.button("⬅ Back"):
        st.session_state.page = "home"
        st.session_state.recommendations = None
