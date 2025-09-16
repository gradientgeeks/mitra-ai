import 'user_model.dart';

// Chat response models
class ChatResponse {
  final String sessionId;
  final String messageId;
  final String? responseText;
  final List<int>? responseAudio;
  final List<int>? generatedImage;
  final String safetyStatus;
  final List<GroundingSource>? groundingSources;
  final DateTime timestamp;
  final String? thinkingText;
  final List<GeneratedResource>? generatedResources;

  const ChatResponse({
    required this.sessionId,
    required this.messageId,
    this.responseText,
    this.responseAudio,
    this.generatedImage,
    required this.safetyStatus,
    this.groundingSources,
    required this.timestamp,
    this.thinkingText,
    this.generatedResources,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      sessionId: json['session_id'] as String,
      messageId: json['message_id'] as String,
      responseText: json['response_text'] as String?,
      responseAudio: json['response_audio'] != null
          ? List<int>.from(json['response_audio'])
          : null,
      generatedImage: json['generated_image'] != null
          ? List<int>.from(json['generated_image'])
          : null,
      safetyStatus: json['safety_status'] as String,
      groundingSources: json['grounding_sources'] != null
          ? (json['grounding_sources'] as List)
              .map((item) => GroundingSource.fromJson(item))
              .toList()
          : null,
      timestamp: DateTime.parse(json['timestamp'] as String),
      thinkingText: json['thinking_text'] as String?,
      generatedResources: json['generated_resources'] != null
          ? (json['generated_resources'] as List)
              .map((item) => GeneratedResource.fromJson(item))
              .toList()
          : null,
    );
  }
}

class MeditationResponse {
  final String sessionId;
  final String title;
  final String script;
  final int durationMinutes;
  final List<String> instructions;
  final DateTime createdAt;

  const MeditationResponse({
    required this.sessionId,
    required this.title,
    required this.script,
    required this.durationMinutes,
    required this.instructions,
    required this.createdAt,
  });

