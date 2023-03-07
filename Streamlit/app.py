import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from bcembedgen import tracks, embed_tracks_generator
# tracks(tag): returns dataframe
# embed_tracks_generator(tracks): takes in that dataframe, gives out another


st.set_page_config(page_title="Bandcamp Discover", page_icon=":tiger2:", layout="wide")

# Header

st.subheader('Bandcamp Discover')
st.title('Discover Bandcamp artists & tracks by tags')
title = st.text_input('Enter genre or tag', '')
st.write    ('e.g. house, deep house, funk. You entered ', title)
if title:
    temp = tracks(title)
    embeds = embed_tracks_generator(temp)

    if len(embeds) > 0:
        tracks = list(embeds.track_embed)

        components.html(
            html=
            f"""
            {tracks}
            """
            ,height=1400
            )
    else:
        st.write(f'{title} is not a valid keyword. Try again')