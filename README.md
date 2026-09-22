# Cyberbullying Analyzer — YouTube Comment Analysis

A web application that receives a YouTube video URL, collects the comments,
applies machine learning models for sentiment analysis and cyberbullying
detection, and presents the results organized into sections with
percentages and classification justification.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Local Installation and Setup](#local-installation-and-setup)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Configure the Backend](#2-configure-the-backend)
  - [3. Configure the Frontend](#3-configure-the-frontend)
  - [4. Run with Docker Compose](#4-run-with-docker-compose-alternative)
- [Environment Variables](#environment-variables)
- [API — Endpoints](#api--endpoints)
- [Machine Learning Models](#machine-learning-models)
- [Database](#database)
- [Production Deployment](#production-deployment)
- [Tests](#tests)
- [Roadmap](#roadmap)
- [Known Limitations](#known-limitations)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **Cyberbullying Analyzer** helps content creators, moderators, and
researchers quickly understand the "mood" of comments on a YouTube video,
identifying not only overall negative sentiment, but specifically comments
that constitute cyberbullying (insults, threats, hate speech) along with the
reason for the classification.

**Summary flow:**

```
YouTube URL → Comment extraction → Preprocessing →
Sentiment + toxicity analysis → Aggregation and percentages →
Section organization → Presentation in the frontend
```

---

## Features

- Analysis from a single YouTube video URL
- Multilingual support (automatic language detection)
- Calculation of the percentage of negative comments and cyberbullying comments
- Classification justification (insult, threat, obscenity, identity hate)
- Comments organized into 4 sections: positive, simple negative,
  cyberbullying, neutral
- Cache for previously processed analyses (avoids reprocessing the same video)
- Docker support for consistent development and deployment

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend / API | FastAPI (Python 3.11) |
| ASGI server | Uvicorn |
| Sentiment analysis | Hugging Face Transformers — `cardiffnlp/twitter-xlm-roberta-base-sentiment` |
| Toxicity detection | Detoxify (`multilingual`) |
| Language detection | langdetect |
| Database | PostgreSQL |
| ORM | SQLModel |
| Frontend | Next.js (React + TypeScript) |
| Styling | Tailwind CSS |
| Containerization | Docker + Docker Compose |
| Backend deployment | Railway (or Render) |
| Frontend deployment | Vercel |

---

## Architecture

```
┌─────────────┐        HTTPS         ┌──────────────┐        SQL        ┌──────────────┐
│  Frontend   │  ───────────────▶   │   Backend     │  ───────────────▶ │  PostgreSQL  │
│  (Next.js)  │  ◀───────────────   │   (FastAPI)   │  ◀─────────────── │              │
└─────────────┘        JSON          └──────┬───────┘                    └──────────────┘
                                             │
                                             ▼
                                  ┌───────────────────────┐
                                  │  YouTube Data API v3    │
                                  └───────────────────────┘
                                             │
                                             ▼
                                  ┌───────────────────────┐
                                  │ ML Models              │
                                  │ (Sentiment + Toxicity) │
                                  └───────────────────────┘
```

---

## Project Structure

```
cyberbullying-analyzer/
│
├── docker-compose.yml
│
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── main.py                      # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── routers/
│   │   └── analyze.py               # POST /api/analyze endpoint
│   │
│   ├── services/
│   │   ├── youtube_client.py        # comment extraction
│   │   ├── preprocess.py            # text cleaning + language detection
│   │   ├── sentiment_model.py       # sentiment analysis
│   │   └── toxicity_model.py        # toxicity detection
│   │
│   ├── models/
│   │   └── analysis.py              # "Analysis" table model
│   │
│   └── database.py                  # PostgreSQL connection and session
│
└── frontend/
    ├── Dockerfile
    ├── .dockerignore
    ├── package.json
    ├── .env.local.example
    │
    ├── app/
    │   └── page.tsx                 # main page
    │
    └── components/
        └── SectionList.tsx          # comment list by section
```

---

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16 (or Docker, which already includes the image)
- A Google Cloud Console account (for the YouTube Data API v3 key)
- Docker and Docker Compose (optional, but recommended)

---

## Local Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-user/cyberbullying-analyzer.git
cd cyberbullying-analyzer
```

### 2. Configure the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# edit the .env file and fill in YOUTUBE_API_KEY and DATABASE_URL
```

Run the server:

```bash
uvicorn main:app --reload --port 8000
```

The API is available at `http://localhost:8000`, and the interactive
documentation (Swagger) at `http://localhost:8000/docs`.

### 3. Configure the Frontend

```bash
cd ../frontend
npm install

cp .env.local.example .env.local
# edit it and define NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run the development server:

```bash
npm run dev
```

The application is available at `http://localhost:3000`.

### 4. Run with Docker Compose (alternative)

Instead of steps 2 and 3, you can run everything in one go:

```bash
docker-compose up --build
```

This starts the backend (`:8000`), the frontend (`:3000`), and PostgreSQL
(`:5432`) already connected to each other.

---

## Environment Variables

### `backend/.env`

| Variable | Description | Example |
|---|---|---|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | `AIzaSy...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@localhost:5432/cyberbullying_db` |

### `frontend/.env.local`

| Variable | Description | Example |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Base URL for the backend API | `http://localhost:8000` |

> Never commit the real `.env` / `.env.local` files.
> Always use the `.env.example` files as a reference.

---

## API — Endpoints

### `GET /`

Simple health check.

**Response:**
```json
{ "status": "ok" }
```

### `POST /api/analyze`

Analyzes the comments from a YouTube video.

**Body:**
```json
{ "url": "https://www.youtube.com/watch?v=XXXXXXXXXXX" }
```

**Response:**
```json
{
  "video_id": "XXXXXXXXXXX",
  "total_comentarios": 184,
  "pct_negativos": 12.5,
  "pct_cyberbullying": 6.0,
  "secoes": {
    "positivos": [ { "author": "...", "text": "...", "sentiment": "positive" } ],
    "negativos_simples": [ { "author": "...", "text": "...", "sentiment": "negative" } ],
    "cyberbullying": [
      {
        "author": "...",
        "text": "...",
        "toxicity": 0.87,
        "motivo": "insult"
      }
    ],
    "neutros": [ { "author": "...", "text": "...", "sentiment": "neutral" } ]
  }
}
```

Full interactive documentation is available at `/docs` (Swagger UI) when
the backend is running.

---

## Machine Learning Models

| Task | Model | Library |
|---|---|---|
| Sentiment (positive/neutral/negative) | `cardiffnlp/twitter-xlm-roberta-base-sentiment` | `transformers` |
| Toxicity / cyberbullying | `multilingual` model | `detoxify` |
| Language detection | Statistical algorithm | `langdetect` |

**Toxicity categories detected by Detoxify:**
`toxicity`, `severe_toxicity`, `obscene`, `threat`, `insult`,
`identity_attack`.

> The models are loaded only once at backend startup
> (outside request functions) to avoid costly reloads on every analysis.

---

## Database

Main table `analysis`:

| Column | Type | Description |
|---|---|---|
| `id` | int (PK) | Unique identifier |
| `video_id` | string | YouTube video ID |
| `pct_negativos` | float | Percentage of negative comments |
| `pct_cyberbullying` | float | Percentage of cyberbullying comments |
| `total_comentarios` | int | Total comments analyzed |
| `created_at` | datetime | Analysis date |

Analyses are reused from cache for 24 hours for the same video,
avoiding unnecessary reprocessing.

---

## Production Deployment

| Component | Service | Notes |
|---|---|---|
| Backend | [Railway](https://railway.app) | Define a `Procfile` with `web: uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Database | Railway PostgreSQL or [Supabase](https://supabase.com) | Copy the connection string to `DATABASE_URL` |
| Frontend | [Vercel](https://vercel.com) | Automatic deployment from the repository |

**Quick steps:**

1. Push the code to GitHub
2. Connect the backend repository to Railway and configure environment variables
3. Add a PostgreSQL service on Railway (or use Supabase)
4. Connect the frontend repository to Vercel and configure `NEXT_PUBLIC_API_URL`
5. Update `allow_origins` in the backend CORS to the final frontend domain
6. (Optional) Configure a custom domain with automatic HTTPS on both services

> Check the full guide in `Guia_Completo_Construcao_e_Deploy.pdf`
> for step-by-step instructions.

---

## Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

> Suggestion: add unit tests for `preprocess.py` (text cleaning) and
> integration tests for the `/api/analyze` endpoint using simulated comments
> (mocks) to avoid consuming the YouTube API quota during tests.

---

## Roadmap

- [ ] User authentication and personal analysis history
- [ ] Export results as PDF/CSV
- [ ] Real-time comment analysis support (streaming)
- [ ] Administration panel for moderators
- [ ] Support for other platforms (Instagram, TikTok)
- [ ] Asynchronous processing queue (Celery + Redis) for videos with
      many comments

---

## Known Limitations

- The free quota for the YouTube Data API v3 is limited (10,000 units/day)
- Multilingual toxicity models have lower accuracy in languages with limited training data
- Sarcasm and irony may be misclassified by sentiment models
- Very short comments or comments containing only emojis may be less reliable

---

## Contributing

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/feature-name`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/feature-name`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT license — see the `LICENSE` file for more details.