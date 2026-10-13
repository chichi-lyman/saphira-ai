package com.saphira.ai

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat

/**
 * Persistent foreground service that keeps Saphira's WebSocket connection
 * and voice listener alive when the app is backgrounded or the screen is off.
 *
 * Start from Flutter via MethodChannel or from MainActivity on launch:
 *   SaphiraForegroundService.start(context)
 *
 * © 2026 Chelsea Megan Woods / Woods AI Studio / Nova Umbrella
 */
class SaphiraForegroundService : Service() {

    companion object {
        private const val TAG = "SaphiraFG"
        private const val CHANNEL_ID = "SaphiraBackgroundEngine"
        private const val NOTIFICATION_ID = 8801

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

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
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
        // Future: open/maintain WebSocket, start wake-word engine here.
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        Log.i(TAG, "onDestroy")
        super.onDestroy()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Saphira Agent Service",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Keeps Saphira voice and tool engine running in the background"
                setShowBadge(false)
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager?.createNotificationChannel(channel)
        }
    }
}
