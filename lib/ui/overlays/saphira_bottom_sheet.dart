// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Gemini-style floating bottom sheet — dark luxury Saphira overlay

import 'package:flutter/material.dart';
import '../../services/autonomy_gate.dart';

class SaphiraBottomSheetOverlay extends StatelessWidget {
  final bool isListening;
  final String userQuery;
  final String samanthaResponse;
  final String? pendingL1Intent;
  final VoidCallback? onConfirmL1;
  final VoidCallback? onClose;
  final VoidCallback? onMic;

  const SaphiraBottomSheetOverlay({
    super.key,
    required this.isListening,
    required this.userQuery,
    required this.samanthaResponse,
    this.pendingL1Intent,
    this.onConfirmL1,
    this.onClose,
    this.onMic,
  });

  static const Color _bg = Color(0xFF0F0F14);
  static const Color _glow = Color(0xFF8A2BE2);

  @override
  Widget build(BuildContext context) {
    final needsConfirm = pendingL1Intent != null &&
        !AutonomyGate.canExecute(pendingL1Intent!, userConfirmed: false);

    return Positioned(
      bottom: 0,
      left: 0,
      right: 0,
      child: Material(
        color: Colors.transparent,
        child: Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: _bg.withOpacity(0.95),
            borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
            boxShadow: [
              BoxShadow(
                color: _glow.withOpacity(0.3),
                blurRadius: 25,
                spreadRadius: 2,
              ),
            ],
            border: Border.all(color: Colors.white10),
          ),
          child: SafeArea(
            top: false,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.white24,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                if (userQuery.isNotEmpty)
                  Text(
                    userQuery,
                    style: const TextStyle(color: Colors.white70, fontSize: 16),
                  ),
                const SizedBox(height: 8),
                Text(
                  samanthaResponse.isEmpty && isListening
                      ? 'Saphira is listening...'
                      : (samanthaResponse.isEmpty ? ' ' : samanthaResponse),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                if (needsConfirm) ...[
                  const SizedBox(height: 12),
                  Text(
                    AutonomyGate.label(SaphiraAutonomyLevel.l1ConfirmFirst),
                    style: const TextStyle(color: Colors.amberAccent, fontSize: 12),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      FilledButton(
                        onPressed: onConfirmL1,
                        child: Text('Confirm ${pendingL1Intent ?? "action"}'),
                      ),
                      const SizedBox(width: 8),
                      TextButton(
                        onPressed: onClose,
                        child: const Text('Cancel'),
                      ),
                    ],
                  ),
                ],
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.mic, color: Color(0xFFC0C0C0)),
                      onPressed: onMic,
                    ),
                    const _WaveformPlaceholder(),
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.white38),
                      onPressed: onClose,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _WaveformPlaceholder extends StatelessWidget {
  const _WaveformPlaceholder();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(
        5,
        (i) => Container(
          margin: const EdgeInsets.symmetric(horizontal: 2),
          width: 3,
          height: 8.0 + i * 4.0,
          decoration: BoxDecoration(
            color: const Color(0xFF8A2BE2).withOpacity(0.7),
            borderRadius: BorderRadius.circular(2),
          ),
        ),
      ),
    );
  }
}
