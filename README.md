# **Mitra AI: Technical Design Document for Flutter Implementation**

  * **Version:** 1.0
  * **Date:** August 28, 2025

## 1\. Overview

### 1.1 Project Name

**Mitra AI** (मित्र: Friend)

### 1.2 Vision & Mission

  * **Vision:** A future where every young person in India feels empowered to prioritize their mental well-being without fear of judgment.
  * **Mission:** To provide a confidential, empathetic, and culturally sensitive digital companion that offers immediate mental wellness support, accessible information, and a safe space for self-expression.

### 1.3 Core Principles

  * **Anonymity:** Users must be able to engage without revealing their identity.
  * **Empathy:** The AI's persona should be supportive, non-judgmental, and understanding.
  * **Accessibility:** The app must be free, intuitive, and available 24/7.
  * **Safety:** User safety is paramount, with clear protocols for crisis situations.

-----

## 2\. Core Features & Functionality

### 2.1 The Empathetic Companion

The core interactive experience of the app.

  * **Confidential Text Chat:** A secure, multi-turn conversational interface for users to text with Mitra.
  * **Real-Time Voice Conversations:** A low-latency, audio-to-audio chat feature for users who prefer to speak. This will leverage the Gemini Live API for a natural, responsive feel.

### 2.2 Personalized Resource Hub

Dynamically generated content to support the user's journey.

  * **Dynamic Wellness Guides:** Instead of static articles, Mitra will generate rich, structured content combining text, headings, lists, and AI-generated images. This will be rendered in-app for a seamless experience.
  * **Real-Time Information:** Using **Grounding with Google Search**, Mitra can provide up-to-date information on topics like nearby clinics, articles, or helpline numbers.
  * **HTML-Rendered Content:** For detailed articles or resources, Gemini will generate simple HTML to be rendered within the app, allowing for a richer format than plain text.

### 2.3 Interactive Wellness Tools

Proactive tools to encourage mental wellness practices.

  * **AI-Guided Meditations:** On-demand, AI-generated audio for guided breathing exercises and meditations, tailored to the user's stated needs.
  * **Reflective Journaling:** A private space for users to type or speak their thoughts, with gentle, AI-powered reflective prompts.
  * **Mood Tracker:** A simple interface for daily mood logging, helping users and Mitra identify patterns over time.

### 2.4 Safety & Crisis Intervention

A non-negotiable safety net for users.

  * **Crisis Detection:** Backend logic will monitor conversations for keywords indicating severe distress or self-harm intent.
  * **Redirection Protocol:** Upon detection, the AI conversation is immediately halted and a **pre-written, non-AI-generated** screen is displayed, providing direct access and contact information for verified Indian crisis hotlines (e.g., AASRA, Vandrevala Foundation).

-----

## 3\. User Identity & Data Persistence

### 3.1 Initial Sign-Up (Anonymous)

The app must be immediately usable without providing personal information.

  * **Flow:** On first launch, the Flutter app will call `FirebaseAuth.instance.signInAnonymously()`.
  * **Data Collected:** Only the auto-generated, non-identifiable Firebase UID.
  * **UID on App Update:** An app update **will not** change the UID. The user's data is preserved.

### 3.2 Optional Account Linking & Sync

To prevent data loss, users can optionally secure their account.

  * **Trigger:** This is a user-initiated action from the Settings screen (e.g., "Secure & Sync Your Journey").
  * **Flow:** The Flutter app will use `FirebaseAuth.instance.currentUser.linkWithCredential()` to link a permanent method (Google, Apple, or Email) to the existing anonymous account.
  * **UID on App Re-install:** If an unlinked user re-installs the app, their UID **will change** and data will be lost. If their account was linked, they can sign in with their permanent method to recover their original UID and all associated data.

-----

## 4\. Technical Architecture & Stack

### 4.1 Frontend (Flutter App)

  * **State Management:** **Riverpod** is recommended for its simplicity, scalability, and compile-safe nature, making it ideal for managing complex states like chat sessions and user authentication.
  * **UI:** **Material Design 3** for a modern, clean, and responsive user interface.
  * **Key Packages:**
      * `firebase_auth`: For all authentication flows.
      * `cloud_firestore`: For database interaction.
      * `google_generative_ai`: The official Dart SDK for interacting with the Gemini API.
      * `flutter_sound` or similar: For capturing and playing audio in the voice chat feature.
      * `flutter_html`: For rendering the generated HTML content in the resource hub.
      * `firebase_app_check`: To protect backend resources from abuse.
  * **Responsibilities:**
      * Render the UI and manage the local state.
      * Handle user input (text, voice, button taps).
      * Securely communicate with the backend via Cloud Functions.

### 4.2 Backend (Google Cloud)

  * **Authentication:** **Firebase Authentication** (Anonymous, Google, Apple, Email providers).
  * **Database:** **Cloud Firestore** for storing all user data in a scalable, NoSQL structure.
  * **Business Logic:** **Cloud Functions for Firebase (2nd Gen)** written in TypeScript or Python. These will act as a secure intermediary between the Flutter app and the Gemini API.
      * **Responsibilities:**
          * Receive requests from the authenticated Flutter app.
          * Construct prompts (including context summaries).
          * Call the Gemini API.
          * Perform crisis keyword detection.
          * Save conversation history back to Firestore.
  * **AI Services:** **Google Gemini API** (`gemini-2.5-flash`, `gemini-live-2.5-flash-preview`, etc.).
  * **Storage:** **Cloud Storage for Firebase** to store any larger generated assets like audio meditation files.

-----

## 5\. Firestore Database Schema

The database will be structured with a root `users` collection. All user-specific data will live in sub-collections under that user's document to ensure strong security rules.

```
/users/{userId}
  - createdAt: Timestamp
  - linkedProviders: Array<String> (e.g., ["google.com", "password"])
  - contextSummary: String (The AI-generated memory)

  /users/{userId}/chats/{messageId}
    - timestamp: Timestamp
    - role: String ("user" or "model")
    - content: String

  /users/{userId}/journalEntries/{entryId}
    - timestamp: Timestamp
    - content: String
    - mood: String

  /users/{userId}/moodLogs/{logId}
    - timestamp: Timestamp
    - mood: String ("Happy", "Anxious", etc.)
    - trigger: String (Optional)
```

**Security Rules:** Firestore Security Rules will be implemented to ensure users can only access their own data.
`match /users/{userId}/{document=**} { allow read, write: if request.auth.uid == userId; }`

-----

## 6\. API Interaction Flow (Example: Sending a Chat Message)

1.  **Flutter App:** User types "I'm feeling stressed" and hits send. The UI optimistically displays the message.
2.  **Flutter App:** A call is made to a Cloud Function named `sendChatMessage` with the message content. The user's Firebase Auth token is automatically included in the request headers.
3.  **Cloud Function:**
      * Verifies the user's auth token.
      * Reads the user's `contextSummary` from their document in Firestore.
      * Constructs the full conversation history and prepends the summary.
      * Calls the Gemini API with the complete prompt.
4.  **Gemini API:** Processes the request and returns a response.
5.  **Cloud Function:**
      * Performs a final safety check on the response.
      * Saves the user's message and the model's response as new documents in the `/chats` sub-collection in Firestore.
      * Returns the model's response text to the Flutter app.
6.  **Flutter App:** Receives the response and updates the chat UI to display Mitra's message.