import re

file_path = "lib/services/astra_api_service.dart"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

bad_block = """      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }"""

# We know the first occurrence is fine, the second is orphan.
# Actually, let's just replace the exact orphan lines.

orphan = """      final response = await _postWithDnsFallback(Apis.astra_brain_chat, data: data);
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }"""

good = """      final response = await _postWithDnsFallback(Apis.astra_brain_chat, data: data);
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  /// General AI Chat with Astra Brain (Streaming)
  Stream<String> brainChatStream(Map<String, dynamic> data) async* {
    try {
      if (data['user_metadata'] == null) {
        data['user_metadata'] = {'role': 'doctor'};
      } else if (data['user_metadata'] is Map && data['user_metadata']['role'] == null) {
        data['user_metadata']['role'] = 'doctor';
      }
      
      final response = await _postWithDnsFallback(
        Apis.astra_brain_chat, 
        data: data,
        options: Options(responseType: ResponseType.stream),
      );

      final stream = response.data.stream;
      
      await for (var chunk in stream) {
        if (chunk is List<int>) {
           String text = String.fromCharCodes(chunk);
           yield text;
        }
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  /// AI-powered doctor summary generation
  Future<Map<String, dynamic>> generateDoctorSummary(Map<String, dynamic> data) async {
    try {
      final response = await _dio.post('/api/v1/brain/doctor-summary', data: data);
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }"""

if orphan in content:
    new_content = content.replace(orphan, good)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Fixed.")
else:
    print("Orphan block not found.")
