import requests
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


    
anime = pickle.load(open('anime_list.pkl', 'rb'))
similiary = pickle.load(open('model_similiarity.pkl', 'rb'))
model_jaccard = pickle.load(open('model_jaccurd.pkl', 'rb'))
hidden_gem = pickle.load(open('hidden_gem_list.pkl','rb'))

anime_list_combined = np.union1d(anime['title'].values, hidden_gem['title'].values)


st.header('Your Anime Recommendation')

anime_dipilih = st.selectbox('Pilih judul anime', anime_list_combined)

# Dropdown untuk memilih model
model_choice = st.selectbox(
    'Pilih model similarity:',
    ['Cosine Similarity', 'Jaccard Similarity']
)

# Simpan indeks awal di session_state
if 'display_count' not in st.session_state:
    st.session_state.display_count = 5  # Mulai dengan 5 rekomendasi

if 'anime_name' not in st.session_state:
    st.session_state.anime_name = []

if 'anime_img' not in st.session_state:
    st.session_state.anime_img = []

if 'anime_links' not in st.session_state:  # Inisialisasi anime_links
    st.session_state.anime_links = []


# Fungsi rekomendasi
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
    for i in sim[1:21]:  # Ambil hingga 20 rekomendasi
        anime_id = dataset.iloc[i[0]].anime_id
        title = dataset.iloc[i[0]].title
        # Tambahkan label jika berasal dari hidden gem
        if title in hidden_gem['title'].values:
            title = f"🌟 {title}"
        anime_recom.append(title)
        anime_ids.append(anime_id)
        anime_links.append(f"https://myanimelist.net/anime/{anime_id}")

    # Fetch posters asynchronously
    posters = run(fetch_posters_batch(anime_ids))

    return anime_recom, posters, anime_links




# Tombol Show Recommend
if st.button('Show Recommend'):
    # Pilih model berdasarkan dropdown
    selected_model = similiary if model_choice == 'Cosine Similarity' else model_jaccard
    anime_name, anime_img, anime_links = recommend_combined(anime_dipilih, selected_model)
    st.session_state.anime_name = anime_name
    st.session_state.anime_img = anime_img
    st.session_state.anime_links = anime_links
    st.session_state.display_count = 5  # Reset jumlah yang ditampilkan
  # Reset jumlah yang ditampilkan



# Periksa apakah ada rekomendasi di session_state
if st.session_state.anime_name and st.session_state.anime_img:
    anime_name = st.session_state.anime_name
    anime_img = st.session_state.anime_img
    anime_links = st.session_state.anime_links
    display_count = st.session_state.display_count

    # Tampilkan anime berdasarkan jumlah yang telah ditentukan
    for row_start in range(0, display_count, 5):
        cols = st.columns(5, gap="medium")  # Membuat layout kolom
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(anime_name):  # Pastikan tidak melebihi panjang daftar
                with col:
                    st.image(anime_img[idx], use_container_width=True)
                    # Tampilkan judul sebagai link
                    st.markdown(f"[{anime_name[idx]}]({anime_links[idx]})", unsafe_allow_html=True)

    # Tambahkan tombol "Tampilkan Lainnya" jika masih ada rekomendasi tersisa
    if display_count < len(anime_name):
        if st.button('Tampilkan Lainnya'):
            st.session_state.display_count += 5  # Tambah jumlah yang ditampilkan
