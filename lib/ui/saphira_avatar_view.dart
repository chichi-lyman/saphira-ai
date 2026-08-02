// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Classy light-mode sci-fi holographic Saphira avatar canvas.
// Ivory / white base + electric blue + ultraviolet bloom.
// Renders Grok Imagine frames/clips of Chelsea-look Saphira.

import 'package:flutter/material.dart';

/// Visual states mirrored from backend AvatarState.
enum SaphiraAvatarState {
  idle,
  welcome,
  talking,
  thinking,
  listening,
  glow,
  confirm,
}

class SaphiraAvatarView extends StatefulWidget {
  final String? avatarImageUrl;
  final String? avatarVideoUrl;
  final SaphiraAvatarState state;
  final String statusLabel;
  final VoidCallback? onTap;

  const SaphiraAvatarView({
    super.key,
    this.avatarImageUrl,
    this.avatarVideoUrl,
    this.state = SaphiraAvatarState.idle,
    this.statusLabel = 'SAPHIRA AI // ONLINE',
    this.onTap,
  });

  @override
  State<SaphiraAvatarView> createState() => _SaphiraAvatarViewState();
}

class _SaphiraAvatarViewState extends State<SaphiraAvatarView>
    with SingleTickerProviderStateMixin {
  static const Color ivory = Color(0xFFF9F9FB);
  static const Color electricBlue = Color(0xFF00E5FF);
  static const Color ultraviolet = Color(0xFF9D00FF);
  static const Color ink = Color(0xFF101018);

  late AnimationController _pulse;

  @override
  void initState() {
    super.initState();
    _pulse = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1600),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulse.dispose();
    super.dispose();
  }

  bool get _active =>
      widget.state == SaphiraAvatarState.talking ||
      widget.state == SaphiraAvatarState.listening ||
      widget.state == SaphiraAvatarState.glow;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onTap,
      child: Container(
        color: ivory,
        child: Stack(
          alignment: Alignment.center,
          children: [
            // Soft radial ambient
            Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: RadialGradient(
                    colors: [
                      electricBlue.withOpacity(0.06),
                      ivory,
                    ],
                    radius: 0.85,
                  ),
                ),
              ),
            ),

            // Holographic pulse ring
            AnimatedBuilder(
              animation: _pulse,
              builder: (context, _) {
                final t = _pulse.value;
                final scale = _active ? 1.0 + t * 0.04 : 1.0 + t * 0.015;
                return Transform.scale(
                  scale: scale,
                  child: Container(
                    width: 320,
                    height: 560,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(28),
                      boxShadow: [
                        BoxShadow(
                          color: electricBlue.withOpacity(0.25 + t * 0.2),
                          blurRadius: 28 + t * 12,
                          spreadRadius: 4,
                        ),
                        BoxShadow(
                          color: ultraviolet.withOpacity(0.18 + t * 0.15),
                          blurRadius: 40 + t * 16,
                          spreadRadius: 8,
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),

            // Avatar frame
            ClipRRect(
              borderRadius: BorderRadius.circular(24),
              child: Container(
                width: 300,
                height: 540,
                decoration: BoxDecoration(
                  color: Colors.white,
                  border: Border.all(color: electricBlue, width: 2),
                  borderRadius: BorderRadius.circular(24),
                ),
                child: _buildMedia(),
              ),
            ),

            // Top HUD chip
            Positioned(
              top: 48,
              child: _HudChip(
                label: _stateLabel(widget.state),
                accent: ultraviolet,
              ),
            ),

            // Bottom status bar
            Positioned(
              bottom: 36,
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 22, vertical: 12),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.92),
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(color: electricBlue, width: 1.5),
                  boxShadow: [
                    BoxShadow(
                      color: electricBlue.withOpacity(0.35),
                      blurRadius: 14,
                    ),
                  ],
                ),
                child: Text(
                  widget.statusLabel,
                  style: const TextStyle(
                    color: ink,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 2.2,
                    fontSize: 12,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMedia() {
    final url = widget.avatarImageUrl;
    if (url != null && url.isNotEmpty) {
      return Image.network(
        url,
        fit: BoxFit.cover,
        width: 300,
        height: 540,
        errorBuilder: (_, __, ___) => _placeholder(),
        loadingBuilder: (context, child, progress) {
          if (progress == null) return child;
          return _placeholder();
        },
      );
    }
    return _placeholder();
  }

  Widget _placeholder() {
    return Container(
      color: const Color(0xFFF0F2F8),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.auto_awesome, size: 48, color: ultraviolet.withOpacity(0.7)),
            const SizedBox(height: 12),
            Text(
              'SAPHIRA',
              style: TextStyle(
                color: ink.withOpacity(0.5),
                letterSpacing: 4,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            SizedBox(
              width: 28,
              height: 28,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: electricBlue.withOpacity(0.8),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _stateLabel(SaphiraAvatarState s) {
    switch (s) {
      case SaphiraAvatarState.welcome:
        return 'WELCOME';
      case SaphiraAvatarState.talking:
        return 'SPEAKING';
      case SaphiraAvatarState.thinking:
        return 'THINKING';
      case SaphiraAvatarState.listening:
        return 'LISTENING';
      case SaphiraAvatarState.glow:
        return 'GLOW';
      case SaphiraAvatarState.confirm:
        return 'CONFIRMED';
      case SaphiraAvatarState.idle:
      default:
        return 'STANDBY';
    }
  }
}

class _HudChip extends StatelessWidget {
  final String label;
  final Color accent;

  const _HudChip({required this.label, required this.accent});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.9),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: accent.withOpacity(0.7)),
        boxShadow: [
          BoxShadow(color: accent.withOpacity(0.25), blurRadius: 10),
        ],
      ),
      child: Text(
        label,
        style: TextStyle(
          color: accent,
          fontWeight: FontWeight.w700,
          letterSpacing: 1.8,
          fontSize: 11,
        ),
      ),
    );
  }
}
