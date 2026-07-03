import 'dart:io';
import 'dart:async';
import 'package:uuid/uuid.dart';
import 'dart:typed_data';
import 'package:flutter/foundation.dart' show kDebugMode, debugPrint;

class SupabaseService {
  /// Generate a unique Doctor ID
  String generateDoctorID() {
    final year = DateTime.now().year;
    final randomPart = const Uuid().v4().substring(0, 4).toUpperCase();
    return 'DOC-$year-$randomPart';
  }

  /// Store doctor registration data in Supabase
  Future<void> saveDoctorProfile({
    required String doctorId,
    required String name,
    required String email,
    required String phone,
    required String gender,
    required String dob,
    required String? photoUrl,
    required bool isFaceVerified,
  }) async {
    // Dummy implementation
    if (kDebugMode) debugPrint("Dummy saveDoctorProfile called");
  }

  /// Upload captured live photo to Supabase Storage
  Future<String?> uploadProfilePhoto(File photoFile, String doctorId) async {
    // Dummy implementation
    if (kDebugMode) debugPrint("Dummy uploadProfilePhoto called");
    return "https://dummy.url/photo.jpg";
  }

  /// Upload cleaned signature PNG to Supabase Storage
  Future<String?> uploadSignature(Uint8List signatureBytes, String doctorId) async {
    // Dummy implementation
    if (kDebugMode) debugPrint("Dummy uploadSignature called");
    return "https://dummy.url/signature.png";
  }

  /// Update the signature URL in the doctor's database record
  Future<void> updateSignatureUrl(String doctorId, String signatureUrl) async {
    // Dummy implementation
    if (kDebugMode) debugPrint("Dummy updateSignatureUrl called");
  }

  /// Log document verification metadata in Supabase
  Future<void> logVerificationDocument({
    required String doctorId,
    required String docType,
    required String docNumber,
    required String wasabiUrl,
  }) async {
    // Dummy implementation
    if (kDebugMode) debugPrint("Dummy logVerificationDocument called");
  }
}
