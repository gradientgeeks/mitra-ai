# Mitra AI Server

A comprehensive backend server for the Mitra AI mental wellness application, built with FastAPI and Google's Gemini AI.

## Features

### 🤖 AI-Powered Conversations
- **Text Chat**: Natural language conversations with Mitra using Gemini 2.5 Flash
- **Voice Chat**: Real-time voice conversations using Gemini Live API
- **Multimodal**: Support for text + image interactions
- **Grounding**: Real-time information from Google Search when needed
- **Thinking**: Advanced reasoning capabilities with Gemini 2.5

### 🛡️ Safety & Crisis Intervention
- **Crisis Detection**: Multi-language keyword detection for self-harm indicators
- **Safety Assessment**: Real-time analysis of conversation content
- **Crisis Response**: Immediate intervention with helpline information
- **Cultural Sensitivity**: Tailored for Indian youth mental health context

### 🧘 Wellness Features
- **Mood Tracking**: Daily mood logging with analysis and insights
- **Journaling**: Guided and free-form journaling with AI prompts
- **Meditation**: AI-generated custom meditation sessions
- **Analytics**: Personalized wellness insights and recommendations

### 🔐 Authentication & Privacy
- **Anonymous Users**: Immediate access without personal information
- **Account Linking**: Optional secure account creation
- **Firebase Integration**: Secure authentication and data storage
- **Privacy First**: All data encrypted and user-controlled

## Architecture

```
server/
├── main.py                 # FastAPI application entry point
├── core/
│   ├── config.py          # Configuration and settings
│   └── __init__.py
├── models/                # Pydantic data models
│   ├── user.py           # User and authentication models
│   ├── chat.py           # Chat and conversation models
│   ├── wellness.py       # Wellness and mental health models
│   ├── common.py         # Common response models
│   └── __init__.py
├── services/             # Business logic services
│   ├── gemini_service.py  # Gemini AI interactions
│   ├── firebase_service.py # Firebase auth and Firestore
│   ├── safety_service.py  # Crisis detection and safety
│   └── __init__.py
├── repository/           # Data access layer
│   ├── firestore_repository.py # Database operations
│   └── __init__.py
└── routers/             # API route handlers
    ├── chat.py          # Chat endpoints
    ├── wellness.py      # Wellness endpoints
    ├── user.py          # User management endpoints
    └── __init__.py
```

## API Endpoints

### Chat API (`/api/v1/chat`)
- `POST /text` - Send text message to Mitra
- `POST /voice` - Send voice message (with audio file upload)
- `POST /multimodal` - Send text + image message
- `GET /session/{session_id}` - Get session summary
- `GET /sessions` - List user sessions
- `DELETE /session/{session_id}` - Delete session

### Wellness API (`/api/v1/wellness`)
- `POST /mood` - Create mood entry
- `GET /mood` - Get mood history
- `PUT /mood/{entry_id}` - Update mood entry
- `GET /mood/analysis` - Get mood insights
- `POST /journal` - Create journal entry
- `GET /journal` - Get journal entries
- `POST /journal/guided-prompt` - Get AI writing prompt
- `POST /meditation/generate` - Generate custom meditation
- `POST /meditation/{session_id}/complete` - Complete meditation
- `GET /dashboard` - Get wellness dashboard

### User API (`/api/v1/user`)
- `POST /create-anonymous` - Create anonymous user
- `GET /profile` - Get user profile
- `PUT /profile` - Update profile
- `POST /link-account` - Link anonymous to permanent account
- `POST /signin` - Sign in existing user
- `POST /refresh-session` - Refresh session
- `DELETE /account` - Delete account
- `GET /preferences` - Get user preferences
- `PUT /preferences` - Update preferences
- `GET /stats` - Get user statistics

## Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key
FIREBASE_PROJECT_ID=your_firebase_project_id

# Optional
FIREBASE_CREDENTIALS_PATH=/path/to/service-account.json
DEBUG=true
ENVIRONMENT=development
PORT=8000
```

## Safety Features

### Crisis Detection
- **Keyword Matching**: Advanced regex patterns for crisis indicators
- **Multi-language Support**: English and Hindi crisis terms
- **Context Analysis**: Conversation history analysis for escalating risk
- **Severity Assessment**: Graduated response based on risk level

### Crisis Response
- **Immediate Intervention**: Conversation halted for severe cases
- **Helpline Information**: Indian crisis hotlines (AASRA, Vandrevala Foundation, etc.)
- **Culturally Appropriate**: Messaging tailored for Indian context
- **Professional Resources**: Clear guidance toward professional help

### Privacy & Security
- **Data Minimization**: Collect only necessary information
- **Encryption**: All data encrypted in transit and at rest
- **Anonymous Options**: Full functionality without personal information
- **User Control**: Users can delete their data at any time

## AI Capabilities

### Gemini Integration
- **Text Generation**: Natural, empathetic conversations
- **Voice Processing**: Real-time voice-to-voice interactions
- **Image Understanding**: Analyze and describe images
- **Image Generation**: Create calming, supportive imagery
- **Structured Output**: Generate formatted content and insights
- **Grounding**: Access real-time information when needed

### Wellness AI Features
- **Mood Analysis**: Pattern recognition and insights
- **Journal Prompts**: Personalized writing prompts
- **Meditation Scripts**: Custom meditation content
- **Wellness Insights**: AI-generated recommendations
- **Cultural Sensitivity**: Content appropriate for Indian youth

## Development

### Setup
```bash
# Install dependencies
cd server
pip install -r ../requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your_api_key"
export FIREBASE_PROJECT_ID="your_project_id"

# Run development server
python main.py
```

### Production Deployment
- Configure Firebase Admin SDK with service account
- Set up Cloud Run or similar container platform
- Configure domain and SSL certificates
- Set up monitoring and logging
- Configure rate limiting and security headers

## Security Considerations

- **Input Validation**: All inputs validated with Pydantic
- **Rate Limiting**: Prevent abuse with request limits
- **CORS**: Properly configured for client domains
- **Authentication**: Firebase tokens validated on each request
- **Data Privacy**: User data isolated and encrypted
- **Crisis Logging**: Anonymous logging for safety monitoring

## Monitoring & Analytics

- **Health Checks**: Application health endpoints
- **Error Logging**: Comprehensive error tracking
- **Safety Metrics**: Crisis detection and intervention tracking
- **Performance**: Response times and system metrics
- **Usage Analytics**: Anonymous usage patterns (privacy-preserving)

## Cultural Considerations

- **Indian Context**: Content and responses tailored for Indian youth
- **Language Support**: English and Hindi crisis detection
- **Cultural Sensitivity**: Respect for diverse backgrounds and beliefs
- **Academic Pressure**: Understanding of Indian educational system stress
- **Family Dynamics**: Awareness of family and social pressures
- **Stigma Awareness**: Sensitive to mental health stigma in Indian society

This server implementation provides a robust, scalable, and culturally sensitive foundation for the Mitra AI mental wellness application.