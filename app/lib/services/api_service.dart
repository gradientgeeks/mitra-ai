import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user_model.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api/v1'; // Updated to match backend routes

  static Future<http.Response> _makeRequest({
    required String method,
    required String endpoint,
    Map<String, dynamic>? body,
    Map<String, String>? headers,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');
    
    final defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    if (headers != null) {
      defaultHeaders.addAll(headers);
    }
    
    http.Response response;
    
    switch (method.toUpperCase()) {
      case 'GET':
        response = await http.get(uri, headers: defaultHeaders);
        break;
      case 'POST':
        response = await http.post(
          uri,
          headers: defaultHeaders,
          body: body != null ? jsonEncode(body) : null,
        );
        break;
      case 'PUT':
        response = await http.put(
          uri,
          headers: defaultHeaders,
          body: body != null ? jsonEncode(body) : null,
        );
        break;
      case 'DELETE':
        response = await http.delete(uri, headers: defaultHeaders);
        break;
      default:
        throw ArgumentError('Unsupported HTTP method: $method');
    }
    
    return response;
  }
  
  static Future<Map<String, dynamic>> _handleResponse(http.Response response) async {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      final errorBody = jsonDecode(response.body) as Map<String, dynamic>;
      throw ApiException(
        statusCode: response.statusCode,
        message: errorBody['detail'] ?? 'An error occurred',
      );
    }
  }
  
  // User Management APIs
  static Future<UserModel> getCurrentUser(String authToken) async {
    final response = await _makeRequest(
      method: 'GET',
      endpoint: '/users/me',
      headers: {'Authorization': 'Bearer $authToken'},
    );
    
    final data = await _handleResponse(response);
    return UserModel.fromJson(data);
  }
  
  static Future<Map<String, dynamic>> completeOnboarding({
    required String authToken,
    required OnboardingRequest request,
  }) async {
    final response = await _makeRequest(
      method: 'POST',
      endpoint: '/users/complete-onboarding',
      headers: {'Authorization': 'Bearer $authToken'},
      body: request.toJson(),
    );
    
    return await _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> updateUserPreferences({
    required String authToken,
    required UserPreferences preferences,
  }) async {
    final response = await _makeRequest(
      method: 'PUT',
      endpoint: '/users/preferences',
      headers: {'Authorization': 'Bearer $authToken'},
      body: preferences.toJson(),
    );
    
    return await _handleResponse(response);
  }
  
  // Chat APIs
  static Future<Map<String, dynamic>> sendTextMessage({
    required String authToken,
    required String message,
    String? sessionId,
  }) async {
    final response = await _makeRequest(
      method: 'POST',
      endpoint: '/chat/text',
      headers: {'Authorization': 'Bearer $authToken'},
      body: {
        'text': message,
        if (sessionId != null) 'session_id': sessionId,
      },
    );
    
    return await _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> setSessionProblemCategories({
    required String authToken,
    required String sessionId,
    required List<String> categories,
  }) async {
    final response = await _makeRequest(
      method: 'POST',
      endpoint: '/chat/session/$sessionId/categories',
      headers: {'Authorization': 'Bearer $authToken'},
      body: {'categories': categories},
    );
    
    return await _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> completeSession({
    required String authToken,
    required String sessionId,
  }) async {
    final response = await _makeRequest(
      method: 'POST',
      endpoint: '/chat/session/$sessionId/complete',
      headers: {'Authorization': 'Bearer $authToken'},
    );
    
    return await _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> getSessionSummary({
    required String authToken,
    required String sessionId,
    bool includeMessages = false,
  }) async {
    final response = await _makeRequest(
      method: 'GET',
      endpoint: '/chat/session/$sessionId?include_messages=$includeMessages',
      headers: {'Authorization': 'Bearer $authToken'},
    );
    
    return await _handleResponse(response);
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;
  
  const ApiException({
    required this.statusCode,
    required this.message,
  });
  
  @override
  String toString() {
    return 'ApiException: $statusCode - $message';
  }
}