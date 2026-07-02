# 📱 Flutter UI Implementation Guide - Astra Medical Flow

This document provides production-ready Flutter code snippets for implementing the "Knee Pain" automation flow in your Patient and Doctor apps.

---

## 🎨 1. Global Theme (Ayurveda Aesthetic)

Add this to your `main.dart` or `theme.dart`.

```dart
// theme.dart
import 'package:flutter/material.dart';

class AppTheme {
  static const primaryGreen = Color(0xFF2E7D32); // Healing Green
  static const secondarySage = Color(0xFFC8E6C9); // Sage Green
  static const accentGold = Color(0xFFFFD700);    // Ayurvedic Gold
  static const textDark = Color(0xFF1B1B1B);

  static ThemeData get lightTheme {
    return ThemeData(
      primaryColor: primaryGreen,
      scaffoldBackgroundColor: Colors.white,
      fontFamily: 'Inter', // Used per "Modern Typography" rule
      colorScheme: ColorScheme.light(
        primary: primaryGreen,
        secondary: accentGold,
      ),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: primaryGreen,
        elevation: 8,
      ),
    );
  }
}
```

---

## 🏠 2. Patient Home Screen with "Ask Astra" FAB

The Floating Action Button triggers the AI Chat.

```dart
// home_screen.dart
import 'package:flutter/material.dart';
import 'astra_chat_screen.dart';

class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Top Carousel
            _buildCarousel(),
            SizedBox(height: 20),
            // Functional Grid
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildFeatureIcon(Icons.medical_services, "Doctors"),
                _buildFeatureIcon(Icons.medication, "Medicines"),
                _buildFeatureIcon(Icons.spa, "Panchakarma"),
              ],
            ),
          ],
        ),
      ),
      // ✨ THE ASTRA BUTTON
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => AstraChatScreen()),
          );
        },
        icon: Icon(Icons.auto_awesome, color: Colors.white), // Sparkle Icon
        label: Text("Ask Astra", style: TextStyle(color: Colors.white)),
        backgroundColor: AppTheme.primaryGreen,
      ),
    );
  }

  Widget _buildFeatureIcon(IconData icon, String label) {
    return Column(
      children: [
        CircleAvatar(
          radius: 30,
          backgroundColor: AppTheme.secondarySage,
          child: Icon(icon, color: AppTheme.primaryGreen, size: 30),
        ),
        SizedBox(height: 8),
        Text(label, style: TextStyle(fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _buildCarousel() {
    return Container(
      height: 200,
      color: Colors.grey[200], // Placeholder for Image Slider
      child: Center(child: Text("Promotional Banners")),
    );
  }
}
```

---

## 💬 3. Astra Chat Screen (Rich Widgets & Doctor Cards)

This handles the chat flow and renders specialized "Doctor Cards" when the AI suggests them.

