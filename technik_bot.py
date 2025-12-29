import streamlit as st
import google.generativeai as genai

# --- KONFIGURATION ---
st.set_page_config(page_title="Tyrannus Technik-Bot", page_icon="🎛️")

# Logo anzeigen (falls vorhanden)
try:
    st.image("svt_logo.jpg", width=300)
except FileNotFoundError:
    pass # Kein Fehler anzeigen, einfach weitermachen

st.title("🎛️ Tyrannus Technik-Support")
st.caption("Dein KI-Kollege für XR18, Logic & Stream")

# --- API KEY MANAGEMENT (AUTOMATISCH) ---
# Wir schauen erst in den "Secrets" Tresor, ob der Key da liegt.
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    # Falls nicht (oder lokal), fragen wir in der Sidebar
    with st.sidebar:
        api_key = st.text_input("Gib deinen Google API Key ein", type="password")
        if not api_key:
            st.warning("Bitte API Key eingeben.")

# --- SYSTEM PROMPT ---
system_instruction = """
Du bist der Voice Agent des Technik-Teams der "Schule von Tyrannus".
Deine Mission: Du sicherst den technischen Erfolg von Veranstaltungen.
Haltung: Fachlich präzise, entspannt, motivierend, leichter Humor.

HARDWARE & SOFTWARE WISSEN:
- Mixer: Behringer XR18. Kanal 1: Flow8/BT, 2: Cajon, 3/4: Room, 9/10: Keys, 11-13: BV, 14/15: Main Vocals.
- Routing: BUS 1/2 Monitore, BUS 3/4 Stream.
- FX: FX1 Delay, FX2 Hall (Vocals), FX3 Mod Delay, FX4 Chorus.
- Zoom: Originalton AN, Geräuschunterdrückung NIEDRIG.
- Logic Pro: Aufnahme Start strikt 18:30 Uhr.
- Zeiten: 18:00 Soundcheck Raum, 18:30 Soundcheck Stream.

REGELN:
- Fasse dich kurz.
- Keine Listen vorlesen, führe Schritt-für-Schritt.
- Frage nach, wenn Infos fehlen.
"""

# --- LOGIK ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # WICHTIG: Hier nutzen wir das Modell, das bei dir funktioniert hat!
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=system_instruction
        )

        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append({"role": "model", "parts": ["Moin! Alles klar am Pult? Wo brennt's?"]})

        for message in st.session_state.messages:
            with st.chat_message("user" if message["role"] == "user" else "assistant"):
                st.write(message["parts"][0])

        if prompt := st.chat_input("Frage stellen..."):
            st.chat_message("user").write(prompt)
            st.session_state.messages.append({"role": "user", "parts": [prompt]})

            history_for_gemini = [
                {"role": m["role"], "parts": m["parts"]} 
                for m in st.session_state.messages 
                if m["role"] != "system"
            ]
            
            chat = model.start_chat(history=history_for_gemini[:-1])
            
            with st.spinner("Checke Handbücher..."):
                response = chat.send_message(prompt)
            
            st.chat_message("assistant").write(response.text)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})

    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {e}")
