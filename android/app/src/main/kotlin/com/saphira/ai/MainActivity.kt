package com.saphira.ai

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.net.Uri
import android.os.Build
import android.provider.Settings
import android.util.Log
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.EventChannel
import io.flutter.plugin.common.MethodChannel

/**
 * Flutter host activity.
 * Channels:
 *   com.saphira.ai/background_service  – FG service start/stop + overlay permission
 *   com.saphira.ai/overlay_hud         – floating HUD visibility + SYSTEM_ALERT_WINDOW
 *   com.saphira.ai/accessibility        – A11y authorize/click/inject/tap
 *   com.saphira.ai/assistant            – voice-interaction overlay trigger
 *   com.saphira.ai/wakeword_events      – on-device wake-word EventChannel stream
 *
 * © 2026 Chelsea Megan Woods / Woods AI Studio / Nova Umbrella
 */
class MainActivity : FlutterActivity() {

    private val BACKGROUND_CHANNEL = "com.saphira.ai/background_service"
    private val OVERLAY_CHANNEL = "com.saphira.ai/overlay_hud"
    private val A11Y_CHANNEL = "com.saphira.ai/accessibility"
    private val ASSISTANT_CHANNEL = "com.saphira.ai/assistant"
    private val WAKEWORD_EVENT_CHANNEL = "com.saphira.ai/wakeword_events"

