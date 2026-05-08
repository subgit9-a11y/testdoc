import 'dart:io';
import 'dart:typed_data';
import 'package:minio/minio.dart';
import 'package:path/path.dart' as path;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class WasabiService {
  static final WasabiService _instance = WasabiService._internal();

  String _env(String key) {
    try {
      return dotenv.maybeGet(key) ?? '';
    } catch (_) {
      return '';
    }
  }
  
  // Credentials from Environment
  late final String _accessKey;
  late final String _secretKey;
  late final String _region;
  late final String _bucket;
  late final String _endpoint;

  Minio? _minio;

  factory WasabiService() {
    return _instance;
  }

  WasabiService._internal() {
    _accessKey = _env('WASABI_ACCESS_KEY');
    _secretKey = _env('WASABI_SECRET_KEY');
    _region = _env('WASABI_REGION');
    _bucket = _env('WASABI_BUCKET');
    _endpoint = _env('WASABI_ENDPOINT');

    if (_endpoint.isNotEmpty && _accessKey.isNotEmpty && _secretKey.isNotEmpty) {
      _minio = Minio(
        endPoint: _endpoint,
        accessKey: _accessKey,
        secretKey: _secretKey,
        region: _region,
      );
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
      );

      // Return the Wasabi Public URL
      return "https://$_bucket.$_endpoint/$folderPath";
    } catch (e) {
      print("Wasabi Upload Error: $e");
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
      );

      return "https://$_bucket.$_endpoint/$folderPath";
    } catch (e) {
      print("Wasabi Byte Upload Error: $e");
      return null;
    }
  }
}
