// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Nova Umbrella

import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';

import '../services/websocket_voice_client.dart';

/// Minimal voice + transcript surface that drives [SaphiraWebSocketVoiceClient].
/// Replace styling with the full glassmorphism HUD when ready.
class VoiceChatScreen extends StatefulWidget {
  const VoiceChatScreen({
    super.key,
    required this.wsClient,
  });

  final SaphiraWebSocketVoiceClient wsClient;

  @override
  State<VoiceChatScreen> createState() => _VoiceChatScreenState();
}

class _VoiceChatScreenState extends State<VoiceChatScreen> {
  final _textController = TextEditingController();
  final List<TranscriptEvent> _messages = [];
  String _status = 'idle';
  bool _micGranted = false;

  @override
  void initState() {
    super.initState();
    _requestMic();
    widget.wsClient.transcripts.listen((e) {
      if (!mounted) return;
      setState(() {
        if (e.isFinal) {
          _messages.add(e);
        }
      });
    });
    widget.wsClient.statusStream.listen((s) {
      if (!mounted) return;
      setState(() => _status = s);
    });
    widget.wsClient.addListener(_onClientChange);
    widget.wsClient.connect().catchError((e) {
      debugPrint('WS connect failed: $e');
    });
  }

  void _onClientChange() {
    if (mounted) setState(() {});
  }

  Future<void> _requestMic() async {
    final status = await Permission.microphone.request();
    setState(() => _micGranted = status.isGranted);
  }

  void _sendText() {
    final text = _textController.text.trim();
    if (text.isEmpty) return;
    widget.wsClient.sendText(text);
    setState(() {
      _messages.add(TranscriptEvent(role: 'user', content: text));
      _textController.clear();
    });
  }

  @override
  void dispose() {
    widget.wsClient.removeListener(_onClientChange);
    _textController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final conn = widget.wsClient.connectionState;
    return Scaffold(
      backgroundColor: const Color(0xFF0B0F1A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        title: const Text('Saphira', style: TextStyle(color: Colors.white)),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Center(
              child: Text(
                '$conn · $_status',
                style: TextStyle(
                  color: conn == 'connected' ? Colors.greenAccent : Colors.orangeAccent,
                  fontSize: 12,
                ),
              ),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (_, i) {
                final m = _messages[i];
                final isUser = m.role == 'user';
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: isUser
                          ? const Color(0xFF3B82F6).withOpacity(0.85)
                          : const Color(0xFF1E293B),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Text(m.content, style: const TextStyle(color: Colors.white)),
                  ),
                );
              },
            ),
          ),
          if (!_micGranted)
            const Padding(
              padding: EdgeInsets.all(8),
              child: Text(
                'Microphone permission required for voice',
                style: TextStyle(color: Colors.orangeAccent, fontSize: 12),
              ),
            ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _textController,
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        hintText: 'Message Saphira…',
                        hintStyle: TextStyle(color: Colors.white.withOpacity(0.4)),
                        filled: true,
                        fillColor: const Color(0xFF1E293B),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      ),
                      onSubmitted: (_) => _sendText(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton.filled(
                    onPressed: _sendText,
                    icon: const Icon(Icons.send_rounded),
                    style: IconButton.styleFrom(
                      backgroundColor: const Color(0xFF3B82F6),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
