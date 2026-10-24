package com.saphira.ai

import android.annotation.SuppressLint
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import kotlin.concurrent.thread

/**
 * Persistent foreground service that keeps Saphira's WebSocket connection
 * and on-device wake-word listener alive when the app is backgrounded or
 * the screen is off.
 *
 * Start from Flutter via MethodChannel or from MainActivity on launch:
 *   SaphiraForegroundService.start(context)
 *
 * HUD visibility is toggled via ACTION_SHOW_HUD / ACTION_HIDE_HUD and
 * broadcast on ACTION_HUD_STATE for overlay hosts.
 *
 * © 2026 Chelsea Megan Woods / Woods AI Studio / Nova Umbrella
 */
class SaphiraForegroundService : Service() {

    companion object {
        private const val TAG = "SaphiraFG"
        private const val CHANNEL_ID = "SaphiraBackgroundEngine"
        private const val NOTIFICATION_ID = 8801
        private const val WAKE_THRESHOLD = 0.75f

        const val ACTION_SHOW_HUD = "com.saphira.ai.ACTION_SHOW_HUD"
        const val ACTION_HIDE_HUD = "com.saphira.ai.ACTION_HIDE_HUD"
        const val ACTION_HUD_STATE = "com.saphira.ai.HUD_STATE_CHANGED"

        fun start(context: Context) {
            val intent = Intent(context, SaphiraForegroundService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                @Suppress("DEPRECATION")
                context.startService(intent)
            }
            Log.i(TAG, "start() requested")
        }

        fun stop(context: Context) {
            val intent = Intent(context, SaphiraForegroundService::class.java)
            context.stopService(intent)
            Log.i(TAG, "stop() requested")
        }
    }

    private var audioRecord: AudioRecord? = null
    private var isRecordLoopRunning = false
    private lateinit var wakeWordEngine: SaphiraWakeWordEngine
    @Volatile private var hudVisible: Boolean = false

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        wakeWordEngine = SaphiraWakeWordEngine(this)
        wakeWordEngine.initialize("saphira_wakeword.onnx")
        Log.i(TAG, "onCreate")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification: Notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Saphira AI Active")
            .setContentText("Listening for wake word and monitoring system policy...")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .build()

        startForeground(NOTIFICATION_ID, notification)
        Log.i(TAG, "Foreground started (START_STICKY)")

        when (intent?.action) {
            ACTION_SHOW_HUD -> setHudVisible(true)
            ACTION_HIDE_HUD -> setHudVisible(false)
        }
        startLocalWakeWordListener()
        return START_STICKY
    }

    private fun setHudVisible(visible: Boolean) {
        hudVisible = visible
        Log.i(TAG, "HUD visibility -> $visible")
        val broadcast = Intent(ACTION_HUD_STATE).apply {
            putExtra("visible", visible)
            setPackage(packageName)
        }
        sendBroadcast(broadcast)
    }

    @SuppressLint("MissingPermission")
    private fun startLocalWakeWordListener() {
        if (isRecordLoopRunning) return

        val sampleRate = 16000
        val bufferSize = 1280 * 2

        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            sampleRate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            bufferSize
        )

        audioRecord?.startRecording()
        isRecordLoopRunning = true

        thread(start = true) {
            val audioBuffer = ShortArray(1280)
            while (isRecordLoopRunning) {
                val readCount = audioRecord?.read(audioBuffer, 0, audioBuffer.size) ?: 0
                if (readCount == 1280) {
                    val confidence = wakeWordEngine.processAudioFrame(audioBuffer)
                    if (confidence > WAKE_THRESHOLD) {
                        notifyWakeWordTriggered(confidence)
                    }
                }
            }
        }
        Log.i(TAG, "Local wake-word listener started (16 kHz / 80 ms frames)")
    }

    private fun notifyWakeWordTriggered(confidence: Float) {
        Log.i(TAG, "Wake word triggered confidence=$confidence")
        val intent = Intent("com.saphira.ai.WAKEWORD_TRIGGERED").apply {
            putExtra("confidence", confidence)
            setPackage(packageName)
        }
        sendBroadcast(intent)
    }

    override fun onDestroy() {
        isRecordLoopRunning = false
        try {
            audioRecord?.stop()
            audioRecord?.release()
        } catch (_: Exception) {
        }
        audioRecord = null
        Log.i(TAG, "onDestroy")
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Saphira Background Engine",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Keeps Saphira wake-word and policy monitoring alive"
                setShowBadge(false)
            }
            val nm = getSystemService(NotificationManager::class.java)
            nm.createNotificationChannel(channel)
        }
    }
}
