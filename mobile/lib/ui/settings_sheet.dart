// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/saphira_config.dart';

class SettingsSheet extends StatefulWidget {
  const SettingsSheet({super.key});

  @override
  State<SettingsSheet> createState() => _SettingsSheetState();
}

class _SettingsSheetState extends State<SettingsSheet> {
  late TextEditingController _apiCtrl;

  @override
  void initState() {
    super.initState();
    final config = context.read<SaphiraConfig>();
    _apiCtrl = TextEditingController(text: config.apiBaseUrl);
  }

  @override
  void dispose() {
    _apiCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 20, right: 20, top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Saphira Settings',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: Color(0xFF00E5FF))),
          const SizedBox(height: 6),
          Text('Architected by Chelsea Megan Woods',
              style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 12)),
          const SizedBox(height: 20),
          const Text('Backend API Base URL', style: TextStyle(color: Colors.white70)),
          const SizedBox(height: 8),
          TextField(
            controller: _apiCtrl,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: 'https://your-saphira-backend.example.com',
              hintStyle: TextStyle(color: Colors.white.withOpacity(0.3)),
              filled: true,
              fillColor: const Color(0xFF1A1A24),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF00E5FF),
                foregroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              onPressed: () async {
                await context.read<SaphiraConfig>().setApiBaseUrl(_apiCtrl.text);
                if (context.mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('API URL saved')),
                  );
                }
              },
              child: const Text('Save'),
            ),
          ),
          const SizedBox(height: 12),
          Text('Version 1.3.0  •  Dual-interface assistant',
              style: TextStyle(color: Colors.white.withOpacity(0.35), fontSize: 11)),
        ],
      ),
    );
  }
}
