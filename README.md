# myanimerecomendation
![Image](https://github.com/user-attachments/assets/25eb1747-fe1e-4abb-b0f5-18a3d08c9ce5)
I used 6,000 anime data collected by crawling 120 pages from the MyAnimeList website using async I/O and batching techniques. The crawled data was then processed using regex to extract anime links. These links were then used to fetch data via the MyAnimeList API.  

After obtaining the complete dataset, the 6,000 anime entries were processed using text processing techniques such as text cleaning, stopword removal, lemmatization, and text vectorization. Their similarity was then measured using two similarity algorithms: Jaccard and Cosine.  

To identify hidden gem anime, I applied a threshold to filter anime with a minimum rating as a standard for high-quality anime and a minimum popularity level to identify lesser-known anime.  

You can easily access my project at the link below:  
[https://myanimerecomendation-akbarhann.streamlit.app/](https://myanimerecomendation-akbarhann.streamlit.app/)

