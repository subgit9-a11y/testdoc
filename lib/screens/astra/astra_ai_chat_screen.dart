import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:doctro/services/astra_api_service.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/model/astra/ai_response_models.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:intl/intl.dart';

class AstraAIChatScreen extends StatefulWidget {
  const AstraAIChatScreen({Key? key}) : super(key: key);

  @override
  _AstraAIChatScreenState createState() => _AstraAIChatScreenState();
}

class _AstraAIChatScreenState extends State<AstraAIChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final AstraApiService _apiService = AstraApiService();
  final List<ChatMessage> _messages = [];
  
  // Voice Recording state
  final AudioRecorder _audioRecorder = AudioRecorder();
  bool _isRecording = false;
  String? _recordingPath;

  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _addInitialMessage();
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _audioRecorder.dispose();
    super.dispose();
  }

  void _addInitialMessage() {
    setState(() {
      _messages.add(ChatMessage(
        text: "Hello Doctor! I'm Astra, your AI clinical assistant. How can I help you today?",
        isMe: false,
        time: DateTime.now(),
      ));
    });
  }

  Future<void> _sendMessage({String? voicePath}) async {
    String message = _messageController.text.trim();
    if (message.isEmpty && voicePath == null) return;

    setState(() {
      if (message.isNotEmpty) {
        _messages.add(ChatMessage(
          text: message,
          isMe: true,
          time: DateTime.now(),
        ));
        _messageController.clear();
      }
      _isLoading = true;
    });

    _scrollToBottom();

    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception("User not authenticated");

      Map<String, dynamic> response;
      
      if (voicePath != null) {
        // Handle voice processing
        setState(() {
           _messages.add(ChatMessage(
            text: "🎤 Processing voice recording...",
            isMe: true,
            time: DateTime.now(),
            isSystem: true,
          ));
        });
        
        final voiceResponse = await _apiService.processVoice(File(voicePath), user.uid);
        
        // After voice processing, we might get an extraction or just text
        String extractedText = voiceResponse['text'] ?? "Voice processed successfully.";
        response = await _apiService.brainChat({
          'message': "I just dictated this: $extractedText. Please analyze it.",
          'user_id': user.uid,
          'user_metadata': {'role': 'doctor', 'source': 'voice'}
        });
      } else {
        // Regular text chat
        response = await _apiService.brainChat({
          'message': message,
          'user_id': user.uid,
          'user_metadata': {'role': 'doctor'}
        });
      }

      final aiResponse = AIChatResponse.fromJson(response);

      setState(() {
        _messages.add(ChatMessage(
          text: aiResponse.response ?? "I apologize, I couldn't process that request.",
          isMe: false,
          time: DateTime.now(),
        ));
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          text: "Error: ${e.toString()}",
          isMe: false,
          time: DateTime.now(),
          isError: true,
        ));
        _isLoading = false;
      });
    }

    _scrollToBottom();
  }

  Future<void> _toggleRecording() async {
    try {
      if (_isRecording) {
        final path = await _audioRecorder.stop();
        setState(() {
          _isRecording = false;
          _recordingPath = path;
        });
        if (path != null) {
          _sendMessage(voicePath: path);
        }
      } else {
        if (await _audioRecorder.hasPermission()) {
          final directory = await getTemporaryDirectory();
          _recordingPath = '${directory.path}/astra_voice_${DateTime.now().millisecondsSinceEpoch}.wav';
          
          await _audioRecorder.start(const RecordConfig(), path: _recordingPath!);
          setState(() {
            _isRecording = true;
          });
        }
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Recording error: $e")),
      );
    }
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 300), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FE),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: purple.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(Icons.psychology, color: purple, size: 20),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text("Astra AI Assistant", 
                  style: TextStyle(color: Color(0xFF333333), fontSize: 16, fontWeight: FontWeight.bold)),
                Row(
                  children: [
                    Container(width: 8, height: 8, decoration: const BoxDecoration(color: Colors.green, shape: BoxShape.circle)),
                    const SizedBox(width: 4),
                    const Text("Always Active", style: TextStyle(color: Colors.grey, fontSize: 10)),
                  ],
                ),
              ],
            ),
          ],
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.black, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.more_vert, color: Colors.grey),
            onPressed: () {},
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(20),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                return _buildMessageBubble(_messages[index]);
              },
            ),
          ),
          if (_isLoading)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              child: Row(
                children: [
                   SizedBox(height: 15, width: 15, child: CircularProgressIndicator(strokeWidth: 2, color: purple)),
                   const SizedBox(width: 10),
                   const Text("Astra is thinking...", style: TextStyle(color: Colors.grey, fontSize: 12)),
                ],
              ),
            ),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    return Align(
      alignment: message.isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 15),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: message.isError 
              ? Colors.red[50] 
              : (message.isSystem ? Colors.blue[50] : (message.isMe ? purple : Colors.white)),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(20),
            topRight: const Radius.circular(20),
            bottomLeft: Radius.circular(message.isMe ? 20 : 0),
            bottomRight: Radius.circular(message.isMe ? 0 : 20),
          ),
          boxShadow: [
            if (!message.isMe)
              BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 4)),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.text,
              style: TextStyle(
                color: message.isError 
                    ? Colors.red 
                    : (message.isSystem ? Colors.blue[800] : (message.isMe ? Colors.white : const Color(0xFF333333))),
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 5),
            Text(
              DateFormat('hh:mm a').format(message.time),
              style: TextStyle(
                color: message.isMe ? Colors.white70 : Colors.grey,
                fontSize: 10,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 15),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 20, offset: const Offset(0, -5)),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            GestureDetector(
              onLongPress: _toggleRecording,
              onLongPressEnd: (_) => _toggleRecording(),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _isRecording ? Colors.red : const Color(0xFFF0F0F0),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  _isRecording ? Icons.stop : Icons.mic,
                  color: _isRecording ? Colors.white : purple,
                  size: 20,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: const Color(0xFFF0F0F0),
                  borderRadius: BorderRadius.circular(25),
                ),
                child: TextField(
                  controller: _messageController,
                  decoration: const InputDecoration(
                    hintText: "Type or hold mic to dictate...",
                    border: InputBorder.none,
                    hintStyle: TextStyle(fontSize: 14, color: Colors.grey),
                  ),
                  onSubmitted: (_) => _sendMessage(),
                ),
              ),
            ),
            const SizedBox(width: 12),
            GestureDetector(
              onTap: () => _sendMessage(),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: purple,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.send, color: Colors.white, size: 20),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class ChatMessage {
  final String text;
  final bool isMe;
  final DateTime time;
  final bool isError;
  final bool isSystem;

  ChatMessage({
    required this.text,
    required this.isMe,
    required this.time,
    this.isError = false,
    this.isSystem = false,
  });
}
