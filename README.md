# Missing Child Identification System

A full-stack application for identifying missing children using AI-powered face recognition.

## Features
*   **AI Engine**: Uses ArcFace (CNN) and SVM for high-accuracy face matching.
*   **Dashboard**: Manage missing person cases with search, filtering, and pagination.
*   **Notifications**: Real-time alerts for system events and matches.
*   **Modern UI**: Responsive interface built with React and Tailwind CSS.

## Quick Start (Production Mode)

The application is deployed as a unified server where the backend serves the frontend.

1.  **Start the Server**:
    ```bash
    cd backend
    python -m uvicorn app.main:app --host :: --port 8000
    ```
2.  **Access the App**: Open [http://localhost:8000](http://localhost:8000) in your browser.

## Development Mode

To run frontend and backend separately with hot-reloading:

1.  **Run the script**:
    ```bash
    run_app.bat
    ```
    *   Backend: [http://localhost:8000](http://localhost:8000)
    *   Frontend: [http://localhost:5173](http://localhost:5173)

## Re-Building Frontend

If you make changes to the frontend code and want to update the production build:

```bash
build_only.bat
```
This will rebuild the React app and copy the files to `backend/static`.

## Project Structure
*   `backend/`: FastAPI application, AI logic, and Database.
*   `frontend/`: React application (Vite).
*   `backend/static/`: Compiled frontend files served by FastAPI.
