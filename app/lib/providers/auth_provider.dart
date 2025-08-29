import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/firebase_service.dart';
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

// User document provider
final userDocumentProvider = FutureProvider<UserModel?>((ref) async {
  final user = ref.watch(currentUserProvider);
  if (user == null) return null;

  final firebaseService = ref.watch(firebaseServiceProvider);
  return await firebaseService.getUserDocument(user.uid);
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

  Future<void> signOut() async {
    await _firebaseService.signOut();
    state = const AsyncValue.data(null);
  }
}
