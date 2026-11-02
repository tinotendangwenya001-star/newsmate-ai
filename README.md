# NewsMate AI
AI assistant for resource-constrained Zimbabwean newsrooms: transcribe, translate, summarise, draft and
package stories, with mandatory human approval.

## Setup (Ubuntu)
```bash
sudo apt update && sudo apt install -y python3-venv ffmpeg
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
streamlit run app.py
```

## Pipeline
audio/notes -> faster-whisper transcript (low-confidence flagged) -> editable text -> translation (EN/Shona/Ndebele)
-> summary -> article + headlines + Facebook/X/WhatsApp copy (timestamp-cited) -> journalist approval -> export

## Known limits
- Whisper supports English and Shona (weak accuracy); Ndebele speech is unsupported.
- Shona/Ndebele translation needs human review.
