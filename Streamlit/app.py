import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Bandcamp Discover", page_icon=":musical_score:")

# Header
st.subheader('This is the subheader')
st.title('Default title text')

components.html(
    html=
    """
    <iframe style="border: 0; width: 350px; height: 470px;" src="https://bandcamp.com/EmbeddedPlayer/album=3966460462/size=large/bgcol=ffffff/linkcol=0687f5/tracklist=false/track=2459919090/transparent=true/" seamless><a href="https://fantasticman.bandcamp.com/album/visions-of-dance-vol-2">Beyond Control by Fantastic Man</a></iframe>
    """,
    height=600
)