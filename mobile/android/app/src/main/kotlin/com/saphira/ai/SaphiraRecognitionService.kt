// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
package com.saphira.ai

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log

class SaphiraRecognitionService : Service() {
    override fun onBind(intent: Intent?): IBinder? = null
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.i(TAG, "Recognition service started (stub)")
        return START_STICKY
    }
    companion object { private const val TAG = "SaphiraRecog" }
}
