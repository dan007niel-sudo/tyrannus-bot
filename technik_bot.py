import streamlit as st
import google.generativeai as genai

# --- KONFIGURATION ---
# Titel der App
st.set_page_config(page_title="Tyrannus Technik-Bot", page_icon="🎛️")

# --- NEU: Großes Logo über dem Titel ---
# width=300 ist die Breite in Pixeln. Spiel damit rum (z.B. 200 oder 400).
try:
    st.image("svt_logo.jpg", width=300)
except FileNotFoundError:
    st.warning("Logo 'svt_logo.jpg' nicht gefunden.")

st.title("🎛️ Tyrannus Technik-Support")
st.caption("Dein KI-Kollege für XR18, Logic & Stream")

# Sidebar für API Key (damit du ihn nicht im Code speichern musst)
with st.sidebar:
    api_key = st.text_input("Gib deinen Google API Key ein", type="password")
    st.markdown("[Hier API Key holen](https://aistudio.google.com/app/apikey)")
    if not api_key:
        st.warning("Bitte API Key eingeben, um zu starten.")

# --- SYSTEM PROMPT (Das Gehirn) ---
system_instruction = """
Du bist der Voice Agent des Technik-Teams der "Schule von Tyrannus".
Deine Mission: Du sicherst den technischen Erfolg von Veranstaltungen.
Haltung: Fachlich präzise, entspannt, motivierend.

HARDWARE & SOFTWARE WISSEN:
- Mixer: Behringer XR18. Kanal 1: Flow8/BT, 2: Cajon, 3/4: Room, 9/10: Keys, 11-13: BV, 14/15: Main Vocals.
- Routing: BUS 1/2 Monitore, BUS 3/4 Stream.
- FX: FX1 Delay, FX2 Hall (Vocals), FX3 Mod Delay, FX4 Chorus.
- Zoom: Originalton AN, Geräuschunterdrückung NIEDRIG.
- Logic Pro: Aufnahme Start strikt 18:30 Uhr.
- Zeiten: 18:00 Soundcheck Raum, 18:30 Soundcheck Stream.

REGELN:
- Fasse dich kurz (Voice-optimiert).
- Keine Listen vorlesen, sondern Schritt-für-Schritt führen.
- Frage nach, wenn Infos fehlen.
- Keine physischen Aktionen, nur Anleitung.
"""

# --- LOGIK ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Modell laden (Gemini 1.5 Flash ist schnell und günstig)
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=system_instruction
        )

        # Chat-History initialisieren, falls noch nicht vorhanden
        if "messages" not in st.session_state:
            st.session_state.messages = []
            # Begrüßung vom Bot faken
            st.session_state.messages.append({"role": "model", "parts": ["Moin! Alles klar am Pult? Wo brennt's gerade?"]})

        # Chat-Verlauf anzeigen
        for message in st.session_state.messages:
            with st.chat_message("user" if message["role"] == "user" else "assistant"):
                st.write(message["parts"][0])

        # Eingabefeld für den User
        if prompt := st.chat_input("Frage stellen (z.B. 'Ich hab Feedback auf dem Monitor')..."):
            
            # User-Nachricht anzeigen und speichern
            st.chat_message("user").write(prompt)
            st.session_state.messages.append({"role": "user", "parts": [prompt]})

            # Chat-Objekt erstellen mit History
            history_for_gemini = [
                {"role": m["role"], "parts": m["parts"]} 
                for m in st.session_state.messages 
                if m["role"] != "system" # System prompt ist separat
            ]
            
            chat = model.start_chat(history=history_for_gemini[:-1]) # History ohne die letzte Nachricht laden
            
            # Antwort generieren
            with st.spinner("Checke Handbücher..."):
                response = chat.send_message(prompt)
            
            # Bot-Antwort anzeigen und speichern
            st.chat_message("assistant").write(response.text)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})

    except Exception as e:
        st.error(f"Fehler: {e}")