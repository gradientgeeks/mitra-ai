import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/user_model.dart';
import '../models/chat_models.dart';

class ApiService {
  // Platform-aware base URL configuration
  static String get baseUrl {
    if (kIsWeb) {
      // For Flutter Web, use localhost
      return 'http://localhost:8000/api/v1';
    } else if (Platform.isAndroid) {
      // For Android, use the machine's local IP address
      return 'http://192.168.94.12:8000/api/v1';
    } else if (Platform.isIOS) {
      // For iOS Simulator, use localhost; for device, use IP
      return 'http://192.168.94.12:8000/api/v1';
    } else {
      // Default fallback
      return 'http://localhost:8000/api/v1';
    }
  }
  
  // For production, override with:
  // static const String baseUrl = 'https://your-backend-domain.com/api/v1';
  
  final http.Client _client = http.Client();
  String? _authToken;

  ApiService() {
    print('🌐 API Service initialized with baseUrl: $baseUrl');
  }

  // Set the authentication token
  void setAuthToken(String token) {
    _authToken = token;
  }

  // Clear the authentication token
  void clearAuthToken() {
    _authToken = null;
  }

  // Get headers with authentication
  Map<String, String> get _headers {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    
    return headers;
  }

  // Handle API responses
  Map<String, dynamic> _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json.decode(response.body);
    } else {
      throw ApiException(
        statusCode: response.statusCode,
        message: response.body,
      );
    }
  }

  // Generic HTTP methods for internal use
  Future<Map<String, dynamic>> get(String endpoint, {Map<String, String>? queryParams}) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint').replace(queryParameters: queryParams);
      final response = await _client.get(uri, headers: _headers);
      return _handleResponse(response);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Generate a custom meditation
  Future<MeditationResponse> generateMeditation({
    required String type,
    required int duration,
    String? focusArea,
  }) async {
    try {
      final response = await post('/meditation/generate', data: {
        'type': type,
        'duration_minutes': duration,
        'focus_area': focusArea,
      });
      return MeditationResponse.fromJson(response);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Generate flashcards from journal entry
  Future<FlashcardResponse> generateFlashcards(String journalEntryId) async {
    try {
      final response = await post('/journal/$journalEntryId/flashcards');
      return FlashcardResponse.fromJson(response);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> post(String endpoint, {Map<String, dynamic>? data}) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl$endpoint'),
        headers: _headers,
        body: data != null ? json.encode(data) : null,
      );
      return _handleResponse(response);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> put(String endpoint, {Map<String, dynamic>? data}) async {
    try {
      final response = await _client.put(
        Uri.parse('$baseUrl$endpoint'),
        headers: _headers,
        body: data != null ? json.encode(data) : null,
      );
      return _handleResponse(response);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> delete(String endpoint) async {
    try {
      await _client.delete(
        Uri.parse('$baseUrl$endpoint'),
        headers: _headers,
      );
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Create anonymous user
  Future<UserModel> createAnonymousUser({UserPreferences? preferences}) async {
    try {
      final requestBody = {
        if (preferences != null) 'preferences': preferences.toJson(),
      };

      final response = await _client.post(
        Uri.parse('$baseUrl/user/create-anonymous'),
        headers: _headers,
        body: json.encode(requestBody),
      );

      final data = _handleResponse(response);
      return UserModel.fromJson(data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Complete user onboarding
  Future<UserModel> completeOnboarding({
    required AgeGroup ageGroup,
    int? birthYear,
    required String mitraName,
    required Gender mitraGender,
    required VoiceOption preferredVoice,
    String language = 'en',
    bool notificationEnabled = true,
    bool meditationReminders = false,
    bool journalReminders = false,
  }) async {
    try {
      final requestBody = {
        'age_group': _mapAgeGroupToBackend(ageGroup),
        if (birthYear != null) 'birth_year': birthYear,
        'mitra_name': mitraName,
        'mitra_gender': _mapGenderToBackend(mitraGender),
        'preferred_voice': _mapVoiceToBackend(preferredVoice),
        'language': language,
        'notification_enabled': notificationEnabled,
        'meditation_reminders': meditationReminders,
        'journal_reminders': journalReminders,
      };

      final response = await _client.post(
        Uri.parse('$baseUrl/user/onboarding'),
        headers: _headers,
        body: json.encode(requestBody),
      );

      final data = _handleResponse(response);
      return UserModel.fromJson(data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Get onboarding options
  Future<OnboardingOptions> getOnboardingOptions() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/user/onboarding/options'),
        headers: _headers,
      );

      final data = _handleResponse(response);
      return OnboardingOptions.fromJson(data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Get user profile
  Future<UserModel> getUserProfile() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/user/profile'),
        headers: _headers,
      );

      final data = _handleResponse(response);
      return UserModel.fromJson(data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Update user profile
  Future<UserModel> updateUserProfile({
    String? displayName,
    UserPreferences? preferences,
    AgeGroup? ageGroup,
    int? birthYear,
  }) async {
    try {
      final requestBody = <String, dynamic>{};
      
      if (displayName != null) requestBody['display_name'] = displayName;
      if (preferences != null) requestBody['preferences'] = preferences.toJson();
      if (ageGroup != null) requestBody['age_group'] = _mapAgeGroupToBackend(ageGroup);
      if (birthYear != null) requestBody['birth_year'] = birthYear;

      final response = await _client.put(
        Uri.parse('$baseUrl/user/profile'),
        headers: _headers,
        body: json.encode(requestBody),
      );

      final data = _handleResponse(response);
      return UserModel.fromJson(data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Get user preferences
  Future<UserPreferences> getUserPreferences() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/user/preferences'),
        headers: _headers,
      );

      final data = _handleResponse(response);
      return UserPreferences.fromJson(data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Update user preferences
  Future<UserPreferences> updateUserPreferences(UserPreferences preferences) async {
    try {
      final response = await _client.put(
        Uri.parse('$baseUrl/user/preferences'),
        headers: _headers,
        body: json.encode(preferences.toJson()),
      );

      final data = _handleResponse(response);
      return UserPreferences.fromJson(data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Link anonymous account with permanent provider
  Future<UserModel> linkAccount({
    required UserProvider provider,
    String? email,
    required String idToken,
  }) async {
    try {
      final requestBody = {
        'provider': provider.name.toLowerCase(),
        if (email != null) 'email': email,
        'id_token': idToken,
      };

      final response = await _client.post(
        Uri.parse('$baseUrl/user/link-account'),
        headers: _headers,
        body: json.encode(requestBody),
      );

      final data = _handleResponse(response);
      return UserModel.fromJson(data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Sign in user
  Future<Map<String, dynamic>> signInUser(String idToken) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/user/signin'),
        headers: _headers,
        body: json.encode({'id_token': idToken}),
      );

      return _handleResponse(response);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Refresh session
  Future<void> refreshSession() async {
    try {
      await _client.post(
        Uri.parse('$baseUrl/user/refresh-session'),
        headers: _headers,
      );
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Delete user account
  Future<void> deleteAccount() async {
    try {
      await _client.delete(
        Uri.parse('$baseUrl/user/account'),
        headers: _headers,
      );
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Get user stats
  Future<Map<String, dynamic>> getUserStats() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/user/stats'),
        headers: _headers,
      );

      return _handleResponse(response);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Generate Mitra profile image
  Future<List<int>> generateMitraProfileImage({
    required String mitraName,
    required Gender mitraGender,
    AgeGroup? ageGroup,
  }) async {
    try {
      final genderDescription = _mapGenderToDescription(mitraGender);
      final ageDescription = _mapAgeGroupToDescription(ageGroup);

      final prompt = 'A friendly AI companion named $mitraName, $genderDescription, $ageDescription, '
          'with a warm, welcoming expression, modern minimalist art style, soft colors, '
          'suitable for mental wellness app, culturally appropriate for Indian youth, '
          'peaceful and trustworthy appearance';

      final requestBody = {
        'prompt': prompt,
        'style': 'friendly_ai_companion'
      };

      final response = await _client.post(
        Uri.parse('$baseUrl/chat/generate-image'),
        headers: _headers,
        body: json.encode(requestBody),
      );

      if (response.statusCode == 200) {
        return response.bodyBytes;
      } else {
        throw ApiException(
          statusCode: response.statusCode,
          message: 'Failed to generate image',
        );
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  // ================= CHAT & VOICE SESSION METHODS =================

  // Send text message to chat
  Future<ChatResponse> sendTextMessage({
    required String message,
    String? sessionId,
    ProblemCategory? problemCategory,
    bool includeGrounding = false,
    bool generateImage = false,
  }) async {
    try {
      final requestBody = {
        'message': message,
        if (sessionId != null) 'session_id': sessionId,
        if (problemCategory != null) 'problem_category': _mapProblemCategoryToBackend(problemCategory),
        'include_grounding': includeGrounding,
        'generate_image': generateImage,
      };

      final response = await _client.post(
        Uri.parse('$baseUrl/chat/text'),
        headers: _headers,
        body: json.encode(requestBody),
      );

      final data = _handleResponse(response);
      return ChatResponse.fromJson(data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Send voice message to chat
  Future<ChatResponse> sendVoiceMessage({
    required List<int> audioData,
    String? sessionId,
    ProblemCategory? problemCategory,
    String responseFormat = 'audio',
  }) async {
    try {
      final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/chat/voice'));
      request.headers.addAll(_headers);

      // Add audio file
      request.files.add(http.MultipartFile.fromBytes(
        'audio_file',
        audioData,
        filename: 'audio.wav',
      ));

      // Add other fields
      if (sessionId != null) request.fields['session_id'] = sessionId;
      if (problemCategory != null) request.fields['problem_category'] = _mapProblemCategoryToBackend(problemCategory);
      request.fields['response_format'] = responseFormat;

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      final data = _handleResponse(response);
      return ChatResponse.fromJson(data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Get chat session summary
  Future<ChatSessionSummary> getChatSessionSummary({
    required String sessionId,
    bool includeMessages = false,
    int limit = 50,
  }) async {
    try {
      final queryParams = {
        'include_messages': includeMessages.toString(),
        'limit': limit.toString(),
      };

      final uri = Uri.parse('$baseUrl/chat/session/$sessionId').replace(
        queryParameters: queryParams,
      );

      final response = await _client.get(uri, headers: _headers);
      final data = _handleResponse(response);
      return ChatSessionSummary.fromJson(data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Get user's chat sessions
  Future<List<ChatSessionSummary>> getUserChatSessions({int limit = 10}) async {
    try {
      final queryParams = {'limit': limit.toString()};
      final uri = Uri.parse('$baseUrl/chat/sessions').replace(
        queryParameters: queryParams,
      );

      final response = await _client.get(uri, headers: _headers);
      final data = _handleResponse(response);

      return (data as List).map((item) => ChatSessionSummary.fromJson(item)).toList();
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Delete chat session
  Future<void> deleteChatSession(String sessionId) async {
    try {
      await _client.delete(
        Uri.parse('$baseUrl/chat/session/$sessionId'),
        headers: _headers,
      );
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Generate session resources
  Future<SessionResourcesResponse> generateSessionResources({
    required String sessionId,
    List<String>? resourceTypes,
    int maxResources = 3,
  }) async {
    try {
      final requestBody = {
        'session_id': sessionId,
        if (resourceTypes != null) 'resource_types': resourceTypes,
        'max_resources': maxResources,
      };

      final response = await _client.post(
        Uri.parse('$baseUrl/chat/session/$sessionId/resources'),
        headers: _headers,
        body: json.encode(requestBody),
      );

      final data = _handleResponse(response);
      return SessionResourcesResponse.fromJson(data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Get problem categories
  Future<List<ProblemCategoryInfo>> getProblemCategories() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/chat/categories'),
        headers: _headers,
      );

      final data = _handleResponse(response);
      return (data['categories'] as List)
          .map((item) => ProblemCategoryInfo.fromJson(item))
          .toList();
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Map frontend enums to backend string values
  String _mapAgeGroupToBackend(AgeGroup ageGroup) {
    switch (ageGroup) {
      case AgeGroup.teen:
        return 'teen';
      case AgeGroup.young_adult:
        return 'young_adult';
      case AgeGroup.adult:
        return 'adult';
      case AgeGroup.mature_adult:
        return 'mature_adult';
    }
  }

  String _mapGenderToBackend(Gender gender) {
    switch (gender) {
      case Gender.male:
        return 'male';
      case Gender.female:
        return 'female';
      case Gender.non_binary:
        return 'non_binary';
      case Gender.prefer_not_to_say:
        return 'prefer_not_to_say';
    }
  }

  String _mapVoiceToBackend(VoiceOption voice) {
    switch (voice) {
      case VoiceOption.puck:
        return 'Puck';
      case VoiceOption.charon:
        return 'Charon';
      case VoiceOption.kore:
        return 'Kore';
      case VoiceOption.fenrir:
        return 'Fenrir';
      case VoiceOption.aoede:
        return 'Aoede';
    }
  }

  String _mapProblemCategoryToBackend(ProblemCategory category) {
    switch (category) {
      case ProblemCategory.stress_anxiety:
        return 'stress_anxiety';
      case ProblemCategory.depression_sadness:
        return 'depression_sadness';
      case ProblemCategory.relationship_issues:
        return 'relationship_issues';
      case ProblemCategory.academic_pressure:
        return 'academic_pressure';
      case ProblemCategory.career_confusion:
        return 'career_confusion';
      case ProblemCategory.family_problems:
        return 'family_problems';
      case ProblemCategory.social_anxiety:
        return 'social_anxiety';
      case ProblemCategory.self_esteem:
        return 'self_esteem';
      case ProblemCategory.sleep_issues:
        return 'sleep_issues';
      case ProblemCategory.anger_management:
        return 'anger_management';
      case ProblemCategory.addiction_habits:
        return 'addiction_habits';
      case ProblemCategory.grief_loss:
        return 'grief_loss';
      case ProblemCategory.identity_crisis:
        return 'identity_crisis';
      case ProblemCategory.loneliness:
        return 'loneliness';
      case ProblemCategory.general_wellness:
        return 'general_wellness';
    }
  }

  String _mapGenderToDescription(Gender gender) {
    switch (gender) {
      case Gender.male:
        return 'masculine features';
      case Gender.female:
        return 'feminine features';
      case Gender.non_binary:
        return 'ambiguous, androgynous features';
      case Gender.prefer_not_to_say:
        return 'features that do not conform to traditional gender norms';
    }
  }

  String _mapAgeGroupToDescription(AgeGroup? ageGroup) {
    if (ageGroup == null) return 'ageless';

    switch (ageGroup) {
      case AgeGroup.teen:
        return 'teenage';
      case AgeGroup.young_adult:
        return 'young adult';
      case AgeGroup.adult:
        return 'adult';
      case AgeGroup.mature_adult:
        return 'mature adult';
    }
  }

  // Handle errors
  Exception _handleError(dynamic error) {
    if (error is ApiException) {
      return error;
    } else if (error is http.ClientException) {
      return ApiException(
        statusCode: 0,
        message: 'Network error: ${error.message}',
      );
    } else {
      return ApiException(
        statusCode: 0,
        message: 'Unexpected error: $error',
      );
    }
  }

  // Dispose the client
  void dispose() {
    _client.close();
  }
}

// Custom exception for API errors
class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException({required this.statusCode, required this.message});

  @override
  String toString() => 'ApiException: $statusCode - $message';
}

// Model for onboarding options
class OnboardingOptions {
  final List<OptionItem> ageGroups;
  final List<OptionItem> genders;
  final List<VoiceOptionItem> voices;
  final List<String> sampleMitraNames;

  OnboardingOptions({
    required this.ageGroups,
    required this.genders,
    required this.voices,
    required this.sampleMitraNames,
  });

  factory OnboardingOptions.fromJson(Map<String, dynamic> json) {
    return OnboardingOptions(
      ageGroups: (json['age_groups'] as List)
          .map((item) => OptionItem.fromJson(item))
          .toList(),
      genders: (json['genders'] as List)
          .map((item) => OptionItem.fromJson(item))
          .toList(),
      voices: (json['voices'] as List)
          .map((item) => VoiceOptionItem.fromJson(item))
          .toList(),
      sampleMitraNames: List<String>.from(json['sample_mitra_names']),
    );
  }
}

class OptionItem {
  final String value;
  final String label;

  OptionItem({required this.value, required this.label});

  factory OptionItem.fromJson(Map<String, dynamic> json) {
    return OptionItem(
      value: json['value'],
      label: json['label'],
    );
  }
}

class VoiceOptionItem {
  final String value;
  final String label;
  final String? description;

  VoiceOptionItem({
    required this.value,
    required this.label,
    this.description,
  });

  factory VoiceOptionItem.fromJson(Map<String, dynamic> json) {
    return VoiceOptionItem(
      value: json['value'],
      label: json['label'],
      description: json['description'],
    );
  }
}
