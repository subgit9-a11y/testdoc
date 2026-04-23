
import 'dart:io';
import 'package:http/http.dart' as http;

void main() async {
  final baseUrl = 'https://astra.ayureze.in';
  final endpoints = [
    '/health',
    '/api/v1/health',
    '/api/v1/auth/health',
    '/api/v1/api/prescriptions/status',
    '/api/v1/shopify/health',
  ];

  for (var endpoint in endpoints) {
    try {
      final response = await http.get(Uri.parse('$baseUrl$endpoint'));
      print('Endpoint: $endpoint');
      print('Status Code: ${response.statusCode}');
      print('Response: ${response.body}');
      print('-----------------------------');
    } catch (e) {
      print('Error connecting to $endpoint: $e');
    }
  }
}
