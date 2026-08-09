package ai.saphira.mobile

import android.os.Bundle
import android.speech.RecognitionListener

class SimpleRecognitionListener(private val onResult: (String) -> Unit) : RecognitionListener {
    override fun onReadyForSpeech(params: Bundle?) = Unit
    override fun onBeginningOfSpeech() = Unit
    override fun onRmsChanged(rmsdB: Float) = Unit
    override fun onBufferReceived(buffer: ByteArray?) = Unit
    override fun onEndOfSpeech() = Unit
    override fun onError(error: Int) = Unit
    override fun onResults(results: Bundle?) {
        val text = results?.getStringArrayList(android.speech.SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()
        if (!text.isNullOrBlank()) onResult(text)
    }
    override fun onPartialResults(partialResults: Bundle?) = Unit
    override fun onEvent(eventType: Int, params: Bundle?) = Unit
}
