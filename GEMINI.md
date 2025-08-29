# Project: Mitra AI

## Project Overview

Mitra AI is a mental wellness application designed to provide a confidential, empathetic, and culturally sensitive digital companion for young people in India. The project consists of a Flutter-based mobile application for the frontend and a Python FastAPI server for the backend. It leverages Google's Gemini API for its AI-powered features.

### Key Technologies

*   **Frontend:** Flutter
*   **Backend:** Python with FastAPI
*   **Database:** Cloud Firestore
*   **Authentication:** Firebase Authentication
*   **AI:** Google Gemini API

### Architecture

The application follows a client-server architecture:

*   The **Flutter app** serves as the user interface, handling user interactions and communicating with the backend.
*   The **FastAPI backend** acts as a secure intermediary between the app and the Gemini API. It manages business logic, such as constructing prompts, handling crisis detection, and persisting conversation history to Firestore.

## Building and Running

### Backend (Python Server)

To run the backend server locally for development:

1.  **Navigate to the `server` directory:**
    ```bash
    cd server
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the development server:**
    ```bash
    python run_dev.py
    ```
    The server will be available at `http://127.0.0.1:8000`.

### Frontend (Flutter App)

To run the Flutter application:

1.  **Navigate to the `app` directory:**
    ```bash
    cd app
    ```

2.  **Get Flutter packages:**
    ```bash
    flutter pub get
    ```

3.  **Run the app:**
    ```bash
    flutter run
    ```

## Development Conventions

### Backend

*   The backend follows a structured layout, separating concerns into `core`, `models`, `repository`, `routers`, and `services`.
*   It uses FastAPI for building the RESTful API and Pydantic for data validation.
*   The `main.py` file serves as the entry point for the application.

### Frontend

*   The frontend is a standard Flutter project.
*   The `pubspec.yaml` file manages the project's dependencies.
*   The main application code is located in the `lib` directory.
