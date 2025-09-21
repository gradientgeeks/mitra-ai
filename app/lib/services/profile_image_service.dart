import 'dart:typed_data';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:http/http.dart' as http;
import '../models/user_model.dart';

class ProfileImageService {
  static const String baseUrl = 'https://mitra-ai-server-188702930872.us-central1.run.app/api/v1';
  final FirebaseStorage _storage = FirebaseStorage.instance;

  /// Generate Mitra profile image using backend AI service
  Future<Uint8List?> generateMitraProfileImage(
    String mitraName,
    Gender mitraGender,
    AgeGroup? ageGroup,
    String? authToken,
  ) async {
    try {
      final genderDescription = _getGenderDescription(mitraGender);
      final ageDescription = _getAgeDescription(ageGroup);

      final prompt = 'A friendly AI companion named $mitraName, $genderDescription, $ageDescription, '
          'with a warm, welcoming expression, modern minimalist art style, soft colors, '
          'suitable for mental wellness app, culturally appropriate for Indian youth, '
          'peaceful and trustworthy appearance';

      final response = await http.post(
        Uri.parse('$baseUrl/chat/generate-image'),
        headers: {
          'Content-Type': 'application/json',
          if (authToken != null) 'Authorization': 'Bearer $authToken',
        },
        body: '{"prompt": "$prompt", "style": "friendly_ai_companion"}',
      );

      if (response.statusCode == 200) {
        return response.bodyBytes;
      } else {
        throw Exception('Failed to generate profile image: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error generating profile image: $e');
    }
  }

  /// Save profile image to Firebase Storage and return download URL
  Future<String> saveProfileImageToStorage(
    String userId,
    String mitraName,
    Uint8List imageData,
  ) async {
    try {
      final fileName = 'mitra_profile_${userId}_${DateTime.now().millisecondsSinceEpoch}.jpg';
      final ref = _storage.ref().child('profile_images').child(fileName);

      await ref.putData(
        imageData,
        SettableMetadata(
          contentType: 'image/jpeg',
          customMetadata: {
            'userId': userId,
            'mitraName': mitraName,
            'generatedAt': DateTime.now().toIso8601String(),
          },
        ),
      );

      return await ref.getDownloadURL();
    } catch (e) {
      throw Exception('Error saving profile image to storage: $e');
    }
  }

  /// Get or generate Mitra profile image URL
  Future<String?> getMitraProfileImageUrl(
    String userId,
    String mitraName,
    Gender mitraGender,
    AgeGroup? ageGroup,
    String? authToken,
    {bool forceRegenerate = false}
  ) async {
    try {
      // If not forcing regeneration, try to get existing image
      if (!forceRegenerate) {
        final existingUrl = await _getExistingProfileImageUrl(userId);
        if (existingUrl != null) {
          return existingUrl;
        }
      }

      // Generate new profile image
      final imageData = await generateMitraProfileImage(
        mitraName,
        mitraGender,
        ageGroup,
        authToken,
      );

      if (imageData != null) {
        return await saveProfileImageToStorage(userId, mitraName, imageData);
      }

      return null;
    } catch (e) {
      print('Error getting profile image URL: $e');
      return null;
    }
  }

  /// Check if profile image already exists in storage
  Future<String?> _getExistingProfileImageUrl(String userId) async {
    try {
      final listResult = await _storage.ref().child('profile_images').listAll();

      for (var item in listResult.items) {
        final metadata = await item.getMetadata();
        if (metadata.customMetadata?['userId'] == userId) {
          return await item.getDownloadURL();
        }
      }

      return null;
    } catch (e) {
      print('Error checking existing profile image: $e');
      return null;
    }
  }

  /// Delete existing profile image from storage
  Future<void> deleteProfileImage(String userId) async {
    try {
      final listResult = await _storage.ref().child('profile_images').listAll();

      for (var item in listResult.items) {
        final metadata = await item.getMetadata();
        if (metadata.customMetadata?['userId'] == userId) {
          await item.delete();
        }
      }
    } catch (e) {
      print('Error deleting profile image: $e');
    }
  }

  String _getGenderDescription(Gender gender) {
    switch (gender) {
      case Gender.male:
        return 'masculine appearance';
      case Gender.female:
        return 'feminine appearance';
      case Gender.non_binary:
        return 'androgynous appearance';
      case Gender.prefer_not_to_say:
        return 'neutral friendly appearance';
    }
  }

  String _getAgeDescription(AgeGroup? ageGroup) {
    switch (ageGroup) {
      case AgeGroup.teen:
        return 'youthful and energetic';
      case AgeGroup.young_adult:
        return 'young and approachable';
      case AgeGroup.adult:
        return 'mature and wise';
      case AgeGroup.mature_adult:
        return 'experienced and caring';
      case null:
        return 'timeless and friendly';
    }
  }
}
