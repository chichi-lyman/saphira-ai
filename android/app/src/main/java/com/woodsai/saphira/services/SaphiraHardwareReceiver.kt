// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// System broadcast receiver that pauses microphone capture during
// telephony events and Bluetooth profile changes to protect privacy
// and avoid resource conflicts. Works with the existing Android
// VoiceInteractionService scaffolding.

package com.woodsai.saphira.services

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.media.AudioManager
import android.telephony.TelephonyManager
import android.util.Log

class SaphiraHardwareReceiver : BroadcastReceiver() {

    companion object {
        private const val TAG = "SaphiraHardwareReceiver"
        const val ACTION_MUTE_MIC = "com.woodsai.saphira.MUTE_MIC"
        const val ACTION_UNMUTE_MIC = "com.woodsai.saphira.UNMUTE_MIC"
        const val EXTRA_REASON = "reason"
    }

    override fun onReceive(context: Context, intent: Intent?) {
        if (intent == null) return

        when (intent.action) {
            TelephonyManager.ACTION_PHONE_STATE_CHANGED -> {
                val state = intent.getStringExtra(TelephonyManager.EXTRA_STATE)
                when (state) {
                    TelephonyManager.EXTRA_STATE_RINGING,
                    TelephonyManager.EXTRA_STATE_OFFHOOK -> {
                        Log.i(TAG, "Telephony active – muting Saphira mic capture")
                        sendMute(context, "telephony")
                    }
                    TelephonyManager.EXTRA_STATE_IDLE -> {
                        Log.i(TAG, "Telephony idle – restoring Saphira mic capture")
                        sendUnmute(context, "telephony")
                    }
                }
            }

            AudioManager.ACTION_SCO_AUDIO_STATE_UPDATED,
            Intent.ACTION_HEADSET_PLUG,
            "android.bluetooth.headset.profile.action.CONNECTION_STATE_CHANGED",
            "android.bluetooth.a2dp.profile.action.CONNECTION_STATE_CHANGED" -> {
                Log.d(TAG, "Bluetooth / headset state change detected")
                sendMute(context, "bluetooth_transition")
                // Main service may schedule a short delayed unmute after
                // AudioManager reports the new preferred device.
            }
        }
    }

    private fun sendMute(context: Context, reason: String) {
        val i = Intent(ACTION_MUTE_MIC).apply {
            setPackage(context.packageName)
            putExtra(EXTRA_REASON, reason)
        }
        context.sendBroadcast(i)
    }

    private fun sendUnmute(context: Context, reason: String) {
        val i = Intent(ACTION_UNMUTE_MIC).apply {
            setPackage(context.packageName)
            putExtra(EXTRA_REASON, reason)
        }
        context.sendBroadcast(i)
    }
}
