# 🎶 AI Music Generator

This repository contains a full-stack AI-powered music generation system built with **FastAPI (backend)** and **Streamlit (frontend)**.  
It allows users to generate music based on text prompts using state-of-the-art machine learning models.

### 🧩 Components

#### 🎵 Backend (FastAPI)
- Handles music generation requests.
- Uses models such as `MusicGen` or similar for AI-generated music.
- Deployed on Hugging Face Spaces.

#### 🎧 Frontend (Streamlit)
- Provides a simple UI for users to input prompts and play/download generated music.
- Communicates with the backend through REST API endpoints.

# 🎵 AI Music Backend (FastAPI)

This is the backend service for the **AI Music Generator**, built with **FastAPI** and deployed on **Hugging Face Spaces**.

It provides REST API endpoints for generating AI-composed music based on user prompts.

## 🚀 Features
- Accepts text prompts for music generation.
- Uses **MusicGen / AudioCraft** models from Hugging Face.
- Returns downloadable audio files.
- Asynchronous processing for multiple users.
- Lightweight deployment-ready Docker setup.

## 🧰 Tech Stack
- **FastAPI**
- **Transformers**
- **PyTorch**
- **SciPy**
- **Uvicorn**
- **LangChain**
