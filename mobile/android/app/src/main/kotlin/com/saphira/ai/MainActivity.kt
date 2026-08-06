// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
package com.saphira.ai

import android.app.Activity
import android.content.Intent
import android.util.Log
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {

    private var methodChannel: MethodChannel? = null
    private var pendingRoleResult: MethodChannel.Result? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        methodChannel = MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger, CHANNEL
        ).also { channel ->
            channel.setMethodCallHandler { call, result ->
                when (call.method) {
                    "startListening" -> result.success(true)
                    "stopListening" -> result.success(true)
                    "overlayReady" -> result.success(null)
                    "endSession" -> result.success(null)
                    "getAssistantRoleStatus" -> result.success(SaphiraRoleHelper.statusMap(this))
                    "isAssistantRoleHeld" -> result.success(SaphiraRoleHelper.isAssistantRoleHeld(this))
                    "requestAssistantRole" -> requestAssistantRole(result)
                    "openAssistantSettings" -> {
                        SaphiraRoleHelper.openVoiceInputSettings(this)
                        result.success(true)
                    }
                    else -> result.notImplemented()
                }
            }
        }

        handleAssistantIntent(intent)

        MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            SaphiraActionHandler.CHANNEL
        ).setMethodCallHandler(SaphiraActionHandler(this))
    }

    private fun requestAssistantRole(result: MethodChannel.Result) {
        if (SaphiraRoleHelper.isAssistantRoleHeld(this)) {
            result.success(mapOf("held" to true, "requested" to false))
            return
        }
        val intent = SaphiraRoleHelper.createRequestRoleIntent(this)
        if (intent == null) {
            SaphiraRoleHelper.openVoiceInputSettings(this)
            result.success(mapOf("held" to false, "requested" to false, "openedSettings" to true))
            return
        }
        pendingRoleResult = result
        try {
            @Suppress("DEPRECATION")
            startActivityForResult(intent, REQUEST_ASSISTANT_ROLE)
        } catch (e: Exception) {
            pendingRoleResult = null
            SaphiraRoleHelper.openVoiceInputSettings(this)
            result.success(mapOf("held" to false, "requested" to false, "openedSettings" to true, "error" to e.message))
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_ASSISTANT_ROLE) {
            val held = SaphiraRoleHelper.isAssistantRoleHeld(this)
            pendingRoleResult?.success(mapOf(
                "held" to held,
                "requested" to true,
                "resultOk" to (resultCode == Activity.RESULT_OK)
            ))
            pendingRoleResult = null
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleAssistantIntent(intent)
    }

    private fun handleAssistantIntent(intent: Intent?) {
        if (intent == null) return
        val fromAssistant =
            intent.action == SaphiraVoiceInteractionService.ACTION_ASSISTANT_INVOKED ||
                intent.action == Intent.ACTION_ASSIST ||
                intent.getBooleanExtra("show_overlay", false)
        if (fromAssistant) {
            val source = intent.getStringExtra("source")
                ?: if (intent.action == Intent.ACTION_ASSIST) "action_assist" else "voice_interaction"
            methodChannel?.invokeMethod("openOverlay", mapOf("source" to source, "show_overlay" to true))
        }
    }

    companion object {
        private const val TAG = "SaphiraMain"
        const val CHANNEL = "com.saphira.ai/assistant"
        private const val REQUEST_ASSISTANT_ROLE = 9101
    }
}
