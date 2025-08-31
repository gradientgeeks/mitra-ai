import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:typed_data';
import '../services/voice_service.dart';
import '../services/audio_recorder_service.dart';
import '../models/user_model.dart';
import 'auth_provider.dart';

// Voice service provider
final voiceServiceProvider = Provider<VoiceService>((ref) {
  final apiService = ref.watch(apiServiceProvider);
  return VoiceService(apiService);
});

// Audio recorder service provider
final audioRecorderServiceProvider = Provider<AudioRecorderService>((ref) {
  return AudioRecorderService();
});

// Voice conversation controller
final voiceConversationControllerProvider = StateNotifierProvider<VoiceConversationController, VoiceConversationState>((ref) {
  final voiceService = ref.watch(voiceServiceProvider);
  final audioService = ref.watch(audioRecorderServiceProvider);
  return VoiceConversationController(voiceService, audioService);
});

// Voice conversation state for Live API
class VoiceConversationState {
  final VoiceConnectionState connectionState;
  final VoiceSession? currentSession;
  final List<VoiceTranscriptEvent> transcript;
  final bool isStreaming;      // Audio streaming to Live API
  final bool isPlaying;        // Playing AI response
  final String? error;
  final bool isInitialized;
  final double audioLevel;     // For visual feedback

  const VoiceConversationState({
    this.connectionState = VoiceConnectionState.disconnected,
    this.currentSession,
    this.transcript = const [],
    this.isStreaming = false,
    this.isPlaying = false,
    this.error,
    this.isInitialized = false,
    this.audioLevel = 0.0,
  });

  VoiceConversationState copyWith({
    VoiceConnectionState? connectionState,
    VoiceSession? currentSession,
    List<VoiceTranscriptEvent>? transcript,
    bool? isStreaming,
    bool? isPlaying,
    String? error,
    bool? isInitialized,
    double? audioLevel,
  }) {
    return VoiceConversationState(
      connectionState: connectionState ?? this.connectionState,
      currentSession: currentSession ?? this.currentSession,
      transcript: transcript ?? this.transcript,
      isStreaming: isStreaming ?? this.isStreaming,
      isPlaying: isPlaying ?? this.isPlaying,
      error: error,
      isInitialized: isInitialized ?? this.isInitialized,
      audioLevel: audioLevel ?? this.audioLevel,
    );
  }

  // Convenience getters for Live API states
  bool get isConnected => connectionState == VoiceConnectionState.connected ||
                         connectionState == VoiceConnectionState.listening ||
                         connectionState == VoiceConnectionState.userSpeaking ||
                         connectionState == VoiceConnectionState.processing ||
                         connectionState == VoiceConnectionState.aiSpeaking;

  bool get isUserSpeaking => connectionState == VoiceConnectionState.userSpeaking;
  bool get isAiSpeaking => connectionState == VoiceConnectionState.aiSpeaking;
  bool get isListening => connectionState == VoiceConnectionState.listening;
  bool get isProcessing => connectionState == VoiceConnectionState.processing;
  bool get hasError => error != null;
  bool get canStartConversation => isInitialized && !isConnected;
  bool get isInActiveCall => isConnected && currentSession != null;
}

class VoiceConversationController extends StateNotifier<VoiceConversationState> {
  final VoiceService _voiceService;
  final AudioRecorderService _audioService;

  VoiceConversationController(this._voiceService, this._audioService)
      : super(const VoiceConversationState()) {
    _initializeServices();
  }

  // Initialize services for Live API
  Future<void> _initializeServices() async {
    try {
      // Initialize audio services
      final audioInitialized = await _audioService.initialize();

      state = state.copyWith(isInitialized: audioInitialized);

      if (!audioInitialized) {
        state = state.copyWith(error: 'Failed to initialize audio services');
        return;
      }

      // Set up voice service listeners for Live API events
      _voiceService.addStateListener(_onConnectionStateChanged);
      _voiceService.addTranscriptListener(_onTranscriptReceived);
      _voiceService.addInterruptionListener(_onInterruption);
      _voiceService.addAudioListener(_onAudioReceived);
      _voiceService.addErrorListener(_onError);

      // Set up audio service listeners for continuous streaming
      _audioService.addStateListener(_onStreamingStateChanged);
      _audioService.addAudioDataListener(_onAudioDataCaptured);
      _audioService.addErrorListener(_onAudioError);

      print('✅ Live API voice conversation services initialized');

    } catch (e) {
      state = state.copyWith(error: 'Failed to initialize services: $e');
    }
  }

  // Start Live API voice conversation
  Future<void> startVoiceConversation({
    ProblemCategory? problemCategory,
    String voiceOption = 'Puck',
    String language = 'en',
  }) async {
    try {
      state = state.copyWith(error: null);

      if (!state.isInitialized) {
        state = state.copyWith(error: 'Services not initialized');
        return;
      }

      // Start Live API voice session
      final session = await _voiceService.startVoiceSession(
        problemCategory: problemCategory,
        voiceOption: voiceOption,
        language: language,
        enableVAD: true, // Enable Voice Activity Detection
      );

      state = state.copyWith(
        currentSession: session,
        transcript: [], // Clear previous transcript
      );

    } catch (e) {
      state = state.copyWith(error: 'Failed to start voice conversation: $e');
    }
  }

