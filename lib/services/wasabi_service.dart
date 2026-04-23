import 'dart:io';
import 'dart:typed_data';
import 'package:minio/minio.dart';
import 'package:path/path.dart' as path;

class WasabiService {
  static final WasabiService _instance = WasabiService._internal();
  
  // Credentials from USER
  final String _accessKey = "NFFPC7HWJXCNXQ3VL16K";
  final String _secretKey = "UmienYXZwtzRffe5yhbuP5uLRquGd6g6a22AgUWC";
  final String _region = "ap-southeast-1";
  final String _bucket = "astraehr";
  final String _endpoint = "s3.ap-southeast-1.wasabisys.com";

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
