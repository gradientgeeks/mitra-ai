import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../providers/chat_provider.dart';
import '../models/user_model.dart';
import '../models/chat_models.dart';
import '../widgets/profile_avatar.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);

    return authState.when(
      data: (state) => _buildChatContent(context, ref, state.backendUser),
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

  Widget _buildChatContent(BuildContext context, WidgetRef ref, UserModel? user) {
    final chatState = ref.watch(chatControllerProvider);

    return chatState.when(
      data: (state) => _buildChatInterface(context, ref, user, state),
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
              Text('Chat Error: $error'),
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

  Widget _buildChatInterface(BuildContext context, WidgetRef ref, UserModel? user, ChatState chatState) {
    return Scaffold(
      backgroundColor: const Color(0xFFECE5DD), // WhatsApp-like background
      appBar: AppBar(
        backgroundColor: const Color(0xFF128C7E), // WhatsApp green
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () {
            // End chat session when going back
            ref.read(chatControllerProvider.notifier).endSession();
            Navigator.of(context).pop();
          },
        ),
        title: Row(
          children: [
            // Mitra Profile Avatar
            Container(
              width: 35,
              height: 35,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white70, width: 1),
              ),
              child: ClipOval(
                child: MitraProfileAvatar(
                  imageUrl: user?.preferences.mitraProfileImageUrl,
                  mitraName: user?.preferences.mitraName ?? 'Mitra',
                  size: 35,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    user?.preferences.mitraName ?? 'Mitra',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                  if (chatState.problemCategory != null)
                    Text(
                      getProblemCategoryDisplayName(chatState.problemCategory!),
                      style: const TextStyle(
                        fontSize: 13,
                        color: Colors.white70,
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            onPressed: () => _showChatOptions(context, ref, chatState),
            icon: const Icon(
              Icons.more_vert,
              color: Colors.white,
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // Problem category banner
          if (chatState.problemCategory != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: const Color(0xFF25D366).withValues(alpha: 0.1),
                border: Border(
                  bottom: BorderSide(
                    color: const Color(0xFF25D366).withValues(alpha: 0.2),
                    width: 1,
                  ),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.psychology_outlined,
                    color: const Color(0xFF128C7E),
                    size: 18,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Talking about: ${getProblemCategoryDisplayName(chatState.problemCategory!)}',
                      style: const TextStyle(
                        fontSize: 13,
                        color: Color(0xFF128C7E),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),

          // Chat messages area
          Expanded(
            child: chatState.messages.isEmpty
                ? _buildEmptyState(context, user, chatState)
                : _buildMessagesList(context, ref, chatState),
          ),

          // Message input area
          _buildMessageInput(context, ref, chatState),
        ],
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context, UserModel? user, ChatState chatState) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: ConstrainedBox(
        constraints: BoxConstraints(
          minHeight: MediaQuery.of(context).size.height -
                    MediaQuery.of(context).padding.top -
                    AppBar().preferredSize.height -
                    100, // Account for input area
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            MitraProfileAvatar(
              imageUrl: user?.preferences.mitraProfileImageUrl,
              mitraName: user?.preferences.mitraName ?? 'Mitra',
              size: 80,
            ),
            const SizedBox(height: 24),
            Text(
              'Hi! I\'m ${user?.preferences.mitraName ?? 'Mitra'}',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: const Color(0xFF2C3E50),
                    fontWeight: FontWeight.w600,
                  ),
            ),
            const SizedBox(height: 12),
            if (chatState.problemCategory != null) ...[
              Text(
                'I understand you\'re dealing with ${getProblemCategoryDisplayName(chatState.problemCategory!).toLowerCase()}.',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: const Color(0xFF7F8C8D),
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
            ],
            Text(
              'I\'m here to listen and support you. Share whatever is on your mind, and we\'ll work through it together.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: const Color(0xFF7F8C8D),
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            // Suggested conversation starters
            _buildConversationStarters(context, ref, chatState),
          ],
        ),
      ),
    );
  }

  Widget _buildConversationStarters(BuildContext context, WidgetRef ref, ChatState chatState) {
    final starters = _getConversationStarters(chatState.problemCategory);

    return Column(
      children: [
        Text(
          'Here are some ways to get started:',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: const Color(0xFF95A5A6),
                fontWeight: FontWeight.w500,
              ),
        ),
        const SizedBox(height: 16),
        ...starters.map((starter) => Container(
          width: double.infinity,
          margin: const EdgeInsets.only(bottom: 8),
          child: OutlinedButton(
            onPressed: () {
              _messageController.text = starter;
              _sendMessage(ref);
            },
            style: OutlinedButton.styleFrom(
              foregroundColor: const Color(0xFF3498DB),
              side: const BorderSide(color: Color(0xFF3498DB)),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              padding: const EdgeInsets.all(16),
            ),
            child: Text(
              starter,
              style: const TextStyle(fontSize: 14),
              textAlign: TextAlign.center,
            ),
          ),
        )).toList(),
      ],
    );
  }

  List<String> _getConversationStarters(ProblemCategory? category) {
    if (category == null) {
      return [
        "I'm feeling overwhelmed today",
        "I need someone to talk to",
        "Help me understand my feelings",
      ];
    }

    switch (category) {
      case ProblemCategory.stress_anxiety:
        return [
          "I'm feeling really anxious about something",
          "My stress levels are through the roof",
          "I can't stop worrying about things",
        ];
      case ProblemCategory.depression_sadness:
        return [
          "I've been feeling really down lately",
          "Everything feels hopeless right now",
          "I don't enjoy things I used to love",
        ];
      case ProblemCategory.relationship_issues:
        return [
          "I'm having problems with someone close to me",
          "I don't know how to handle this relationship",
          "I feel misunderstood by people around me",
        ];
      case ProblemCategory.academic_pressure:
        return [
          "I'm stressed about my studies",
          "The pressure to perform is overwhelming",
          "I'm struggling to keep up with everything",
        ];
      default:
        return [
          "I need help dealing with this situation",
          "I'm not sure how to handle what I'm going through",
          "Can you help me understand my feelings?",
        ];
    }
  }

  Widget _buildMessagesList(BuildContext context, WidgetRef ref, ChatState chatState) {
    // Scroll to bottom after messages are built
    WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());

    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: chatState.messages.length,
      itemBuilder: (context, index) {
        final message = chatState.messages[index];
        return _buildMessageBubble(context, message);
      },
    );
  }

  Widget _buildMessageBubble(BuildContext context, ChatMessage message) {
    final isUser = message.role == 'user';

    return Container(
      margin: EdgeInsets.only(
        bottom: 8,
        left: isUser ? 64 : 8,
        right: isUser ? 8 : 64,
      ),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser) ...[
            Container(
              width: 32,
              height: 32,
              margin: const EdgeInsets.only(right: 8, bottom: 2),
              child: ClipOval(
                child: MitraProfileAvatar(
                  imageUrl: null,
                  mitraName: 'Mitra',
                  size: 32,
                ),
              ),
            ),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: isUser
                    ? const Color(0xFFDCF8C6) // WhatsApp user message green
                    : Colors.white, // WhatsApp received message white
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(15),
                  topRight: const Radius.circular(15),
                  bottomLeft: Radius.circular(isUser ? 15 : 5),
                  bottomRight: Radius.circular(isUser ? 5 : 15),
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.1),
                    blurRadius: 2,
                    offset: const Offset(0, 1),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (message.content.text != null)
                    Text(
                      message.content.text!,
                      style: TextStyle(
                        color: const Color(0xFF303030),
                        fontSize: 16,
                        height: 1.3,
                      ),
                    ),
                  const SizedBox(height: 4),
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        _formatTimestamp(message.timestamp),
                        style: TextStyle(
                          color: const Color(0xFF999999),
                          fontSize: 12,
                        ),
                      ),
                      if (isUser) ...[
                        const SizedBox(width: 4),
                        Icon(
                          Icons.done_all,
                          size: 16,
                          color: const Color(0xFF4FC3F7), // Read receipt blue
                        ),
                      ],
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageInput(BuildContext context, WidgetRef ref, ChatState chatState) {
    return Container(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 16,
        bottom: 16 + MediaQuery.of(context).viewInsets.bottom,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Color(0x1A000000),
            offset: Offset(0, -2),
            blurRadius: 8,
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: const Color(0xFFF8F9FA),
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(
                    color: const Color(0xFFE0E0E0),
                    width: 1,
                  ),
                ),
                child: TextField(
                  controller: _messageController,
                  decoration: const InputDecoration(
                    hintText: 'Type your message...',
                    hintStyle: TextStyle(color: Color(0xFF7F8C8D)),
                    border: InputBorder.none,
                    contentPadding: EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 16,
                    ),
                  ),
                  maxLines: 4,
                  minLines: 1,
                  textCapitalization: TextCapitalization.sentences,
                  onSubmitted: (_) => _sendMessage(ref),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Container(
              decoration: BoxDecoration(
                color: chatState.isLoading
                    ? const Color(0xFF95A5A6)
                    : const Color(0xFF3498DB),
                borderRadius: BorderRadius.circular(24),
              ),
              child: IconButton(
                onPressed: chatState.isLoading ? null : () => _sendMessage(ref),
                icon: chatState.isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Icon(
                        Icons.send,
                        color: Colors.white,
                        size: 20,
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _sendMessage(WidgetRef ref) {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;

    _messageController.clear();
    ref.read(chatControllerProvider.notifier).sendTextMessage(message);
  }

  void _showChatOptions(BuildContext context, WidgetRef ref, ChatState chatState) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Chat Options',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 20),
            ListTile(
              leading: const Icon(Icons.refresh),
              title: const Text('Start New Conversation'),
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

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else {
      return '${timestamp.day}/${timestamp.month}';
    }
  }
}