  // Start continuous audio streaming (phone call mode)
  Future<void> startContinuousStreaming() async {
    if (!state.isInitialized || !state.isConnected) {
      state = state.copyWith(error: 'Not ready to start streaming');
      return;
    }

    try {
      // Start continuous audio streaming to Live API
      final success = await _audioService.startContinuousStreaming();

      if (!success) {
        state = state.copyWith(error: 'Failed to start audio streaming');
      }
    } catch (e) {
      state = state.copyWith(error: 'Failed to start streaming: $e');
    }
  }

  // Stop continuous streaming
  Future<void> stopContinuousStreaming() async {
    try {
      await _audioService.stopStreaming();
    } catch (e) {
      state = state.copyWith(error: 'Failed to stop streaming: $e');
    }
  }

  // End voice conversation
  Future<void> endVoiceConversation() async {
    try {
      await _audioService.stopStreaming();
      await _voiceService.endVoiceSession();

      state = state.copyWith(
        connectionState: VoiceConnectionState.disconnected,
        currentSession: null,
        isStreaming: false,
        isPlaying: false,
        error: null,
        audioLevel: 0.0,
      );
    } catch (e) {
      state = state.copyWith(error: 'Failed to end conversation: $e');
    }
  }

  // Toggle microphone (mute/unmute during call)
  Future<void> toggleMicrophone() async {
    try {
      if (state.isStreaming) {
        await _audioService.pauseStreaming();
      } else if (_audioService.state == AudioRecorderState.paused) {
        await _audioService.resumeStreaming();
      }
    } catch (e) {
      state = state.copyWith(error: 'Failed to toggle microphone: $e');
    }
  }

  // Get current audio level for visual feedback
  Future<void> updateAudioLevel() async {
    try {
      final level = await _audioService.getAudioLevel();
      if (mounted) {
        state = state.copyWith(audioLevel: level);
      }
    } catch (e) {
      // Silently handle audio level errors
    }
  }

  // Clear error
  void clearError() {
    state = state.copyWith(error: null);
  }

  // Event handlers for Live API events
  void _onConnectionStateChanged(VoiceConnectionState newState) {
    state = state.copyWith(connectionState: newState);

    // Auto-start streaming when connected and listening
    if (newState == VoiceConnectionState.listening && !state.isStreaming) {
      startContinuousStreaming();
    }

    // Stop streaming when disconnected
    if (newState == VoiceConnectionState.disconnected) {
      stopContinuousStreaming();
    }
  }

  void _onTranscriptReceived(VoiceTranscriptEvent transcript) {
    final updatedTranscript = [...state.transcript, transcript];
    state = state.copyWith(transcript: updatedTranscript);
  }

  void _onInterruption(VoiceInterruptionEvent interruption) {
    // Handle voice interruption - AI was interrupted by user speech
    print('🛑 Voice interrupted: ${interruption.reason}');

    // Stop current audio playback
    _audioService.stopPlayback();
  }

  void _onAudioReceived(Uint8List audioData) {
    // Play received audio from Live API
    _audioService.playAudio(audioData);
    state = state.copyWith(isPlaying: true);

    // Reset playing state after a short delay
    Future.delayed(const Duration(milliseconds: 200), () {
      if (mounted) {
        state = state.copyWith(isPlaying: false);
      }
    });
  }

  void _onError(String error) {
    state = state.copyWith(error: error);
  }

  void _onStreamingStateChanged(AudioRecorderState streamingState) {
    state = state.copyWith(isStreaming: streamingState == AudioRecorderState.streaming);
  }

  void _onAudioDataCaptured(Uint8List audioData) {
    // Send captured audio data continuously to Live API
    _voiceService.sendAudioStream(audioData);
  }

  void _onAudioError(String error) {
    state = state.copyWith(error: 'Audio error: $error');
  }

  // Get conversation summary
  String getConversationSummary() {
    final userMessages = state.transcript
        .where((t) => t.role == 'user' && t.text.isNotEmpty)
        .map((t) => t.text)
        .join(' ');

    final aiMessages = state.transcript
        .where((t) => t.role == 'assistant' && t.text.isNotEmpty)
        .map((t) => t.text)
        .join(' ');

    return 'User: $userMessages\n\nMitra: $aiMessages';
  }

  // Get call duration
  Duration? getCallDuration() {
    if (state.currentSession?.createdAt == null) return null;

    return DateTime.now().difference(state.currentSession!.createdAt);
  }

  // Get debug info
  Map<String, dynamic> getDebugInfo() {
    return {
      'connection_state': state.connectionState.toString(),
      'is_streaming': state.isStreaming,
      'is_playing': state.isPlaying,
      'audio_level': state.audioLevel,
      'transcript_count': state.transcript.length,
      'audio_info': _audioService.getAudioInfo(),
      'session_id': state.currentSession?.sessionId,
    };
  }

  @override
  void dispose() {
    // Remove listeners
    _voiceService.removeStateListener(_onConnectionStateChanged);
    _voiceService.removeTranscriptListener(_onTranscriptReceived);
    _voiceService.removeInterruptionListener(_onInterruption);
    _voiceService.removeAudioListener(_onAudioReceived);
    _voiceService.removeErrorListener(_onError);

    _audioService.removeStateListener(_onStreamingStateChanged);
    _audioService.removeAudioDataListener(_onAudioDataCaptured);
    _audioService.removeErrorListener(_onAudioError);

    // Dispose services
    _voiceService.dispose();
    _audioService.dispose();

    super.dispose();
  }
}
