// Copyright (c) 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
// All rights reserved.

import 'dart:ui';

import 'package:flutter/material.dart';

enum SaphiraAgentState { idle, listening, thinking, executingAction }

/// Neon glassmorphism floating HUD for Saphira agent status.
///
/// Use inside a Flutter overlay route or embed in a system overlay host.
/// Drive [currentState] / [statusText] from the WebSocket dispatcher stream
/// (listening \u2192 thinking \u2192 executingAction while NovaReign runs a11y commands).
class SaphiraHUDOverlay extends StatefulWidget {
  final SaphiraAgentState currentState;
  final String statusText;
  final String activeAgent;
  final VoidCallback onMicTap;
  final VoidCallback onClose;

  const SaphiraHUDOverlay({
    super.key,
    required this.currentState,
    required this.statusText,
    required this.activeAgent,
    required this.onMicTap,
    required this.onClose,
  });

  @override
  State<SaphiraHUDOverlay> createState() => _SaphiraHUDOverlayState();
}

class _SaphiraHUDOverlayState extends State<SaphiraHUDOverlay>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  Color _getGlowColor() {
    switch (widget.currentState) {
      case SaphiraAgentState.listening:
        return const Color(0xFFFF007A); // Glowing Pink
      case SaphiraAgentState.thinking:
        return const Color(0xFF00F0FF); // Cyan
      case SaphiraAgentState.executingAction:
        return const Color(0xFF9D00FF); // Ultraviolet
      case SaphiraAgentState.idle:
        return const Color(0xFF39FF14); // Lime Green
    }
  }

  @override
  Widget build(BuildContext context) {
    final glowColor = _getGlowColor();

    return Material(
      color: Colors.transparent,
      child: Center(
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 20),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: glowColor.withOpacity(0.4),
                blurRadius: 20,
                spreadRadius: 2,
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(24),
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 16, sigmaY: 16),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.85),
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(
                    color: glowColor.withOpacity(0.6),
                    width: 1.5,
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    AnimatedBuilder(
                      animation: _pulseController,
                      builder: (context, child) {
                        return Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: glowColor.withOpacity(0.2),
                            border: Border.all(
                              color: glowColor,
                              width: 2 + (_pulseController.value * 2),
                            ),
                          ),
                          child: IconButton(
                            icon: Icon(
                              widget.currentState == SaphiraAgentState.listening
                                  ? Icons.mic
                                  : Icons.auto_awesome,
                              color: glowColor,
                              size: 20,
                            ),
                            onPressed: widget.onMicTap,
                          ),
                        );
                      },
                    ),
                    const SizedBox(width: 12),
                    Flexible(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                widget.activeAgent.toUpperCase(),
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w800,
                                  letterSpacing: 1.2,
                                  color: glowColor,
                                ),
                              ),
                              const SizedBox(width: 6),
                              Container(
                                width: 6,
                                height: 6,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: glowColor,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 2),
                          Text(
                            widget.statusText,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFF111111),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      icon: const Icon(Icons.close, size: 18, color: Colors.grey),
                      onPressed: widget.onClose,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
