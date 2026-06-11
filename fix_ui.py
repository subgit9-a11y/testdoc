import re

file_path = "lib/screens/astra/astra_ai_chat_screen.dart"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# We need to replace the `_sendMessage` method from `List<Map<String, String>> history = ...` down to the end of the try block.

# First, let's just find `// Prepare history for memory (last 10 messages)`
# and `} catch (e) {`

start_marker = "      // Prepare history for memory (last 10 messages)"
end_marker = "    } catch (e) {"

if start_marker in content and end_marker in content:
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    
    if start_idx != -1 and end_idx != -1:
        prefix = content[:start_idx]
        suffix = content[end_idx:]
        
        replacement = """      // Prepare history for memory (last 10 messages)
      List<Map<String, String>> history = _messages
          .where((m) => !m.isSystem && !m.isError)
          .toList()
          .reversed
          .skip(1) // Skip the message we just added (or the voice processing message)
          .take(10)
          .toList()
          .reversed
          .map((m) => <String, String>{
                'role': m.isMe ? 'user' : 'assistant',
                'content': m.text,
              })
          .toList();

      if (voicePath != null) {
        // Handle voice processing
        if (mounted) {
          setState(() {
            _messages.add(ChatMessage(
              text: "🎤 Processing voice recording...",
              isMe: true,
              time: DateTime.now(),
              isSystem: true,
            ));
          });
        }
        
        final voiceResponse = await _apiService.processVoice(File(voicePath), effectiveUserId);
        String extractedText = voiceResponse['text'] ?? "Voice processed successfully.";
        
        final response = await _apiService.brainChat({
          'q': extractedText,
          'user_id': effectiveUserId,
          'session_id': _sessionId,
          'history': history,
          'user_metadata': {
            'role': 'doctor', 
            'source': 'voice',
            'precise': true // Request precise clinical response
          }
        });
        final aiResponse = AIChatResponse.fromJson(response);
        if (aiResponse.sessionId != null) _sessionId = aiResponse.sessionId;
        if (mounted) {
          setState(() {
            _messages.add(ChatMessage(
              text: aiResponse.response ?? "I apologize, I couldn't process that request.",
              isMe: false,
              time: DateTime.now(),
            ));
            _isLoading = false;
          });
        }
      } else {
        // Regular text chat via SSE STREAM!
        int aiMessageIndex = _messages.length;
        if (mounted) {
          setState(() {
            _messages.add(ChatMessage(
              text: "", // Empty initial text
              isMe: false,
              time: DateTime.now(),
            ));
            _isLoading = false; // We start getting data immediately
          });
        }

        final stream = _apiService.brainChatStream({
          'q': message,
          'user_id': effectiveUserId,
          'session_id': _sessionId,
          'history': history,
          'user_metadata': {
            'role': 'doctor',
            'precise': true // Request precise clinical response
          }
        });

        await for (String chunk in stream) {
          if (mounted) {
            setState(() {
              // Append chunk to the existing AI message
              _messages[aiMessageIndex] = ChatMessage(
                text: _messages[aiMessageIndex].text + chunk,
                isMe: false,
                time: _messages[aiMessageIndex].time,
              );
            });
            _scrollToBottom();
          }
        }
      }
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(prefix + replacement + suffix)
        print("UI file updated successfully with streaming logic!")
    else:
        print("Could not find exact bounds.")
else:
    print("Markers not found.")
