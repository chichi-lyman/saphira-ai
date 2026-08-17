// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../services/saphira_config.dart';

/// Settings sheet including backend URL and Default Device Assistant controls.
class SettingsSheet extends StatefulWidget {
  const SettingsSheet({super.key});

  @override
  State<SettingsSheet> createState() => _SettingsSheetState();
}

class _SettingsSheetState extends State<SettingsSheet> {
  late TextEditingController _apiCtrl;
  static const MethodChannel _assistantChannel =
      MethodChannel('com.saphira.ai/assistant');

  Map<String, dynamic>? _roleStatus;
  bool _roleBusy = false;
  String? _roleMessage;

  @override
  void initState() {
    super.initState();
    final config = context.read<SaphiraConfig>();
    _apiCtrl = TextEditingController(text: config.apiBaseUrl);
    _refreshRoleStatus();
  }

  @override
  void dispose() {
    _apiCtrl.dispose();
    super.dispose();
  }

  Future<void> _refreshRoleStatus() async {
    try {
      final raw = await _assistantChannel.invokeMethod('getAssistantRoleStatus');
      if (raw is Map && mounted) {
        setState(() {
          _roleStatus = Map<String, dynamic>.from(raw);
          _roleMessage = null;
        });
      }
    } on PlatformException catch (e) {
      if (mounted) {
        setState(() => _roleMessage = 'Unable to query assistant role: ${e.message}');
      }
    } catch (_) {
      // Native layer may be unavailable on non-Android targets.
    }
  }

  Future<void> _requestAssistantRole() async {
    setState(() {
      _roleBusy = true;
      _roleMessage = null;
    });
    try {
      final raw = await _assistantChannel.invokeMethod('requestAssistantRole');
      if (raw is Map && mounted) {
        final held = raw['held'] == true;
        final openedSettings = raw['openedSettings'] == true;
        setState(() {
          _roleMessage = held
              ? 'Saphira is now the default device assistant.'
              : openedSettings
                  ? 'Opened system settings. Select Saphira as the Device Assistant.'
                  : 'Role request completed. Check status below.';
        });
      }
      await _refreshRoleStatus();
    } on PlatformException catch (e) {
      if (mounted) {
        setState(() => _roleMessage = 'Request failed: ${e.message}');
      }
    } finally {
      if (mounted) setState(() => _roleBusy = false);
    }
  }

  Future<void> _openAssistantSettings() async {
    setState(() {
      _roleBusy = true;
      _roleMessage = null;
    });
    try {
      await _assistantChannel.invokeMethod('openAssistantSettings');
      if (mounted) {
        setState(() =>
            _roleMessage = 'Opened Default Apps / Voice Input settings.');
      }
    } on PlatformException catch (e) {
      if (mounted) {
        setState(() => _roleMessage = 'Could not open settings: ${e.message}');
      }
    } finally {
      if (mounted) setState(() => _roleBusy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final roleHeld = _roleStatus?['roleHeld'] == true;
    final roleAvailable = _roleStatus?['roleAvailable'] == true;
    final apiAvailable = _roleStatus?['apiAvailable'] == true;

    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Saphira Settings',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: Color(0xFF00E5FF),
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Architected by Chelsea Megan Woods',
              style: TextStyle(
                color: Colors.white.withOpacity(0.5),
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 20),

            // ── Backend URL ──
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
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
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
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
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

            const SizedBox(height: 28),
            const Divider(color: Color(0xFF2A2A38)),
            const SizedBox(height: 16),

            // ── Default Device Assistant ──
            const Text(
              'Default Device Assistant',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Color(0xFF00E5FF),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Make Saphira appear when you long-press the home or power button, '
              'the same way Gemini or the system assistant does.',
              style: TextStyle(
                color: Colors.white.withOpacity(0.65),
                fontSize: 13,
                height: 1.35,
              ),
            ),
            const SizedBox(height: 12),

            // Status row
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              decoration: BoxDecoration(
                color: const Color(0xFF1A1A24),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _statusLine(
                    'Role API',
                    apiAvailable ? 'Available' : 'Unavailable / non-Android',
                    apiAvailable,
                  ),
                  const SizedBox(height: 6),
                  _statusLine(
                    'Assistant role',
                    roleAvailable ? 'Supported on this device' : 'Not available',
                    roleAvailable,
                  ),
                  const SizedBox(height: 6),
                  _statusLine(
                    'Saphira is default',
                    roleHeld ? 'Yes' : 'No',
                    roleHeld,
                  ),
                ],
              ),
            ),

            if (_roleMessage != null) ...[
              const SizedBox(height: 10),
              Text(
                _roleMessage!,
                style: TextStyle(
                  color: Colors.white.withOpacity(0.75),
                  fontSize: 12,
                ),
              ),
            ],

            const SizedBox(height: 14),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: roleHeld
                      ? const Color(0xFF2A2A38)
                      : const Color(0xFF9D00FF),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onPressed: (_roleBusy || roleHeld) ? null : _requestAssistantRole,
                child: _roleBusy
                    ? const SizedBox(
                        height: 18,
                        width: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : Text(
                        roleHeld
                            ? 'Already set as default assistant'
                            : 'Set Saphira as Default Assistant',
                      ),
              ),
            ),
            const SizedBox(height: 10),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                style: OutlinedButton.styleFrom(
                  foregroundColor: const Color(0xFF00E5FF),
                  side: const BorderSide(color: Color(0xFF00E5FF)),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onPressed: _roleBusy ? null : _openAssistantSettings,
                child: const Text('Open System Assistant Settings'),
              ),
            ),

            const SizedBox(height: 16),
            Text(
              'Version 1.3.1  •  Dual-interface assistant',
              style: TextStyle(
                color: Colors.white.withOpacity(0.35),
                fontSize: 11,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _statusLine(String label, String value, bool positive) {
    return Row(
      children: [
        Text(
          '$label: ',
          style: TextStyle(
            color: Colors.white.withOpacity(0.55),
            fontSize: 13,
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: TextStyle(
              color: positive ? const Color(0xFF00E5FF) : Colors.white70,
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }
}
