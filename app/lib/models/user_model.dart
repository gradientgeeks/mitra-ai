class UserModel {
  final String id;
  final String email;
  final bool isOnboardingCompleted;
  final UserPreferences preferences;
  final int totalSessions;
  final DateTime createdAt;
  final DateTime updatedAt;

  const UserModel({
    required this.id,
    required this.email,
    required this.isOnboardingCompleted,
    required this.preferences,
    required this.totalSessions,
    required this.createdAt,
    required this.updatedAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as String,
      email: json['email'] as String,
      isOnboardingCompleted: json['isOnboardingCompleted'] as bool,
      preferences: UserPreferences.fromJson(json['preferences'] as Map<String, dynamic>),
      totalSessions: json['totalSessions'] as int,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'isOnboardingCompleted': isOnboardingCompleted,
      'preferences': preferences.toJson(),
      'totalSessions': totalSessions,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
    };
  }
}

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
}
