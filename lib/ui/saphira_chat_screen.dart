// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Full-screen public chat: holographic avatar + message stream.

import 'package:flutter/material.dart';
import 'saphira_avatar_view.dart';
import '../services/avatar_channel.dart';

class SaphiraChatScreen extends StatefulWidget {
  final String apiBase;

  const SaphiraChatScreen({super.key, this.apiBase = 'http://localhost:8000'});

  @override
  State<SaphiraChatScreen> createState() => _SaphiraChatScreenState();
}

class _SaphiraChatScreenState extends State<SaphiraChatScreen> {
  final _controller = TextEditingController();
  final _messages = <_ChatLine>[];
  SaphiraAvatarState _avatarState = SaphiraAvatarState.welcome;
  String? _avatarUrl;
  bool _busy = false;

  late final AvatarChannel _avatar;

  static const Color ivory = Color(0xFFF9F9FB);
  static const Color electricBlue = Color(0xFF00E5FF);
  static const Color ultraviolet = Color(0xFF9D00FF);
  static const Color ink = Color(0xFF101018);

  @override
  void initState() {
    super.initState();
    _avatar = AvatarChannel(baseUrl: widget.apiBase);
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    try {
      final frame = await _avatar.frame(state: SaphiraAvatarState.welcome);
      if (mounted) {
        setState(() {
          _avatarUrl = frame['url'] as String?;
          _avatarState = SaphiraAvatarState.welcome;
        });
      }
    } catch (_) {}
  }

  Future<void> _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _busy) return;
    setState(() {
      _busy = true;
      _avatarState = SaphiraAvatarState.listening;
      _messages.add(_ChatLine(text, isUser: true));
      _controller.clear();
    });

    try {
      final res = await _avatar.baseUrl.isNotEmpty
          ? await _postChat(text)
          : <String, dynamic>{};
      final reply = (res['message'] as String?) ?? 'I heard you.';
      final stateName = res['avatar_state'] as String? ?? 'talking';
      final frameUrl = (res['avatar_frame'] as Map?)?['url'] as String?;

      setState(() {
        _messages.add(_ChatLine(reply, isUser: false));
        _avatarState = _parseState(stateName);
        if (frameUrl != null) _avatarUrl = frameUrl;
        _busy = false;
      });
    } catch (e) {
      setState(() {
        _messages.add(_ChatLine("I'm having a moment — try again shortly.", isUser: false));
        _avatarState = SaphiraAvatarState.thinking;
        _busy = false;
      });
    }
  }

  Future<Map<String, dynamic>> _postChat(String message) async {
    final uri = Uri.parse('${widget.apiBase}/chat');
    // ignore: depend_on_referenced_packages
    final http = await _httpPost(uri, {'message': message});
    return http;
  }

  Future<Map<String, dynamic>> _httpPost(Uri uri, Map body) async {
    // Lightweight to avoid hard dependency if http not in pubspec yet
    try {
      // Prefer package http if available via avatar channel pattern
      final channel = AvatarChannel(baseUrl: widget.apiBase);
      // Reuse frame endpoint pattern — chat is parallel REST
      final client = await Future.value(null);
      // Direct implementation using dart:io would need more imports;
      // for production add `http` to pubspec and use http.post.
      // Fallback: use AvatarChannel's host for frame only.
      final _ = client;
    } catch (_) {}
    // Minimal stub until http package is declared in project pubspec
    return {
      'message': "Got it — I'm on it.",
      'avatar_state': 'talking',
      'avatar_frame': {'url': _avatarUrl},
    };
  }

  SaphiraAvatarState _parseState(String name) {
    return SaphiraAvatarState.values.firstWhere(
      (e) => e.name == name,
      orElse: () => SaphiraAvatarState.talking,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ivory,
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              flex: 5,
              child: SaphiraAvatarView(
                avatarImageUrl: _avatarUrl,
                state: _avatarState,
                statusLabel: _busy ? 'SAPHIRA AI // LISTENING' : 'SAPHIRA AI // ONLINE',
              ),
            ),
            Expanded(
              flex: 4,
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: electricBlue.withOpacity(0.4)),
                  boxShadow: [
                    BoxShadow(color: ultraviolet.withOpacity(0.08), blurRadius: 20),
                  ],
                ),
                child: ListView.builder(
                  itemCount: _messages.length,
                  itemBuilder: (_, i) {
                    final m = _messages[i];
                    return Align(
                      alignment: m.isUser ? Alignment.centerRight : Alignment.centerLeft,
                      child: Container(
                        margin: const EdgeInsets.symmetric(vertical: 4),
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                        decoration: BoxDecoration(
                          color: m.isUser
                              ? electricBlue.withOpacity(0.12)
                              : ultraviolet.withOpacity(0.08),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Text(
                          m.text,
                          style: const TextStyle(color: ink, fontSize: 15),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      onSubmitted: (_) => _send(),
                      decoration: InputDecoration(
                        hintText: 'Talk to Saphira…',
                        filled: true,
                        fillColor: Colors.white,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide(color: electricBlue.withOpacity(0.5)),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide(color: electricBlue.withOpacity(0.35)),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  FloatingActionButton(
                    mini: true,
                    backgroundColor: ultraviolet,
                    onPressed: _send,
                    child: const Icon(Icons.send, color: Colors.white, size: 18),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ChatLine {
  final String text;
  final bool isUser;
  _ChatLine(this.text, {required this.isUser});
}
