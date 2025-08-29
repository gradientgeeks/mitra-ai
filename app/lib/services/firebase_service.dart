import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/user_model.dart';

class FirebaseService {
  static final FirebaseService _instance = FirebaseService._internal();
  factory FirebaseService() => _instance;
  FirebaseService._internal();

  final FirebaseAuth _auth = FirebaseAuth.instance;
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  // Get current user stream
  Stream<User?> get authStateChanges => _auth.authStateChanges();

  // Get current user
  User? get currentUser => _auth.currentUser;

  // Anonymous sign in
  Future<UserCredential?> signInAnonymously() async {
    try {
      final UserCredential result = await _auth.signInAnonymously();
      await _createUserDocument(result.user!);
      return result;
    } catch (e) {
      print('Error signing in anonymously: $e');
      return null;
    }
  }

  // Create user document in Firestore
  Future<void> _createUserDocument(User user) async {
    try {
      final userDoc = _firestore.collection('users').doc(user.uid);
      final docSnapshot = await userDoc.get();
      
      if (!docSnapshot.exists) {
        final now = DateTime.now();
        final userModel = UserModel(
          uid: user.uid,
          provider: user.isAnonymous ? 'anonymous' : 'other',
          email: user.email,
          displayName: user.displayName,
          isAnonymous: user.isAnonymous,
          status: 'active',
          createdAt: now,
          lastLogin: now,
          preferences: const UserPreferences(),
          totalSessions: 1,
        );

        await userDoc.set(userModel.toJson());
      } else {
        // Update last login
        await userDoc.update({
          'lastLogin': DateTime.now().toIso8601String(),
          'totalSessions': FieldValue.increment(1),
        });
      }
    } catch (e) {
      print('Error creating user document: $e');
    }
  }

  // Get user document
  Future<UserModel?> getUserDocument(String uid) async {
    try {
      final doc = await _firestore.collection('users').doc(uid).get();
      if (doc.exists) {
        return UserModel.fromJson(doc.data()!);
      }
      return null;
    } catch (e) {
      print('Error getting user document: $e');
      return null;
    }
  }

  // Sign out
  Future<void> signOut() async {
    try {
      await _auth.signOut();
    } catch (e) {
      print('Error signing out: $e');
    }
  }

  // Link anonymous account with credential
  Future<UserCredential?> linkWithCredential(AuthCredential credential) async {
    try {
      if (currentUser != null) {
        return await currentUser!.linkWithCredential(credential);
      }
      return null;
    } catch (e) {
      print('Error linking account: $e');
      return null;
    }
  }
}
