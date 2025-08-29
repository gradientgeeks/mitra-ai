import 'package:firebase_auth/firebase_auth.dart';
import '../models/user_model.dart';

class FirebaseService {
  final FirebaseAuth _auth = FirebaseAuth.instance;

  // Stream of authentication state changes
  Stream<User?> get authStateChanges => _auth.authStateChanges();

  // Get current user
  User? get currentUser => _auth.currentUser;

  // Sign in anonymously
  Future<UserCredential?> signInAnonymously() async {
    try {
      print('Attempting anonymous sign-in...');
      final result = await _auth.signInAnonymously();
      print('Anonymous sign-in successful: ${result.user?.uid}');
      return result;
    } catch (e) {
      print('Anonymous sign-in failed: $e');
      rethrow;
    }
  }

  // Sign out
  Future<void> signOut() async {
    try {
      await _auth.signOut();
      print('User signed out successfully');
    } catch (e) {
      print('Sign out failed: $e');
      rethrow;
    }
  }

  // Get ID token for backend authentication
  Future<String?> getIdToken() async {
    try {
      final user = _auth.currentUser;
      if (user != null) {
        return await user.getIdToken();
      }
      return null;
    } catch (e) {
      print('Failed to get ID token: $e');
      return null;
    }
  }

  // Create user preferences for new users
  UserPreferences createDefaultPreferences() {
    return const UserPreferences();
  }

  // Link anonymous account with email/password
  Future<UserCredential?> linkWithEmailAndPassword(String email, String password) async {
    try {
      final user = _auth.currentUser;
      if (user != null && user.isAnonymous) {
        final credential = EmailAuthProvider.credential(email: email, password: password);
        return await user.linkWithCredential(credential);
      }
      return null;
    } catch (e) {
      print('Failed to link account: $e');
      rethrow;
    }
  }

  // Convert anonymous account to permanent account
  Future<UserCredential?> upgradeAnonymousAccount(String email, String password) async {
    try {
      final user = _auth.currentUser;
      if (user != null && user.isAnonymous) {
        final credential = EmailAuthProvider.credential(email: email, password: password);
        return await user.linkWithCredential(credential);
      }
      return null;
    } catch (e) {
      print('Failed to upgrade anonymous account: $e');
      rethrow;
    }
  }

  // Check if user is anonymous
  bool get isAnonymous => _auth.currentUser?.isAnonymous ?? false;

  // Get user display name
  String? get displayName => _auth.currentUser?.displayName;

  // Get user email
  String? get email => _auth.currentUser?.email;

  // Get user UID
  String? get uid => _auth.currentUser?.uid;
}