```dart
// astra_chat_screen.dart
import 'package:flutter/material.dart';
// import http package for API calls

class AstraChatScreen extends StatefulWidget {
  @override
  _AstraChatScreenState createState() => _AstraChatScreenState();
}

class _AstraChatScreenState extends State<AstraChatScreen> {
  final List<Map<String, dynamic>> messages = [
    {"role": "astra", "text": "Namaste! I am Astra. How can I help you today?", "type": "text"}
  ];
  final TextEditingController _controller = TextEditingController();

  void _sendMessage(String text) {
    setState(() {
      messages.add({"role": "user", "text": text, "type": "text"});
    });
    // Call Astra API Backend here
    // Mock Response from Backend for "Knee Pain" Scenario
    Future.delayed(Duration(seconds: 1), () {
      setState(() {
        messages.add({
          "role": "astra",
          "text": "I understand you have knee pain. This is often Vata aggravation. I recommend seeing a specialist.",
          "type": "text"
        });
        // DYNAMIC WIDGET: Doctor Card
        messages.add({
          "role": "astra",
          "type": "doctor_card",
          "data": {
            "name": "Dr. Ramesh",
            "spec": "Ayurvedic Ortho",
            "rating": 4.9,
            "image": "assets/doctor_ramesh.png"
          }
        });
      });
    });
    _controller.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Astra Companion")),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final msg = messages[index];
                if (msg['type'] == 'doctor_card') {
                  return DoctorCard(data: msg['data']);
                }
                return ChatBubble(
                  text: msg['text'],
                  isUser: msg['role'] == 'user',
                );
              },
            ),
          ),
          _buildInputArea(),
        ],
      ),
    );
  }
  
  Widget _buildInputArea() {
      return Padding(
          padding: EdgeInsets.all(8.0),
          child: Row(
              children: [
                  Expanded(child: TextField(controller: _controller, decoration: InputDecoration(hintText: "Type..."))),
                  IconButton(icon: Icon(Icons.send), onPressed: () => _sendMessage(_controller.text)),
                  // Voice Mode Trigger
                  IconButton(
                      icon: Icon(Icons.mic, color: Colors.blue),
                      onPressed: () {
                          // Navigate to Astra Fill Voice Mode
                      }
                  )
              ]
          )
      );
  }
}

class DoctorCard extends StatelessWidget {
  final Map<String, dynamic> data;
  DoctorCard({required this.data});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: EdgeInsets.all(12),
        child: Column(
          children: [
            Row(
              children: [
                CircleAvatar(radius: 25, backgroundImage: AssetImage("assets/doctor_placeholder.png")),
                SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(data['name'], style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                    Text(data['spec'], style: TextStyle(color: Colors.grey[700])),
                    Row(children: [Icon(Icons.star, size: 16, color: Colors.amber), Text(" ${data['rating']}")])
                  ],
                )
              ],
            ),
            SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: Color(0xFF2E7D32)),
                onPressed: () {
                   // Trigger Booking Flow
                },
                child: Text("Book Appointment", style: TextStyle(color: Colors.white)),
              ),
            )
          ],
        ),
      ),
    );
  }
}

class ChatBubble extends StatelessWidget {
    final String text;
    final bool isUser;
    
    ChatBubble({required this.text, required this.isUser});
    
    @override
    Widget build(BuildContext context) {
        return Align(
            alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
            child: Container(
                margin: EdgeInsets.symmetric(vertical: 4, horizontal: 16),
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                    color: isUser ? Colors.blue[100] : Colors.grey[200],
                    borderRadius: BorderRadius.circular(12)
                ),
                child: Text(text)
            )
        );
    }
}
```

---

## 🎙️ 4. Doctor App: Voice Prescription Mode

This screen records voice and sends it to `/astra-fill/process-voice`.

```dart
// doctor_voice_dictation.dart
import 'package:flutter/material.dart';
// import 'package:flutter_sound/flutter_sound.dart'; // Audio Recorder plugin

class DoctorVoicePage extends StatefulWidget {
  @override
  _DoctorVoicePageState createState() => _DoctorVoicePageState();
}

class _DoctorVoicePageState extends State<DoctorVoicePage> {
  bool isRecording = false;

  void toggleRecording() {
    setState(() => isRecording = !isRecording);
    // Logic to start/stop flutter_sound recorder
    if (!isRecording) {
        // Prepare file and post to Astra API
        submitVoiceToAstra();
    }
  }
  
  void submitVoiceToAstra() async {
      // API Call to /astra-fill/process-voice
      // On success: Navigate to Confirmation Screen
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF121212), // Dark Mode for Focus
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              isRecording ? "Listening..." : "Tap to Dictate Prescription",
              style: TextStyle(color: Colors.white, fontSize: 20),
            ),
            SizedBox(height: 40),
            // Waveform Visualization (Placeholder)
            Container(
                height: 100,
                width: 300,
                child: isRecording 
                    ? Image.asset("assets/waveform_anim.gif") // Dynamic Waveform
                    : Container()
            ),
            SizedBox(height: 40),
            GestureDetector(
              onTap: toggleRecording,
              child: AnimatedContainer(
                duration: Duration(milliseconds: 200),
                height: isRecording ? 100 : 80,
                width: isRecording ? 100 : 80,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isRecording ? Colors.red : Colors.blue,
                  boxShadow: [
                      BoxShadow(color: isRecording ? Colors.red.withOpacity(0.5) : Colors.blue.withOpacity(0.5), blurRadius: 20)
                  ]
                ),
                child: Icon(
                  isRecording ? Icons.stop : Icons.mic,
                  color: Colors.white,
                  size: 40,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 📦 5. Asset Requirements
To make the UI look premium as requested:
1.  **Fonts**: Download `Inter` or `Roboto` from Google Fonts.
2.  **Icons**: Use `CupertinoIcons` or Material Icons.
3.  **Animations**: Use `Lottie` files for the "Listening" waveform.
