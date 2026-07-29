// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Speech recognition service stub required by voice_interaction_service.xml.
// Production: forward audio to Flutter STT / Gemini Live / on-device model.

package com.saphira.ai

import android.content.Intent
import android.os.Bundle
import android.os.RemoteException
import android.speech.RecognitionService
import android.util.Log

class SaphiraRecognitionService : RecognitionService() {

    override fun onStartListening(recognizerIntent: Intent, listener: Callback) {
        Log.i(TAG, "onStartListening")
        try {
            listener.ready(recognizerIntent)
            // TODO: stream mic → STT; then listener.results(Bundle)
            // For now signal end so session can rely on Flutter overlay mic
            val empty = Bundle()
            listener.results(empty)
        } catch (e: RemoteException) {
            Log.e(TAG, "Recognition callback failed", e)
        }
    }

    override fun onCancel(listener: Callback) {
        Log.i(TAG, "onCancel")
        try {
            listener.endOfSpeech()
        } catch (_: RemoteException) {
        }
    }

    override fun onStopListening(listener: Callback) {
        Log.i(TAG, "onStopListening")
        try {
            listener.endOfSpeech()
        } catch (_: RemoteException) {
        }
    }

    companion object {
        private const val TAG = "SaphiraRecognition"
    }
}
