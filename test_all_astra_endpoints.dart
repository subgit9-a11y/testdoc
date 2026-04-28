import 'dart:convert';
import 'dart:io';

// Testing all essential Astra AI Backend Endpoints
void main() async {
  final String baseUrl = 'https://astra.ayureze.in';
  
  print("=========================================================================");
  print("      🚀 ASTRA AI ENDPOINT CONNECTIVITY AUDIT 🚀      ");
  print("=========================================================================\n");

  final List<Map<String, dynamic>> endpoints = [
    {
      'name': 'Root Health',
      'url': '/',
      'method': 'GET',
    },
    {
      'name': 'Backend Health',
      'url': '/api/v1/health',
      'method': 'GET',
    },
    {
      'name': 'Brain Chat (AI Core)',
      'url': '/api/v1/brain/chat',
      'method': 'POST',
      'body': {
        "message": "Hello AI",
        "user_metadata": {"role": "doctor"}
      }
    },
    {
      'name': 'Astra Fill (Text processing)',
      'url': '/api/v1/astra-fill/process-text',
      'method': 'POST',
      'body': {
        "text": "Patient has 102 fever and headache."
      }
    },
    {
      'name': 'Patient Search',
      'url': '/api/v1/patients/search/test',
      'method': 'GET',
    },
    {
      'name': 'Pending Prescription Queue',
      'url': '/api/v1/api/prescriptions/queue/pending',
      'method': 'GET',
    },
    {
      'name': 'Shopify Sync',
      'url': '/api/v1/shopify/sync',
      'method': 'POST',
      'body': {}
    },
    {
       'name': 'Available Medicines',
       'url': '/api/v1/shopify/products/available',
       'method': 'GET',
    },
    {
      'name': 'Translate Supported Languages',
      'url': '/api/v1/api/translate/languages',
      'method': 'GET',
    }
  ];

  HttpClient client = HttpClient();
  client.badCertificateCallback = ((X509Certificate cert, String host, int port) => true);
  client.connectionTimeout = Duration(seconds: 15);

  int successCount = 0;
  int failCount = 0;

  for (var endpoint in endpoints) {
    print('Testing [${endpoint['name']}]');
    String url = '$baseUrl${endpoint['url']}';
    print('URL: $url');
    
    try {
      HttpClientRequest request;
      
      if (endpoint['method'] == 'POST') {
        request = await client.postUrl(Uri.parse(url));
        request.headers.set('Content-Type', 'application/json');
        request.headers.set('X-Role', 'doctor');
        
        if (endpoint['body'] != null) {
          request.write(json.encode(endpoint['body']));
        }
      } else {
        request = await client.getUrl(Uri.parse(url));
        request.headers.set('X-Role', 'doctor');
      }

      HttpClientResponse response = await request.close().timeout(Duration(seconds: 15));
      final responseBody = await response.transform(utf8.decoder).join();
      
      print('Status Code: ${response.statusCode}');
      if (response.statusCode >= 200 && response.statusCode < 300) {
        print('✅ SUCCESS - Response received.');
        // Print snippet of response
        String snippet = responseBody;
        if (snippet.length > 200) {
            snippet = snippet.substring(0, 200) + "...";
        }
        print('Response Snippet: $snippet\n');
        successCount++;
      } else if (response.statusCode == 404 || response.statusCode == 401 || response.statusCode == 403 || response.statusCode == 422) {
        // Some endpoints might require real auth or specific data structures, 404/401/403 means the server is reachable at least but auth or route failed.
        print('⚠️ REACHABLE BUT RETURNED ${response.statusCode} (Expected if missing Auth/Data).');
        print('Response Snippet: $responseBody\n');
        successCount++; // Count as reachable
      } else {
        print('❌ ERROR - Returned ${response.statusCode}');
        print('Body: $responseBody\n');
        failCount++;
      }
    } catch (e) {
      print('❌ CONNECTION FAILED: $e\n');
      failCount++;
    }
  }
  
  client.close();

  print("=========================================================================");
  print("AUDIT COMPLETE: $successCount reachable endpoints, $failCount failed endpoints.");
  print("=========================================================================");
}
