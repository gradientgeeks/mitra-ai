# Firebase Setup Guide

This document explains how to set up Firebase for the Mitra AI server.

## Prerequisites

1. A Google Cloud Project with Firebase enabled
2. Firebase Admin SDK service account credentials

## Setup Steps

### 1. Create Firebase Project

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Enable Authentication and Firestore Database

### 2. Generate Service Account Key

1. Go to Project Settings > Service Accounts
2. Click "Generate new private key"
3. Download the JSON file and save it securely
4. Set the path to this file in the `FIREBASE_CREDENTIALS_PATH` environment variable

### 3. Environment Variables

Set the following environment variables:

```bash
# Path to Firebase service account credentials JSON file
FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-service-account.json

# Firebase project ID
FIREBASE_PROJECT_ID=your-project-id

# Google API key for Gemini (if different from Firebase project)
GOOGLE_API_KEY=your-google-api-key
```

### 4. Firestore Security Rules

Set up Firestore security rules to protect user data:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
      
      // Allow access to user's subcollections
      match /{document=**} {
        allow read, write: if request.auth != null && request.auth.uid == userId;
      }
    }
  }
}
```

### 5. Authentication Setup

Enable the following sign-in methods in Firebase Console:
- Email/Password
- Google
- Anonymous (for guest users)

## Data Structure

The service uses the following Firestore collections:

### Users Collection (`/users/{uid}`)
```json
{
  "uid": "user_id",
  "provider": "email|google|anonymous",
  "email": "user@example.com",
  "display_name": "User Name",
  "is_anonymous": false,
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T00:00:00Z",
  "preferences": {
    "language": "en",
    "timezone": "UTC",
    "notifications_enabled": true
  },
  "total_sessions": 0,
  "last_mood_entry": "2024-01-01T00:00:00Z"
}
```

### Subcollections

#### Chat Sessions (`/users/{uid}/chat_sessions/{session_id}`)
```json
{
  "session_id": "session_123",
  "user_id": "user_id",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "messages": [
    {
      "id": "msg_1",
      "role": "user|assistant",
      "content": "Message content",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Mood Entries (`/users/{uid}/mood_entries/{entry_id}`)
```json
{
  "id": "mood_123",
  "user_id": "user_id",
  "mood_score": 7,
  "emotions": ["happy", "excited"],
  "notes": "User notes about their mood",
  "date": "2024-01-01",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Journal Entries (`/users/{uid}/journal_entries/{entry_id}`)
```json
{
  "id": "journal_123",
  "user_id": "user_id",
  "title": "Entry title",
  "content": "Journal entry content",
  "mood_tags": ["reflective", "grateful"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Meditation Sessions (`/users/{uid}/meditation_sessions/{session_id}`)
```json
{
  "id": "meditation_123",
  "user_id": "user_id",
  "type": "mindfulness|breathing|guided",
  "duration_seconds": 600,
  "completed": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Deployment Considerations

### Cloud Run / App Engine
When deploying to Google Cloud services, you can use Application Default Credentials instead of a service account file:

```bash
# Only set the project ID, credentials will be automatically detected
FIREBASE_PROJECT_ID=your-project-id
```

### Local Development
For local development, use the service account JSON file:

```bash
FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
FIREBASE_PROJECT_ID=your-project-id
```

## Error Handling

The Firebase service includes comprehensive error handling for:
- Authentication errors (invalid tokens, expired tokens)
- Permission errors (insufficient access)
- Network errors (service unavailable)
- Data validation errors (invalid document structure)
- Quota exceeded errors

## Health Check

The service includes a health check endpoint that verifies:
- Firebase Admin SDK initialization
- Authentication service connectivity
- Firestore database connectivity

Access the health check at: `GET /api/health/firebase`

## Security Best Practices

1. **Service Account Security**: Keep service account credentials secure and never commit them to version control
2. **Environment Variables**: Use environment variables for all sensitive configuration
3. **Network Security**: Use HTTPS for all communications
4. **Data Validation**: Validate all data before writing to Firestore
5. **Rate Limiting**: Implement rate limiting to prevent abuse
6. **Monitoring**: Set up monitoring and alerting for Firebase usage

## Troubleshooting

### Common Issues

1. **"Firebase app not initialized"**
   - Check that FIREBASE_CREDENTIALS_PATH or FIREBASE_PROJECT_ID is set
   - Verify the service account JSON file is valid and accessible

2. **"Permission denied"**
   - Check Firestore security rules
   - Verify the service account has necessary permissions

3. **"User not found"**
   - Ensure the user exists in Firebase Auth
   - Check that the UID is correct

4. **"Quota exceeded"**
   - Monitor Firebase usage in the console
   - Implement caching to reduce API calls
   - Consider upgrading your Firebase plan

### Debugging

Enable debug logging by setting:
```bash
DEBUG=true
```

This will provide detailed logging for all Firebase operations.