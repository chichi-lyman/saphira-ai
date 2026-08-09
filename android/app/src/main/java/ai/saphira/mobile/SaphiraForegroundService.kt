package ai.saphira.mobile

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.IBinder
import androidx.core.app.NotificationCompat

class SaphiraForegroundService : Service() {
    companion object {
        const val CHANNEL_ID = "saphira_assistant"
        const val NOTIFICATION_ID = 4101
    }

    override fun onCreate() {
        super.onCreate()
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(
            NotificationChannel(CHANNEL_ID, "Saphira Assistant", NotificationManager.IMPORTANCE_LOW)
        )
        startForeground(NOTIFICATION_ID, notification())
    }

    private fun notification(): Notification = NotificationCompat.Builder(this, CHANNEL_ID)
        .setContentTitle("Saphira is ready")
        .setContentText("Voice assistant service is active")
        .setSmallIcon(android.R.drawable.ic_btn_speak_now)
        .setOngoing(true)
        .build()

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
