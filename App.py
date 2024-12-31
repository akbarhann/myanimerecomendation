import pickle
import streamlit as st
import numpy as np
import aiohttp
from aiohttp import ClientSession
from asyncio import run, gather

async def fetch_poster_async(anime_id, client_id="62986d92d36fbc6807be6cda65390ad8"):
    url = f"https://api.myanimelist.net/v2/anime/{anime_id}?fields=main_picture"
    headers = {"X-MAL-CLIENT-ID": client_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("main_picture", {}).get("large", None)
            return None

async def fetch_posters_batch(anime_ids, client_id="62986d92d36fbc6807be6cda65390ad8", batch_size=10):
    results = []
    for i in range(0, len(anime_ids), batch_size):
        batch_ids = anime_ids[i:i+batch_size]
        tasks = [fetch_poster_async(anime_id, client_id) for anime_id in batch_ids]
        posters = await gather(*tasks)
        results.extend(posters)
    return results

# Load data from pickle files
anime = pickle.load(open('anime_list.pkl', 'rb'))
similiary = pickle.load(open('model_similiarity.pkl', 'rb'))
model_jaccard = pickle.load(open('model_jaccurd.pkl', 'rb'))
hidden_gem = pickle.load(open('hidden_gem_list.pkl','rb'))

anime_list_combined = np.union1d(anime['title'].values, hidden_gem['title'].values)

st.header('Your Anime Recommendation')

# Dropdown for selecting anime title
anime_dipilih = st.selectbox('Pilih judul anime', anime_list_combined)

# Dropdown for selecting similarity model
model_choice = st.selectbox(
    'Pilih model similarity:',
    ['Cosine Similarity', 'Jaccard Similarity']
)

# Initialize session state variables if they do not exist
if 'display_count' not in st.session_state:
    st.session_state.display_count = 5  # Start with 5 recommendations

if 'anime_name' not in st.session_state:
    st.session_state.anime_name = []

if 'anime_img' not in st.session_state:
    st.session_state.anime_img = []

if 'anime_links' not in st.session_state:  # Initialize anime_links
    st.session_state.anime_links = []


# Recommendation function
def recommend_combined(animex, model):
    if animex in hidden_gem['title'].values:
        idx = hidden_gem[hidden_gem['title'] == animex].index[0]
        sim = sorted(list(enumerate(model[idx])), reverse=True, key=lambda vector1: vector1[1])
        dataset = hidden_gem
    elif animex in anime['title'].values:
        idx = anime[anime['title'] == animex].index[0]
        sim = sorted(list(enumerate(model[idx])), reverse=True, key=lambda vector1: vector1[1])
        dataset = anime
    else:
        st.error(f"Anime '{animex}' tidak ditemukan.")
        return [], [], []

    anime_recom = []
    anime_ids = []
    anime_links = []
    
    # Ensure we do not access indices out of range
    for i in sim[1:21]:  # Take up to 20 recommendations
        if i[0] < len(dataset):  # Ensure index is within bounds
            anime_id = dataset.iloc[i[0]].anime_id
            title = dataset.iloc[i[0]].title
            # Add label if it is from hidden gem
            if title in hidden_gem['title'].values:
                title = f"🌟 {title}"
            anime_recom.append(title)
            anime_ids.append(anime_id)
            anime_links.append(f"https://myanimelist.net/anime/{anime_id}")
        else:
            continue  # Skip if index is out of range

    # Fetch posters asynchronously
    posters = run(fetch_posters_batch(anime_ids))

    return anime_recom, posters, anime_links


# Show recommendations button
if st.button('Show Recommend'):
    # Select model based on dropdown choice
    selected_model = similiary if model_choice == 'Cosine Similarity' else model_jaccard
    anime_name, anime_img, anime_links = recommend_combined(anime_dipilih, selected_model)
    st.session_state.anime_name = anime_name
    st.session_state.anime_img = anime_img
    st.session_state.anime_links = anime_links
    st.session_state.display_count = 5  # Reset number displayed

# Check if recommendations are in session state
if st.session_state.anime_name and st.session_state.anime_img:
    anime_name = st.session_state.anime_name
    anime_img = st.session_state.anime_img
    anime_links = st.session_state.anime_links
    display_count = st.session_state.display_count

    # Ensure both anime_name and anime_img have the same length
    if len(anime_name) != len(anime_img):
        st.error("Jumlah gambar anime tidak sesuai dengan jumlah judul anime.")
    else:
        # Display anime based on the number to show
        for row_start in range(0, display_count, 5):
            cols = st.columns(5)  # Create columns layout
            for i, col in enumerate(cols):
                idx = row_start + i
                if idx < len(anime_name):  # Ensure it does not exceed the list length
                    with col:
                        # Handle cases where the image may be None or invalid
                        if anime_img[idx]:
                            st.image(anime_img[idx], use_container_width=True)
                        else:
                            st.warning(f"Gambar tidak tersedia untuk {anime_name[idx]}")
                        # Display title as a link
                        st.markdown(f"[{anime_name[idx]}]({anime_links[idx]})", unsafe_allow_html=True)

        # Add "Show More" button if there are more recommendations
        if display_count < len(anime_name):
            if st.button('Tampilkan Lainnya'):
                st.session_state.display_count += 5  # Show 5 more recommendations