  factory MeditationResponse.fromJson(Map<String, dynamic> json) {
    return MeditationResponse(
      sessionId: json['session_id'] as String,
      title: json['title'] as String,
      script: json['script'] as String,
      durationMinutes: json['duration_minutes'] as int,
      instructions: List<String>.from(json['instructions']),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

class GroundingSource {
  final String title;
  final String url;
  final String snippet;
  final double? relevanceScore;

  const GroundingSource({
    required this.title,
    required this.url,
    required this.snippet,
    this.relevanceScore,
  });

  factory GroundingSource.fromJson(Map<String, dynamic> json) {
    return GroundingSource(
      title: json['title'] as String,
      url: json['url'] as String,
      snippet: json['snippet'] as String,
      relevanceScore: json['relevance_score'] as double?,
    );
  }
}

class GeneratedResource {
  final String id;
  final String type;
  final String title;
  final String description;
  final String content;
  final int? durationMinutes;
  final String difficultyLevel;
  final List<String> tags;
  final DateTime createdAt;
  final ProblemCategory problemCategory;

  const GeneratedResource({
    required this.id,
    required this.type,
    required this.title,
    required this.description,
    required this.content,
    this.durationMinutes,
    required this.difficultyLevel,
    required this.tags,
    required this.createdAt,
    required this.problemCategory,
  });

  factory GeneratedResource.fromJson(Map<String, dynamic> json) {
    return GeneratedResource(
      id: json['id'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      content: json['content'] as String,
      durationMinutes: json['duration_minutes'] as int?,
      difficultyLevel: json['difficulty_level'] as String,
      tags: List<String>.from(json['tags']),
      createdAt: DateTime.parse(json['created_at'] as String),
      problemCategory: ProblemCategory.values.firstWhere(
        (category) => category.name == json['problem_category'],
        orElse: () => ProblemCategory.general_wellness,
      ),
    );
  }
}

class ChatSessionSummary {
  final String sessionId;
  final String userId;
  final String mode;
  final DateTime createdAt;
  final DateTime updatedAt;
  final int totalMessages;
  final String? contextSummary;
  final List<ChatMessage>? recentMessages;
  final bool isActive;
  final ProblemCategory? problemCategory;
  final List<GeneratedResource> generatedResources;

  const ChatSessionSummary({
    required this.sessionId,
    required this.userId,
    required this.mode,
    required this.createdAt,
    required this.updatedAt,
    required this.totalMessages,
    this.contextSummary,
    this.recentMessages,
    required this.isActive,
    this.problemCategory,
    required this.generatedResources,
  });

  factory ChatSessionSummary.fromJson(Map<String, dynamic> json) {
    return ChatSessionSummary(
      sessionId: json['session_id'] as String,
      userId: json['user_id'] as String,
      mode: json['mode'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      totalMessages: json['total_messages'] as int,
      contextSummary: json['context_summary'] as String?,
      recentMessages: json['recent_messages'] != null
          ? (json['recent_messages'] as List)
              .map((item) => ChatMessage.fromJson(item))
              .toList()
          : null,
      isActive: json['is_active'] as bool,
      problemCategory: json['problem_category'] != null
          ? ProblemCategory.values.firstWhere(
              (category) => category.name == json['problem_category'],
              orElse: () => ProblemCategory.general_wellness,
            )
          : null,
      generatedResources: json['generated_resources'] != null
          ? (json['generated_resources'] as List)
              .map((item) => GeneratedResource.fromJson(item))
              .toList()
          : [],
    );
  }
}

class ChatMessage {
  final String id;
  final String role;
  final String type;
  final MessageContent content;
  final DateTime timestamp;
  final String safetyStatus;
  final Map<String, dynamic>? metadata;

  const ChatMessage({
    required this.id,
    required this.role,
    required this.type,
    required this.content,
    required this.timestamp,
    required this.safetyStatus,
    this.metadata,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] as String,
      role: json['role'] as String,
      type: json['type'] as String,
      content: MessageContent.fromJson(json['content']),
      timestamp: DateTime.parse(json['timestamp'] as String),
      safetyStatus: json['safety_status'] as String,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }
}

class MessageContent {
  final String? text;
  final List<int>? audioData;
  final List<int>? imageData;
  final Map<String, dynamic>? structuredData;
  final String? htmlContent;

  const MessageContent({
    this.text,
    this.audioData,
    this.imageData,
    this.structuredData,
    this.htmlContent,
  });

  factory MessageContent.fromJson(Map<String, dynamic> json) {
    return MessageContent(
      text: json['text'] as String?,
      audioData: json['audio_data'] != null
          ? List<int>.from(json['audio_data'])
          : null,
      imageData: json['image_data'] != null
          ? List<int>.from(json['image_data'])
          : null,
      structuredData: json['structured_data'] as Map<String, dynamic>?,
      htmlContent: json['html_content'] as String?,
    );
  }
}

class SessionResourcesResponse {
  final String sessionId;
  final List<GeneratedResource> resources;
  final ProblemCategory problemCategory;
  final DateTime generatedAt;

  const SessionResourcesResponse({
    required this.sessionId,
    required this.resources,
    required this.problemCategory,
    required this.generatedAt,
  });

  factory SessionResourcesResponse.fromJson(Map<String, dynamic> json) {
    return SessionResourcesResponse(
      sessionId: json['session_id'] as String,
      resources: (json['resources'] as List)
          .map((item) => GeneratedResource.fromJson(item))
          .toList(),
      problemCategory: ProblemCategory.values.firstWhere(
        (category) => category.name == json['problem_category'],
        orElse: () => ProblemCategory.general_wellness,
      ),
      generatedAt: DateTime.parse(json['generated_at'] as String),
    );
  }
}

class ProblemCategoryInfo {
  final String value;
  final String label;
  final String description;

  const ProblemCategoryInfo({
    required this.value,
    required this.label,
    required this.description,
  });

  factory ProblemCategoryInfo.fromJson(Map<String, dynamic> json) {
    return ProblemCategoryInfo(
      value: json['value'] as String,
      label: json['label'] as String,
      description: json['description'] as String,
    );
  }
}

// Resource types enum
enum ResourceType {
  meditation,
  breathing_exercise,
  coping_strategies,
  affirmations,
  articles,
  videos,
  worksheets,
  emergency_contacts,
}

class Flashcard {
  final String id;
  final String front;
  final String back;
  final DateTime createdAt;

  const Flashcard({
    required this.id,
    required this.front,
    required this.back,
    required this.createdAt,
  });

  factory Flashcard.fromJson(Map<String, dynamic> json) {
    return Flashcard(
      id: json['id'] as String,
      front: json['front'] as String,
      back: json['back'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

class FlashcardResponse {
  final String journalEntryId;
  final List<Flashcard> flashcards;
  final DateTime generatedAt;

  const FlashcardResponse({
    required this.journalEntryId,
    required this.flashcards,
    required this.generatedAt,
  });

  factory FlashcardResponse.fromJson(Map<String, dynamic> json) {
    return FlashcardResponse(
      journalEntryId: json['journal_entry_id'] as String,
      flashcards: (json['flashcards'] as List)
          .map((item) => Flashcard.fromJson(item))
          .toList(),
      generatedAt: DateTime.parse(json['generated_at'] as String),
    );
  }
}
