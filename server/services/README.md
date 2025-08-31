# Gemini Services Architecture

The Gemini AI service has been refactored into separate, focused services for better maintainability and single responsibility. The architecture now consists of:

## Service Structure

### `BaseGeminiService`
- **Purpose**: Provides common functionality for all Gemini-based services
- **Contains**: 
  - Gemini client initialization
  - System instruction for Mitra AI
  - Utility methods for message conversion and configuration
- **File**: `base_gemini_service.py`

### `TextGenerationService`
- **Purpose**: Handles text generation and structured content
- **Capabilities**:
  - Generate text responses with conversation history
  - Create structured content using JSON schemas
  - Support for grounding (Google Search integration)
  - Thinking mode support (Gemini 2.5)
- **File**: `text_generation_service.py`

### `VoiceService`
- **Purpose**: Handles voice input/output processing
- **Capabilities**:
  - Convert voice input to text (speech-to-text)
  - Generate voice responses (text-to-speech)
  - Live API integration for real-time voice conversations
- **File**: `voice_service.py`

### `ImageService`
- **Purpose**: Handles image generation and editing
- **Capabilities**:
  - Generate images from text prompts
  - Edit existing images with text instructions
  - Wellness-focused image enhancement
- **File**: `image_service.py`

### `WellnessService`
- **Purpose**: Provides wellness-specific AI functionality
- **Capabilities**:
  - Generate meditation scripts
  - Create wellness insights from user data
  - Generate personalized coping strategies
  - Create mood check-in prompts
- **File**: `wellness_service.py`

### `GeminiService` (Composite)
- **Purpose**: Maintains backward compatibility while using new modular services
- **Implementation**: Delegates all calls to appropriate specialized services
- **File**: `gemini_service.py` and `gemini_service_composite.py`

## Usage

### Using Individual Services

```python
from services import TextGenerationService, VoiceService, ImageService, WellnessService

# Text generation
text_service = TextGenerationService()
response = await text_service.generate_text_response(messages)

# Voice processing
voice_service = VoiceService()
transcription = await voice_service.process_voice_input(audio_data)

# Image generation
image_service = ImageService()
image_data = await image_service.generate_image("peaceful scene")

# Wellness features
wellness_service = WellnessService()
meditation = await wellness_service.generate_meditation_script("mindfulness", 10)
```

### Using Composite Service (Backward Compatible)

```python
from services import GeminiService

# All functionality available through single service
gemini = GeminiService()
response = await gemini.generate_text_response(messages)
audio = await gemini.generate_voice_response(messages)
image = await gemini.generate_image("calm landscape")
script = await gemini.generate_meditation_script("breathing", 5)
```

## Benefits

1. **Single Responsibility**: Each service has a clear, focused purpose
2. **Maintainability**: Easier to maintain and test individual components
3. **Flexibility**: Can use only the services you need
4. **Extensibility**: Easy to add new specialized services
5. **Backward Compatibility**: Existing code continues to work unchanged
6. **Resource Efficiency**: Load only required services

## Migration Guide

### For New Code
Use individual services directly for better performance and clarity:

```python
# Instead of
gemini = GeminiService()
await gemini.generate_text_response(messages)

# Use
text_service = TextGenerationService()
await text_service.generate_text_response(messages)
```

### For Existing Code
No changes required - the composite `GeminiService` maintains full compatibility.

## Testing

Each service can be tested independently:

```python
# Test text generation only
text_service = TextGenerationService()
# ... test text functionality

# Test voice processing only  
voice_service = VoiceService()
# ... test voice functionality
```

## Dependencies

- **BaseGeminiService**: Core dependency for all other services
- **TextGenerationService**: Used by WellnessService for structured content
- **Individual Services**: No dependencies between specialized services
- **Composite Service**: Depends on all individual services

## Configuration

All services share the same configuration from `core.config.settings`:
- `google_api_key`: Google AI API key
- `gemini_text_model`: Model for text generation
- `gemini_live_model`: Model for voice processing
- `gemini_image_model`: Model for image generation