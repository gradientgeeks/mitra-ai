import 'dart:convert';
import 'dart:typed_data';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import '../models/user_model.dart';
import 'api_service.dart';

// Voice session models
class VoiceSession {
  final String sessionId;
  final String state;
  final String websocketUrl;
  final DateTime createdAt;
  final ProblemCategory? problemCategory;
  final String voiceOption;
  final String language;

  VoiceSession({
    required this.sessionId,
    required this.state,
    required this.websocketUrl,
    required this.createdAt,
    this.problemCategory,
    required this.voiceOption,
    required this.language,
  });

  factory VoiceSession.fromJson(Map<String, dynamic> json) {
    return VoiceSession(
      sessionId: json['session_id'] as String,
      state: json['state'] as String,
      websocketUrl: json['websocket_url'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      problemCategory: json['problem_category'] != null
          ? ProblemCategory.values.firstWhere(
              (category) => category.name == json['problem_category'],
              orElse: () => ProblemCategory.general_wellness,
            )
          : null,
      voiceOption: json['voice_option'] as String? ?? 'Puck',
      language: json['language'] as String? ?? 'en',
    );
  }
}

class VoiceSessionRequest {
  final ProblemCategory? problemCategory;
  final String voiceOption;
  final String language;

  VoiceSessionRequest({
    this.problemCategory,
    this.voiceOption = 'Puck',
    this.language = 'en',
  });

  Map<String, dynamic> toJson() {
    return {
      if (problemCategory != null) 'problem_category': problemCategory!.name,
      'voice_option': voiceOption,
      'language': language,
    };
  }
}

class VoiceTranscriptEvent {
  final String sessionId;
  final String role;
  final String text;
  final DateTime timestamp;
  final bool isPartial;

  VoiceTranscriptEvent({
    required this.sessionId,
    required this.role,
    required this.text,
    required this.timestamp,
    this.isPartial = false,
  });

  factory VoiceTranscriptEvent.fromJson(Map<String, dynamic> json) {
    return VoiceTranscriptEvent(
      sessionId: json['session_id'] as String? ?? '',
      role: json['role'] as String,
      text: json['text'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      isPartial: json['is_partial'] as bool? ?? false,
    );
  }
}

class VoiceInterruptionEvent {
  final String sessionId;
  final DateTime interruptedAt;
  final String reason;

  VoiceInterruptionEvent({
    required this.sessionId,
    required this.interruptedAt,
    required this.reason,
  });

  factory VoiceInterruptionEvent.fromJson(Map<String, dynamic> json) {
    return VoiceInterruptionEvent(
      sessionId: json['session_id'] as String,
      interruptedAt: DateTime.parse(json['interrupted_at'] as String),
      reason: json['reason'] as String,
    );
  }
}

enum VoiceConnectionState {
  disconnected,
  connecting,
  connected,
  listening,     // Mitra is listening for user speech
  userSpeaking,  // User is speaking (detected by VAD)
  processing,    // Processing user input
  aiSpeaking,    // Mitra is speaking
  error,
}

class VoiceService {
  final ApiService _apiService;
  WebSocketChannel? _webSocketChannel;
  VoiceSession? _currentSession;
  VoiceConnectionState _connectionState = VoiceConnectionState.disconnected;

  // Event streams
  final List<Function(VoiceConnectionState)> _stateListeners = [];
  final List<Function(VoiceTranscriptEvent)> _transcriptListeners = [];
  final List<Function(VoiceInterruptionEvent)> _interruptionListeners = [];
  final List<Function(Uint8List)> _audioListeners = [];
  final List<Function(String)> _errorListeners = [];

  // Live API session state
  bool _isLiveSessionActive = false;
  bool _vadEnabled = true;

  VoiceService(this._apiService);

  // Getters
  VoiceConnectionState get connectionState => _connectionState;
  VoiceSession? get currentSession => _currentSession;
  bool get isConnected => _connectionState != VoiceConnectionState.disconnected && _connectionState != VoiceConnectionState.error;
  bool get isUserSpeaking => _connectionState == VoiceConnectionState.userSpeaking;
  bool get isAiSpeaking => _connectionState == VoiceConnectionState.aiSpeaking;
  bool get isListening => _connectionState == VoiceConnectionState.listening;

