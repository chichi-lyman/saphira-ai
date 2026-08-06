// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Full-screen chat with holographic avatar aesthetic.

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

import '../services/saphira_api.dart';
import '../services/saphira_config.dart';
import '../services/saphira_tts.dart';
import 'saphira_avatar_view.dart';
import 'settings_sheet.dart';

class SaphiraChatScreen extends StatefulWidget {
  const SaphiraChatScreen({super.key});

  @override
  State<SaphiraChatScreen> createState() => _SaphiraChatScreenState();
}

class _SaphiraChatScreenState extends State<SaphiraChatScreen> {
  final _controller = TextEditingController();
  final _scroll = ScrollController();
  final List<_ChatLine> _messages = [];
  final stt.SpeechToText _speech = stt.SpeechToText();

  SaphiraAvatarState _avatarState = SaphiraAvatarState.welcome;
  bool _busy = false;
  bool _listening = false;
  late SaphiraTts _tts;

  static const Color electricBlue = Color(0xFF00E5FF);
  static const Color ultraviolet = Color(0xFF9D00FF);
  static const Color ink = Color(0xFF0A0A12);

  @override
  void initState() {
    super.initState();
    final config = context.read<SaphiraConfig>();
    _tts = SaphiraTts(backendTtsUrl: '${config.apiBaseUrl}/tts');
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    final api = context.read<SaphiraApi>();
    final online = await api.isOnline();
    if (!mounted) return;
    setState(() {
      _messages.add(_ChatLine(
        online
            ? "I'm here. Talk to me or type \u2014 I'll handle the rest quietly in the background."
            : "I'm offline right now. You can still type; I'll reconnect when the servers are reachable.",
        isUser: false,
      ));
      _avatarState = online ? SaphiraAvatarState.welcome : SaphiraAvatarState.thinking;
    });
  }

  Future<void> _send([String? forced]) async {
    final text = (forced ?? _controller.text).trim();
    if (text.isEmpty || _busy) return;

    setState(() {
      _busy = true;
      _avatarState = SaphiraAvatarState.listening;
      _messages.add(_ChatLine(text, isUser: true));
      _controller.clear();
    });
    _scrollToBottom();

    final api = context.read<SaphiraApi>();
    final res = await api.chat(message: text);
    final reply = (res['message'] as String?) ?? "I heard you.";
    final stateName = (res['avatar_state'] as String?) ?? 'talking';

    if (!mounted) return;
    setState(() {
      _messages.add(_ChatLine(reply, isUser: false));
      _avatarState = _parseState(stateName);
      _busy = false;
    });
    _scrollToBottom();
    await _tts.speak(reply, style: 'assist');
  }

  SaphiraAvatarState _parseState(String name) {
    switch (name.toLowerCase()) {
      case 'listening': return SaphiraAvatarState.listening;
      case 'thinking': return SaphiraAvatarState.thinking;
      case 'confirm': return SaphiraAvatarState.confirm;
      case 'glow': return SaphiraAvatarState.glow;
      case 'talking': return SaphiraAvatarState.talking;
      default: return SaphiraAvatarState.idle;
    }
  }

  Future<void> _toggleListen() async {
    if (_listening) {
      await _speech.stop();
      setState(() => _listening = false);
      return;
    }
    final available = await _speech.initialize(
      onStatus: (s) {
        if (s == 'done' || s == 'notListening') {
          if (mounted) setState(() => _listening = false);
        }
      },
    );
    if (!available) return;
    setState(() {
      _listening = true;
      _avatarState = SaphiraAvatarState.listening;
    });
    await _speech.listen(
      onResult: (r) {
        if (r.finalResult) _send(r.recognizedWords);
      },
      listenFor: const Duration(seconds: 12),
      pauseFor: const Duration(seconds: 3),
    );
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scroll.hasClients) {
        _scroll.animateTo(
          _scroll.position.maxScrollExtent + 80,
          duration: const Duration(milliseconds: 280),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _scroll.dispose();
    _tts.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ink,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('Saphira',
            style: TextStyle(fontWeight: FontWeight.w600, letterSpacing: 1.2, color: electricBlue)),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: Colors.white70),
            onPressed: () => showModalBottomSheet(
              context: context,
              backgroundColor: const Color(0xFF12121A),
              isScrollControlled: true,
              builder: (_) => const SettingsSheet(),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          SizedBox(height: 180, child: SaphiraAvatarView(state: _avatarState)),
          const Divider(color: Color(0xFF1E1E2A), height: 1),
          Expanded(
            child: ListView.builder(
              controller: _scroll,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              itemCount: _messages.length,
              itemBuilder: (_, i) {
                final m = _messages[i];
                return Align(
                  alignment: m.isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.78),
                    decoration: BoxDecoration(
                      color: m.isUser ? ultraviolet.withOpacity(0.35) : const Color(0xFF1A1A24),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: m.isUser ? ultraviolet.withOpacity(0.5) : electricBlue.withOpacity(0.25),
                      ),
                    ),
                    child: Text(m.text, style: const TextStyle(color: Colors.white, height: 1.35)),
                  ),
                );
              },
            ),
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
              child: Row(
                children: [
                  IconButton(
                    icon: Icon(_listening ? Icons.mic : Icons.mic_none,
                        color: _listening ? electricBlue : Colors.white70),
                    onPressed: _busy ? null : _toggleListen,
                  ),
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      enabled: !_busy,
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        hintText: _listening ? 'Listening\u2026' : 'Talk to Saphira\u2026',
                        hintStyle: TextStyle(color: Colors.white.withOpacity(0.4)),
                        filled: true,
                        fillColor: const Color(0xFF16161F),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                      ),
                      onSubmitted: (_) => _send(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: _busy
                        ? const SizedBox(width: 22, height: 22,
                            child: CircularProgressIndicator(strokeWidth: 2, color: electricBlue))
                        : const Icon(Icons.send_rounded, color: electricBlue),
                    onPressed: _busy ? null : () => _send(),
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

class _ChatLine {
  final String text;
  final bool isUser;
  _ChatLine(this.text, {required this.isUser});
}
