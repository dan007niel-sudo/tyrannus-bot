import streamlit as st
import google.generativeai as genai

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Tyrannus Technik-Bot", page_icon="🎛️", layout="wide")

# --- 2. SESSION STATE INIT ---
if "mode" not in st.session_state:
    st.session_state.mode = None 

# --- 3. SIDEBAR ---
with st.sidebar:
    try:
        # Check ob Logo existiert, sonst Warnung statt Absturz
        st.image("svt_logo.jpg", use_container_width=True)
    except:
        st.warning("⚠️ Datei 'svt_logo.jpg' fehlt im Ordner.")
    
    st.header("📅 Wochenplan")
    st.markdown("""
    **DO (Schule)**
    17:30 Aufbau | 19:00 Start
    
    **FR (Allnacht)**
    22:30 Treffen | 23:30 Start
    
    **SO (Briefing)**
    22:00 Weekly Call
    """)
    st.divider()
    
    # Reset Button (Um Modus zu wechseln)
    if st.session_state.mode:
        if st.button("🔄 Modus wechseln"):
            st.session_state.mode = None
            st.session_state.messages = []
            st.rerun()

    # API Key Handling
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("System: Online 🟢")
    else:
        api_key = st.text_input("🔑 Google API Key", type="password")

# --- 4. MODUS-AUSWAHL ---
if st.session_state.mode is None:
    st.title("🎛️ Tyrannus Technik-Center")
    st.write("### Wähle deinen Einsatzbereich:")
    st.write("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Für neue Teammitglieder**")
        st.markdown("_Ich führe dich Schritt-für-Schritt ins Team und die Technik ein._")
        if st.button("🚀 Onboarding Starten", use_container_width=True):
            st.session_state.mode = "onboarding"
            st.rerun()
            
    with col2:
        st.error("**Während der Veranstaltung**")
        st.markdown("_Ich liefere dir sofortige Lösungen, wenn es brennt – ohne Gelaber._")
        if st.button("🔥 Live-Support (Notfall)", use_container_width=True):
            st.session_state.mode = "live"
            st.rerun()
            
    with col3:
        st.success("**Lernen & Verstehen**")
        st.markdown("_Ich erkläre dir Zusammenhänge und mache dich zum Profi._")
        if st.button("🎓 Schulung / Deep Dive", use_container_width=True):
            st.session_state.mode = "training"
            st.rerun()

    st.stop() # Stoppt hier, bis ein Button gedrückt wird

# --- 5. SYSTEM PROMPT (DAS GEHIRN) ---

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

# Dynamische Anweisungen je nach Modus
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

# --- 6. CHAT LOGIK ---
st.title(f"Technik-Bot: {st.session_state.mode.upper()}")

if api_key:
    # Konfiguration
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=final_system_prompt)

    # Initiale Nachricht (Nur beim ersten Start des Modus)
    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        st.session_state.messages = []
        if st.session_state.mode == "onboarding":
            welcome = "Willkommen im Team! Ich bin dein Technik-Mentor. Wie heißt du und wo willst du starten?"
        elif st.session_state.mode == "live":
            welcome = "System bereit. Was ist das Problem?"
        else:
            welcome = "Schulung bereit. Welches Thema aus dem Workflow wollen wir vertiefen?"
        st.session_state.messages.append({"role": "model", "parts": [welcome]})

    # Chat Verlauf anzeigen
    for message in st.session_state.messages:
        with st.chat_message("user" if message["role"] == "user" else "assistant"):
            st.write(message["parts"][0])

    # User Input verarbeiten
    if prompt := st.chat_input("Eingabe..."):
        # 1. User Input anzeigen
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "parts": [prompt]})
        
        # 2. History für API vorbereiten (System-Prompt wird automatisch durch model-init gehändelt)
        history = [{"role": m["role"], "parts": m["parts"]} for m in st.session_state.messages if m["role"] != "system"]
        
        # 3. API Anfrage
        try:
            # history[:-1] nimmt alles außer dem gerade getippten Prompt als Kontext
            chat = model.start_chat(history=history[:-1])
            
            with st.spinner("Verarbeite..."):
                response = chat.send_message(prompt)
            
            # 4. Antwort anzeigen
            st.chat_message("assistant").write(response.text)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
            
        except Exception as e:
            st.error(f"⚠️ Verbindungsfehler: {e}. Bitte versuche es erneut.")
