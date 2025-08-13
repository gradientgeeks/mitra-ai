# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Project Mitra** is an AI-powered mental wellness solution for Indian youth, designed to overcome stigma and provide accessible mental health support. The project uses Google Cloud's generative AI (Gemini) to create an empathetic digital companion.

### Core Innovation: "Breathe-to-Talk" Interface
- Users hold a button and breathe into their phone's microphone
- AI analyzes respiratory patterns to infer emotional state
- Provides proactive, physiologically-based engagement without requiring words

## Architecture

### Polyglot Microservices Architecture
- **Flutter Frontend**: Cross-platform mobile app (Android, iOS, Web PWA)
- **Go Backend**: High-performance API Gateway, text-based Gemini API calls, WebSocket management
- **Python Backend**: Media AI service for audio streams, speech generation, image/video generation
- **Database**: Cloud Firestore
- **Cloud Platform**: Google Cloud Platform (Mumbai/Delhi regions)

### Current State
The project is in early development with:
- Basic Flutter app skeleton in `/mitra` directory
- Go and Python server directories created but not yet implemented
- Documentation outlining the vision and technical approach

## Development Commands

### Flutter Development
```bash
cd mitra

# Install dependencies
flutter pub get

# Run the app
flutter run

# Run on specific device
flutter run -d chrome  # Web
flutter run -d <device-id>  # Mobile

# Build for production
flutter build apk  # Android
flutter build ios  # iOS
flutter build web  # Web

# Run tests
flutter test

# Analyze code
flutter analyze
```

## Key Features to Implement

1. **AI Companion**
   - Culturally-tuned conversations in English, Bengali, and Hindi
   - 24/7 availability with low-latency responses
   - Integration with Gemini API for empathetic interactions

2. **Generative Wellness Tools**
   - Mindscapes: AI-generated calming videos
   - Visual mood journaling with abstract art generation
   - Anonymous avatar generation

3. **Safety & Privacy**
   - Anonymous-first design
   - Crisis detection and intervention system
   - One-tap data deletion
   - Compliance with India's DPDP Act 2023

## Important Considerations

- **No Diagnosis**: The AI must never diagnose, prescribe medication, or replace professional therapy
- **Data Privacy**: All data must be stored in Mumbai/Delhi regions
- **Crisis Support**: Automated system to detect distress and provide local helpline information
- **Cultural Sensitivity**: Content and interactions must be appropriate for Indian youth context