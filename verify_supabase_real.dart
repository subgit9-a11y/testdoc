import 'package:dio/dio.dart';

void main() async {
  final dio = Dio();
  final String supabaseUrl = 'https://ykewayjfdanhqtqpziwt.supabase.co';
  final String anonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlrZXdheWpmZGFuaHF0cXB6aXd0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU5NDc2OTIsImV4cCI6MjA3MTUyMzY5Mn0.OJDr91V4He1zv0k3Dn88-ZgErOOo1eeUtee23qh6G7s';

  print("Directly verifying Supabase table 'doctors'...");

  try {
    final response = await dio.get(
      "$supabaseUrl/rest/v1/doctors",
      queryParameters: {"select": "*", "limit": 1},
      options: Options(headers: {
        "apikey": anonKey,
        "Authorization": "Bearer $anonKey",
      }),
    );

    print("Supabase connection: SUCCESS");
    print("Table Access: SUCCESS");
    print("Existing Data Sample: ${response.data}");
    
    print("\nAttempting to INSERT 'Subbu' profile...");
    
    final insertResponse = await dio.post(
      "$supabaseUrl/rest/v1/doctors",
      data: {
        'unique_id': 'DOC-2026-SUBBU-1',
        'name': 'Subbu',
        'email': 'subbu@ayureze.in',
        'phone': '+919876543210',
        'gender': 'Male',
        'dob': '1990-01-01',
        'is_face_verified': true,
        'created_at': DateTime.now().toIso8601String(),
      },
      options: Options(headers: {
        "apikey": anonKey,
        "Authorization": "Bearer $anonKey",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
      }),
    );
    
    if (insertResponse.statusCode == 201 || insertResponse.statusCode == 200) {
      print("Insert Status: SUCCESS - Subbu is now in Supabase!");
    } else {
      print("Insert Status: FAILED - ${insertResponse.statusMessage}");
    }
  } catch (e) {
    if (e is DioException) {
      print("Supabase Error: ${e.response?.statusCode} - ${e.response?.data}");
    } else {
      print("Error: $e");
    }
  }
}
