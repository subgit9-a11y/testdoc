import 'package:flutter_test/flutter_test.dart';
import 'package:doctro/model/astra/ai_response_models.dart';

void main() {
  group('Astra AI Chat Response Parsing', () {
    test('Should parse direct response key', () {
      final json = {'response': 'Hello Doctor'};
      final response = AIChatResponse.fromJson(json);
      expect(response.response, 'Hello Doctor');
    });

    test('Should parse fallback message key', () {
      final json = {'message': 'Ayurvedic text here'};
      final response = AIChatResponse.fromJson(json);
      expect(response.response, 'Ayurvedic text here');
    });

    test('Should parse wrapped data object', () {
      final json = {
        'status': 200,
        'data': {
          'answer': 'Nested ayurvedic text'
        }
      };
      final response = AIChatResponse.fromJson(json);
      expect(response.response, 'Nested ayurvedic text');
    });

    test('Should handle null gracefully when NO known key exists', () {
      final json = {'something_else': 'nothing'};
      final response = AIChatResponse.fromJson(json);
      expect(response.response, isNull);
    });
  });
}
