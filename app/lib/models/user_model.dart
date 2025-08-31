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
<<<<<<< HEAD
  final String id;
  final String email;
  final bool isOnboardingCompleted;
  final UserPreferences preferences;
  final int totalSessions;
  final DateTime createdAt;
  final DateTime updatedAt;
=======
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
>>>>>>> feat/voice

  const UserModel({
    required this.id,
    required this.email,
    required this.isOnboardingCompleted,
    required this.preferences,
<<<<<<< HEAD
    required this.totalSessions,
    required this.createdAt,
    required this.updatedAt,
=======
    this.totalSessions = 0,
    this.lastMoodEntry,
    this.ageGroup,
    this.birthYear,
    this.onboardingCompleted = false,
    this.mitraProfileImageUrl,
>>>>>>> feat/voice
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
<<<<<<< HEAD
      id: json['id'] as String,
      email: json['email'] as String,
      isOnboardingCompleted: json['isOnboardingCompleted'] as bool,
      preferences: UserPreferences.fromJson(json['preferences'] as Map<String, dynamic>),
      totalSessions: json['totalSessions'] as int,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
=======
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
>>>>>>> feat/voice
    );
  }

  Map<String, dynamic> toJson() {
    return {
<<<<<<< HEAD
      'id': id,
      'email': email,
      'isOnboardingCompleted': isOnboardingCompleted,
      'preferences': preferences.toJson(),
      'totalSessions': totalSessions,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
=======
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
>>>>>>> feat/voice
    };
  }

<<<<<<< HEAD
class UserPreferences {
  final String mitraName;
  final VoiceType preferredVoice;
  final List<String> interests;
  final bool enableNotifications;

  const UserPreferences({
    required this.mitraName,
    required this.preferredVoice,
    required this.interests,
    required this.enableNotifications,
  });

  factory UserPreferences.fromJson(Map<String, dynamic> json) {
    return UserPreferences(
      mitraName: json['mitraName'] as String,
      preferredVoice: VoiceType.values.firstWhere(
        (e) => e.name == json['preferredVoice'],
        orElse: () => VoiceType.femaleYoung,
      ),
      interests: List<String>.from(json['interests'] as List),
      enableNotifications: json['enableNotifications'] as bool,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'mitraName': mitraName,
      'preferredVoice': preferredVoice.name,
      'interests': interests,
      'enableNotifications': enableNotifications,
    };
  }
}

class OnboardingRequest {
  final String name;
  final int age;
  final String gender;
  final List<String> interests;
  final String mitraName;
  final VoiceType preferredVoice;

  const OnboardingRequest({
    required this.name,
    required this.age,
    required this.gender,
    required this.interests,
    required this.mitraName,
    required this.preferredVoice,
  });

  factory OnboardingRequest.fromJson(Map<String, dynamic> json) {
    return OnboardingRequest(
      name: json['name'] as String,
      age: json['age'] as int,
      gender: json['gender'] as String,
      interests: List<String>.from(json['interests'] as List),
      mitraName: json['mitraName'] as String,
      preferredVoice: VoiceType.values.firstWhere(
        (e) => e.name == json['preferredVoice'],
        orElse: () => VoiceType.femaleYoung,
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'age': age,
      'gender': gender,
      'interests': interests,
      'mitraName': mitraName,
      'preferredVoice': preferredVoice.name,
    };
  }
}

enum VoiceType {
  femaleYoung,
  femaleMature,
  maleYoung,
  maleMature,
}

enum AgeGroup {
  young,    // 13-17
  adult,    // 18-64
  senior,   // 65+
}

enum Gender {
  male,
  female,
  nonBinary,
}

extension VoiceTypeExtension on VoiceType {
  String get displayName {
    switch (this) {
      case VoiceType.femaleYoung:
        return 'Female (Young)';
      case VoiceType.femaleMature:
        return 'Female (Mature)';
      case VoiceType.maleYoung:
        return 'Male (Young)';
      case VoiceType.maleMature:
        return 'Male (Mature)';
    }
  }
}

extension AgeGroupExtension on AgeGroup {
  String get displayName {
    switch (this) {
      case AgeGroup.young:
        return 'Teen (13-17)';
      case AgeGroup.adult:
        return 'Adult (18-64)';
      case AgeGroup.senior:
        return 'Senior (65+)';
    }
  }
}

extension GenderExtension on Gender {
  String get displayName {
    switch (this) {
      case Gender.male:
        return 'Male';
      case Gender.female:
        return 'Female';
      case Gender.nonBinary:
        return 'Non-binary';
    }
  }
=======
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
>>>>>>> feat/voice
}
