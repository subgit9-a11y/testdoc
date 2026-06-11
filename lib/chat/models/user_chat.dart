import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:doctro/chat/constants/firestore_constants.dart';
import 'package:flutter/foundation.dart' show kDebugMode, debugPrint;

class UserChat {
  String id;
  String photoUrl;
  String nickname;
  String content;
  String shopId;
  String userType;
  String doctorId;
  String token;
  String userId;

  UserChat({required this.id, required this.photoUrl, required this.nickname, required this.content, required this.shopId, required this.userType, required this.doctorId, required this.token, required this.userId});

  Map<String, String> toJson() {
    return {
      FirestoreConstants.nickname: nickname,
      FirestoreConstants.photoUrl: photoUrl,
      FirestoreConstants.content: content,
      FirestoreConstants.shopId: shopId,
      FirestoreConstants.userType: userType,
      FirestoreConstants.doctorId: doctorId,
      FirestoreConstants.token: token,
      FirestoreConstants.userId: userId
    };
  }

  factory UserChat.fromDocument(DocumentSnapshot doc) {
    String photoUrl = "";
    String nickname = "";
    String content = "";
    String shopId = "";
    String userType = "";
    String doctorId = "";
    String token = "";
    String userId = "";

    try {
      photoUrl = doc.get(FirestoreConstants.photoUrl);
    } catch (e) {
      if (kDebugMode) debugPrint('UserChat: photoUrl missing: $e');
    }
    try {
      nickname = doc.get(FirestoreConstants.nickname);
    } catch (e) {
      if (kDebugMode) debugPrint('UserChat: nickname missing: $e');
    }
    try {
      content = doc.get(FirestoreConstants.content);
    } catch (e) {
      if (kDebugMode) debugPrint('UserChat: content missing: $e');
    }
    try {
      shopId = doc.get(FirestoreConstants.shopId);
    } catch (e) {
      if (kDebugMode) debugPrint('UserChat: shopId missing: $e');
    }
    try {
      userType = doc.get(FirestoreConstants.userType);
    } catch (e) {
      if (kDebugMode) debugPrint('UserChat: userType missing: $e');
    }
    try {
      doctorId = doc.get(FirestoreConstants.doctorId);
    } catch (e) {
      if (kDebugMode) debugPrint('UserChat: doctorId missing: $e');
    }
    try {
      token = doc.get(FirestoreConstants.token);
    } catch (e) {
      if (kDebugMode) debugPrint('UserChat: token missing: $e');
    }
    try {
      userId = doc.get(FirestoreConstants.userId);
    } catch (e) {
      if (kDebugMode) debugPrint('UserChat: userId missing: $e');
    }
    return UserChat(userId: userId, id: doc.id, photoUrl: photoUrl, nickname: nickname, content: content, shopId: shopId, userType: userType, doctorId: doctorId, token: token);
  }
}
