// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Saphira L1–L3 autonomy gate for Flutter / overlay paths

enum SaphiraAutonomyLevel {
  l1ConfirmFirst,
  l2Supervised,
  l3Background,
}

class AutonomyGate {
  static const Set<String> l1Intents = {
    'unlock',
    'lock',
    'payment',
    'send_email',
    'deploy_prod',
    'migrate',
    'cold_outreach',
  };

  static const Set<String> l2Intents = {
    'turn_on',
    'turn_off',
    'set_brightness',
    'set_temperature',
    'activate_scene',
    'sandbox_code',
    'ui_draft',
  };

  /// Resolve required level for an intent string.
  static SaphiraAutonomyLevel levelFor(String intent) {
    final i = intent.toLowerCase().trim();
    if (l1Intents.contains(i)) return SaphiraAutonomyLevel.l1ConfirmFirst;
    if (l2Intents.contains(i)) return SaphiraAutonomyLevel.l2Supervised;
    // Default conservative for unknown actions from overlay
    return SaphiraAutonomyLevel.l1ConfirmFirst;
  }

  /// Returns true if action may run without blocking on UI confirm.
  static bool canExecute(String intent, {required bool userConfirmed}) {
    final level = levelFor(intent);
    if (level == SaphiraAutonomyLevel.l1ConfirmFirst) {
      return userConfirmed;
    }
    return true; // L2/L3 within policy; backend still enforces Agent Two
  }

  static String label(SaphiraAutonomyLevel level) {
    switch (level) {
      case SaphiraAutonomyLevel.l1ConfirmFirst:
        return 'L1 — Confirm first';
      case SaphiraAutonomyLevel.l2Supervised:
        return 'L2 — Supervised';
      case SaphiraAutonomyLevel.l3Background:
        return 'L3 — Background';
    }
  }

  /// SAE reference only — not used as execution policy.
  static String saeNoteLevel4vs5() {
    return 'SAE Level 4 = full automation inside a defined domain. '
        'SAE Level 5 = everywhere, all conditions. '
        'Saphira L3 is background software autonomy, not SAE 5 physical autonomy.';
  }
}
