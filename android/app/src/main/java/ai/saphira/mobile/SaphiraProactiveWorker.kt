package ai.saphira.mobile

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import okhttp3.OkHttpClient
import okhttp3.Request

class SaphiraProactiveWorker(
    appContext: Context,
    params: WorkerParameters
) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        val url = BuildConfig.SAPHIRA_BASE_URL.trimEnd('/') + "/health"
        return runCatching {
            OkHttpClient().newCall(Request.Builder().url(url).get().build()).execute().use { response ->
                if (response.isSuccessful) Result.success() else Result.retry()
            }
        }.getOrElse { Result.retry() }
    }
}
