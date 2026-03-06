# 📚 Project Study Notes: Missing Child Identification System

This document provides a comprehensive breakdown of the technologies, architecture, and logic used in this application. Use this as a guide to learn how each part works perfectly.

---

## 🏛 1. High-Level Architecture
The application follows a **Client-Server Architecture**:
1.  **Client (Frontend)**: The visual interface built with React. It runs in the user's browser.
2.  **Server (Backend)**: The "brain" built with FastAPI. It handles data, security, and AI processing.
3.  **Database**: A SQLite file that stores user accounts, child profiles, and face scans.

---

## 💻 2. Frontend Technologies (The "Face" of the App)
*   **React (Library)**: Used to build a "Single Page Application" (SPA). This means links open instantly without the whole page reloading.
*   **Vite (Build Tool)**: A modern, ultra-fast tool that bundles the Javascript and CSS files so they load quickly in the browser.
*   **TailwindCSS (Style)**: A utility-first CSS framework. Instead of writing long CSS files, we use classes like `bg-blue-500` and `font-bold` directly in the HTML.
*   **Framer Motion (Animations)**: Used for smooth transitions, fades, and hover effects that make the app feel "premium."
*   **Axios (API Calls)**: A Javascript library used to send data from the browser to our Backend (e.g., sending a login request).

---

## ⚙️ 3. Backend Technologies (The "Brain" of the App)
*   **FastAPI (Framework)**: An extremely fast Python framework for building APIs. It automatically handles data validation (making sure ages are numbers, etc.).
*   **Uvicorn (Server)**: The engine that runs the FastAPI code so it can listen for web requests.
*   **SQLAlchemy (ORM)**: A tool that lets Python "talk" to the database using Python objects instead of writing raw SQL commands.
*   **JWT (Security)**: "JSON Web Tokens" are used to keep you logged in. After you login, the server gives you a "ticket" (Token) that your browser shows every time it asks for data.

---

## 🧠 4. AI Engine: How Face Matching Works
This is the most advanced part of the project. It uses **Deep Learning**:
*   **DeepFace (Library)**: A lightweight Python library that wraps several expert-level AI models for face recognition.
*   **ArcFace (Model)**: The specific AI "brain" we used. It is one of the most accurate models in the world for identifying individuals.
*   **Embeddings (The Key)**:
    - The AI doesn't compare "pixels" of photos.
    - Instead, it turns a face into a list of **512 numbers** (called an Embedding).
    - These numbers represent features like the distance between eyes, nose shape, etc.
    - **Cosine Similarity**: To find a match, the AI calculates the "mathematical distance" between two lists of numbers. If the numbers are very close (similarity > 0.6), it's a match!
*   **Detector Backends**: We use `opencv`, `mtcnn`, and `retinaface`. These are different algorithms that find *where* the face is in a photo before scanning it.

---

## 🗄 5. Database & Data Storage
*   **SQLite**: A "serverless" database. The entire database is just one file (`missing_child.db`). It's perfect for local development.
*   **Uploads Folder**: Photos are not stored *inside* the database. The database only stores the **File Path** (where the photo is on your hard drive) and the **Face Embedding** (the 512 numbers).

---

## 🛠 6. Running the Application
| Script | Use Case |
| :--- | :--- |
| `run_app.bat` | **Best for Development**. Runs both Frontend and Backend in separate windows so you can see error logs easily. |
| `reset_backend.bat` | **Maintenance**. Kills hung processes and deletes the old database to fix "Match Not Found" errors. |
| `publish_app.bat` | **Final Product**. Combines the entire app into a single link (`http://localhost:8000`). |

---

## 💡 Learning Tips
1.  **Check `backend/app/main.py`**: This is the entry point of the server. Look at how it "includes" different routers like `auth` and `cases`.
2.  **Check `frontend/src/api.js`**: See how we dynamically change the API URL depending on if you are in "Dev" or "Production" mode.
3.  **Check `backend/app/ai_engine.py`**: This is where the magic happens. Look at the `get_embedding` function to see how it tries multiple AI detectors.

---
*Created by Antigravity for MadhuSudhan*
