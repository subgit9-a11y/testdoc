import 'package:dio/dio.dart';

void main() async {
  final dio = Dio();
  final String baseUrl = 'https://ayureze.org/public/api/';

  print("Verifying legacy backend 'ayureze.org'...");

  try {
    // Try to reach the setting endpoint which is often public or easy to check
    final response = await dio.get("${baseUrl}allMedicines");

    print("Retrieving Data from DB...");
    print("Status Code: ${response.statusCode}");
    print("Data Received: ${response.data.toString()}");
  } catch (e) {
    if (e is DioException) {
      print("Legacy Backend Error: ${e.response?.statusCode} - ${e.response?.data}");
    } else {
      print("Error: $e");
    }
  }
}