  // Event listeners
  void addStateListener(Function(VoiceConnectionState) listener) {
    _stateListeners.add(listener);
  }

  void removeStateListener(Function(VoiceConnectionState) listener) {
    _stateListeners.remove(listener);
  }

  void addTranscriptListener(Function(VoiceTranscriptEvent) listener) {
    _transcriptListeners.add(listener);
  }

  void removeTranscriptListener(Function(VoiceTranscriptEvent) listener) {
    _transcriptListeners.remove(listener);
  }

  void addInterruptionListener(Function(VoiceInterruptionEvent) listener) {
    _interruptionListeners.add(listener);
  }

  void removeInterruptionListener(Function(VoiceInterruptionEvent) listener) {
    _interruptionListeners.remove(listener);
  }

  void addAudioListener(Function(Uint8List) listener) {
    _audioListeners.add(listener);
  }

  void removeAudioListener(Function(Uint8List) listener) {
    _audioListeners.remove(listener);
  }

  void addErrorListener(Function(String) listener) {
    _errorListeners.add(listener);
  }

  void removeErrorListener(Function(String) listener) {
    _errorListeners.remove(listener);
  }

  // Start voice session with Live API
  Future<VoiceSession> startVoiceSession({
    ProblemCategory? problemCategory,
    String voiceOption = 'Puck',
    String language = 'en',
    bool enableVAD = true,
  }) async {
    try {
      _updateConnectionState(VoiceConnectionState.connecting);
      _vadEnabled = enableVAD;

      final request = VoiceSessionRequest(
        problemCategory: problemCategory,
        voiceOption: voiceOption,
        language: language,
      );

      final response = await _apiService.post(
        '/voice/start',
        data: request.toJson(),
      );

      final session = VoiceSession.fromJson(response);
      _currentSession = session;

      // Connect to WebSocket for Live API streaming
      await _connectWebSocket(session.websocketUrl);

      return session;
    } catch (e) {
      _updateConnectionState(VoiceConnectionState.error);
      _notifyError('Failed to start voice session: $e');
      throw Exception('Failed to start voice session: $e');
    }
  }

  // Connect to WebSocket for Live API
  Future<void> _connectWebSocket(String websocketUrl) async {
    try {
      // Convert HTTP URL to WebSocket URL
      final wsUrl = websocketUrl.replaceFirst('http://', 'ws://').replaceFirst('https://', 'wss://');
      final baseUrl = _apiService.baseUrl.replaceFirst('http://', 'ws://').replaceFirst('https://', 'wss://');
      final fullUrl = '$baseUrl$wsUrl';

      print('🔌 Connecting to Live API WebSocket: $fullUrl');

      _webSocketChannel = WebSocketChannel.connect(Uri.parse(fullUrl));

      // Listen to WebSocket messages
      _webSocketChannel!.stream.listen(
        (message) => _handleWebSocketMessage(message),
        onError: (error) => _handleWebSocketError(error),
        onDone: () => _handleWebSocketDisconnect(),
      );

      // Initialize Live API session
      await _initializeLiveSession();

    } catch (e) {
      _updateConnectionState(VoiceConnectionState.error);
      _notifyError('Failed to connect WebSocket: $e');
      throw Exception('Failed to connect WebSocket: $e');
    }
  }

