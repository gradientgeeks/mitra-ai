import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_model.freezed.dart';
part 'user_model.g.dart';

@freezed
class UserModel with _$UserModel {
  const factory UserModel({
    required String uid,
    required String provider,
    String? email,
    String? displayName,
    required bool isAnonymous,
    required String status,
    required DateTime createdAt,
    required DateTime lastLogin,
    required UserPreferences preferences,
    @Default(0) int totalSessions,
    DateTime? lastMoodEntry,
  }) = _UserModel;

  factory UserModel.fromJson(Map<String, dynamic> json) => _$UserModelFromJson(json);
}

@freezed
class UserPreferences with _$UserPreferences {
  const factory UserPreferences({
    @Default('en') String language,
    @Default(true) bool notificationEnabled,
    @Default(true) bool voiceEnabled,
    @Default(false) bool meditationReminders,
    @Default(false) bool journalReminders,
    @Default(true) bool crisisSupportEnabled,
    @Default('Puck') String preferredVoice,
  }) = _UserPreferences;

  factory UserPreferences.fromJson(Map<String, dynamic> json) => _$UserPreferencesFromJson(json);
}

enum UserProvider {
  anonymous,
  google,
  apple,
  email,
}

enum UserStatus {
  active,
  inactive,
  suspended,
}
