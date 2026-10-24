package com.saphira.ai

import android.content.Context
import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import java.nio.ShortBuffer
import java.util.Collections

/**
 * On-device openwakeword inference via ONNX Runtime.
 * Operates on 16 kHz PCM audio chunks (1280 samples = 80 ms).
 *
 * © 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
 */
class SaphiraWakeWordEngine(private val context: Context) {

    private var ortEnv: OrtEnvironment? = null
    private var session: OrtSession? = null

    // openwakeword operates on 16kHz PCM audio chunks (1280 samples = 80ms)
    private val chunkSize = 1280

    fun initialize(modelAssetName: String = "saphira_wakeword.onnx") {
        try {
            ortEnv = OrtEnvironment.getEnvironment()
            val modelBytes = context.assets.open(modelAssetName).readBytes()
            session = ortEnv?.createSession(modelBytes, OrtSession.SessionOptions())
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    /**
     * Processes raw 16kHz PCM audio frame and returns confidence score [0.0 - 1.0]
     */
    fun processAudioFrame(pcmAudioFrame: ShortArray): Float {
        val currentSession = session ?: return 0.0f
        val currentEnv = ortEnv ?: return 0.0f

        if (pcmAudioFrame.size != chunkSize) return 0.0f

        val shape = longArrayOf(1, chunkSize.toLong())
        val buffer = ShortBuffer.wrap(pcmAudioFrame)

        val inputTensor = OnnxTensor.createTensor(currentEnv, buffer, shape)
        val inputs = Collections.singletonMap("input", inputTensor)

        val results = currentSession.run(inputs)
        val outputTensor = results[0].value as Array<FloatArray>

        inputTensor.close()
        results.close()

        return outputTensor[0][0]
    }

    fun close() {
        session?.close()
        ortEnv?.close()
    }
}
