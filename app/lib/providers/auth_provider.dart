import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/firebase_service.dart';
import '../services/api_service.dart';
import '../models/user_model.dart';

// API service provider
final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService();
});

// Firebase service provider (still needed for Firebase Auth tokens)
final firebaseServiceProvider = Provider<FirebaseService>((ref) {
  return FirebaseService();
});

// Auth state provider (Firebase Auth for token management)
final authStateProvider = StreamProvider<User?>((ref) {
  final firebaseService = ref.watch(firebaseServiceProvider);
  return firebaseService.authStateChanges;
});

// Current Firebase user provider
final currentFirebaseUserProvider = Provider<User?>((ref) {
  final authState = ref.watch(authStateProvider);
  return authState.whenData((user) => user).value;
});

// User document provider (from backend API)
final userDocumentProvider = FutureProvider<UserModel?>((ref) async {
  final firebaseUser = ref.watch(currentFirebaseUserProvider);
  final apiService = ref.watch(apiServiceProvider);
  
  if (firebaseUser == null) return null;

  try {
    // Set the Firebase token for API authentication
    final token = await firebaseUser.getIdToken();
    if (token != null) {
      apiService.setAuthToken(token);

      // Get user profile from backend
      return await apiService.getUserProfile();
    }
    return null;
  } catch (e) {
    // If user doesn't exist in backend, return null
    return null;
  }
});

// Authentication controller
final authControllerProvider = StateNotifierProvider<AuthController, AsyncValue<AuthState>>((ref) {
  final firebaseService = ref.watch(firebaseServiceProvider);
  final apiService = ref.watch(apiServiceProvider);
  return AuthController(firebaseService, apiService);
});

// Auth state model
class AuthState {
  final User? firebaseUser;
  final UserModel? backendUser;
  final bool isLoading;
  final String? error;

  const AuthState({
    this.firebaseUser,
    this.backendUser,
    this.isLoading = false,
    this.error,
  });

  bool get isAuthenticated => firebaseUser != null;
  bool get hasBackendUser => backendUser != null;
  bool get needsOnboarding => isAuthenticated && hasBackendUser && !backendUser!.onboardingCompleted;

  AuthState copyWith({
    User? firebaseUser,
    UserModel? backendUser,
    bool? isLoading,
    String? error,
  }) {
    return AuthState(
      firebaseUser: firebaseUser ?? this.firebaseUser,
      backendUser: backendUser ?? this.backendUser,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class AuthController extends StateNotifier<AsyncValue<AuthState>> {
  final FirebaseService _firebaseService;
  final ApiService _apiService;

  AuthController(this._firebaseService, this._apiService) 
      : super(const AsyncValue.loading()) {
    _init();
  }

  void _init() {
    _firebaseService.authStateChanges.listen((firebaseUser) async {
      try {
        state = AsyncValue.data(state.value?.copyWith(
          firebaseUser: firebaseUser,
          isLoading: true,
        ) ?? AuthState(firebaseUser: firebaseUser, isLoading: true));

        if (firebaseUser != null) {
          // Set auth token and try to get backend user
          final token = await firebaseUser.getIdToken();
          if (token != null) {
            _apiService.setAuthToken(token);

            try {
              final backendUser = await _apiService.getUserProfile();
              state = AsyncValue.data(AuthState(
                firebaseUser: firebaseUser,
                backendUser: backendUser,
                isLoading: false,
              ));
            } catch (e) {
              // User doesn't exist in backend yet, create anonymous user
              try {
                final backendUser = await _apiService.createAnonymousUser();
                state = AsyncValue.data(AuthState(
                  firebaseUser: firebaseUser,
                  backendUser: backendUser,
                  isLoading: false,
                ));
              } catch (createError) {
                // If backend user creation fails, still keep Firebase user
                state = AsyncValue.data(AuthState(
                  firebaseUser: firebaseUser,
                  backendUser: null,
                  isLoading: false,
                  error: 'Failed to create backend user: $createError',
                ));
              }
            }
          } else {
            state = AsyncValue.data(AuthState(
              firebaseUser: firebaseUser,
              backendUser: null,
              isLoading: false,
              error: 'Failed to get authentication token',
            ));
          }
        } else {
          _apiService.clearAuthToken();
          state = const AsyncValue.data(AuthState());
        }
      } catch (e, stackTrace) {
        state = AsyncValue.error(e, stackTrace);
      }
    });
  }

  Future<void> signInAnonymously() async {
    try {
      state = AsyncValue.data(state.value?.copyWith(isLoading: true) ?? 
          const AuthState(isLoading: true));

      // Sign in with Firebase Auth
      final result = await _firebaseService.signInAnonymously();
      if (result?.user != null) {
        final firebaseUser = result!.user!;
        final token = await firebaseUser.getIdToken();
        if (token != null) {
          _apiService.setAuthToken(token);

          // Create user in backend
          try {
            final backendUser = await _apiService.createAnonymousUser();
            state = AsyncValue.data(AuthState(
              firebaseUser: firebaseUser,
              backendUser: backendUser,
              isLoading: false,
            ));
          } catch (e) {
            // If backend user creation fails, still keep Firebase user
            state = AsyncValue.data(AuthState(
              firebaseUser: firebaseUser,
              backendUser: null,
              isLoading: false,
              error: 'Failed to create backend user: $e',
            ));
          }
        } else {
          state = AsyncValue.data(AuthState(
            firebaseUser: firebaseUser,
            backendUser: null,
            isLoading: false,
            error: 'Failed to get authentication token',
          ));
        }
      } else {
        state = AsyncValue.data(const AuthState(
          isLoading: false,
          error: 'Failed to sign in anonymously',
        ));
      }
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  Future<void> completeOnboarding({
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
      final currentState = state.value;
      if (currentState?.firebaseUser == null) {
        throw Exception('User not authenticated');
      }

      state = AsyncValue.data(currentState!.copyWith(isLoading: true));

      final backendUser = await _apiService.completeOnboarding(
        ageGroup: ageGroup,
        birthYear: birthYear,
        mitraName: mitraName,
        mitraGender: mitraGender,
        preferredVoice: preferredVoice,
        language: language,
        notificationEnabled: notificationEnabled,
        meditationReminders: meditationReminders,
        journalReminders: journalReminders,
      );

      state = AsyncValue.data(currentState.copyWith(
        backendUser: backendUser,
        isLoading: false,
      ));
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  Future<void> updateUserProfile({
    String? displayName,
    UserPreferences? preferences,
  }) async {
    try {
      final currentState = state.value;
      if (currentState?.firebaseUser == null) {
        throw Exception('User not authenticated');
      }

      state = AsyncValue.data(currentState!.copyWith(isLoading: true));

      final updatedUser = await _apiService.updateUserProfile(
        displayName: displayName,
        preferences: preferences,
      );

      state = AsyncValue.data(currentState.copyWith(
        backendUser: updatedUser,
        isLoading: false,
      ));
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  Future<void> signOut() async {
    try {
      await _firebaseService.signOut();
      _apiService.clearAuthToken();
      state = const AsyncValue.data(AuthState());
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  Future<void> refreshUserData() async {
    try {
      final currentState = state.value;
      if (currentState?.firebaseUser == null) return;

      final backendUser = await _apiService.getUserProfile();
      state = AsyncValue.data(currentState!.copyWith(
        backendUser: backendUser,
      ));
    } catch (e) {
      // Silently handle refresh errors
    }
  }
}
