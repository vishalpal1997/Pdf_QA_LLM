# PDF Chat with LLaMA

A Flask web application that lets you upload PDFs and chat about their content using LLaMA (via Ollama).  
**Now with a live demo video!**

[![Demo Video](screen-recording-2025-05-05-090852_kflI3lhN.mp4)  
*(Click the image above to watch the demo video)*

## ✨ Features
- 📄 Upload PDFs and extract text automatically
- 💬 Chat with **LLaMA 3** about the document content
- 🧠 Context-aware conversations (remembers chat history)
- 🚀 Fast PDF processing with PyMuPDF
- ♻️ Delete files or clear chat with one click
- 📱 Responsive UI with typing indicators

## 🛠️ Prerequisites
- Python 3.7+
- [Ollama](https://ollama.ai/) installed and running
- LLaMA model: `ollama pull llama3`
- GPU recommended for faster inference

## 🚀 Quick Start
```bash
# 1. Clone repo
git clone https://github.com/yourusername/pdf-chat-llama.git
cd pdf-chat-llama

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Ollama (in a new terminal)
ollama serve

# 4. Run the app
python app.py
