package ai.saphira.mobile

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import androidx.lifecycle.lifecycleScope
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import kotlinx.coroutines.launch
import java.util.Locale
import java.util.concurrent.TimeUnit

class MainActivity : ComponentActivity(), TextToSpeech.OnInitListener {
    private lateinit var tts: TextToSpeech
    private lateinit var api: SaphiraApi
    private var speechRecognizer: SpeechRecognizer? = null
    private var input by mutableStateOf("")
    private var response by mutableStateOf("Hi. I'm Saphira. What are we getting done?")

    private val requestAudio = registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) startListening()
    }
    private val requestNotifications = registerForActivityResult(ActivityResultContracts.RequestPermission()) { }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        tts = TextToSpeech(this, this)
        api = SaphiraApi(BuildConfig.SAPHIRA_BASE_URL)
        if (SpeechRecognizer.isRecognitionAvailable(this)) {
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this)
        }

        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestNotifications.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
            startService(Intent(this, SaphiraForegroundService::class.java))
        }
        scheduleProactiveHealthCheck()

        setContent {
            MaterialTheme {
                Column(
                    modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // Native placeholder orb keeps the APK build self-contained; branded assets can be added later.
                    Column(
                        modifier = Modifier.size(190.dp).clip(CircleShape).background(MaterialTheme.colorScheme.primary),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Text("S", style = MaterialTheme.typography.displayLarge, color = MaterialTheme.colorScheme.onPrimary)
                    }
                    Text("Saphira AI", style = MaterialTheme.typography.headlineLarge)
                    Text("Your conversational executive assistant", style = MaterialTheme.typography.bodyMedium)
                    Text(response, modifier = Modifier.fillMaxWidth())
                    OutlinedTextField(value = input, onValueChange = { input = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Talk to Saphira") })
                    Button(onClick = { sendToSaphira() }, modifier = Modifier.fillMaxWidth()) { Text("Ask Saphira") }
                    Button(onClick = {
                        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) startListening()
                        else requestAudio.launch(Manifest.permission.RECORD_AUDIO)
                    }, modifier = Modifier.fillMaxWidth()) { Text("🎙 Listen") }
                }
            }
        }
    }

    private fun scheduleProactiveHealthCheck() {
        val request = PeriodicWorkRequestBuilder<SaphiraProactiveWorker>(15, TimeUnit.MINUTES).build()
        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "saphira-proactive-runtime",
            ExistingPeriodicWorkPolicy.UPDATE,
            request
        )
    }

    private fun sendToSaphira() {
        val message = input.trim()
        if (message.isEmpty()) return
        response = "I'm working on it..."
        lifecycleScope.launch {
            api.sendMessage(message).onSuccess { answer ->
                response = answer
                speak(answer)
            }.onFailure { error ->
                response = "I couldn't reach my Saphira backend yet: ${error.message}"
            }
        }
    }

    private fun startListening() {
        val recognizer = speechRecognizer ?: return
        val intent = RecognizerIntent().apply {
            action = RecognizerIntent.ACTION_RECOGNIZE_SPEECH
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
        }
        recognizer.setRecognitionListener(SimpleRecognitionListener { text ->
            input = text
            sendToSaphira()
        })
        recognizer.startListening(intent)
    }

    private fun speak(text: String) {
        response = text
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "saphira-response")
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) tts.language = Locale.US
    }

    override fun onDestroy() {
        speechRecognizer?.destroy()
        tts.shutdown()
        super.onDestroy()
    }
}
