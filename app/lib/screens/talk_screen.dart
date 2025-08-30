import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:async';
import '../providers/auth_provider.dart';
import '../providers/chat_provider.dart';
import '../providers/voice_provider.dart';
import '../services/voice_service.dart';
import '../models/user_model.dart';
import '../widgets/profile_avatar.dart';

class TalkScreen extends ConsumerStatefulWidget {
  const TalkScreen({super.key});

  @override
  ConsumerState<TalkScreen> createState() => _TalkScreenState();
}

class _TalkScreenState extends ConsumerState<TalkScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  Timer? _audioLevelTimer;
  bool _isMuted = false;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _audioLevelTimer?.cancel();
    super.dispose();
  }

  // Start audio level monitoring for visual feedback
  void _startAudioLevelMonitoring() {
    _audioLevelTimer?.cancel();
    _audioLevelTimer = Timer.periodic(const Duration(milliseconds: 100), (timer) {
      ref.read(voiceConversationControllerProvider.notifier).updateAudioLevel();
    });
  }

  void _stopAudioLevelMonitoring() {
    _audioLevelTimer?.cancel();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final voiceState = ref.watch(voiceConversationControllerProvider);

    return authState.when(
      data: (state) => _buildTalkContent(context, ref, state.backendUser, voiceState),
      loading: () => const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      ),
      error: (error, stack) => Scaffold(
        body: Center(
          child: Text('Error: $error'),
        ),
      ),
    );
  }

  Widget _buildTalkContent(BuildContext context, WidgetRef ref, UserModel? user, VoiceConversationState voiceState) {
    final chatState = ref.watch(chatControllerProvider);

    return chatState.when(
      data: (state) => _buildTalkInterface(context, ref, user, state, voiceState),
      loading: () => const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      ),
      error: (error, stack) => Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text('Voice Chat Error: $error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Go Back'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTalkInterface(BuildContext context, WidgetRef ref, UserModel? user, ChatState chatState, VoiceConversationState voiceState) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A1A1A), // Dark theme for phone call
      appBar: _buildCallAppBar(context, ref, user, voiceState),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            // Error display
            if (voiceState.hasError)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                margin: const EdgeInsets.only(bottom: 24),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.red.withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: Colors.red, size: 20),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        voiceState.error!,
                        style: const TextStyle(color: Colors.red, fontWeight: FontWeight.w500),
                      ),
                    ),
                    IconButton(
                      onPressed: () => ref.read(voiceConversationControllerProvider.notifier).clearError(),
                      icon: const Icon(Icons.close, color: Colors.red, size: 18),
                    ),
                  ],
                ),
              ),

            // Main voice interface
            Expanded(
              child: _buildVoiceInterface(context, ref, user, voiceState, chatState),
            ),
          ],
        ),
      ),
    );
  }

  PreferredSizeWidget _buildCallAppBar(BuildContext context, WidgetRef ref, UserModel? user, VoiceConversationState voiceState) {
    final callDuration = ref.read(voiceConversationControllerProvider.notifier).getCallDuration();

    return AppBar(
      backgroundColor: const Color(0xFF2A2A2A),
      elevation: 0,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back, color: Colors.white),
        onPressed: () => _handleBackPress(ref, voiceState),
      ),
      title: Column(
        children: [
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              MitraProfileAvatar(
                imageUrl: user?.preferences.mitraProfileImageUrl,
                mitraName: user?.preferences.mitraName ?? 'Mitra',
                size: 28,
              ),
              const SizedBox(width: 8),
              Text(
                user?.preferences.mitraName ?? 'Mitra',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: Colors.white),
              ),
            ],
          ),
          const SizedBox(height: 2),
          Text(
            _getCallStatusText(voiceState, callDuration),
            style: TextStyle(fontSize: 12, color: _getCallStatusColor(voiceState)),
          ),
        ],
      ),
      centerTitle: true,
      actions: [
        // Debug info button (only in debug mode)
        if (true) // Replace with kDebugMode in production
          IconButton(
            onPressed: () => _showDebugInfo(context, ref),
            icon: const Icon(Icons.info_outline, color: Colors.white70, size: 20),
          ),
      ],
    );
  }

  Widget _buildVoiceInterface(BuildContext context, WidgetRef ref, UserModel? user, VoiceConversationState voiceState, ChatState chatState) {
    switch (voiceState.connectionState) {
      case VoiceConnectionState.disconnected:
        return _buildStartCallInterface(context, ref, user, chatState);

      case VoiceConnectionState.connecting:
        return _buildConnectingInterface(context, user);

      case VoiceConnectionState.connected:
      case VoiceConnectionState.listening:
      case VoiceConnectionState.userSpeaking:
      case VoiceConnectionState.processing:
      case VoiceConnectionState.aiSpeaking:
        return _buildActiveCallInterface(context, ref, user, voiceState);

      case VoiceConnectionState.error:
        return _buildErrorInterface(context, ref);
    }
  }

  Widget _buildStartCallInterface(BuildContext context, WidgetRef ref, UserModel? user, ChatState chatState) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Mitra avatar
        Container(
          width: 160,
          height: 160,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                const Color(0xFF27AE60),
                const Color(0xFF229A54),
              ],
            ),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF27AE60).withOpacity(0.4),
                blurRadius: 30,
                offset: const Offset(0, 15),
              ),
            ],
          ),
          child: MitraProfileAvatar(
            imageUrl: user?.preferences.mitraProfileImageUrl,
            mitraName: user?.preferences.mitraName ?? 'Mitra',
            size: 160,
          ),
        ),

        const SizedBox(height: 40),

        Text(
          'Call ${user?.preferences.mitraName ?? 'Mitra'}',
          style: const TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
          textAlign: TextAlign.center,
        ),

        const SizedBox(height: 16),

        if (chatState.problemCategory != null)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFF3498DB).withOpacity(0.2),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFF3498DB).withOpacity(0.5)),
            ),
            child: Text(
              'Talk about: ${getProblemCategoryDisplayName(chatState.problemCategory!)}',
              style: const TextStyle(
                color: Color(0xFF3498DB),
                fontWeight: FontWeight.w500,
              ),
            ),
          ),

        const SizedBox(height: 60),

        // Call button
        GestureDetector(
          onTap: () => _startVoiceCall(ref, chatState.problemCategory, user),
          child: Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: const Color(0xFF27AE60),
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF27AE60).withOpacity(0.4),
                  blurRadius: 25,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: const Icon(
              Icons.phone,
              size: 40,
              color: Colors.white,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildConnectingInterface(BuildContext context, UserModel? user) {
    // Start pulse animation
    _pulseController.repeat();

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Animated connecting indicator
        SizedBox(
          width: 180,
          height: 180,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Pulsing circles
              AnimatedBuilder(
                animation: _pulseController,
                builder: (context, child) {
                  return Container(
                    width: 180 + (60 * _pulseController.value),
                    height: 180 + (60 * _pulseController.value),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: const Color(0xFF3498DB).withOpacity(0.3 - (0.3 * _pulseController.value)),
                    ),
                  );
                },
              ),
              // Mitra avatar
              Container(
                width: 160,
                height: 160,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: const Color(0xFF3498DB),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF3498DB).withOpacity(0.4),
                      blurRadius: 30,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: MitraProfileAvatar(
                  imageUrl: user?.preferences.mitraProfileImageUrl,
                  mitraName: user?.preferences.mitraName ?? 'Mitra',
                  size: 160,
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 40),

        const Text(
          'Connecting...',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),

        const SizedBox(height: 16),

        const Text(
          'Setting up Live API session',
          style: TextStyle(
            fontSize: 16,
            color: Colors.white70,
          ),
        ),

        const SizedBox(height: 32),

        const CircularProgressIndicator(
          valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF3498DB)),
        ),
      ],
    );
  }

  Widget _buildActiveCallInterface(BuildContext context, WidgetRef ref, UserModel? user, VoiceConversationState voiceState) {
    // Start audio level monitoring
    if (!voiceState.hasError) {
      _startAudioLevelMonitoring();
    }

    return Column(
      children: [
        const SizedBox(height: 40),

        // Mitra avatar with real-time visual feedback
        _buildAnimatedMitraAvatar(user, voiceState),

        const SizedBox(height: 40),

        // Call status
        Text(
          _getVoiceStatusText(voiceState),
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
          textAlign: TextAlign.center,
        ),

        const SizedBox(height: 12),

        Text(
          _getVoiceStatusSubtext(voiceState),
          style: const TextStyle(
            fontSize: 16,
            color: Colors.white70,
          ),
          textAlign: TextAlign.center,
        ),

        const Spacer(),

        // Real-time transcript
        if (voiceState.transcript.isNotEmpty)
          _buildLiveTranscript(voiceState.transcript),

        const Spacer(),

        // Call controls
        _buildCallControls(context, ref, voiceState),

        const SizedBox(height: 40),
      ],
    );
  }

  Widget _buildAnimatedMitraAvatar(UserModel? user, VoiceConversationState voiceState) {
    final baseSize = 180.0;
    final pulseSize = voiceState.isAiSpeaking ? 20.0 :
                     voiceState.isUserSpeaking ? 15.0 :
                     voiceState.audioLevel > 0.1 ? (voiceState.audioLevel * 10) : 0.0;

    return Container(
      width: baseSize + pulseSize,
      height: baseSize + pulseSize,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: _getAvatarColors(voiceState),
        ),
        boxShadow: [
          BoxShadow(
            color: _getAvatarColors(voiceState)[0].withOpacity(0.4),
            blurRadius: 30 + (pulseSize * 0.5),
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: MitraProfileAvatar(
        imageUrl: user?.preferences.mitraProfileImageUrl,
        mitraName: user?.preferences.mitraName ?? 'Mitra',
        size: baseSize,
      ),
    );
  }

  Widget _buildLiveTranscript(List<VoiceTranscriptEvent> transcript) {
    return Container(
      constraints: const BoxConstraints(maxHeight: 120),
      margin: const EdgeInsets.symmetric(horizontal: 20),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.black26,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white24),
      ),
      child: ListView.builder(
        reverse: true, // Show latest messages at bottom
        itemCount: transcript.length,
        itemBuilder: (context, index) {
          final reversedIndex = transcript.length - 1 - index;
          final event = transcript[reversedIndex];
          final isUser = event.role == 'user';

          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  isUser ? Icons.person : Icons.smart_toy,
                  size: 16,
                  color: isUser ? const Color(0xFF3498DB) : const Color(0xFF27AE60),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    event.text,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white.withOpacity(event.isPartial ? 0.7 : 1.0),
                      fontWeight: isUser ? FontWeight.w500 : FontWeight.normal,
                      fontStyle: event.isPartial ? FontStyle.italic : FontStyle.normal,
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildCallControls(BuildContext context, WidgetRef ref, VoiceConversationState voiceState) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        // Mute button
        GestureDetector(
          onTap: () => _toggleMute(ref),
          child: Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: _isMuted ? Colors.red : Colors.white24,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white38),
            ),
            child: Icon(
              _isMuted ? Icons.mic_off : Icons.mic,
              size: 28,
              color: _isMuted ? Colors.white : Colors.white70,
            ),
          ),
        ),

        // End call button
        GestureDetector(
          onTap: () => _endVoiceCall(ref),
          child: Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: Colors.red,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: Colors.red.withOpacity(0.4),
                  blurRadius: 20,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: const Icon(
              Icons.call_end,
              size: 32,
              color: Colors.white,
            ),
          ),
        ),

        // Speaker button (placeholder)
        GestureDetector(
          onTap: () {
            // TODO: Implement speaker toggle
          },
          child: Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: Colors.white24,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white38),
            ),
            child: const Icon(
              Icons.volume_up,
              size: 28,
              color: Colors.white70,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildErrorInterface(BuildContext context, WidgetRef ref) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Icon(
          Icons.error_outline,
          size: 100,
          color: Colors.red,
        ),

        const SizedBox(height: 32),

        const Text(
          'Connection Failed',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),

        const SizedBox(height: 16),

        const Text(
          'Unable to establish Live API connection',
          style: TextStyle(
            fontSize: 16,
            color: Colors.white70,
          ),
        ),

        const SizedBox(height: 40),

        ElevatedButton(
          onPressed: () => ref.read(voiceConversationControllerProvider.notifier).clearError(),
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF3498DB),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          ),
          child: const Text('Try Again'),
        ),
      ],
    );
  }

  // Helper methods
  String _getCallStatusText(VoiceConversationState voiceState, Duration? callDuration) {
    if (voiceState.connectionState == VoiceConnectionState.disconnected) {
      return 'Not connected';
    } else if (voiceState.connectionState == VoiceConnectionState.connecting) {
      return 'Connecting...';
    } else if (callDuration != null) {
      final minutes = callDuration.inMinutes;
      final seconds = callDuration.inSeconds % 60;
      return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
    }
    return 'Connected';
  }

  Color _getCallStatusColor(VoiceConversationState voiceState) {
    switch (voiceState.connectionState) {
      case VoiceConnectionState.disconnected:
        return Colors.white60;
      case VoiceConnectionState.connecting:
        return const Color(0xFF3498DB);
      case VoiceConnectionState.error:
        return Colors.red;
      default:
        return const Color(0xFF27AE60);
    }
  }

  List<Color> _getAvatarColors(VoiceConversationState voiceState) {
    if (voiceState.isAiSpeaking) {
      return [const Color(0xFF27AE60), const Color(0xFF2ECC71)]; // Green when Mitra speaks
    } else if (voiceState.isUserSpeaking) {
      return [const Color(0xFF3498DB), const Color(0xFF5DADE2)]; // Blue when user speaks
    } else if (voiceState.isListening) {
      return [const Color(0xFF9B59B6), const Color(0xFFAB7CCF)]; // Purple when listening
    } else {
      return [const Color(0xFF95A5A6), const Color(0xFFBDC3C7)]; // Gray when idle
    }
  }

  String _getVoiceStatusText(VoiceConversationState voiceState) {
    if (voiceState.isAiSpeaking) {
      return 'Mitra is speaking';
    } else if (voiceState.isUserSpeaking) {
      return 'You are speaking';
    } else if (voiceState.isProcessing) {
      return 'Processing...';
    } else if (voiceState.isListening) {
      return 'Listening';
    } else {
      return 'Connected';
    }
  }

  String _getVoiceStatusSubtext(VoiceConversationState voiceState) {
    if (voiceState.isAiSpeaking) {
      return 'You can interrupt anytime';
    } else if (voiceState.isUserSpeaking) {
      return 'Speak naturally';
    } else if (voiceState.isProcessing) {
      return 'Preparing response...';
    } else if (voiceState.isListening) {
      return 'Just start talking';
    } else {
      return 'Live conversation active';
    }
  }

  // Action methods
  void _handleBackPress(WidgetRef ref, VoiceConversationState voiceState) {
    if (voiceState.isInActiveCall) {
      _showEndCallDialog(context, ref);
    } else {
      ref.read(chatControllerProvider.notifier).endSession();
      Navigator.of(context).pop();
    }
  }

  void _showEndCallDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF2A2A2A),
        title: const Text('End Call', style: TextStyle(color: Colors.white)),
        content: const Text(
          'Are you sure you want to end your conversation with Mitra?',
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF3498DB))),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _endVoiceCall(ref);
              Navigator.of(context).pop();
            },
            child: const Text('End Call', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  Future<void> _startVoiceCall(WidgetRef ref, ProblemCategory? problemCategory, UserModel? user) async {
    final voiceOption = user?.preferences.preferredVoice.value ?? 'Puck';
    final language = user?.preferences.language ?? 'en';

    await ref.read(voiceConversationControllerProvider.notifier).startVoiceConversation(
      problemCategory: problemCategory,
      voiceOption: voiceOption,
      language: language,
    );
  }

  void _toggleMute(WidgetRef ref) {
    setState(() {
      _isMuted = !_isMuted;
    });

    ref.read(voiceConversationControllerProvider.notifier).toggleMicrophone();
  }

  Future<void> _endVoiceCall(WidgetRef ref) async {
    _stopAudioLevelMonitoring();
    _pulseController.stop();

    await ref.read(voiceConversationControllerProvider.notifier).endVoiceConversation();
  }

  void _showDebugInfo(BuildContext context, WidgetRef ref) {
    final debugInfo = ref.read(voiceConversationControllerProvider.notifier).getDebugInfo();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF2A2A2A),
        title: const Text('Debug Info', style: TextStyle(color: Colors.white)),
        content: SingleChildScrollView(
          child: Text(
            debugInfo.entries.map((e) => '${e.key}: ${e.value}').join('\n'),
            style: const TextStyle(color: Colors.white70, fontSize: 12),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close', style: TextStyle(color: Color(0xFF3498DB))),
          ),
        ],
      ),
    );
  }
}
