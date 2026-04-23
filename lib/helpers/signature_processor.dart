import 'dart:typed_data';
import 'package:image/image.dart' as img;

class SignatureProcessor {
  /// Extracts the ink from a signature photo and removes the background on-device.
  /// 
  /// [rawBytes] - The raw bytes of the captured signature photo.
  /// [threshold] - The brightness threshold (0-255). Pixels above this become transparent.
  static Future<Uint8List?> cleanSignature(Uint8List rawBytes, {int threshold = 200}) async {
    try {
      // Decode image
      img.Image? original = img.decodeImage(rawBytes);
      if (original == null) return null;

      // Optimization: Scale down if image is too large for a signature (max 1024px)
      if (original.width > 1024 || original.height > 1024) {
        original = img.copyResize(original, width: 1024);
      }

      // Ensure we are working with at least 4 channels (RGBA)
      img.Image processed = original.convert(numChannels: 4);

      // Deep Check: Iterate through pixels using the new 4.x pixel iterator
      for (final pixel in processed) {
        // Calculate brightness (Luminance)
        double luminance = (0.299 * pixel.r) + (0.587 * pixel.g) + (0.114 * pixel.b);

        if (luminance > threshold) {
          pixel.setRgba(0, 0, 0, 0); // Make paper transparent
        } else {
          pixel.setRgba(0, 20, 80, 255); // Professional Dark Blue ink
        }
      }

      // Encode as PNG to preserve transparency
      return Uint8List.fromList(img.encodePng(processed));
    } catch (e) {
      print("Signature Processing Error: $e");
      return null;
    }
  }
}
