import os
import streamlit as st
import tempfile
from models.claude import ClaudeAPI
from models.translator import Translator
from models.elevenlabs import ElevenLabsAPI
try:
    from config import CREDENTIALS
except ImportError:
    CREDENTIALS = {
        "username": st.secrets["credentials"]["username"],
        "password": st.secrets["credentials"]["password"]
    }
from dotenv import load_dotenv
load_dotenv()

# Initialize API keys
def get_api_key(key_name):
    """Get API key from environment or streamlit secrets"""
    return os.getenv(key_name) or st.secrets[key_name]

ELEVENLABS_API_KEY = get_api_key("ELEVENLABS_API_KEY")
CLAUDE_API_KEY = get_api_key("CLAUDE_API_KEY")

# Security functions
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] == CREDENTIALS["username"]
            and st.session_state["password"] == CREDENTIALS["password"]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
            del st.session_state["username"]  # Don't store username
        else:
            st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
            st.session_state["username"] = ""  # Clear username
            st.session_state["password"] = ""  # Clear password
            return False

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        # First run, show input for password
        st.set_page_config(layout="wide", page_title="Système de génération d'avis de décès")
        
        st.markdown("""
        <style>
            .stButton button {
                width: 100%;
            }
            .centered {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            div[data-testid="stToolbar"] {
                display: none;
            }
            footer {
                display: none;
            }
            #MainMenu {
                display: none;
            }
            .stAlert {
                margin-top: 1rem;
                margin-bottom: 1rem;
            }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("## Connexion")
            st.text_input("Nom d'utilisateur", key="username")
            st.text_input("Mot de passe", type="password", key="password")
            st.button("Se connecter", on_click=password_entered)
        return False
    
    return True

def clear_session_state():
    """Clear all relevant session state variables"""
    keys_to_clear = [
        'info_dict', 
        'original_obituary', 
        'edited_obituary', 
        'translations', 
        'audio_files'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clean up audio files
    if 'temp_audio_files' in st.session_state:
        for temp_file in st.session_state.temp_audio_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass
        st.session_state.temp_audio_files = []

# Initialize APIs
@st.cache_resource
def initialize_apis():
    claude_api = ClaudeAPI(CLAUDE_API_KEY)
    translator = Translator()
    elevenlabs_api = ElevenLabsAPI(ELEVENLABS_API_KEY)
    return claude_api, translator, elevenlabs_api

def main():
    st.set_page_config(page_title="Avis de décès")
    
    if st.button("Déconnexion"):
        st.session_state["password_correct"] = False
        st.rerun()
        
    

    st.title("Avis de décès")

    if st.button("Rafraîchir"):
            clear_session_state()
            st.rerun()

    # Initialize APIs
    claude_api, translator, elevenlabs_api = initialize_apis()

    # Initialize session state variables
    if 'info_dict' not in st.session_state:
        st.session_state.info_dict = None
    if 'original_obituary' not in st.session_state:
        st.session_state.original_obituary = None
    if 'edited_obituary' not in st.session_state:
        st.session_state.edited_obituary = None
    if 'translations' not in st.session_state:
        st.session_state.translations = {}
    if 'temp_audio_files' not in st.session_state:
        st.session_state.temp_audio_files = []




    # Form for collecting information
    with st.form("obituary_form"):
        gender = st.selectbox(
            "Titre",
            options=[
                "M.",        # Monsieur
                "Mme",       # Madame
            ]
        )
        name = st.text_input("Nom complet du sujet")
        age = st.number_input("Âge", min_value=0, max_value=120)
        date_of_death = st.date_input("Date du décès")
        children = st.number_input("Nombre d'enfants", min_value=0)
        grandchildren = st.number_input("Nombre de petits-enfants", min_value=0)
        interests = st.text_area("Intérêts et passions")
        profession = st.text_input("Profession")
        date_of_ceremonie = st.date_input("Date de la cérémonie")
        
        # Add tone selection
        tone = st.selectbox(
            "Choisir le ton de l'avis",
            options=[
                "Formel et respectueux",
                "Chaleureux et empathique",
                "Traditionnel",
                "Narratif"
            ],
            help="Sélectionnez le style d'écriture pour l'avis de décès"
        )
        notes = st.text_area("Notes supplémentaires")

        submit_button = st.form_submit_button("Générer l'avis de décès")

    if submit_button:
        # Prepare info dictionary
        st.session_state.info_dict = {
            'title': gender,
            'name': name,
            'age': age,
            'date_of_death': date_of_death.strftime("%d/%m/%Y"),
            'children': children,
            'grandchildren': grandchildren,
            'interests': interests,
            'profession': profession,
            'date_of_ceremonie': date_of_ceremonie,
            'tone': tone, 
            'notes': notes
        }


        # Generate obituary
        with st.spinner("Génération de l'avis de décès..."):
            st.session_state.original_obituary = claude_api.generate_obituary(st.session_state.info_dict)
            st.session_state.edited_obituary = st.session_state.original_obituary
            st.session_state.translations = {}

    # Translation section with improved UI
    if st.session_state.original_obituary is not None:
        st.subheader("Avis de décès")
        # Calculate height based on number of lines (approximate)
        st.session_state.edited_obituary = st.text_area(
            "Modifier l'avis si nécessaire", 
            value=st.session_state.edited_obituary,
            height=400
        )

        # Translation section with improved UI
        st.markdown("---")
        st.subheader("Traductions")
        
        # Language selection in a more compact format
        st.markdown("### Sélection de la langue")

        lang1 = st.selectbox(
                "Langue à traduire",
                list(translator.available_languages.keys()),
                key="lang1"
            )
            

        if st.button("Traduire", use_container_width=True):
            
            with st.spinner("Traduction en cours..."):
                translated = translator.translate_text(
                        st.session_state.edited_obituary, 
                        translator.available_languages[lang1]
                    )
                st.session_state.translations[lang1] = translated
                    

        # Display translations in full width
        if st.session_state.translations:
            st.markdown("### Versions traduites")
            if lang1 in st.session_state.translations:
                translated_text = st.session_state.translations[lang1]
                st.markdown(f"**Version {lang1}**")
                st.text_area(
                    "",
                    value=translated_text,
                    height=400,
                    key=f"translation_{lang1}",
                    label_visibility="collapsed"
                )
                st.markdown("---")
                
    # Audio generation section
    if st.session_state.original_obituary is not None:
        st.markdown("---")
        st.subheader("Génération Audio")
        voice_selection = st.selectbox(
            "Choisir une voix",
            list(ElevenLabsAPI.VOICES.keys())
        )

        if st.button("Générer l'audio dans toutes les langues", use_container_width=True):
            # Dictionary to store audio files for each language
            st.session_state.audio_files = {}
            
            # Clean up previous temp files
            for temp_file in st.session_state.temp_audio_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    st.error(f"Error removing temporary file: {e}")
            st.session_state.temp_audio_files = []
            
            with st.spinner("Génération des fichiers audio..."):
                # Generate French audio
                french_audio = elevenlabs_api.text_to_speech_stream(
                    st.session_state.edited_obituary,
                    ElevenLabsAPI.VOICES[voice_selection],
                    language_code="fr"
                )
                if french_audio:
                    st.session_state.audio_files['Français'] = french_audio
                    st.session_state.temp_audio_files.append(french_audio)

                # Generate audio for translated versions
                if lang1 in st.session_state.translations:
                    audio_file = elevenlabs_api.text_to_speech_stream(
                        st.session_state.translations[lang1],
                        ElevenLabsAPI.VOICES[voice_selection],
                        language_code=translator.available_languages[lang1]
                    )
                    if audio_file:
                        st.session_state.audio_files[lang1] = audio_file
                        st.session_state.temp_audio_files.append(audio_file)

            # Display all generated audio files
            if st.session_state.audio_files:
                st.markdown("### Versions audio")
                for language, audio_file in st.session_state.audio_files.items():
                    st.markdown(f"**Version {language}:**")
                    st.audio(audio_file)
                    st.markdown("---")

        # Clear audio files when generating new notice
        if submit_button and 'audio_files' in st.session_state:
            for temp_file in st.session_state.temp_audio_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception:
                    pass
            st.session_state.temp_audio_files = []
            del st.session_state.audio_files

if __name__ == "__main__":
    if check_password():
        main()