  // Initialize Live API session with proper configuration
  Future<void> _initializeLiveSession() async {
    try {
      final config = {
        'type': 'initialize_live_session',
        'data': {
          'response_modalities': ['AUDIO'], // Audio output
          'speech_config': {
            'voice_config': {
              'prebuilt_voice_config': {
                'voice_name': _currentSession?.voiceOption ?? 'Puck'
              }
            },
            'language_code': _currentSession?.language ?? 'en-US'
          },
          'input_audio_transcription': {}, // Enable input transcription
          'output_audio_transcription': {}, // Enable output transcription
          'realtime_input_config': {
            'automatic_activity_detection': {
              'disabled': !_vadEnabled,
              'start_of_speech_sensitivity': 'START_SENSITIVITY_MEDIUM',
              'end_of_speech_sensitivity': 'END_SENSITIVITY_MEDIUM',
              'prefix_padding_ms': 300,
              'silence_duration_ms': 1000,
            }
          }
        }
      };

      _sendWebSocketMessage(config);
      _isLiveSessionActive = true;
      _updateConnectionState(VoiceConnectionState.connected);

      print('✅ Live API session initialized');

    } catch (e) {
      _updateConnectionState(VoiceConnectionState.error);
      _notifyError('Failed to initialize Live API session: $e');
    }
  }

  // Handle WebSocket messages from Live API
  void _handleWebSocketMessage(dynamic message) {
    try {
      final data = jsonDecode(message as String);
      final messageType = data['type'] as String;
      final messageData = data['data'] as Map<String, dynamic>? ?? {};

      print('📨 Live API WebSocket message: $messageType');

      switch (messageType) {
        case 'session_ready':
          _updateConnectionState(VoiceConnectionState.listening);
          print('🎤 Live API session ready - listening for speech');
          break;

        case 'speech_started':
          _updateConnectionState(VoiceConnectionState.userSpeaking);
          print('🗣️ User speech detected');
          break;

        case 'speech_ended':
          _updateConnectionState(VoiceConnectionState.processing);
          print('⏸️ User speech ended - processing');
          break;

        case 'input_transcription':
          final text = messageData['text'] as String? ?? '';
          final transcriptEvent = VoiceTranscriptEvent(
            sessionId: _currentSession?.sessionId ?? '',
            role: 'user',
            text: text,
            timestamp: DateTime.now(),
            isPartial: messageData['is_partial'] as bool? ?? false,
          );
          _notifyTranscript(transcriptEvent);
          break;

        case 'audio_response_start':
          _updateConnectionState(VoiceConnectionState.aiSpeaking);
          print('🔊 AI started speaking');
          break;

        case 'audio_response_chunk':
          final audioDataB64 = messageData['audio'] as String?;
          if (audioDataB64 != null) {
            final audioData = base64Decode(audioDataB64);
            _notifyAudio(audioData);
          }
          break;

        case 'audio_response_end':
          _updateConnectionState(VoiceConnectionState.listening);
          print('🔇 AI finished speaking - back to listening');
          break;

        case 'output_transcription':
          final text = messageData['text'] as String? ?? '';
          final transcriptEvent = VoiceTranscriptEvent(
            sessionId: _currentSession?.sessionId ?? '',
            role: 'assistant',
            text: text,
            timestamp: DateTime.now(),
            isPartial: messageData['is_partial'] as bool? ?? false,
          );
          _notifyTranscript(transcriptEvent);
          break;

        case 'interruption':
          final interruptionEvent = VoiceInterruptionEvent(
            sessionId: _currentSession?.sessionId ?? '',
            interruptedAt: DateTime.now(),
            reason: messageData['reason'] as String? ?? 'speech_detected',
          );
          _notifyInterruption(interruptionEvent);
          _updateConnectionState(VoiceConnectionState.userSpeaking);
          break;

        case 'error':
          final errorMessage = messageData['message'] as String? ?? 'Unknown error';
          _notifyError(errorMessage);
          _updateConnectionState(VoiceConnectionState.error);
          break;

        case 'session_ended':
          _updateConnectionState(VoiceConnectionState.disconnected);
          break;

        default:
          print('⚠️ Unknown Live API message type: $messageType');
          break;
      }
    } catch (e) {
      print('❌ Error handling Live API message: $e');
      _notifyError('Error processing message: $e');
    }
  }

  // Send continuous audio stream to Live API
  void sendAudioStream(Uint8List audioData) {
    if (!_isLiveSessionActive || _webSocketChannel == null) {
      print('⚠️ Cannot send audio: Live session not active');
      return;
    }

    try {
      final audioDataB64 = base64Encode(audioData);
      _sendWebSocketMessage({
        'type': 'audio_stream',
        'data': {
          'audio': audioDataB64,
          'mime_type': 'audio/pcm;rate=16000'
        }
      });
    } catch (e) {
      print('❌ Error sending audio stream: $e');
      _notifyError('Failed to send audio: $e');
    }
  }

