// Enums should be defined at the top level
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

enum AgeGroup {
  teen,          // 13-17 years
  young_adult,   // 18-24 years
  adult,         // 25-34 years
  mature_adult,  // 35+ years
}

enum Gender {
  male,
  female,
  non_binary,
  prefer_not_to_say,
}

enum VoiceOption {
  puck,
  charon,
  kore,
  fenrir,
  aoede;

  // Add value getter for backward compatibility
  String get value {
    switch (this) {
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

  // Add display name getter
  String get displayName {
    switch (this) {
      case VoiceOption.puck:
        return 'Puck (Upbeat)';
      case VoiceOption.charon:
        return 'Charon (Informative)';
      case VoiceOption.kore:
        return 'Kore (Firm)';
      case VoiceOption.fenrir:
        return 'Fenrir (Excitable)';
      case VoiceOption.aoede:
        return 'Aoede (Breezy)';
    }
  }
}

enum ProblemCategory {
  stress_anxiety,
  depression_sadness,
  relationship_issues,
  academic_pressure,
  career_confusion,
  family_problems,
  social_anxiety,
  self_esteem,
  sleep_issues,
  anger_management,
  addiction_habits,
  grief_loss,
  identity_crisis,
  loneliness,
  general_wellness,
}

class UserPreferences {
  final String language;
  final bool notificationEnabled;
  final bool voiceEnabled;
  final bool meditationReminders;
  final bool journalReminders;
  final bool crisisSupportEnabled;
  final VoiceOption preferredVoice;
  final String mitraName;
  final Gender mitraGender;
  final AgeGroup? ageGroup;
  final String? mitraProfileImageUrl;
  final bool onboardingCompleted;

  const UserPreferences({
    this.language = 'en',
    this.notificationEnabled = true,
    this.voiceEnabled = true,
    this.meditationReminders = false,
    this.journalReminders = false,
    this.crisisSupportEnabled = true,
    this.preferredVoice = VoiceOption.puck,
    this.mitraName = 'Mitra',
    this.mitraGender = Gender.female,
    this.ageGroup,
    this.mitraProfileImageUrl,
    this.onboardingCompleted = false,
  });

  factory UserPreferences.fromJson(Map<String, dynamic> json) {
    return UserPreferences(
      language: json['language'] as String? ?? 'en',
      notificationEnabled: json['notification_enabled'] as bool? ?? true,
      voiceEnabled: json['voice_enabled'] as bool? ?? true,
      meditationReminders: json['meditation_reminders'] as bool? ?? false,
      journalReminders: json['journal_reminders'] as bool? ?? false,
      crisisSupportEnabled: json['crisis_support_enabled'] as bool? ?? true,
      preferredVoice: VoiceOption.values.firstWhere(
        (v) => v.name.toLowerCase() == (json['preferred_voice'] as String? ?? 'puck').toLowerCase(),
        orElse: () => VoiceOption.puck,
      ),
      mitraName: json['mitra_name'] as String? ?? 'Mitra',
      mitraGender: Gender.values.firstWhere(
        (g) => g.name.toLowerCase() == (json['mitra_gender'] as String? ?? 'female').toLowerCase(),
        orElse: () => Gender.female,
      ),
      ageGroup: json['age_group'] != null
        ? AgeGroup.values.firstWhere(
            (a) => a.name.toLowerCase() == (json['age_group'] as String).toLowerCase(),
            orElse: () => AgeGroup.adult,
          )
        : null,
      mitraProfileImageUrl: json['mitra_profile_image_url'] as String?,
      onboardingCompleted: json['onboarding_completed'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'language': language,
      'notification_enabled': notificationEnabled,
      'voice_enabled': voiceEnabled,
      'meditation_reminders': meditationReminders,
      'journal_reminders': journalReminders,
      'crisis_support_enabled': crisisSupportEnabled,
      'preferred_voice': preferredVoice.name.toLowerCase(),
      'mitra_name': mitraName,
      'mitra_gender': mitraGender.name.toLowerCase(),
      'age_group': ageGroup?.name.toLowerCase(),
      'mitra_profile_image_url': mitraProfileImageUrl,
      'onboarding_completed': onboardingCompleted,
    };
  }

  UserPreferences copyWith({
    String? language,
    bool? notificationEnabled,
    bool? voiceEnabled,
    bool? meditationReminders,
    bool? journalReminders,
    bool? crisisSupportEnabled,
    VoiceOption? preferredVoice,
    String? mitraName,
    Gender? mitraGender,
    AgeGroup? ageGroup,
    String? mitraProfileImageUrl,
    bool? onboardingCompleted,
  }) {
    return UserPreferences(
      language: language ?? this.language,
      notificationEnabled: notificationEnabled ?? this.notificationEnabled,
      voiceEnabled: voiceEnabled ?? this.voiceEnabled,
      meditationReminders: meditationReminders ?? this.meditationReminders,
      journalReminders: journalReminders ?? this.journalReminders,
      crisisSupportEnabled: crisisSupportEnabled ?? this.crisisSupportEnabled,
      preferredVoice: preferredVoice ?? this.preferredVoice,
      mitraName: mitraName ?? this.mitraName,
      mitraGender: mitraGender ?? this.mitraGender,
      ageGroup: ageGroup ?? this.ageGroup,
      mitraProfileImageUrl: mitraProfileImageUrl ?? this.mitraProfileImageUrl,
      onboardingCompleted: onboardingCompleted ?? this.onboardingCompleted,
    );
  }
}

class UserModel {
  final String uid;
  final UserProvider provider;
  final String? email;
  final String? displayName;
  final bool isAnonymous;
  final UserStatus status;
  final DateTime createdAt;
  final DateTime lastLogin;
  final UserPreferences preferences;
  final int totalSessions;
  final DateTime? lastMoodEntry;
  final AgeGroup? ageGroup;
  final int? birthYear;
  final bool onboardingCompleted;
  final String? mitraProfileImageUrl;

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
    this.ageGroup,
    this.birthYear,
    this.onboardingCompleted = false,
    this.mitraProfileImageUrl,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      uid: json['uid'] as String,
      provider: UserProvider.values.firstWhere(
        (p) => p.name.toLowerCase() == (json['provider'] as String).toLowerCase(),
        orElse: () => UserProvider.anonymous,
      ),
      email: json['email'] as String?,
      displayName: json['display_name'] as String?,
      isAnonymous: json['is_anonymous'] as bool,
      status: UserStatus.values.firstWhere(
        (s) => s.name.toLowerCase() == (json['status'] as String).toLowerCase(),
        orElse: () => UserStatus.active,
      ),
      createdAt: DateTime.parse(json['created_at'] as String),
      lastLogin: DateTime.parse(json['last_login'] as String),
      preferences: UserPreferences.fromJson(json['preferences'] as Map<String, dynamic>),
      totalSessions: json['total_sessions'] as int? ?? 0,
      lastMoodEntry: json['last_mood_entry'] != null
          ? DateTime.parse(json['last_mood_entry'] as String)
          : null,
      ageGroup: json['age_group'] != null
        ? AgeGroup.values.firstWhere(
            (a) => a.name.toLowerCase() == (json['age_group'] as String).toLowerCase(),
            orElse: () => AgeGroup.adult,
          )
        : null,
      birthYear: json['birth_year'] as int?,
      onboardingCompleted: json['onboarding_completed'] as bool? ?? false,
      mitraProfileImageUrl: json['mitra_profile_image_url'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'uid': uid,
      'provider': provider.name.toLowerCase(),
      'email': email,
      'display_name': displayName,
      'is_anonymous': isAnonymous,
      'status': status.name.toLowerCase(),
      'created_at': createdAt.toIso8601String(),
      'last_login': lastLogin.toIso8601String(),
      'preferences': preferences.toJson(),
      'total_sessions': totalSessions,
      'last_mood_entry': lastMoodEntry?.toIso8601String(),
      'age_group': ageGroup?.name.toLowerCase(),
      'birth_year': birthYear,
      'onboarding_completed': onboardingCompleted,
      'mitra_profile_image_url': mitraProfileImageUrl,
    };
  }

  UserModel copyWith({
    String? uid,
    UserProvider? provider,
    String? email,
    String? displayName,
    bool? isAnonymous,
    UserStatus? status,
    DateTime? createdAt,
    DateTime? lastLogin,
    UserPreferences? preferences,
    int? totalSessions,
    DateTime? lastMoodEntry,
    AgeGroup? ageGroup,
    int? birthYear,
    bool? onboardingCompleted,
    String? mitraProfileImageUrl,
  }) {
    return UserModel(
      uid: uid ?? this.uid,
      provider: provider ?? this.provider,
      email: email ?? this.email,
      displayName: displayName ?? this.displayName,
      isAnonymous: isAnonymous ?? this.isAnonymous,
      status: status ?? this.status,
      createdAt: createdAt ?? this.createdAt,
      lastLogin: lastLogin ?? this.lastLogin,
      preferences: preferences ?? this.preferences,
      totalSessions: totalSessions ?? this.totalSessions,
      lastMoodEntry: lastMoodEntry ?? this.lastMoodEntry,
      ageGroup: ageGroup ?? this.ageGroup,
      birthYear: birthYear ?? this.birthYear,
      onboardingCompleted: onboardingCompleted ?? this.onboardingCompleted,
      mitraProfileImageUrl: mitraProfileImageUrl ?? this.mitraProfileImageUrl,
    );
  }
}
