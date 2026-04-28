import 'dart:convert';
import 'dart:io';

// Dart natively supports HTTP requests. We will use HttpClient to avoid pub get issues if 'http' package is unavailable.
void main() async {
  final String testPatientId = 'PATIENT-PRIYA-TEST'; // The exact patient ID we generated earlier!
  
  final String url = 'https://astra.ayureze.in/api/v1/astra-fill/patient/$testPatientId/latest';

  print("=========================================================================");
  print("🚀 DOCTOR APP <-> ASTRA COMPANION (20-PARAM) CONNECTION DIAGNOSTIC 🚀");
  print("=========================================================================\n");

  print('📡 Target: Astra Fill Medical Summary Endpoint');
  print('🔗 URL: $url\n');
  
  try {
    HttpClient client = HttpClient();
    // Allow self-signed certs just in case Cloudflare tunnel acts up locally
    client.badCertificateCallback = ((X509Certificate cert, String host, int port) => true);
    
    HttpClientRequest request = await client.getUrl(Uri.parse(url));
    request.headers.set('Content-Type', 'application/json');
    request.headers.set('X-Role', 'doctor');
    
    print('⏳ Requesting Data from Astra AI Gateway...');
    HttpClientResponse response = await request.close();
    
    final responseBody = await response.transform(utf8.decoder).join();
    
    print('📥 Network Status Code: ${response.statusCode}');
    
    if (response.statusCode == 200 || response.statusCode == 201) {
       print('✅ SUCCESS! Doctor App successfully securely tapped into Astra Fill!\n');
       
       try {
         final data = json.decode(responseBody);
         print('🧠 20-Parameter AI Response Detected:\n');
         print(JsonEncoder.withIndent('  ').convert(data));
       } catch (e) {
         print('⚠️ Raw JSON received (Not fully parsed format):');
         print(responseBody);
       }
    } else {
       print('⚠️ Warning (Non-200 HTTP code):');
       print(responseBody);
    }
    
    client.close();
  } catch (e) {
    print('❌ CONNECTION FAILED: $e');
    print('Did you ensure the Astra backend tunnel is running and public?');
  }
  
  print('\n=========================================================================');
}