  // Signal end of audio stream (for VAD disabled mode)
  void endAudioStream() {
    if (!_isLiveSessionActive || _webSocketChannel == null) return;

    try {
      _sendWebSocketMessage({
        'type': 'audio_stream_end',
        'data': {}
      });
    } catch (e) {
      print('❌ Error ending audio stream: $e');
    }
  }

  // Send WebSocket message
  void _sendWebSocketMessage(Map<String, dynamic> message) {
    try {
      final jsonString = jsonEncode(message);
      _webSocketChannel?.sink.add(jsonString);
    } catch (e) {
      print('❌ Error sending WebSocket message: $e');
      _notifyError('Failed to send message: $e');
    }
  }

  // Handle WebSocket errors
  void _handleWebSocketError(dynamic error) {
    print('❌ Live API WebSocket error: $error');
    _updateConnectionState(VoiceConnectionState.error);
    _notifyError('Connection error: $error');
  }

  // Handle WebSocket disconnect
  void _handleWebSocketDisconnect() {
    print('🔌 Live API WebSocket disconnected');
    _isLiveSessionActive = false;
    _updateConnectionState(VoiceConnectionState.disconnected);
    _webSocketChannel = null;
  }

  // End voice session
  Future<void> endVoiceSession() async {
    try {
      if (_currentSession != null && _isLiveSessionActive) {
        // Send end session message
        _sendWebSocketMessage({
          'type': 'end_session',
          'data': {}
        });

        // Call API to end session
        await _apiService.delete('/voice/session/${_currentSession!.sessionId}');
      }
    } catch (e) {
      print('❌ Error ending voice session: $e');
    } finally {
      _cleanup();
    }
  }

  // Cleanup resources
  void _cleanup() {
    _webSocketChannel?.sink.close(status.normalClosure);
    _webSocketChannel = null;
    _currentSession = null;
    _isLiveSessionActive = false;
    _updateConnectionState(VoiceConnectionState.disconnected);
  }

  // Update connection state and notify listeners
  void _updateConnectionState(VoiceConnectionState newState) {
    if (_connectionState != newState) {
      _connectionState = newState;
      print('🔄 Voice connection state: $newState');
      for (final listener in _stateListeners) {
        try {
          listener(newState);
        } catch (e) {
          print('❌ Error in state listener: $e');
        }
      }
    }
  }

  // Notify listeners
  void _notifyTranscript(VoiceTranscriptEvent event) {
    for (final listener in _transcriptListeners) {
      try {
        listener(event);
      } catch (e) {
        print('❌ Error in transcript listener: $e');
      }
    }
  }

  void _notifyInterruption(VoiceInterruptionEvent event) {
    for (final listener in _interruptionListeners) {
      try {
        listener(event);
      } catch (e) {
        print('❌ Error in interruption listener: $e');
      }
    }
  }

  void _notifyAudio(Uint8List audioData) {
    for (final listener in _audioListeners) {
      try {
        listener(audioData);
      } catch (e) {
        print('❌ Error in audio listener: $e');
      }
    }
  }

  void _notifyError(String error) {
    for (final listener in _errorListeners) {
      try {
        listener(error);
      } catch (e) {
        print('❌ Error in error listener: $e');
      }
    }
  }

  // Get session info
  VoiceSession? getSessionInfo(String sessionId) {
    return _currentSession?.sessionId == sessionId ? _currentSession : null;
  }

  // Get active sessions count
  int getActiveSessionsCount() {
    return _isLiveSessionActive ? 1 : 0;
  }

  // Dispose and cleanup
  void dispose() {
    _cleanup();
    _stateListeners.clear();
    _transcriptListeners.clear();
    _interruptionListeners.clear();
    _audioListeners.clear();
    _errorListeners.clear();
  }
}
