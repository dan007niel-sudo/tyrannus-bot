import streamlit as st
import google.generativeai as genai

# --- 1. KONFIGURATION & DESIGN ---
st.set_page_config(
    page_title="Tyrannus Technik-Bot",
    page_icon="🎛️",
    layout="wide"
)

# --- SVT DESIGN SYSTEM (FINAL & BUGFIXED) ---
st.markdown("""
    <style>
    /* 1. GRUNDLAGE: Weißer Hintergrund */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* 2. TEXT-FARBE (Global Schwarz) */
    /* Wir setzen Text global auf Schwarz, aber schließen Icons aus */
    .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp li, .stApp span, .stApp div, .stApp label, .stMarkdown {
        color: #000000 !important; 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    }

    /* 3. SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #f4f4f4 !important;
        border-right: 1px solid #ddd;
    }
    section[data-testid="stSidebar"] * {
        color: #1c1c1c !important;
    }

    /* 4. BUTTONS (SCHWARZ MIT WEISSER SCHRIFT) */
    .stButton > button {
        background-color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 4px !important;
        transition: all 0.2s ease;
    }
    
    /* WICHTIG: Text im Button MUSS weiß sein */
    .stButton > button * {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Hover: Invertieren (Weißer Button, Schwarzer Text) */
    .stButton > button:hover {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
    }
    .stButton > button:hover * {
        color: #000000 !important;
    }

    /* 5. INPUTS & CHAT */
    .stTextInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #ccc !important;
    }
    
    /* HIER WAR DER FIX: Keine erzwungene Textfarbe, damit Icons funktionieren */
    .stChatMessage {
        background-color: #f8f9fa !important;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE INIT ---
if "mode" not in st.session_state:
    st.session_state.mode = None 

# --- 3. SICHERHEITSSCHLEUSE (PASSWORT) ---
def check_password():
    """Fragt das Passwort ab."""
    def password_entered():
        if st.session_state["password"] == "SVT2026": 
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔒 TEAM-LOGIN: Passwort", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔒 TEAM-LOGIN: Passwort", type="password", on_change=password_entered, key="password")
        st.error("Zugriff verweigert.")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- 4. SIDEBAR ---
with st.sidebar:
    try:
        st.image("svt_logo.jpg", use_container_width=True)
    except:
        st.markdown("<h2 style='text-align: center;'>SVT TECHNIK</h2>", unsafe_allow_html=True)
    
    st.markdown("### 📅 WOCHENPLAN")
    st.markdown("""
    **DO (Schule)**
    17:30 Aufbau | 19:00 Start
    
    **FR (Allnacht)**
    22:30 Treffen | 23:30 Start
    
    **SO (Briefing)**
    22:00 Weekly Call
    """)
    st.divider()
    
    if st.session_state.mode:
        if st.button("🔄 ZURÜCK"):
            st.session_state.mode = None
            st.session_state.messages = []
            st.rerun()

    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.markdown("<small>● System Online</small>", unsafe_allow_html=True)
    else:
        api_key = st.text_input("🔑 API Key", type="password")

# --- 5. MODUS-AUSWAHL ---
if st.session_state.mode is None:
    st.title("🎛️ TECHNIK-CENTER")
    st.markdown("##### WÄHLE DEINEN EINSATZBEREICH")
    st.write("---")
    
    col1, col2, col3 = st.columns(3)
    
    # HIER SIND DIE GEKÜRZTEN ÜBERSCHRIFTEN FÜR PERFEKTE AUSRICHTUNG
    with col1:
        st.markdown("**ONBOARDING**")
        st.caption("Einführung & Basics")
        if st.button("🚀 ONBOARDING STARTEN", use_container_width=True):
            st.session_state.mode = "onboarding"
            st.rerun()
            
    with col2:
        st.markdown("**LIVE-SUPPORT**")
        st.caption("Schnelle Lösungen")
        if st.button("🔥 LIVE-SUPPORT", use_container_width=True):
            st.session_state.mode = "live"
            st.rerun()
            
    with col3:
        st.markdown("**TRAINING**")
        st.caption("Deep Dives & Wissen")
        if st.button("🎓 SCHULUNG", use_container_width=True):
            st.session_state.mode = "training"
            st.rerun()

    st.stop() 

# --- 6. SYSTEM PROMPT ---
base_knowledge = """
Du bist der Technik-Bot der "Schule von Tyrannus" (SVT).

HARDWARE & KANAL-BELEGUNG (XR18):
- CH 01: Flow 8 (Input). WICHTIG: Dient NUR als Bluetooth-Empfänger für Handy-Musik!
- CH 02: Cajon.
- CH 03/04: Atmo (Raummikrofone für Stream).
- CH 09/10: Keys (Stereo).
- CH 11-13: Backing Vocals (BV).
- CH 14/15: Main Vocals (Leitung).
- CH 16: LEER / RESERVE (Nicht beachten).

MASTER-WORKFLOW & PROTOKOLLE:

1. ANKUNFT & POWER-UP
- Check: Raum, Tafel, Stifte, Kabelwege. Mikrofone reinigen & Aufsätze checken.
- STROM-SEQUENZ (WICHTIG ZUM SCHUTZ DER BOXEN): 
  1. Receiver & Peripherie AN.
  2. Mixer (XR18) AN. 
  3. ZULETZT: Boxen/Verstärker AN. (Verhindert Knallen).
- Licht: LED-Scheinwerfer an, Helligkeit/Farbtemperatur für Kamera prüfen.

2. AUDIO & LOGIC PRO
- Setup: MacBook Netzteil dran. Logic Projekt laden.
- Gain Staging: Zuerst Gain einpegeln, DANN Fader hoch.
- PFL/Peak: Kein Clipping (Rote Lampen vermeiden)!
- Aufnahme: Start ab Veranstaltungsbeginn (spätestens 19:00).

3. ZOOM & STREAM
- Vorbereitung: WLAN Check, WhatsApp Link öffnen, Banner in Canva.
- AUDIO-SETTINGS (Zoom):
  - Lautsprecher: MacBook (aber MUTE am Laptop, sonst Feedback).
  - Mikrofon-Input: XR18 (USB Interface).
  - Features: "Originalton für Musiker" = AN, "Hintergrundgeräusche" = NIEDRIG.
  - Optionen 1 & 3 müssen ausgewählt sein.
- VIDEO-SETTINGS:
  - Kamera: Wechsel auf OBSBOT / Stream-Cam.
  - Check: Fokus & Bildausschnitt (Gerade?).

4. PRÄSENTATION (OpenLP)
- Inhalt: Bibelverse (richtige Übersetzung!) und Banner laden.
- Display: Prüfen, ob OpenLP korrekt auf dem Beamer liegt.

5. ABBAU (PROTOCOL)
- STROM-SEQUENZ:
  1. ZUERST: Boxen AUS.
  2. DANN: Mixer & Rest AUS.
- Daten: Logic stoppen, speichern. Datei via WeTransfer hochladen.
- Ordnung: Batterien raus, Mikros reinigen, Kabel ordentlich wickeln.
"""

if st.session_state.mode == "onboarding":
    mode_instruction = """
    MODUS: ONBOARDING.
    Ziel: Mentor für neue Teammitglieder.
    Stil: Freundlich, erklärend, Schritt-für-Schritt.
    Start: Frage nach Namen und Interesse (Ton/Licht/Video). Führe dann durch Phase 1 des Workflows.
    """
elif st.session_state.mode == "live":
    mode_instruction = """
    MODUS: LIVE SUPPORT.
    Ziel: Sofortige Problemlösung.
    Stil: Kurz, direkt, Befehlston. Keine Theorie.
    Regel: Nutze den Workflow oben als Checkliste zur Fehlerfindung. Priorität: Signalfluss wiederherstellen.
    """
elif st.session_state.mode == "training":
    mode_instruction = """
    MODUS: SCHULUNG.
    Ziel: Wissensvermittlung.
    Stil: Geduldig, tiefgehend.
    Methode: Wenn eine Frage kommt, erkläre nicht nur WAS zu tun ist (laut Workflow), sondern WARUM (Signalfluss, Physik).
    """

final_system_prompt = base_knowledge + "\n" + mode_instruction

# --- 7. CHAT LOGIK ---
st.title(f"TECHNIK-BOT: {st.session_state.mode.upper()}")

if api_key:
    genai.configure(api_key=api_key)
    
    # WICHTIG: Verwende 'gemini-flash-latest' für Stabilität
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest", 
        system_instruction=final_system_prompt
    )

    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        st.session_state.messages = []
        if st.session_state.mode == "onboarding":
            welcome = "Willkommen im Team! Ich bin dein Technik-Mentor. Wie heißt du und wo willst du starten?"
        elif st.session_state.mode == "live":
            welcome = "System bereit. Was ist das Problem?"
        else:
            welcome = "Schulung bereit. Welches Thema aus dem Workflow wollen wir vertiefen?"
        st.session_state.messages.append({"role": "model", "parts": [welcome]})

    for message in st.session_state.messages:
        with st.chat_message("user" if message["role"] == "user" else "assistant"):
            st.write(message["parts"][0])

    if prompt := st.chat_input("Eingabe..."):
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "parts": [prompt]})
        
        history = [{"role": m["role"], "parts": m["parts"]} for m in st.session_state.messages if m["role"] != "system"]
        
        try:
            chat = model.start_chat(history=history[:-1])
            with st.spinner("..."):
                response = chat.send_message(prompt)
            
            st.chat_message("assistant").write(response.text)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
            
        except Exception as e:
            st.error(f"⚠️ Verbindungsfehler: {e}. Bitte versuche es erneut.")