    private var assistantChannel: MethodChannel? = null
    private var wakeWordReceiver: BroadcastReceiver? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        // ── Background service + overlay permission ─────────────────────────
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, BACKGROUND_CHANNEL)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "startService" -> {
                        SaphiraForegroundService.start(this)
                        result.success(true)
                    }
                    "stopService" -> {
                        SaphiraForegroundService.stop(this)
                        result.success(true)
                    }
                    "isServiceRunning" -> {
                        result.success(true)
                    }
                    "requestOverlayPermission" -> {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M &&
                            !Settings.canDrawOverlays(this)
                        ) {
                            val intent = Intent(
                                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                                Uri.parse("package:$packageName")
                            )
                            startActivity(intent)
                            result.success(false)
                        } else {
                            result.success(true)
                        }
                    }
                    "canDrawOverlays" -> {
                        val ok = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                            Settings.canDrawOverlays(this)
                        } else {
                            true
                        }
                        result.success(ok)
                    }
                    else -> result.notImplemented()
                }
            }

        // ── Floating HUD overlay (SYSTEM_ALERT_WINDOW) ──────────────────────
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, OVERLAY_CHANNEL)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "checkOverlayPermission" -> {
                        val hasPermission = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                            Settings.canDrawOverlays(this)
                        } else {
                            true
                        }
                        result.success(hasPermission)
                    }
                    "requestOverlayPermission" -> {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M &&
                            !Settings.canDrawOverlays(this)
                        ) {
                            val intent = Intent(
                                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                                Uri.parse("package:$packageName")
                            )
                            startActivity(intent)
                            result.success(false)
                        } else {
                            result.success(true)
                        }
                    }
                    "toggleHUDVisibility" -> {
                        val visible = call.argument<Boolean>("visible") ?: false
                        val intent = Intent(this, SaphiraForegroundService::class.java).apply {
                            action = if (visible) {
                                SaphiraForegroundService.ACTION_SHOW_HUD
                            } else {
                                SaphiraForegroundService.ACTION_HIDE_HUD
                            }
                        }
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                            startForegroundService(intent)
                        } else {
                            @Suppress("DEPRECATION")
                            startService(intent)
                        }
                        result.success(true)
                    }
                    else -> result.notImplemented()
                }
            }

        // ── Accessibility bridge ────────────────────────────────────────────
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, A11Y_CHANNEL)
            .setMethodCallHandler { call, result ->
                val svc = SaphiraAccessibilityService.instance
                if (svc == null && call.method != "isAvailable") {
                    result.error("UNAVAILABLE", "Accessibility service not enabled", null)
                    return@setMethodCallHandler
                }
                try {
                    when (call.method) {
                        "isAvailable" -> result.success(svc != null)
                        "authorize" -> {
                            val token = call.argument<String>("token") ?: ""
                            val ttl = call.argument<Number>("ttlMs")?.toLong() ?: 30_000L
                            result.success(svc!!.authorize(token, ttl))
                        }
                        "revokeAuth" -> {
                            svc!!.revokeAuth()
                            result.success(null)
                        }
                        "clickElementByText" -> {
                            val text = call.argument<String>("text") ?: ""
                            result.success(svc!!.clickElementByText(text))
                        }
                        "injectText" -> {
                            val text = call.argument<String>("text") ?: ""
                            result.success(svc!!.injectTextIntoFocusedInput(text))
                        }
                        "tapAt" -> {
                            val x = call.argument<Double>("x")?.toFloat() ?: 0f
                            val y = call.argument<Double>("y")?.toFloat() ?: 0f
                            result.success(svc!!.performTapAtCoordinates(x, y))
                        }
                        "globalAction" -> {
                            val name = call.argument<String>("name") ?: ""
                            result.success(svc!!.globalAction(name))
                        }
                        else -> result.notImplemented()
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "A11y ${call.method} failed", e)
                    result.error("ERROR", e.message, null)
                }
            }

        // ── Assistant overlay trigger ───────────────────────────────────────
        assistantChannel = MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            ASSISTANT_CHANNEL
        )
        handleAssistantIntent(intent)

        // ── EventChannel for local wake-word trigger broadcasts ─────────────
        EventChannel(flutterEngine.dartExecutor.binaryMessenger, WAKEWORD_EVENT_CHANNEL)
            .setStreamHandler(
                object : EventChannel.StreamHandler {
                    override fun onListen(arguments: Any?, events: EventChannel.EventSink?) {
                        wakeWordReceiver = object : BroadcastReceiver() {
                            override fun onReceive(context: Context?, intent: Intent?) {
                                if (intent?.action == "com.saphira.ai.WAKEWORD_TRIGGERED") {
                                    val confidence = intent.getFloatExtra("confidence", 0.0f)
                                    val payload = mapOf("confidence" to confidence.toDouble())
                                    events?.success(payload)
                                }
                            }
                        }

                        val filter = IntentFilter("com.saphira.ai.WAKEWORD_TRIGGERED")
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                            registerReceiver(
                                wakeWordReceiver,
                                filter,
                                Context.RECEIVER_NOT_EXPORTED
                            )
                        } else {
                            @Suppress("UnspecifiedRegisterReceiverFlag")
                            registerReceiver(wakeWordReceiver, filter)
                        }
                        Log.i(TAG, "Wake-word EventChannel listener registered")
                    }

                    override fun onCancel(arguments: Any?) {
                        wakeWordReceiver?.let {
                            try {
                                unregisterReceiver(it)
                            } catch (_: Exception) {
                            }
                            wakeWordReceiver = null
                        }
                        Log.i(TAG, "Wake-word EventChannel listener cancelled")
                    }
                }
            )
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleAssistantIntent(intent)
    }

    override fun onDestroy() {
        wakeWordReceiver?.let {
            try {
                unregisterReceiver(it)
            } catch (_: Exception) {
            }
            wakeWordReceiver = null
        }
        super.onDestroy()
    }

    private fun handleAssistantIntent(intent: Intent?) {
        if (intent == null) return
        val fromAssistant =
            intent.action == SaphiraVoiceInteractionService.ACTION_ASSISTANT_INVOKED ||
                intent.getBooleanExtra("show_overlay", false)
        if (fromAssistant) {
            Log.i(TAG, "Assistant invoked — requesting Flutter overlay")
            assistantChannel?.invokeMethod(
                "openOverlay",
                mapOf(
                    "source" to (intent.getStringExtra("source") ?: "voice_interaction"),
                    "show_overlay" to true
                )
            )
        }
    }

    companion object {
        private const val TAG = "SaphiraMain"
    }
}
