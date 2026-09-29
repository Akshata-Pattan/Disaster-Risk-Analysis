# DRISKA - Disaster Risk Analysis System

Flask + Supabase academic project.

## Setup

1. Create and activate a Python virtual environment.
2. Install:
   pip install -r requirements.txt
3. Create `.env` from `.env.example`.
4. Add your Supabase URL and publishable key.
5. Make sure the `profiles` and `disaster_analyses` tables and RLS policies from the project setup SQL exist.
6. Run:
   python app.py

Open:
http://127.0.0.1:5000

## Note
The risk engine is a lightweight academic/demo rule-based assessment. It is not an official emergency prediction system.
