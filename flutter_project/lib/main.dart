// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Nova Umbrella

import 'package:flutter/material.dart';

import 'screens/voice_chat_screen.dart';
import 'services/websocket_voice_client.dart';

/// Entry point for the Saphira Flutter client.
///
/// Configure the backend URL via --dart-define at build time:
///   flutter run --dart-define=SAPHIRA_BASE_URL=https://your-backend.example
void main() {
  const baseUrl = String.fromEnvironment(
    'SAPHIRA_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000', // Android emulator → host loopback
  );
  const token = String.fromEnvironment('SAPHIRA_AUTH_TOKEN', defaultValue: '');

  final wsClient = SaphiraWebSocketVoiceClient(
    baseUrl: baseUrl,
    authToken: token.isEmpty ? null : token,
    deviceId: 'flutter-mobile',
  );

  runApp(SaphiraApp(wsClient: wsClient));
}

class SaphiraApp extends StatelessWidget {
  const SaphiraApp({super.key, required this.wsClient});

  final SaphiraWebSocketVoiceClient wsClient;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Saphira AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        colorSchemeSeed: const Color(0xFF3B82F6),
        useMaterial3: true,
      ),
      home: VoiceChatScreen(wsClient: wsClient),
    );
  }
}
