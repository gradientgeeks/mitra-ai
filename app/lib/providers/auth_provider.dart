import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/firebase_service.dart';
import '../services/api_service.dart';
import '../models/user_model.dart';

// Firebase service provider
final firebaseServiceProvider = Provider<FirebaseService>((ref) {
  return FirebaseService();
});

// Auth state provider
final authStateProvider = StreamProvider<User?>((ref) {
  final firebaseService = ref.watch(firebaseServiceProvider);
  return firebaseService.authStateChanges;
});

// Current user provider
final currentUserProvider = Provider<User?>((ref) {
  final authState = ref.watch(authStateProvider);
  return authState.whenData((user) => user).value;
});

// User document provider with API integration
final userDocumentProvider = FutureProvider<UserModel?>((ref) async {
  final user = ref.watch(currentUserProvider);
  if (user == null) return null;

  try {
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
    return null;
  }
});

// Authentication controller
final authControllerProvider = StateNotifierProvider<AuthController, AsyncValue<User?>>((ref) {
  final firebaseService = ref.watch(firebaseServiceProvider);
  return AuthController(firebaseService);
});

class AuthController extends StateNotifier<AsyncValue<User?>> {
  final FirebaseService _firebaseService;

  AuthController(this._firebaseService) : super(const AsyncValue.loading()) {
    _init();
  }

  void _init() {
    _firebaseService.authStateChanges.listen((user) {
      state = AsyncValue.data(user);
    });
  }

  Future<void> signInAnonymously() async {
    state = const AsyncValue.loading();
    try {
      final result = await _firebaseService.signInAnonymously();
      if (result != null) {
        state = AsyncValue.data(result.user);
      } else {
        state = AsyncValue.error('Failed to sign in anonymously', StackTrace.current);
      }
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
    await _firebaseService.signOut();
    state = const AsyncValue.data(null);
  }
}
