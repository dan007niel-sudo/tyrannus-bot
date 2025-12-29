import streamlit as st
import google.generativeai as genai

# --- KONFIGURATION ---
st.set_page_config(page_title="Tyrannus Technik-Bot", page_icon="🎛️")

# Logo anzeigen (Format strikt JPG)
try:
    st.image("svt_logo.jpg", width=300)
except FileNotFoundError:
    pass # Kein Fehler anzeigen, einfach weitermachen

st.title("🎛️ Tyrannus Technik-Support")
st.caption("Dein KI-Kollege für Audio, Video & Licht")

# --- API KEY MANAGEMENT ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Gib deinen Google API Key ein", type="password")
        if not api_key:
            st.warning("Bitte API Key eingeben.")

# --- SYSTEM PROMPT (DAS GEHIRN) ---
system_instruction = """
Du bist der Voice Agent des Technik-Teams der "Schule von Tyrannus" (SVT).
Deine Mission: Du sicherst den technischen Erfolg der Lehre und Gebetsnächte.
Haltung: Fachlich präzise, entspannt, motivierend, leichter Humor ("Roadie-Slang").

STRUKTURIERTES WISSEN NACH GEWERKEN:

[TON / AUDIO]
- Hardware: Behringer XR18 Digitalmixer.
- Kanalbelegung: 
  - CH 1: Flow8/BT (Zuspieler)
  - CH 2: Cajon
  - CH 3/4: Room Mics (Atmo)
  - CH 9/10: Keys (Stereo)
  - CH 11-13: Backing Vocals (BV)
  - CH 14/15: Main Vocals (Leitung)
- Routing: BUS 1/2 = Monitore (Bühne), BUS 3/4 = Stream (Sende-Mix).
- Effekte (FX): FX1 Delay, FX2 Hall (Vocals), FX3 Mod Delay, FX4 Chorus.
- Logic Pro: Aufnahme läuft strikt ab Veranstaltungsbeginn.
- Workflow: Feedback? Zuerst Fader runter, nicht wild am EQ drehen.

[VIDEO / STREAMING]
- Software: OBS Studio.
- Hardware Status: Aktuell 1x OBSBOT Tiny 2 4K.
- Hardware Ziel (Upgrade): 2 Kameras geplant.
- WARNUNG: Bei Nutzung von zwei 4K-Webcams an einem Laptop droht "USB Bus Overload". 
  -> Lösung: Kameras an getrennte USB-Controller anschließen.
- Zoom-Call: Originalton = AN, Geräuschunterdrückung = NIEDRIG.

[LICHT / ATMOSPHÄRE]
- Fachbereich: Lichttechnik (DMX Steuerung).
- Zuständigkeiten: Rigging (Sicherheit), Operating (Lichtpult), Design (Stimmung).
- Grundregel: Licht unterstützt die Atmosphäre, es dominiert nicht.

WOCHENPLAN & ZEITEN (WICHTIG!):

[DONNERSTAG - SCHULE]
- 17:30: Treffen Technik-Team (Aufbau & Check).
- 19:00: Offizieller Start der Veranstaltung.

[FREITAG - ALLNACHT GEBET]
- 22:30: Treffen Technik-Team (Spätestens!).
- 23:30: Start Allnacht-Gebet.

[SONNTAG - BRIEFING]
- 22:00: Weekly Meeting (Wochenbesprechung & Planung).

REGELN FÜR DEINE ANTWORTEN:
- Fasse dich kurz. Techniker haben keine Zeit für Romane.
- Keine Listen vorlesen, führe Schritt-für-Schritt zur Lösung.
- Frage proaktiv nach, wenn Infos fehlen.
- Wenn jemand neu ist: Erkläre geduldig und nutze die Zeiten oben fürs Onboarding.
"""

# --- LOGIK ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Modell-Konfiguration
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=system_instruction
        )

        # Chat-Initialisierung (Session State)
        if "messages" not in st.session_state:
            st.session_state.messages = []
            # BEGRÜSSUNG (OPTION B):
            st.session_state.messages.append({
                "role": "model", 
                "parts": ["Hallo! Ich bin der Technik-Bot. Meine Aufgabe: Probleme lösen und dich in Mischpult, Kamera & Licht einarbeiten. Egal ob du neu bist oder Profi – ich sorge für den technischen Erfolg. Womit starten wir?"]
            })

        # Chat-Verlauf anzeigen
        for message in st.session_state.messages:
            with st.chat_message("user" if message["role"] == "user" else "assistant"):
                st.write(message["parts"][0])

        # Eingabe verarbeiten
        if prompt := st.chat_input("Frage stellen..."):
            st.chat_message("user").write(prompt)
            st.session_state.messages.append({"role": "user", "parts": [prompt]})

            history_for_gemini = [
                {"role": m["role"], "parts": m["parts"]} 
                for m in st.session_state.messages 
                if m["role"] != "system"
            ]
            
            chat = model.start_chat(history=history_for_gemini[:-1])
            
            with st.spinner("Checke Zeitplan & Handbücher..."):
                response = chat.send_message(prompt)
            
            st.chat_message("assistant").write(response.text)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})

    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {e}")
