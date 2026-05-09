import 'dart:io';
import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:doctro/services/astra_api_service.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/model/astra/ai_response_models.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:intl/intl.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';

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

  String? _sessionId;

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
      final String fallbackUserId =
          SharedPreferenceHelper.getString(Preferences.uniqueId) != 'N_A'
              ? SharedPreferenceHelper.getString(Preferences.uniqueId)
              : SharedPreferenceHelper.getString(Preferences.doctorId);
      final String effectiveUserId =
          user?.uid ?? (fallbackUserId == 'N_A' ? 'doctor_app_user' : fallbackUserId);

      // Prepare history for memory (last 10 messages)
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

      Map<String, dynamic> response;
      
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
        
        response = await _apiService.brainChat({
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
      } else {
        // Regular text chat
        response = await _apiService.brainChat({
          'q': message,
          'user_id': effectiveUserId,
          'session_id': _sessionId,
          'history': history,
          'user_metadata': {
            'role': 'doctor',
            'precise': true // Request precise clinical response
          }
        });
      }

      final aiResponse = AIChatResponse.fromJson(response);
      
      // Store session ID for memory
      if (aiResponse.sessionId != null) {
        _sessionId = aiResponse.sessionId;
      }

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
    } catch (e) {
      if (mounted) {
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
    }

    _scrollToBottom();
  }

  Future<void> _startRecording() async {
    try {
      if (_isRecording) return;
      if (await _audioRecorder.hasPermission()) {
        final directory = await getTemporaryDirectory();
        _recordingPath = '${directory.path}/astra_voice_${DateTime.now().millisecondsSinceEpoch}.wav';
        
        await _audioRecorder.start(const RecordConfig(), path: _recordingPath!);
        setState(() {
          _isRecording = true;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Recording error: $e")),
      );
    }
  }

  Future<void> _stopRecording() async {
    try {
      if (!_isRecording) return;
      final path = await _audioRecorder.stop();
      setState(() {
        _isRecording = false;
        _recordingPath = path;
      });
      if (path != null) {
        _sendMessage(voicePath: path);
      }
    } catch (e) {
      setState(() => _isRecording = false);
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
      backgroundColor: AyurezeTheme.canvas,
      appBar: AppBar(
        backgroundColor: AyurezeTheme.canvas,
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                 color: AyurezeTheme.forestDeep.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(Icons.psychology, color: AyurezeTheme.textPrimary, size: 20),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("Astra AI Assistant", 
                  style: TextStyle(color: AyurezeTheme.textPrimary, fontSize: 16, fontWeight: FontWeight.bold)),
                Row(
                  children: [
                    Container(width: 8, height: 8, decoration: const BoxDecoration(color: Colors.green, shape: BoxShape.circle)),
                    const SizedBox(width: 4),
                    Text("Always Active", style: TextStyle(color: AyurezeTheme.textSecondary, fontSize: 10)),
                  ],
                ),
              ],
            ),
          ],
        ),
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios, color: AyurezeTheme.textPrimary, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.more_vert, color: AyurezeTheme.textSecondary),
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
                   SizedBox(height: 15, width: 15, child: CircularProgressIndicator(strokeWidth: 2, color: AyurezeTheme.forestDeep)),
                   const SizedBox(width: 10),
                    Text("Astra is thinking...", style: TextStyle(color: AyurezeTheme.textSecondary, fontSize: 12)),
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
              ? AyurezeTheme.danger.withOpacity(0.1)
              : (message.isSystem ? AyurezeTheme.limeSoft : (message.isMe ? AyurezeTheme.forestDeep : AyurezeTheme.surface)),
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
                    : (message.isSystem
                        ? AyurezeTheme.forestDeep
                        : (message.isMe ? Colors.white : AyurezeTheme.textPrimary)),
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 5),
            Text(
              DateFormat('hh:mm a').format(message.time),
              style: TextStyle(
                color: message.isMe ? Colors.white70 : AyurezeTheme.textSecondary,
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
        color: AyurezeTheme.surface,
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 20, offset: const Offset(0, -5)),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            GestureDetector(
              onLongPress: _startRecording,
              onLongPressEnd: (_) => _stopRecording(),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _isRecording ? Colors.red : AyurezeTheme.surfaceMuted,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  _isRecording ? Icons.stop : Icons.mic,
                  color: _isRecording ? Colors.white : AyurezeTheme.forestDeep,
                  size: 20,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: AyurezeTheme.surfaceMuted,
                  borderRadius: BorderRadius.circular(25),
                ),
                child: TextField(
                  controller: _messageController,
                  decoration: InputDecoration(
                    hintText: "Type or hold mic to dictate...",
                    border: InputBorder.none,
                    hintStyle: TextStyle(fontSize: 14, color: AyurezeTheme.textSecondary),
                  ),
                  style: TextStyle(color: AyurezeTheme.textPrimary),
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
                  color: AyurezeTheme.forestDeep,
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

