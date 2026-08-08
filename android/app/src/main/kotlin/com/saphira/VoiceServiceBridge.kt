// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Saphira Voice Interaction Service Bridge
// Handles Android native voice service with graceful error recovery

package com.saphira

import android.service.voice.VoiceInteractionService
import android.service.voice.VoiceInteractionSession
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.media.AudioManager
import android.content.Context

class SaphiraVoiceService : VoiceInteractionService() {
    companion object {
        private const val TAG = "SaphiraVoiceService"
    }

    private var audioManager: AudioManager? = null

    override fun onCreate() {
        super.onCreate()
        try {
            Log.d(TAG, "Voice service created")
            audioManager = getSystemService(Context.AUDIO_SERVICE) as? AudioManager
        } catch (e: Exception) {
            Log.e(TAG, "Error in onCreate: ${e.message}")
            // Continue gracefully - don't crash on init
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return try {
            Log.d(TAG, "Voice service onStartCommand")
            
            // Verify we have required permissions
            if (!hasVoicePermissions()) {
                Log.w(TAG, "Missing voice interaction permissions")
                return START_STICKY
            }
            
            // Safe initialization
            START_STICKY
        } catch (e: SecurityException) {
            Log.e(TAG, "SecurityException in onStartCommand: ${e.message}")
            // Fall back gracefully instead of crashing
            START_STICKY
        } catch (e: Exception) {
            Log.e(TAG, "Error in onStartCommand: ${e.message}")
            // Continue service even if command fails
            START_STICKY
        }
    }

    override fun onCreateSession(context: Context): VoiceInteractionSession? {
        return try {
            Log.d(TAG, "Creating voice interaction session")
            SaphiraVoiceSession(context, this)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to create session: ${e.message}")
            // Return null gracefully if session creation fails
            null
        }
    }

    override fun onShutdown() {
        try {
            Log.d(TAG, "Voice service shutting down")
            super.onShutdown()
        } catch (e: Exception) {
            Log.e(TAG, "Error during shutdown: ${e.message}")
            // Suppress exception during shutdown
        }
    }

    private fun hasVoicePermissions(): Boolean {
        return try {
            // Check for BIND_VOICE_INTERACTION permission
            val pm = packageManager
            val perm = android.Manifest.permission.BIND_VOICE_INTERACTION
            val result = pm.checkPermission(perm, packageName)
            result == android.content.pm.PackageManager.PERMISSION_GRANTED
        } catch (e: Exception) {
            Log.w(TAG, "Could not verify permissions: ${e.message}")
            false
        }
    }
}

class SaphiraVoiceSession(
    context: Context,
    service: SaphiraVoiceService
) : VoiceInteractionSession(context, service) {
    companion object {
        private const val TAG = "SaphiraVoiceSession"
    }

    private val audioFocusHelper = AudioFocusHelper(context)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            Log.d(TAG, "Voice session created")
            audioFocusHelper.requestAudioFocus()
        } catch (e: Exception) {
            Log.e(TAG, "Error in session onCreate: ${e.message}")
            // Don't crash - continue with degraded functionality
        }
    }

    override fun onResume() {
        super.onResume()
        try {
            Log.d(TAG, "Voice session resumed")
            audioFocusHelper.requestAudioFocus()
        } catch (e: Exception) {
            Log.e(TAG, "Error in onResume: ${e.message}")
        }
    }

    override fun onPause() {
        try {
            Log.d(TAG, "Voice session paused")
            audioFocusHelper.abandonAudioFocus()
        } catch (e: Exception) {
            Log.e(TAG, "Error in onPause: ${e.message}")
        }
        super.onPause()
    }

    override fun onDestroy() {
        try {
            Log.d(TAG, "Voice session destroyed")
            audioFocusHelper.abandonAudioFocus()
        } catch (e: Exception) {
            Log.e(TAG, "Error in onDestroy: ${e.message}")
        }
        super.onDestroy()
    }
}

class AudioFocusHelper(private val context: Context) {
    companion object {
        private const val TAG = "AudioFocusHelper"
    }

    private val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as? AudioManager
    private var hasAudioFocus = false

    fun requestAudioFocus(): Boolean {
        return try {
            if (audioManager == null) {
                Log.w(TAG, "AudioManager is null")
                return false
            }

            // Request audio focus with ducking (other audio reduces volume instead of stopping)
            val result = audioManager!!.requestAudioFocus(
                null,  // No listener needed
                AudioManager.STREAM_MUSIC,
                AudioManager.AUDIOFOCUS_GAIN_TRANSIENT
            )

            hasAudioFocus = (result == AudioManager.AUDIOFOCUS_REQUEST_GRANTED)
            Log.d(TAG, "Audio focus requested: ${if (hasAudioFocus) "granted" else "denied"}")
            hasAudioFocus
        } catch (e: Exception) {
            Log.e(TAG, "Error requesting audio focus: ${e.message}")
            false
        }
    }

    fun abandonAudioFocus(): Boolean {
        return try {
            if (audioManager == null || !hasAudioFocus) {
                return false
            }
            val result = audioManager!!.abandonAudioFocus(null)
            hasAudioFocus = false
            Log.d(TAG, "Audio focus abandoned")
            result == AudioManager.AUDIOFOCUS_REQUEST_GRANTED
        } catch (e: Exception) {
            Log.e(TAG, "Error abandoning audio focus: ${e.message}")
            false
        }
    }
}
