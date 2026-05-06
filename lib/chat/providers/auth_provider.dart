import 'dart:developer';
import 'dart:io';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:doctro/chat/constants/firestore_constants.dart';
import 'package:doctro/chat/models/user_chat.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:google_sign_in/google_sign_in.dart';

enum Status {
  uninitialized,
  authenticated,
  authenticating,
  authenticateError,
  authenticateCanceled
}

class AuthProvider extends ChangeNotifier {
  final FirebaseAuth firebaseAuth;
  final FirebaseFirestore firebaseFirestore;
  final SharedPreferences prefs;

  Status _status = Status.uninitialized;

  Status get status => _status;

  AuthProvider({
    required this.firebaseAuth,
    required this.prefs,
    required this.firebaseFirestore,
  });

  static final FirebaseAuth _auth = FirebaseAuth.instance;

  String? getUserFirebaseId() {
    return prefs.getString(FirestoreConstants.id) ?? "";
  }

  bool check = false;
  Future<bool> handleSignIn() async {
    _status = Status.authenticating;

    notifyListeners();

    try {
      // Use the already-authenticated Firebase user from the sign-in flow
      User? user = _auth.currentUser;
      
      // If no current user, attempt sign-in with email (without stored password)
      if (user == null) {
        _status = Status.authenticateError;
        notifyListeners();
        return check = false;
      }

      final QuerySnapshot result = await firebaseFirestore
          .collection(FirestoreConstants.pathUserCollection)
          .where(FirestoreConstants.id, isEqualTo: user.uid)
          .get();
      final List<DocumentSnapshot> documents = result.docs;
      if (documents.length == 0) {
        firebaseFirestore
            .collection(FirestoreConstants.pathUserCollection)
            .doc(user.uid)
            .set({
          FirestoreConstants.nickname:
              SharedPreferenceHelper.getString(Preferences.user_name),
          FirestoreConstants.photoUrl:
              SharedPreferenceHelper.getString(Preferences.chat_profile),
          FirestoreConstants.userType: "doctor",
          FirestoreConstants.doctorId:
              SharedPreferenceHelper.getString(Preferences.doctorId),
          FirestoreConstants.id: user.uid,
          'createdAt': DateTime.now().millisecondsSinceEpoch.toString(),
          FirestoreConstants.chattingWith: null
        });

        await prefs.setString(FirestoreConstants.id, user.uid);
        await prefs.setString(
            FirestoreConstants.nickname, user.displayName ?? "");
        await prefs.setString(
            FirestoreConstants.photoUrl, user.photoURL ?? "");
      } else {
        DocumentSnapshot documentSnapshot = documents[0];
        UserChat userChat = UserChat.fromDocument(documentSnapshot);
        await prefs.setString(FirestoreConstants.id, userChat.id);
        await prefs.setString(FirestoreConstants.nickname, userChat.nickname);
        await prefs.setString(FirestoreConstants.photoUrl, userChat.photoUrl);
        await prefs.setString(FirestoreConstants.shopId, userChat.shopId);
        await prefs.setString(FirestoreConstants.userType, userChat.userType);
        await prefs.setString(Preferences.doctorId, userChat.doctorId);
      }
      _status = Status.authenticated;
      notifyListeners();
      return check = true;
    } on FirebaseAuthException catch (signUpError) {
      log("signUpError ${signUpError.code} ${signUpError.message}");
      _status = Status.authenticateError;
      notifyListeners();
      return check = false;
    }
  }

  Future<User?> signInWithGoogle() async {
    _status = Status.authenticating;
    notifyListeners();

    try {
      GoogleSignIn googleSignIn = GoogleSignIn(
        clientId: Platform.isIOS ? '298839588168-up4rcmclffgne2hnlemg7n4e29qtovn2.apps.googleusercontent.com' : null,
        serverClientId: '298839588168-6ut75u7g4rqc8grmujtcl4m7obnq3oml.apps.googleusercontent.com',
      );
      GoogleSignInAccount? googleUser = await googleSignIn.signIn();
      if (googleUser != null) {
        GoogleSignInAuthentication googleAuth = await googleUser.authentication;
        final AuthCredential credential = GoogleAuthProvider.credential(
          accessToken: googleAuth.accessToken,
          idToken: googleAuth.idToken,
        );

        User? user = (await _auth.signInWithCredential(credential)).user;
        if (user != null) {
          final QuerySnapshot result = await firebaseFirestore
              .collection(FirestoreConstants.pathUserCollection)
              .where(FirestoreConstants.id, isEqualTo: user.uid)
              .get();
          final List<DocumentSnapshot> documents = result.docs;
          if (documents.length == 0) {
            firebaseFirestore
                .collection(FirestoreConstants.pathUserCollection)
                .doc(user.uid)
                .set({
              FirestoreConstants.nickname: user.displayName,
              FirestoreConstants.photoUrl: user.photoURL,
              FirestoreConstants.id: user.uid,
              'createdAt': DateTime.now().millisecondsSinceEpoch.toString(),
              FirestoreConstants.chattingWith: null,
              FirestoreConstants.userType: "doctor", // Defaulting to doctor

              FirestoreConstants.doctorId: "0" 
            });

            await prefs.setString(FirestoreConstants.id, user.uid);
            await prefs.setString(FirestoreConstants.nickname, user.displayName ?? "");
            await prefs.setString(FirestoreConstants.photoUrl, user.photoURL ?? "");
            await prefs.setString(Preferences.image, user.photoURL ?? "");
            await prefs.setString(Preferences.name, user.displayName ?? "");
            await prefs.setString(Preferences.email, user.email ?? "");
            
          } else {
            DocumentSnapshot documentSnapshot = documents[0];
            UserChat userChat = UserChat.fromDocument(documentSnapshot);
            await prefs.setString(FirestoreConstants.id, userChat.id);
            await prefs.setString(FirestoreConstants.nickname, userChat.nickname);
            await prefs.setString(FirestoreConstants.photoUrl, userChat.photoUrl);
            await prefs.setString(FirestoreConstants.shopId, userChat.shopId);
            await prefs.setString(FirestoreConstants.userType, userChat.userType);
            await prefs.setString(Preferences.doctorId, userChat.doctorId);
             

             await prefs.setString(Preferences.image, userChat.photoUrl);
             await prefs.setString(Preferences.name, userChat.nickname);
          }
          SharedPreferenceHelper.setBoolean(Preferences.is_logged_in, true);
          _status = Status.authenticated;
          notifyListeners();
          return user;
        } else {
          _status = Status.authenticateError;
          notifyListeners();
          return null;
        }
      } else {
        log("Google Sign-In Canceled by user");
        _status = Status.authenticateCanceled;
        notifyListeners();
        return null;
      }
    } catch (e) {
      log("Google Sign-In Error: $e");
      if (e is Exception && e.toString().contains("PlatformException")) {
        log("PlatformException detected: Check if SHA-1 is correctly added to Firebase and if the package name matches.");
      }
      if (e.toString().contains("sign_in_canceled") || e.toString().contains("cancel")) {
        _status = Status.authenticateCanceled;
      } else {
        _status = Status.authenticateError;
      }
      notifyListeners();
      return null;
    }
  }

  Future<void> handleSignOut() async {
    _status = Status.uninitialized;
    await firebaseAuth.signOut();
    await GoogleSignIn().disconnect();
  }
}
