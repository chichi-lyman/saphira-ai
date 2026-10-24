package ai.saphira.mobile

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
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

    // ------------------------------------------------------------------
    // Face recognition endpoints
    // ------------------------------------------------------------------

    /** Ask Saphira who is in this face crop (base64 JPEG). */
    suspend fun perceiveFace(imageB64: String): Result<JSONObject> = withContext(Dispatchers.IO) {
        runCatching {
            val body = JSONObject()
                .put("image_b64", imageB64)
                .put("return_embeddings", false)
                .toString()
                .toRequestBody(jsonType)
            val request = Request.Builder()
                .url(baseUrl.trimEnd('/') + "/api/face/perceive")
                .post(body)
                .build()
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) error("Face perceive failed: ${response.code}")
                JSONObject(response.body?.string().orEmpty())
            }
        }
    }

    /** Request a one-time consent token after the user says "yes, remember this face". */
    suspend fun requestConsentToken(): Result<String> = withContext(Dispatchers.IO) {
        runCatching {
            val request = Request.Builder()
                .url(baseUrl.trimEnd('/') + "/api/face/consent-token")
                .post("{}".toRequestBody(jsonType))
                .build()
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) error("Consent token failed: ${response.code}")
                JSONObject(response.body?.string().orEmpty()).getString("consent_token")
            }
        }
    }

    /** Enroll a face after explicit user consent. */
    suspend fun enrollFace(
        imageB64: String,
        label: String,
        consentToken: String,
    ): Result<JSONObject> = withContext(Dispatchers.IO) {
        runCatching {
            val body = JSONObject()
                .put("image_b64", imageB64)
                .put("label", label)
                .put("consent_token", consentToken)
                .toString()
                .toRequestBody(jsonType)
            val request = Request.Builder()
                .url(baseUrl.trimEnd('/') + "/api/face/enroll")
                .post(body)
                .build()
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) error("Face enroll failed: ${response.code}")
                JSONObject(response.body?.string().orEmpty())
            }
        }
    }

    /** List remembered face labels (no embeddings). */
    suspend fun listFaces(): Result<List<String>> = withContext(Dispatchers.IO) {
        runCatching {
            val request = Request.Builder()
                .url(baseUrl.trimEnd('/') + "/api/face/list")
                .get()
                .build()
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) error("List faces failed: ${response.code}")
                val root = JSONObject(response.body?.string().orEmpty())
                val arr = root.optJSONArray("faces") ?: JSONArray()
                (0 until arr.length()).map { arr.getJSONObject(it).getString("label") }
            }
        }
    }
}
