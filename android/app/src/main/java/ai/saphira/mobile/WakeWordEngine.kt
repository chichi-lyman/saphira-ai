package ai.saphira.mobile

import android.content.Context
import java.io.File

/**
 * Edge wake-word boundary. A packaged ONNX model can be loaded locally without
 * sending microphone audio to the cloud. The model itself is intentionally not
 * committed: wake-word models are replaceable assets and should be licensed and
 * supplied separately.
 */
class WakeWordEngine(private val context: Context) {
    data class Config(
        val phrases: Set<String> = setOf("hey saphira", "okay saphira"),
        val threshold: Float = 0.5f,
        val modelAsset: String = "wakeword/saphira.onnx"
    )

    private var running = false
    private var config = Config()

    fun configure(value: Config) { config = value }

    fun start(onWake: () -> Unit) {
        running = true
        // ONNX inference is intentionally behind this adapter. When the licensed
        // model is packaged at assets/wakeword/saphira.onnx, connect its model-
        // specific tensor preprocessing/postprocessing here. No cloud call occurs.
        val modelExists = runCatching {
            context.assets.open(config.modelAsset).use { true }
        }.getOrDefault(false)
        if (!modelExists) {
            // Fail closed: do not pretend a wake-word model is active.
            running = false
        }
    }

    fun stop() { running = false }

    fun isRunning(): Boolean = running
}
