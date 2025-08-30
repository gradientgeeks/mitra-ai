import 'dart:async';
import 'dart:typed_data';
import 'package:permission_handler/permission_handler.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

enum AudioRecorderState {
  stopped,
  streaming,  // Continuous streaming mode for Live API
  paused,
}

class AudioRecorderService {
  static final AudioRecorderService _instance = AudioRecorderService._internal();
  factory AudioRecorderService() => _instance;
  AudioRecorderService._internal();

  FlutterSoundRecorder? _recorder;
  FlutterSoundPlayer? _player;
  AudioRecorderState _state = AudioRecorderState.stopped;
  StreamSubscription? _recorderSubscription;
  StreamController<Uint8List>? _audioStreamController;

  // Event streams
  final List<Function(AudioRecorderState)> _stateListeners = [];
  final List<Function(Uint8List)> _audioDataListeners = [];
  final List<Function(String)> _errorListeners = [];

  // Live API streaming state
  bool _isStreamingActive = false;
  Timer? _streamTimer;

  // Getters
  AudioRecorderState get state => _state;
  bool get isStreaming => _state == AudioRecorderState.streaming;
  bool get isInitialized => _recorder != null;

  // Initialize audio services for Live API
  Future<bool> initialize() async {
    try {
      // Request microphone permission
      final permission = await Permission.microphone.request();
      if (permission != PermissionStatus.granted) {
        _notifyError('Microphone permission denied');
        return false;
      }

      // Initialize recorder and player
      _recorder = FlutterSoundRecorder();
      _player = FlutterSoundPlayer();

      await _recorder!.openRecorder();
      await _player!.openPlayer();

      print('✅ Audio services initialized for Live API');
      return true;
    } catch (e) {
      _notifyError('Failed to initialize audio: $e');
      return false;
    }
  }

  // Start continuous audio streaming for Live API
  Future<bool> startContinuousStreaming() async {
    if (!isInitialized) {
      _notifyError('Audio services not initialized');
      return false;
    }

    try {
      // Create audio stream controller for continuous streaming
      _audioStreamController = StreamController<Uint8List>.broadcast();

      // Start recording to stream with Live API compatible settings
      await _recorder!.startRecorder(
        toStream: _audioStreamController!.sink,
        codec: Codec.pcm16,        // 16-bit PCM as required by Live API
        sampleRate: 16000,         // 16kHz input as recommended
        numChannels: 1,            // Mono audio
        bitRate: 256000,           // High quality bitrate
      );

      // Listen to continuous audio stream
      _recorderSubscription = _audioStreamController!.stream.listen(
        (audioData) {
          // Send continuous audio chunks to Live API
          _notifyAudioData(audioData);
        },
        onError: (error) {
          _notifyError('Audio stream error: $error');
        },
      );

      _isStreamingActive = true;
      _updateState(AudioRecorderState.streaming);

      // Start periodic check to ensure streaming continues
      _startStreamMonitoring();

      print('🎤 Started continuous audio streaming for Live API');
      return true;
    } catch (e) {
      _notifyError('Failed to start continuous streaming: $e');
      return false;
    }
  }

