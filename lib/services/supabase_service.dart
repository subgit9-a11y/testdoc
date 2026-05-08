import 'dart:io';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:uuid/uuid.dart';
import 'dart:typed_data';

class SupabaseService {
  SupabaseClient get _client {
    try {
      return Supabase.instance.client;
    } catch (e) {
      throw Exception("Supabase is not initialized. Configure SUPABASE_URL and SUPABASE_ANON_KEY.");
    }
  }

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
    try {
      await _client.from('doctors').upsert({
        'unique_id': doctorId,
        'name': name,
        'email': email,
        'phone': phone,
        'gender': gender,
        'dob': dob,
        'photo_url': photoUrl,
        'is_face_verified': isFaceVerified,
        'updated_at': DateTime.now().toIso8601String(),
      }, onConflict: 'unique_id');
    } catch (e) {
      throw Exception("Supabase Database Error: $e");
    }
  }

  /// Upload captured live photo to Supabase Storage
  Future<String?> uploadProfilePhoto(File photoFile, String doctorId) async {
    try {
      final fileName = '$doctorId/profile_${DateTime.now().millisecondsSinceEpoch}.jpg';
      final path = await _client.storage
          .from('doctor-profiles')
          .upload(fileName, photoFile);
      
      if (path.isNotEmpty) {
        return _client.storage.from('doctor-profiles').getPublicUrl(fileName);
      }
      return null;
    } catch (e) {
      throw Exception("Supabase Storage Error: $e");
    }
  }
  /// Upload cleaned signature PNG to Supabase Storage
  Future<String?> uploadSignature(Uint8List signatureBytes, String doctorId) async {
    try {
      final fileName = '$doctorId/signature_${DateTime.now().millisecondsSinceEpoch}.png';
      
      // We assume a bucket 'doctor-profiles' exists or use a folder inside it
      await _client.storage
          .from('doctor-profiles')
          .uploadBinary(fileName, signatureBytes, fileOptions: const FileOptions(contentType: 'image/png'));
      
      return _client.storage.from('doctor-profiles').getPublicUrl(fileName);
    } catch (e) {
      print("Supabase Signature Upload Error: $e");
      return null;
    }
  }

  /// Update the signature URL in the doctor's database record
  Future<void> updateSignatureUrl(String doctorId, String signatureUrl) async {
    try {
      await _client.from('doctors').update({
        'signature_url': signatureUrl,
        'updated_at': DateTime.now().toIso8601String(),
      }).eq('unique_id', doctorId);
    } catch (e) {
       print("Supabase DB Signature Sync Error: $e");
    }
  }
  /// Log document verification metadata in Supabase
  Future<void> logVerificationDocument({
    required String doctorId,
    required String docType,
    required String docNumber,
    required String wasabiUrl,
  }) async {
    try {
      await _client.from('doctor_verification_logs').insert({
        'doctor_unique_id': doctorId,
        'document_type': docType,
        'document_number': docNumber,
        'wasabi_url': wasabiUrl,
        'uploaded_at': DateTime.now().toIso8601String(),
      });
    } catch (e) {
      print("Supabase Verification Log Error: $e");
    }
  }
}
