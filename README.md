# Quiz Helper

A tool that captures a selected region of your screen, sends it to an LLM, and displays the answer in a floating overlay — designed to assist with multiple-choice questions.

## How it works

1. Run the program and choose your provider and model from the interactive menu
2. Press `Ctrl + Shift + Space` to activate
3. Drag to select the area of the screen containing the question
4. The answer appears in a floating overlay in the corner of your screen

## Supported providers

| Provider  | Models                       |
|-----------|------------------------------|
| Anthropic | Claude Haiku, Claude Sonnet  |
| OpenAI    | GPT-4o Mini, GPT-4o          |
| Google    | Gemini Flash, Gemini Pro     |

## Installation

```bash
git clone https://github.com/erik-sig/quiz_helper.git
cd quiz_helper
pip install -r requirements.txt
```

## Usage

```bash
ANTHROPIC_API_KEY=sk-ant-... python3 main.py
# or
OPENAI_API_KEY=sk-... python3 main.py
# or
GOOGLE_API_KEY=... python3 main.py
```

## Requirements

- Python 3.10+
- Linux (X11) or Windows
- `python3-tk` installed (`sudo apt-get install python3-tk` on Linux)
- API key for at least one of the supported providers
