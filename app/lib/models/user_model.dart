class UserModel {
  final String uid;
  final String provider;
  final String? email;
  final String? displayName;
  final bool isAnonymous;
  final String status;
  final DateTime createdAt;
  final DateTime lastLogin;
  final UserPreferences preferences;
  final int totalSessions;
  final DateTime? lastMoodEntry;

  const UserModel({
    required this.uid,
    required this.provider,
    this.email,
    this.displayName,
    required this.isAnonymous,
    required this.status,
    required this.createdAt,
    required this.lastLogin,
    required this.preferences,
    this.totalSessions = 0,
    this.lastMoodEntry,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      uid: json['uid'] as String,
      provider: json['provider'] as String,
      email: json['email'] as String?,
      displayName: json['displayName'] as String?,
      isAnonymous: json['isAnonymous'] as bool,
      status: json['status'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      lastLogin: DateTime.parse(json['lastLogin'] as String),
      preferences: UserPreferences.fromJson(json['preferences'] as Map<String, dynamic>),
      totalSessions: json['totalSessions'] as int? ?? 0,
      lastMoodEntry: json['lastMoodEntry'] != null
          ? DateTime.parse(json['lastMoodEntry'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'uid': uid,
      'provider': provider,
      'email': email,
      'displayName': displayName,
      'isAnonymous': isAnonymous,
      'status': status,
      'createdAt': createdAt.toIso8601String(),
      'lastLogin': lastLogin.toIso8601String(),
      'preferences': preferences.toJson(),
      'totalSessions': totalSessions,
      'lastMoodEntry': lastMoodEntry?.toIso8601String(),
    };
  }
}

class UserPreferences {
  final String language;
  final bool notificationEnabled;
  final bool voiceEnabled;
  final bool meditationReminders;
  final bool journalReminders;
  final bool crisisSupportEnabled;
  final String preferredVoice;

  const UserPreferences({
    this.language = 'en',
    this.notificationEnabled = true,
    this.voiceEnabled = true,
    this.meditationReminders = false,
    this.journalReminders = false,
    this.crisisSupportEnabled = true,
    this.preferredVoice = 'Puck',
  });

  factory UserPreferences.fromJson(Map<String, dynamic> json) {
    return UserPreferences(
      language: json['language'] as String? ?? 'en',
      notificationEnabled: json['notificationEnabled'] as bool? ?? true,
      voiceEnabled: json['voiceEnabled'] as bool? ?? true,
      meditationReminders: json['meditationReminders'] as bool? ?? false,
      journalReminders: json['journalReminders'] as bool? ?? false,
      crisisSupportEnabled: json['crisisSupportEnabled'] as bool? ?? true,
      preferredVoice: json['preferredVoice'] as String? ?? 'Puck',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'language': language,
      'notificationEnabled': notificationEnabled,
      'voiceEnabled': voiceEnabled,
      'meditationReminders': meditationReminders,
      'journalReminders': journalReminders,
      'crisisSupportEnabled': crisisSupportEnabled,
      'preferredVoice': preferredVoice,
    };
  }
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
