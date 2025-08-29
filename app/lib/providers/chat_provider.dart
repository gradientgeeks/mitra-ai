import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import '../models/user_model.dart';
import '../models/chat_models.dart';
import 'auth_provider.dart';

// Problem categories provider
final problemCategoriesProvider = FutureProvider<List<ProblemCategoryInfo>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getProblemCategories();
});

// Current chat session provider
final currentChatSessionProvider = StateProvider<ChatSessionSummary?>((ref) => null);

// Current problem category provider
final currentProblemCategoryProvider = StateProvider<ProblemCategory?>((ref) => null);

// Chat messages provider for current session
final chatMessagesProvider = StateNotifierProvider<ChatMessagesNotifier, List<ChatMessage>>((ref) {
  final apiService = ref.watch(apiServiceProvider);
  return ChatMessagesNotifier(apiService);
});

// Chat controller for managing chat sessions and messages
final chatControllerProvider = StateNotifierProvider<ChatController, AsyncValue<ChatState>>((ref) {
  final apiService = ref.watch(apiServiceProvider);
  return ChatController(apiService);
});

// Chat state model
class ChatState {
  final String? currentSessionId;
  final ProblemCategory? problemCategory;
  final List<ChatMessage> messages;
  final bool isLoading;
  final String? error;
  final bool isConnected;

  const ChatState({
    this.currentSessionId,
    this.problemCategory,
    this.messages = const [],
    this.isLoading = false,
    this.error,
    this.isConnected = false,
  });

  ChatState copyWith({
    String? currentSessionId,
    ProblemCategory? problemCategory,
    List<ChatMessage>? messages,
    bool? isLoading,
    String? error,
    bool? isConnected,
  }) {
    return ChatState(
      currentSessionId: currentSessionId ?? this.currentSessionId,
      problemCategory: problemCategory ?? this.problemCategory,
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      isConnected: isConnected ?? this.isConnected,
    );
  }
}

// Chat messages notifier
class ChatMessagesNotifier extends StateNotifier<List<ChatMessage>> {
  final ApiService _apiService;

  ChatMessagesNotifier(this._apiService) : super([]);

  void addMessage(ChatMessage message) {
    state = [...state, message];
  }

  void clearMessages() {
    state = [];
  }

  void updateMessages(List<ChatMessage> messages) {
    state = messages;
  }
}

// Chat controller
class ChatController extends StateNotifier<AsyncValue<ChatState>> {
  final ApiService _apiService;

  ChatController(this._apiService) : super(const AsyncValue.data(ChatState()));

  // Start a new chat session with problem category
  Future<void> startChatSession({
    required ProblemCategory problemCategory,
    String? initialMessage,
  }) async {
    try {
      state = AsyncValue.data(state.value?.copyWith(
        isLoading: true,
        error: null,
      ) ?? const ChatState(isLoading: true));

      // Send initial message if provided, which will create the session
      if (initialMessage != null && initialMessage.isNotEmpty) {
        final response = await _apiService.sendTextMessage(
          message: initialMessage,
          problemCategory: problemCategory,
        );

        state = AsyncValue.data(ChatState(
          currentSessionId: response.sessionId,
          problemCategory: problemCategory,
          messages: [], // Will be updated when we add the messages
          isLoading: false,
          isConnected: true,
        ));
      } else {
        // Just set up the session without sending a message
        state = AsyncValue.data(ChatState(
          problemCategory: problemCategory,
          isLoading: false,
          isConnected: true,
        ));
      }
    } catch (e) {
      state = AsyncValue.data(ChatState(
        problemCategory: problemCategory,
        isLoading: false,
        error: 'Failed to start chat session: $e',
      ));
    }
  }

