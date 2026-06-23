# README.md

# TiranaFly: Autonomous Urban Drone Logistics Optimization

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![GIS](https://img.shields.io/badge/GIS-H3%20%7C%20PostGIS-orange.svg)](https://h3geo.org/)
[![Optimization](https://img.shields.io/badge/Optimization-OR--Tools%20%7C%20NetworkX-green.svg)](https://developers.google.com/optimization)

**TiranaFly** is a production-grade research and optimization platform designed to orchestrate an autonomous multi-depot drone delivery network for the Municipality of Tirana, Albania.

---

##  Quick Start Guide

Follow these steps to get the full stack running locally:

### 1. Build & Installation
```bash
# Clone the repository
git clone https://github.com/thearchitect/Logistics-Optimization-For-TiranaFly.git
cd Logistics-Optimization-For-TiranaFly

# Backend Setup (Python)
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Frontend Setup (Node)
cd frontend
npm install
```

### 2. Run the System

**Step A: Start Infrastructure (Docker)**
```bash
docker-compose -f backend/docker-compose.yml up -d
```

**Step B: Initialize Database (Run once)**
```bash
python init_db.py
```

**Step C: Run Services (Two Terminals)**
```bash
# Terminal 1: Backend API
uvicorn api.app:app --reload

# Terminal 2: Frontend Dashboard
cd frontend
npm run dev
```

### 3. Visual Verification
*   **API Documentation**: Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to verify all routes (GIS, Fleet, Optimization) are loaded.
*   **Frontend**: Visit [http://localhost:5173](http://localhost:5173). If the map is empty, click the **Initialize** button in the dashboard to seed GIS data into the database.

---

## Table of Contents

- [Project Overview](#-project-overview)
- [Installation & Build Guide](#-installation--build-guide)
- [How to Run](#-how-to-run)
- [Dataset Documentation](#-dataset-documentation)
- [Project Structure](#-project-structure)
- [Reproducibility](#-reproducibility)
- [Common Issues & Debugging](#-common-issues--debugging)
