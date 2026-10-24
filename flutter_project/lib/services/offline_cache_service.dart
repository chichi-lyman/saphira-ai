// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Nova Umbrella
//
// lib/services/offline_cache_service.dart
// Lightweight local SQLite-style cache for offline prompts, state flags,
// and memory logs. Auto-syncs with the PostgreSQL ledger on reconnection.
//
// Production note: replace the in-memory + shared_preferences fallback with
// sqflite / drift / Room (via platform channel) for durable offline storage.

import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';

/// Queued item waiting for server sync.
class OfflineQueueItem {
  final String id;
  final String kind; // prompt | state_flag | memory_log | reminder
  final Map<String, dynamic> payload;
  final DateTime createdAt;
  bool synced;

  OfflineQueueItem({
    required this.id,
    required this.kind,
    required this.payload,
    DateTime? createdAt,
    this.synced = false,
  }) : createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toJson() => {
        'id': id,
        'kind': kind,
        'payload': payload,
        'created_at': createdAt.toIso8601String(),
        'synced': synced,
      };

  factory OfflineQueueItem.fromJson(Map<String, dynamic> j) => OfflineQueueItem(
        id: j['id'] as String,
        kind: j['kind'] as String,
        payload: Map<String, dynamic>.from(j['payload'] as Map? ?? {}),
        createdAt: DateTime.tryParse(j['created_at'] as String? ?? '') ?? DateTime.now(),
        synced: j['synced'] as bool? ?? false,
      );
}

/// Local-first offline cache that queues work while the device is offline
/// and drains to the central ledger (src/memory/ledger.py) on reconnect.
class OfflineCacheService extends ChangeNotifier {
  OfflineCacheService();

  final List<OfflineQueueItem> _queue = [];
  bool _online = true;
  Timer? _syncTimer;

  bool get isOnline => _online;
  int get pendingCount => _queue.where((e) => !e.synced).length;
  List<OfflineQueueItem> get pending =>
      List.unmodifiable(_queue.where((e) => !e.synced));

  void setOnline(bool online) {
    if (_online == online) return;
    _online = online;
    notifyListeners();
    if (online) {
      unawaited(syncPending());
    }
  }

  /// Enqueue a user prompt, system state flag, or memory log while offline
  /// (or always, for durability).
  Future<void> enqueue({
    required String kind,
    required Map<String, dynamic> payload,
  }) async {
    final item = OfflineQueueItem(
      id: 'local_${DateTime.now().microsecondsSinceEpoch}',
      kind: kind,
      payload: payload,
    );
    _queue.add(item);
    notifyListeners();
    // Persist to durable store here (sqflite / shared_preferences).
    if (_online) {
      unawaited(syncPending());
    }
  }

  /// Drain unsynced items to the backend ledger.
  /// Replace the placeholder HTTP calls with the real FastAPI memory endpoints.
  Future<int> syncPending() async {
    if (!_online) return 0;
    int synced = 0;
    for (final item in List<OfflineQueueItem>.from(_queue)) {
      if (item.synced) continue;
      try {
        // Production: POST to /api/memory/ledger or equivalent.
        // await apiClient.postLedgerEntry(item.toJson());
        item.synced = true;
        synced++;
      } catch (e) {
        debugPrint('[OfflineCache] sync failed for ${item.id}: $e');
        break; // stop on first failure; retry later
      }
    }
    // Prune successfully synced items older than 24h
    final cutoff = DateTime.now().subtract(const Duration(hours: 24));
    _queue.removeWhere((e) => e.synced && e.createdAt.isBefore(cutoff));
    if (synced > 0) notifyListeners();
    return synced;
  }

  void startPeriodicSync({Duration interval = const Duration(seconds: 45)}) {
    _syncTimer?.cancel();
    _syncTimer = Timer.periodic(interval, (_) {
      if (_online && pendingCount > 0) {
        unawaited(syncPending());
      }
    });
  }

  @override
  void dispose() {
    _syncTimer?.cancel();
    super.dispose();
  }
}
