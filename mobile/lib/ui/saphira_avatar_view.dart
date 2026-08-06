// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

import 'package:flutter/material.dart';

enum SaphiraAvatarState {
  welcome, idle, listening, thinking, talking, confirm, glow,
}

class SaphiraAvatarView extends StatelessWidget {
  final SaphiraAvatarState state;
  final String? frameUrl;

  const SaphiraAvatarView({super.key, required this.state, this.frameUrl});

  @override
  Widget build(BuildContext context) {
    final (color, label, icon) = _visuals(state);
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          AnimatedContainer(
            duration: const Duration(milliseconds: 400),
            width: 110, height: 110,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(colors: [
                color.withOpacity(0.85), color.withOpacity(0.15), Colors.transparent,
              ]),
              boxShadow: [BoxShadow(
                color: color.withOpacity(0.45),
                blurRadius: state == SaphiraAvatarState.glow ? 36 : 18,
                spreadRadius: state == SaphiraAvatarState.glow ? 8 : 2,
              )],
            ),
            child: Icon(icon, size: 48, color: Colors.white),
          ),
          const SizedBox(height: 12),
          Text(label, style: TextStyle(color: color, fontSize: 13, letterSpacing: 1.1, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  (Color, String, IconData) _visuals(SaphiraAvatarState s) {
    switch (s) {
      case SaphiraAvatarState.welcome: return (const Color(0xFF00E5FF), 'Ready', Icons.auto_awesome);
      case SaphiraAvatarState.listening: return (const Color(0xFF00E5FF), 'Listening', Icons.graphic_eq);
      case SaphiraAvatarState.thinking: return (const Color(0xFF9D00FF), 'Thinking', Icons.psychology);
      case SaphiraAvatarState.talking: return (const Color(0xFF00E5FF), 'Speaking', Icons.record_voice_over);
      case SaphiraAvatarState.confirm: return (const Color(0xFFFFB300), 'Confirm?', Icons.help_outline);
      case SaphiraAvatarState.glow: return (const Color(0xFF00FF9D), 'Done', Icons.check_circle_outline);
      case SaphiraAvatarState.idle:
      default: return (const Color(0xFF6B6B80), 'Idle', Icons.circle_outlined);
    }
  }
}
