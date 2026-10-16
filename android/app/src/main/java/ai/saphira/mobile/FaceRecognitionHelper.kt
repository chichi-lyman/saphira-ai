package ai.saphira.mobile

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Rect
import android.util.Base64
import android.util.Log
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.face.Face
import com.google.mlkit.vision.face.FaceDetection
import com.google.mlkit.vision.face.FaceDetectorOptions
import kotlinx.coroutines.suspendCancellableCoroutine
import java.io.ByteArrayOutputStream
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/**
 * On-device face detection helper for Saphira.
 *
 * Uses Google ML Kit (runs fully on-device). Detection results and/or a
 * cropped face JPEG (base64) can be sent to the Saphira backend for
 * recognition / enrollment. Raw camera frames are never uploaded continuously.
 *
 * © 2026 Chelsea Megan Woods
 */
class FaceRecognitionHelper(private val context: Context) {

    private val detector by lazy {
        val options = FaceDetectorOptions.Builder()
            .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_ACCURATE)
            .setLandmarkMode(FaceDetectorOptions.LANDMARK_MODE_NONE)
            .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_NONE)
            .setMinFaceSize(0.15f)
            .enableTracking()
            .build()
        FaceDetection.getClient(options)
    }

    data class DetectedFace(
        val boundingBox: Rect,
        val trackingId: Int?,
        val headEulerAngleY: Float,
        val headEulerAngleZ: Float,
    )

    data class DetectionResult(
        val faces: List<DetectedFace>,
        val faceJpegBase64: String?, // first face crop, or null
    )

    /**
     * Detect faces in a Bitmap. Optionally returns a base64 JPEG of the largest face
     * so the client can call /api/face/perceive or /api/face/enroll.
     */
    suspend fun detect(bitmap: Bitmap, includeCropBase64: Boolean = true): DetectionResult {
        val image = InputImage.fromBitmap(bitmap, 0)
        val faces = suspendCancellableCoroutine<List<Face>> { cont ->
            detector.process(image)
                .addOnSuccessListener { cont.resume(it) }
                .addOnFailureListener { cont.resumeWithException(it) }
        }

        val mapped = faces.map { f ->
            DetectedFace(
                boundingBox = f.boundingBox,
                trackingId = f.trackingId,
                headEulerAngleY = f.headEulerAngleY,
                headEulerAngleZ = f.headEulerAngleZ,
            )
        }

        val cropB64 = if (includeCropBase64 && faces.isNotEmpty()) {
            val largest = faces.maxByOrNull { it.boundingBox.width() * it.boundingBox.height() }!!
            cropFaceToBase64(bitmap, largest.boundingBox)
        } else null

        return DetectionResult(faces = mapped, faceJpegBase64 = cropB64)
    }

    private fun cropFaceToBase64(source: Bitmap, box: Rect): String? {
        return try {
            val left = box.left.coerceIn(0, source.width - 1)
            val top = box.top.coerceIn(0, source.height - 1)
            val width = box.width().coerceAtMost(source.width - left)
            val height = box.height().coerceAtMost(source.height - top)
            if (width <= 0 || height <= 0) return null
            val crop = Bitmap.createBitmap(source, left, top, width, height)
            val stream = ByteArrayOutputStream()
            crop.compress(Bitmap.CompressFormat.JPEG, 90, stream)
            Base64.encodeToString(stream.toByteArray(), Base64.NO_WRAP)
        } catch (e: Exception) {
            Log.w(TAG, "Failed to crop face", e)
            null
        }
    }

    fun close() {
        detector.close()
    }

    companion object {
        private const val TAG = "SaphiraFace"
    }
}
