// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
package com.saphira.ai

import android.content.Intent
import android.util.Log
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private var methodChannel: MethodChannel? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        methodChannel = MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
        handleAssistantIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleAssistantIntent(intent)
    }

    private fun handleAssistantIntent(intent: Intent?) {
        if (intent == null) return
        val fromAssistant = intent.action == SaphiraVoiceInteractionService.ACTION_ASSISTANT_INVOKED ||
                intent.getBooleanExtra("show_overlay", false)
        if (fromAssistant) {
            Log.i(TAG, "Assistant invoked")
            methodChannel?.invokeMethod("openOverlay", mapOf(
                "source" to (intent.getStringExtra("source") ?: "voice_interaction"),
                "show_overlay" to true
            ))
        }
    }

    companion object {
        private const val TAG = "SaphiraMain"
        const val CHANNEL = "com.saphira.ai/assistant"
    }
}
