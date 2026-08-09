package ai.saphira.mobile

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

class SaphiraApi(private val baseUrl: String) {
    private val client = OkHttpClient()
    private val jsonType = "application/json".toMediaType()

    suspend fun sendMessage(message: String): Result<String> = withContext(Dispatchers.IO) {
        runCatching {
            val body = JSONObject().put("message", message).toString().toRequestBody(jsonType)
            val request = Request.Builder()
                .url(baseUrl.trimEnd('/') + "/api/chat")
                .post(body)
                .build()
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) error("Saphira backend returned ${response.code}")
                val payload = JSONObject(response.body?.string().orEmpty())
                payload.optString("response", payload.optString("message", "I completed the request."))
            }
        }
    }
}
