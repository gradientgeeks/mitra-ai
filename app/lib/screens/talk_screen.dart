import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../providers/chat_provider.dart';
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
  bool _isListening = false;
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      duration: const Duration(seconds: 1),
      vsync: this,
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  void _startListening() {
    setState(() {
      _isListening = true;
    });
    _pulseController.repeat();
    // TODO: Implement actual voice recording
  }

  void _stopListening() {
    setState(() {
      _isListening = false;
      _isProcessing = true;
    });
    _pulseController.stop();
    // TODO: Implement voice processing and send to backend

    // Simulate processing
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        setState(() {
          _isProcessing = false;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);

    return authState.when(
      data: (state) => _buildTalkContent(context, ref, state.backendUser),
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

  Widget _buildTalkContent(BuildContext context, WidgetRef ref, UserModel? user) {
    final chatState = ref.watch(chatControllerProvider);

    return chatState.when(
      data: (state) => _buildTalkInterface(context, ref, user, state),
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

  Widget _buildTalkInterface(BuildContext context, WidgetRef ref, UserModel? user, ChatState chatState) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFF2C3E50)),
          onPressed: () {
            // End chat session when going back
            ref.read(chatControllerProvider.notifier).endSession();
            Navigator.of(context).pop();
          },
        ),
        title: Row(
          children: [
            // Mitra Profile Avatar
            MitraProfileAvatar(
              imageUrl: user?.preferences.mitraProfileImageUrl,
              mitraName: user?.preferences.mitraName ?? 'Mitra',
              size: 32,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    user?.preferences.mitraName ?? 'Mitra',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF2C3E50),
                    ),
                  ),
                  if (chatState.problemCategory != null)
                    Text(
                      getProblemCategoryDisplayName(chatState.problemCategory!),
                      style: const TextStyle(
                        fontSize: 12,
                        color: Color(0xFF7F8C8D),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            onPressed: () {
              _showVoiceOptions(context, ref, chatState);
            },
            icon: const Icon(
              Icons.more_vert,
              color: Color(0xFF7F8C8D),
            ),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            // Problem category banner
            if (chatState.problemCategory != null)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                margin: const EdgeInsets.only(bottom: 24),
                decoration: BoxDecoration(
                  color: const Color(0xFF3498DB).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: const Color(0xFF3498DB).withOpacity(0.3),
                    width: 1,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.psychology_outlined,
                      color: const Color(0xFF3498DB),
                      size: 20,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Voice chat about: ${getProblemCategoryDisplayName(chatState.problemCategory!)}',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: const Color(0xFF3498DB),
                              fontWeight: FontWeight.w500,
                            ),
                      ),
                    ),
                  ],
                ),
              ),

            // Voice feature info
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    const Color(0xFF27AE60),
                    const Color(0xFF229A54),
                  ],
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF27AE60).withOpacity(0.3),
                    blurRadius: 12,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: Column(
                children: [
                  Icon(
                    Icons.record_voice_over,
                    size: 48,
                    color: Colors.white,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Real-time Voice Chat',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Have natural conversations with ${user?.preferences.mitraName ?? 'Mitra'} using voice',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.white.withOpacity(0.9),
                        ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.volume_up,
                        size: 16,
                        color: Colors.white.withOpacity(0.8),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${user?.preferences.preferredVoice.name ?? 'Puck'} Voice',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.white.withOpacity(0.8),
                              fontWeight: FontWeight.w500,
                            ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 40),

            // Voice controls
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Voice status display
                  if (_isListening || _isProcessing) ...[
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                      decoration: BoxDecoration(
                        color: _isListening
                            ? const Color(0xFF27AE60).withOpacity(0.1)
                            : const Color(0xFF3498DB).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(25),
                        border: Border.all(
                          color: _isListening
                              ? const Color(0xFF27AE60)
                              : const Color(0xFF3498DB),
                          width: 1,
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                _isListening
                                    ? const Color(0xFF27AE60)
                                    : const Color(0xFF3498DB),
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            _isListening
                                ? 'Listening...'
                                : 'Processing...',
                            style: TextStyle(
                              color: _isListening
                                  ? const Color(0xFF27AE60)
                                  : const Color(0xFF3498DB),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 32),
                  ],

                  // Large microphone button
                  GestureDetector(
                    onTapDown: (_) => _startListening(),
                    onTapUp: (_) => _stopListening(),
                    onTapCancel: () => _stopListening(),
                    child: AnimatedBuilder(
                      animation: _pulseController,
                      builder: (context, child) {
                        return Container(
                          width: _isListening ? 140 + (20 * _pulseController.value) : 120,
                          height: _isListening ? 140 + (20 * _pulseController.value) : 120,
                          decoration: BoxDecoration(
                            color: _isListening
                                ? const Color(0xFF27AE60)
                                : _isProcessing
                                    ? const Color(0xFF95A5A6)
                                    : const Color(0xFF3498DB),
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(
                                color: (_isListening
                                        ? const Color(0xFF27AE60)
                                        : const Color(0xFF3498DB))
                                    .withOpacity(0.3),
                                blurRadius: _isListening ? 30 : 20,
                                offset: const Offset(0, 10),
                              ),
                              if (_isListening)
                                BoxShadow(
                                  color: const Color(0xFF27AE60).withOpacity(0.2),
                                  blurRadius: 40 + (20 * _pulseController.value),
                                  offset: const Offset(0, 0),
                                ),
                            ],
                          ),
                          child: Icon(
                            _isListening
                                ? Icons.mic
                                : _isProcessing
                                    ? Icons.hourglass_empty
                                    : Icons.mic,
                            size: _isListening ? 70 : 60,
                            color: Colors.white,
                          ),
                        );
                      },
                    ),
                  ),

                  const SizedBox(height: 32),

                  Text(
                    _isListening
                        ? 'Release to stop recording'
                        : _isProcessing
                            ? 'Processing your message...'
                            : 'Hold to start talking',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: const Color(0xFF2C3E50),
                          fontWeight: FontWeight.w600,
                        ),
                  ),

                  const SizedBox(height: 8),

                  Text(
                    _isListening
                        ? 'Speak naturally - ${user?.preferences.mitraName ?? 'Mitra'} is listening'
                        : _isProcessing
                            ? 'Preparing ${user?.preferences.mitraName ?? 'Mitra'}\'s response'
                            : 'Press and hold the microphone to start your conversation',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: const Color(0xFF7F8C8D),
                        ),
                    textAlign: TextAlign.center,
                  ),

                  const SizedBox(height: 40),

                  // Voice chat features
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _buildFeatureItem(
                        context,
                        icon: Icons.volume_up,
                        label: 'Clear Audio',
                        color: const Color(0xFF27AE60),
                      ),
                      _buildFeatureItem(
                        context,
                        icon: Icons.speed,
                        label: 'Real-time',
                        color: const Color(0xFF3498DB),
                      ),
                      _buildFeatureItem(
                        context,
                        icon: Icons.psychology,
                        label: 'Empathetic',
                        color: const Color(0xFF9B59B6),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // Privacy reminder
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF27AE60).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: const Color(0xFF27AE60).withOpacity(0.3),
                  width: 1,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.security,
                    color: const Color(0xFF27AE60),
                    size: 20,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Voice conversations are processed securely and not permanently stored',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: const Color(0xFF27AE60),
                            fontWeight: FontWeight.w500,
                          ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureItem(BuildContext context, {
    required IconData icon,
    required String label,
    required Color color,
  }) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(
            icon,
            color: color,
            size: 24,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: const Color(0xFF7F8C8D),
                fontWeight: FontWeight.w500,
              ),
        ),
      ],
    );
  }

  void _showVoiceOptions(BuildContext context, WidgetRef ref, ChatState chatState) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Voice Chat Options',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 20),
            ListTile(
              leading: const Icon(Icons.refresh),
              title: const Text('Start New Voice Session'),
              onTap: () {
                Navigator.pop(context);
                ref.read(chatControllerProvider.notifier).endSession();
                if (chatState.problemCategory != null) {
                  ref.read(chatControllerProvider.notifier).startChatSession(
                    problemCategory: chatState.problemCategory!,
                  );
                }
              },
            ),
            ListTile(
              leading: const Icon(Icons.chat),
              title: const Text('Switch to Text Chat'),
              onTap: () {
                Navigator.pop(context);
                Navigator.of(context).pushReplacementNamed('/chat');
              },
            ),
            ListTile(
              leading: const Icon(Icons.close),
              title: const Text('End Session'),
              onTap: () {
                Navigator.pop(context);
                ref.read(chatControllerProvider.notifier).endSession();
                Navigator.of(context).pop();
              },
            ),
          ],
        ),
      ),
    );
  }
}
