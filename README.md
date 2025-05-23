# University AI Assistant 

An AI-powered assistant that ingests PDFs and web pages (like university documents, syllabi, and FAQs), stores them in a Qdrant vector database using OpenAI embeddings, and lets users ask questions through a chat interface or desktop app.

##  Features

- Upload and chunk PDFs with semantic splitting
- Scrape and embed university web pages
- Store all content in a Qdrant vector DB (1536-dim OpenAI embeddings)
- Natural language Q&A via OpenAI GPT models
- Desktop GUI using Tkinter
- Web chat interface using Chainlit
- Function-calling support for structured questions (e.g., course, task, references)

---

## Tech Stack

- **Python** (LangChain, OpenAI, Qdrant)
- **Chainlit** – lightweight chat UI
- **Tkinter** – desktop management interface
- **PyMuPDF**, **PyPDF2** – PDF extraction
- **BeautifulSoup** – HTML parsing
- **Strapi (optional)** – external Q&A reference source

---

## Setup Instructions

### 1. Clone this repo

```bash
git clone https://github.com/adiraje7/university-ai-assistant.git
cd university-ai-assistant
