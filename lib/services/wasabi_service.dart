import 'dart:io';
import 'dart:async';
import 'dart:typed_data';
import 'package:minio/minio.dart';
import 'package:path/path.dart' as path;
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter/foundation.dart' show kDebugMode, debugPrint;

class WasabiService {
  static final WasabiService _instance = WasabiService._internal();

  // Credentials from Environment
  final String _accessKey;
  final String _secretKey;
  final String _region;
  final String _bucket;
  final String _endpoint;

  Minio? _minio;

  factory WasabiService() {
    return _instance;
  }

  WasabiService._internal()
      : _accessKey = WasabiService._readEnv('WASABI_ACCESS_KEY'),
        _secretKey = WasabiService._readEnv('WASABI_SECRET_KEY'),
        _region = WasabiService._readEnv('WASABI_REGION'),
        _bucket = WasabiService._readEnv('WASABI_BUCKET'),
        _endpoint = WasabiService._readEnv('WASABI_ENDPOINT'),
        _minio = null {
    if (_endpoint.isNotEmpty && _accessKey.isNotEmpty && _secretKey.isNotEmpty) {
      _minio = Minio(
        endPoint: _endpoint,
        accessKey: _accessKey,
        secretKey: _secretKey,
        region: _region,
      );
    }
  }

  static String _readEnv(String key) {
    try {
      return dotenv.maybeGet(key) ?? '';
    } catch (_) {
      return '';
    }
  }

  /// Uploads a file to Wasabi Storage
  /// Returns the permanent URL of the uploaded document
  Future<String?> uploadDocument({
    required File file,
    required String doctorId,
    required String category, // e.g., 'gov_id' or 'reg_cert'
  }) async {
    try {
      final String fileName = "${doctorId}/${category}_${DateTime.now().millisecondsSinceEpoch}${path.extension(file.path)}";
      final String folderPath = "doctors/verification/$fileName";

      if (_minio == null || _bucket.isEmpty || _endpoint.isEmpty) {
        throw Exception("Wasabi not configured");
      }

      // Uploading to Wasabi
      await _minio!.putObject(
        _bucket,
        folderPath,
        file.openRead().map((chunk) => Uint8List.fromList(chunk)),
        size: await file.length(),
      ).timeout(const Duration(seconds: 30));

      // Return the Wasabi Public URL
      return "https://$_bucket.$_endpoint/$folderPath";
    } on TimeoutException {
      if (kDebugMode) debugPrint("Wasabi Upload Timed Out");
      return null;
    } catch (e) {
      if (kDebugMode) debugPrint("Wasabi Upload Error: $e");
      return null;
    }
  }

  /// Uploads raw bytes to Wasabi (useful for cleaned signatures)
  Future<String?> uploadBytes({
    required Uint8List bytes,
    required String fileName,
    required String doctorId,
  }) async {
    try {
      final String folderPath = "doctors/verification/$doctorId/$fileName";
      
      if (_minio == null || _bucket.isEmpty || _endpoint.isEmpty) {
        throw Exception("Wasabi not configured");
      }

      await _minio!.putObject(
        _bucket,
        folderPath,
        Stream.value(bytes),
        size: bytes.length,
      ).timeout(const Duration(seconds: 30));

      return "https://$_bucket.$_endpoint/$folderPath";
    } on TimeoutException {
      if (kDebugMode) debugPrint("Wasabi Byte Upload Timed Out");
      return null;
    } catch (e) {
      if (kDebugMode) debugPrint("Wasabi Byte Upload Error: $e");
      return null;
    }
  }
}
