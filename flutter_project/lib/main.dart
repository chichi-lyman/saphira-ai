// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Nova Umbrella

import 'package:flutter/material.dart';

import 'services/foreground_service_bridge.dart';
import 'services/saphira_websocket_client.dart';
import 'screens/voice_chat_screen.dart';
import 'services/websocket_voice_client.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const SaphiraApp());
}

class SaphiraApp extends StatelessWidget {
  const SaphiraApp({super.key});

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
      home: const SaphiraHome(),
    );
  }
}

class SaphiraHome extends StatefulWidget {
  const SaphiraHome({super.key});

  @override
  State<SaphiraHome> createState() => _SaphiraHomeState();
}

class _SaphiraHomeState extends State<SaphiraHome> {
  bool _engineRunning = false;
  String _status = 'Idle';

  Future<void> _startEngine() async {
    setState(() => _status = 'Requesting overlay permission…');
    await SaphiraForegroundServiceBridge.requestOverlayPermission();

    setState(() => _status = 'Starting background engine…');
    final ok = await SaphiraForegroundServiceBridge.startService();

    setState(() {
      _engineRunning = ok;
      _status = ok ? 'Saphira background engine active' : 'Failed to start engine';
    });
  }

  Future<void> _stopEngine() async {
    final ok = await SaphiraForegroundServiceBridge.stopService();
    setState(() {
      _engineRunning = !ok ? _engineRunning : false;
      _status = ok ? 'Engine stopped' : 'Failed to stop engine';
    });
  }

  void _openVoiceChat() {
    const baseUrl = String.fromEnvironment(
      'SAPHIRA_BASE_URL',
      defaultValue: 'http://10.0.2.2:8000',
    );
    final wsClient = SaphiraWebSocketVoiceClient(
      baseUrl: baseUrl,
      deviceId: 'flutter-mobile',
    );
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => VoiceChatScreen(wsClient: wsClient)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0F1A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        title: const Text('Saphira AI Companion'),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                _status,
                style: TextStyle(
                  color: _engineRunning ? Colors.greenAccent : Colors.white70,
                  fontSize: 14,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              ElevatedButton.icon(
                onPressed: _engineRunning ? null : _startEngine,
                icon: const Icon(Icons.play_arrow_rounded),
                label: const Text('Start Saphira Background Engine'),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 48),
                ),
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _engineRunning ? _stopEngine : null,
                icon: const Icon(Icons.stop_rounded),
                label: const Text('Stop Saphira Background Engine'),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 48),
                ),
              ),
              const SizedBox(height: 32),
              OutlinedButton.icon(
                onPressed: _openVoiceChat,
                icon: const Icon(Icons.chat_bubble_outline),
                label: const Text('Open Voice Chat'),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 48),
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
