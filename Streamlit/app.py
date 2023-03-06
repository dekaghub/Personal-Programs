import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from bcembedgen import tracks, embed_tracks_generator
# tracks(tag): returns dataframe
# embed_tracks_generator(tracks): takes in that dataframe, gives out another


st.set_page_config(page_title="Bandcamp Discover", page_icon=":musical_score:", layout="wide")

# Header

st.subheader('This is the subheader')
st.title('Default title text')
title = st.text_input('Enter genre or tag', 'house')
st.write('house, deep house, funk. You entered ', title)
temp = tracks(title)
embeds = embed_tracks_generator(temp)


tracks = list(embeds.track_embed)

components.html(
    html=
    f"""
    {tracks}
    """,
    height=1000
    )
# for item in t:
#     components.html(
#         html=
#         f"""
#         {item}
#         """,
#         height=1000
#     )