  // Send text message
  Future<void> sendTextMessage(String message) async {
    final currentState = state.value;
    if (currentState == null) return;

    try {
      state = AsyncValue.data(currentState.copyWith(isLoading: true));

      final response = await _apiService.sendTextMessage(
        message: message,
        sessionId: currentState.currentSessionId,
        problemCategory: currentState.problemCategory,
      );

      // Create user message
      final userMessage = ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        role: 'user',
        type: 'text',
        content: MessageContent(text: message),
        timestamp: DateTime.now(),
        safetyStatus: 'safe',
      );

      // Create assistant message
      final assistantMessage = ChatMessage(
        id: response.messageId,
        role: 'assistant',
        type: 'text',
        content: MessageContent(text: response.responseText),
        timestamp: response.timestamp,
        safetyStatus: response.safetyStatus,
        metadata: response.thinkingText != null
            ? {'thinking': response.thinkingText}
            : null,
      );

      final updatedMessages = [
        ...currentState.messages,
        userMessage,
        assistantMessage,
      ];

      state = AsyncValue.data(currentState.copyWith(
        currentSessionId: response.sessionId,
        messages: updatedMessages,
        isLoading: false,
      ));
    } catch (e) {
      state = AsyncValue.data(currentState.copyWith(
        isLoading: false,
        error: 'Failed to send message: $e',
      ));
    }
  }

  // Send voice message
  Future<void> sendVoiceMessage(List<int> audioData) async {
    final currentState = state.value;
    if (currentState == null) return;

    try {
      state = AsyncValue.data(currentState.copyWith(isLoading: true));

      final response = await _apiService.sendVoiceMessage(
        audioData: audioData,
        sessionId: currentState.currentSessionId,
        problemCategory: currentState.problemCategory,
      );

      // Create user message (voice)
      final userMessage = ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        role: 'user',
        type: 'audio',
        content: MessageContent(audioData: audioData),
        timestamp: DateTime.now(),
        safetyStatus: 'safe',
      );

      // Create assistant message
      final assistantMessage = ChatMessage(
        id: response.messageId,
        role: 'assistant',
        type: response.responseAudio != null ? 'audio' : 'text',
        content: MessageContent(
          text: response.responseText,
          audioData: response.responseAudio,
        ),
        timestamp: response.timestamp,
        safetyStatus: response.safetyStatus,
      );

      final updatedMessages = [
        ...currentState.messages,
        userMessage,
        assistantMessage,
      ];

      state = AsyncValue.data(currentState.copyWith(
        currentSessionId: response.sessionId,
        messages: updatedMessages,
        isLoading: false,
      ));
    } catch (e) {
      state = AsyncValue.data(currentState.copyWith(
        isLoading: false,
        error: 'Failed to send voice message: $e',
      ));
    }
  }

  // End current session
  void endSession() {
    state = const AsyncValue.data(ChatState());
  }

  // Clear error
  void clearError() {
    final currentState = state.value;
    if (currentState != null) {
      state = AsyncValue.data(currentState.copyWith(error: null));
    }
  }
}

// Utility function to get problem category display name
String getProblemCategoryDisplayName(ProblemCategory category) {
  switch (category) {
    case ProblemCategory.stress_anxiety:
      return 'Stress & Anxiety';
    case ProblemCategory.depression_sadness:
      return 'Depression & Sadness';
    case ProblemCategory.relationship_issues:
      return 'Relationships';
    case ProblemCategory.academic_pressure:
      return 'Academic Pressure';
    case ProblemCategory.career_confusion:
      return 'Career Confusion';
    case ProblemCategory.family_problems:
      return 'Family Issues';
    case ProblemCategory.social_anxiety:
      return 'Social Anxiety';
    case ProblemCategory.self_esteem:
      return 'Self-Esteem';
    case ProblemCategory.sleep_issues:
      return 'Sleep Issues';
    case ProblemCategory.anger_management:
      return 'Anger Management';
    case ProblemCategory.addiction_habits:
      return 'Addiction & Habits';
    case ProblemCategory.grief_loss:
      return 'Grief & Loss';
    case ProblemCategory.identity_crisis:
      return 'Identity Crisis';
    case ProblemCategory.loneliness:
      return 'Loneliness';
    case ProblemCategory.general_wellness:
      return 'General Wellness';
  }
}

// Utility function to get problem category description
String getProblemCategoryDescription(ProblemCategory category) {
  switch (category) {
    case ProblemCategory.stress_anxiety:
      return 'Dealing with stress, worry, or anxious thoughts';
    case ProblemCategory.depression_sadness:
      return 'Feeling down, hopeless, or experiencing sadness';
    case ProblemCategory.relationship_issues:
      return 'Problems with friends, family, or romantic relationships';
    case ProblemCategory.academic_pressure:
      return 'School, college, or exam-related stress and pressure';
    case ProblemCategory.career_confusion:
      return 'Uncertainty about career choices or job-related stress';
    case ProblemCategory.family_problems:
      return 'Issues with family dynamics or expectations';
    case ProblemCategory.social_anxiety:
      return 'Difficulty in social situations or meeting new people';
    case ProblemCategory.self_esteem:
      return 'Low confidence or negative self-image';
    case ProblemCategory.sleep_issues:
      return 'Trouble sleeping or sleep-related problems';
    case ProblemCategory.anger_management:
      return 'Difficulty controlling anger or frustration';
    case ProblemCategory.addiction_habits:
      return 'Struggling with harmful habits or addictive behaviors';
    case ProblemCategory.grief_loss:
      return 'Coping with loss or grief';
    case ProblemCategory.identity_crisis:
      return 'Questions about identity, purpose, or life direction';
    case ProblemCategory.loneliness:
      return 'Feeling isolated or disconnected from others';
    case ProblemCategory.general_wellness:
      return 'Overall mental health and wellness support';
  }
}
