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

<<<<<<< HEAD
// User document provider with API integration
=======
// User document provider (from backend API)
>>>>>>> feat/voice
final userDocumentProvider = FutureProvider<UserModel?>((ref) async {
  final firebaseUser = ref.watch(currentFirebaseUserProvider);
  final apiService = ref.watch(apiServiceProvider);
  
  if (firebaseUser == null) return null;

  try {
<<<<<<< HEAD
    // Get auth token
    final token = await user.getIdToken();
    if (token == null) return null;

    // Try to get user from API first
    try {
      return await ApiService.getCurrentUser(token);
    } catch (e) {
      // Fallback to Firebase if API is not available
      final firebaseService = ref.watch(firebaseServiceProvider);
      return await firebaseService.getUserDocument(user.uid);
    }
  } catch (e) {
=======
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
>>>>>>> feat/voice
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
        print('Auth state changed: ${firebaseUser?.uid ?? 'null'}');
        state = AsyncValue.data(state.value?.copyWith(
          firebaseUser: firebaseUser,
          isLoading: true,
        ) ?? AuthState(firebaseUser: firebaseUser, isLoading: true));

        if (firebaseUser != null) {
          print('Getting ID token...');
          // Set auth token and try to get backend user
          final token = await firebaseUser.getIdToken();
          if (token != null) {
            print('ID token obtained');
            _apiService.setAuthToken(token);

            try {
              print('Attempting to get user profile from backend...');
              final backendUser = await _apiService.getUserProfile();
              print('Backend user profile retrieved successfully');
              state = AsyncValue.data(AuthState(
                firebaseUser: firebaseUser,
                backendUser: backendUser,
                isLoading: false,
              ));
            } catch (e) {
              print(' Failed to get user profile: $e');
              // User doesn't exist in backend yet, create anonymous user
              try {
                print(' Attempting to create anonymous user in backend...');
                final backendUser = await _apiService.createAnonymousUser();
                print(' Anonymous user created successfully');
                state = AsyncValue.data(AuthState(
                  firebaseUser: firebaseUser,
                  backendUser: backendUser,
                  isLoading: false,
                ));
              } catch (createError) {
                print('❌ Failed to create backend user: $createError');
                
                // Check if it's a network/connection error
                if (createError.toString().contains('Connection') || 
                    createError.toString().contains('Failed host lookup') ||
                    createError.toString().contains('SocketException') ||
                    createError.toString().contains('XMLHttpRequest')) {
                  
                  print('🔧 Network error detected - creating temporary offline user');
                  // Create a temporary offline user for development
                  final offlineUser = UserModel(
                    uid: firebaseUser.uid,
                    provider: UserProvider.anonymous,
                    isAnonymous: true,
                    status: UserStatus.active,
                    createdAt: DateTime.now(),
                    lastLogin: DateTime.now(),
                    preferences: const UserPreferences(),
                    onboardingCompleted: false,
                  );
                  
                  state = AsyncValue.data(AuthState(
                    firebaseUser: firebaseUser,
                    backendUser: offlineUser,
                    isLoading: false,
                  ));
                } else {
                  // For other errors, keep the Firebase user but show error
                  state = AsyncValue.data(AuthState(
                    firebaseUser: firebaseUser,
                    backendUser: null,
                    isLoading: false,
                    error: 'Failed to create backend user: $createError',
                  ));
                }
              }
            }
          } else {
            print(' Failed to get ID token');
            state = AsyncValue.data(AuthState(
              firebaseUser: firebaseUser,
              backendUser: null,
              isLoading: false,
              error: 'Failed to get authentication token',
            ));
          }
        } else {
          print(' User signed out');
          _apiService.clearAuthToken();
          state = const AsyncValue.data(AuthState());
        }
      } catch (e, stackTrace) {
        print(' Auth state error: $e');
        state = AsyncValue.error(e, stackTrace);
      }
    });
  }

  Future<void> signInAnonymously() async {
    try {
      print(' Starting anonymous sign-in process...');
      state = AsyncValue.data(state.value?.copyWith(isLoading: true) ?? 
          const AuthState(isLoading: true));

      // Sign in with Firebase Auth
      print(' Calling Firebase signInAnonymously...');
      final result = await _firebaseService.signInAnonymously();
      if (result?.user != null) {
        print(' Firebase sign-in successful');
        final firebaseUser = result!.user!;
        final token = await firebaseUser.getIdToken();
        if (token != null) {
          print(' Setting auth token...');
          _apiService.setAuthToken(token);

          // Create user in backend
          try {
            print(' Creating user in backend...');
            final backendUser = await _apiService.createAnonymousUser();
            print(' Backend user created successfully');
            state = AsyncValue.data(AuthState(
              firebaseUser: firebaseUser,
              backendUser: backendUser,
              isLoading: false,
            ));
          } catch (e) {
            print('❌ Backend user creation failed: $e');
            
            // Check if it's a network/connection error  
            if (e.toString().contains('Connection') || 
                e.toString().contains('Failed host lookup') ||
                e.toString().contains('SocketException') ||
                e.toString().contains('XMLHttpRequest')) {
              
              print('🔧 Network error detected - creating temporary offline user');
              // Create a temporary offline user for development
              final offlineUser = UserModel(
                uid: firebaseUser.uid,
                provider: UserProvider.anonymous,
                isAnonymous: true,
                status: UserStatus.active,
                createdAt: DateTime.now(),
                lastLogin: DateTime.now(),
                preferences: const UserPreferences(),
                onboardingCompleted: false,
              );
              
              state = AsyncValue.data(AuthState(
                firebaseUser: firebaseUser,
                backendUser: offlineUser,
                isLoading: false,
              ));
            } else {
              // For other errors, keep the Firebase user but show error
              state = AsyncValue.data(AuthState(
                firebaseUser: firebaseUser,
                backendUser: null,
                isLoading: false,
                error: 'Failed to create backend user: $e',
              ));
            }
          }
        } else {
          print(' Failed to get Firebase ID token');
          state = AsyncValue.data(AuthState(
            firebaseUser: firebaseUser,
            backendUser: null,
            isLoading: false,
            error: 'Failed to get authentication token',
          ));
        }
      } else {
        print(' Firebase sign-in failed');
        state = AsyncValue.data(const AuthState(
          isLoading: false,
          error: 'Failed to sign in anonymously',
        ));
      }
    } catch (e, stackTrace) {
      print(' Sign-in error: $e');
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

  Future<void> completeOnboarding(OnboardingRequest request) async {
    final user = state.value;
    if (user == null) {
      throw Exception('No authenticated user found');
    }

    try {
      // Get auth token
      final token = await user.getIdToken();
      if (token == null) {
        throw Exception('Failed to get authentication token');
      }

      // Complete onboarding via API
      await ApiService.completeOnboarding(
        authToken: token,
        request: request,
      );

      // Refresh user data after onboarding
      // This will trigger a rebuild of any widgets watching userDocumentProvider
    } catch (e) {
      throw Exception('Failed to complete onboarding: $e');
    }
  }

  Future<void> updateUserPreferences(UserPreferences preferences) async {
    final user = state.value;
    if (user == null) {
      throw Exception('No authenticated user found');
    }

    try {
      // Get auth token
      final token = await user.getIdToken();
      if (token == null) {
        throw Exception('Failed to get authentication token');
      }

      // Update preferences via API
      await ApiService.updateUserPreferences(
        authToken: token,
        preferences: preferences,
      );
    } catch (e) {
      throw Exception('Failed to update preferences: $e');
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