  // Start monitoring stream health
  void _startStreamMonitoring() {
    _streamTimer?.cancel();
    _streamTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      if (!_isStreamingActive) {
        timer.cancel();
        return;
      }

      // Check if recorder is still active
      if (_recorder?.isRecording != true) {
        print('⚠️ Audio stream interrupted, attempting to restart...');
        _restartStreaming();
      }
    });
  }

  // Restart streaming if interrupted
  Future<void> _restartStreaming() async {
    try {
      await stopStreaming();
      await Future.delayed(const Duration(milliseconds: 500));
      await startContinuousStreaming();
    } catch (e) {
      _notifyError('Failed to restart audio streaming: $e');
    }
  }

  // Stop continuous streaming
  Future<void> stopStreaming() async {
    if (!isStreaming && !_isStreamingActive) return;

    try {
      _streamTimer?.cancel();
      _streamTimer = null;

      await _recorder!.stopRecorder();
      await _recorderSubscription?.cancel();
      await _audioStreamController?.close();

      _recorderSubscription = null;
      _audioStreamController = null;
      _isStreamingActive = false;

      _updateState(AudioRecorderState.stopped);
      print('🔇 Stopped continuous audio streaming');
    } catch (e) {
      _notifyError('Failed to stop streaming: $e');
    }
  }

  // Pause streaming (for when user is not speaking)
  Future<void> pauseStreaming() async {
    if (!isStreaming) return;

    try {
      await _recorder!.pauseRecorder();
      _updateState(AudioRecorderState.paused);
      print('⏸️ Paused audio streaming');
    } catch (e) {
      _notifyError('Failed to pause streaming: $e');
    }
  }

  // Resume streaming
  Future<void> resumeStreaming() async {
    if (_state != AudioRecorderState.paused) return;

    try {
      await _recorder!.resumeRecorder();
      _updateState(AudioRecorderState.streaming);
      print('▶️ Resumed audio streaming');
    } catch (e) {
      _notifyError('Failed to resume streaming: $e');
    }
  }

  // Play audio from Live API response
  Future<void> playAudio(Uint8List audioData) async {
    if (!isInitialized) return;

    try {
      // Stop current playback if any
      if (_player!.isPlaying) {
        await _player!.stopPlayer();
      }

      // Create a temporary file for the audio data since flutter_sound
      // doesn't support direct buffer playback in recent versions
      final tempDir = await getTemporaryDirectory();
      final tempFile = File('${tempDir.path}/temp_audio_${DateTime.now().millisecondsSinceEpoch}.wav');

      // Write audio data to temporary file
      await tempFile.writeAsBytes(audioData);

      // Play audio from Live API (24kHz output)
      await _player!.startPlayer(
        fromURI: tempFile.path,
        codec: Codec.pcm16,
        sampleRate: 24000, // Live API outputs at 24kHz
        numChannels: 1,
        whenFinished: () {
          // Clean up temporary file when playback finishes
          tempFile.deleteSync();
        },
      );

      print('🔊 Playing Live API audio (${audioData.length} bytes)');
    } catch (e) {
      _notifyError('Failed to play audio: $e');
    }
  }

  // Stop audio playback
  Future<void> stopPlayback() async {
    if (!isInitialized) return;

    try {
      if (_player!.isPlaying) {
        await _player!.stopPlayer();
        print('🔇 Stopped audio playback');
      }
    } catch (e) {
      _notifyError('Failed to stop playback: $e');
    }
  }

  // Check if currently playing audio
  bool get isPlaying => _player?.isPlaying ?? false;

  // Get audio input level (for visual feedback)
  Future<double> getAudioLevel() async {
    try {
      if (_recorder?.isRecording == true) {
        // Note: getRecordAmplitude is not available in newer versions of flutter_sound
        // For now, return a simulated audio level based on streaming state
        // In a real implementation, you would need to calculate amplitude from the audio stream
        return _isStreamingActive ? 0.5 : 0.0;
      }
      return 0.0;
    } catch (e) {
      return 0.0;
    }
  }

  // Event listeners
  void addStateListener(Function(AudioRecorderState) listener) {
    _stateListeners.add(listener);
  }

  void removeStateListener(Function(AudioRecorderState) listener) {
    _stateListeners.remove(listener);
  }

  void addAudioDataListener(Function(Uint8List) listener) {
    _audioDataListeners.add(listener);
  }

  void removeAudioDataListener(Function(Uint8List) listener) {
    _audioDataListeners.remove(listener);
  }

  void addErrorListener(Function(String) listener) {
    _errorListeners.add(listener);
  }

  void removeErrorListener(Function(String) listener) {
    _errorListeners.remove(listener);
  }

  // Update state and notify listeners
  void _updateState(AudioRecorderState newState) {
    if (_state != newState) {
      _state = newState;
      for (final listener in _stateListeners) {
        try {
          listener(newState);
        } catch (e) {
          print('❌ Error in state listener: $e');
        }
      }
    }
  }

  // Notify audio data listeners
  void _notifyAudioData(Uint8List audioData) {
    for (final listener in _audioDataListeners) {
      try {
        listener(audioData);
      } catch (e) {
        print('❌ Error in audio data listener: $e');
      }
    }
  }

  // Notify error listeners
  void _notifyError(String error) {
    print('❌ Audio error: $error');
    for (final listener in _errorListeners) {
      try {
        listener(error);
      } catch (e) {
        print('❌ Error in error listener: $e');
      }
    }
  }

  // Check microphone permission status
  Future<bool> checkMicrophonePermission() async {
    final status = await Permission.microphone.status;
    return status == PermissionStatus.granted;
  }

  // Request microphone permission
  Future<bool> requestMicrophonePermission() async {
    final status = await Permission.microphone.request();
    return status == PermissionStatus.granted;
  }

  // Get audio device info for debugging
  Map<String, dynamic> getAudioInfo() {
    return {
      'is_initialized': isInitialized,
      'is_streaming': isStreaming,
      'is_playing': isPlaying,
      'recorder_state': _recorder?.isRecording ?? false,
      'player_state': _player?.isPlaying ?? false,
      'stream_active': _isStreamingActive,
    };
  }

  // Dispose and cleanup
  Future<void> dispose() async {
    _streamTimer?.cancel();
    await stopStreaming();
    await stopPlayback();

    await _recorder?.closeRecorder();
    await _player?.closePlayer();

    _recorder = null;
    _player = null;

    _stateListeners.clear();
    _audioDataListeners.clear();
    _errorListeners.clear();

    print('🔧 Audio services disposed');
  }
}
