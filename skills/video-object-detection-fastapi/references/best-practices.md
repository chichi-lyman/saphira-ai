# Best Practices for Camera Object Detection with FastAPI

## Model Selection
- Prefer YOLOv8n / YOLOv11n (ultralytics) for speed and accuracy balance on CPU or modest GPUs.
- OpenCV DNN is suitable for classic models (MobileNet-SSD, YOLO-Darknet) when dependency size must be minimal.
- Always cache the loaded model at application startup rather than reloading per request.

## Performance
- Capture at the lowest resolution that still meets accuracy needs.
- Skip frames or process every Nth frame for continuous streams.
- Use `cv2.CAP_PROP_BUFFERSIZE = 1` to reduce latency.
- For multi-client scenarios move inference to a background worker or dedicated inference service.

## Resource Management
- Always release `cv2.VideoCapture` in a finally block or context manager.
- Never leave camera handles open across requests in a multi-worker deployment.
- Prefer a single shared capture process that publishes frames via a queue or Redis when multiple endpoints need the same stream.

## API Design
- Single-frame endpoints (`POST /detect`) are simplest and safest for most use cases.
- Continuous output: implement WebSocket (`/ws/detect`) or Server-Sent Events.
- Return both a human-readable `text_summary` and structured `detections` list so clients can choose the format they need.
- Validate camera index and confidence threshold with Pydantic.

## Security and Deployment
- Do not expose raw camera indices to untrusted clients without authentication.
- Run the service behind a reverse proxy; bind only to localhost if possible.
- Package with Docker; pin library versions in requirements.txt.
- Consider GPU acceleration (CUDA) only when the deployment environment guarantees it.

## Common Failure Modes
- Camera already in use by another process → return 503 with clear message.
- Model file missing → fail fast at startup with a descriptive log.
- Empty frames after capture → treat as transient error and retry once.
- Low-confidence detections → filter before formatting text so the summary stays clean.
