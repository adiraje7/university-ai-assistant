# University AI Assistant 

An AI-powered assistant that ingests PDFs and web pages (like university documents, syllabi, and FAQs), stores them in a Qdrant vector database using OpenAI embeddings, and lets users ask questions through a natural language interface using Chainlit or a desktop GUI.

---

## Overview

![Architecture Diagram](docs/assets/university_assistant_architecture.png)

---

## Features

- Upload and chunk PDFs using semantic splitting
- Scrape and embed university web pages
- Store content in Qdrant using OpenAI vector embeddings
- Chat with your documents via GPT-powered interface
- Desktop GUI built with Tkinter
- Chainlit-based interactive web chat
- LLM function-calling for task-specific structured queries

---

## Tech Stack

| Tool       | Purpose                               |
|------------|----------------------------------------|
| Python     | Core language                          |
| LangChain  | Text chunking and processing           |
| OpenAI     | Embeddings & Chat Completions          |
| Qdrant     | Vector database                        |
| Chainlit   | Web-based chat UI                      |
| Tkinter    | Desktop management interface           |
| PyMuPDF    | PDF page manipulation and extraction   |
| BeautifulSoup | Web scraping and HTML parsing      |

---

