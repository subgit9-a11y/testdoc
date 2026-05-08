import 'dart:io';
import 'dart:typed_data';
import 'package:minio/minio.dart';
import 'package:path/path.dart' as path;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class WasabiService {
  static final WasabiService _instance = WasabiService._internal();
  
  // Credentials from Environment
  final String _accessKey =
      dotenv.maybeGet('WASABI_ACCESS_KEY') ?? const String.fromEnvironment('WASABI_ACCESS_KEY');
  final String _secretKey =
      dotenv.maybeGet('WASABI_SECRET_KEY') ?? const String.fromEnvironment('WASABI_SECRET_KEY');
  final String _region =
      dotenv.maybeGet('WASABI_REGION') ?? const String.fromEnvironment('WASABI_REGION');
  final String _bucket =
      dotenv.maybeGet('WASABI_BUCKET') ?? const String.fromEnvironment('WASABI_BUCKET');
  final String _endpoint =
      dotenv.maybeGet('WASABI_ENDPOINT') ?? const String.fromEnvironment('WASABI_ENDPOINT');

  late Minio _minio;

  factory WasabiService() {
    return _instance;
  }

  WasabiService._internal() {
    _minio = Minio(
      endPoint: _endpoint,
      accessKey: _accessKey,
      secretKey: _secretKey,
      region: _region,
    );
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

      // Uploading to Wasabi
      await _minio.putObject(
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
      
      await _minio.putObject(
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
