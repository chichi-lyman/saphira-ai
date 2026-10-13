"""
Example template for camera-based object detection integrated with FastAPI.
Adapt model loading, confidence thresholds, and output format as needed.
"""

from typing import List, Dict, Any, Optional
import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Optional: replace with ultralytics YOLO for modern detection
# from ultralytics import YOLO

app = FastAPI(title="Camera Object Detection API")

class Detection(BaseModel):
    label: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]


class DetectionResponse(BaseModel):
    text_summary: str
    detections: List[Detection]
    frame_shape: Optional[List[int]] = None


def load_detector():
    """
    Load OpenCV DNN or YOLO model.
    Replace paths and backend with your preferred model.
    """
    # Example using OpenCV DNN (MobileNet-SSD or similar)
    # net = cv2.dnn.readNetFromCaffe("deploy.prototxt", "model.caffemodel")
    # return net

    # Preferred modern approach (uncomment and install ultralytics):
    # model = YOLO("yolov8n.pt")
    # return model

    raise NotImplementedError("Configure model loading here")


def decode_detections(raw_output: Any, confidence_threshold: float = 0.5) -> List[Detection]:
    """
    Convert model-specific output into a list of Detection objects.
    Implement according to the chosen model format.
    """
    detections: List[Detection] = []
    # Example skeleton for YOLO-style results:
    # for box in raw_output.boxes:
    #     conf = float(box.conf)
    #     if conf < confidence_threshold:
    #         continue
    #     cls_id = int(box.cls)
    #     label = raw_output.names[cls_id]
    #     xyxy = box.xyxy[0].tolist()
    #     detections.append(Detection(label=label, confidence=conf, bbox=xyxy))
    return detections


def format_detections_as_text(detections: List[Detection]) -> str:
    """Produce a concise human-readable summary suitable for logging or API clients."""
    if not detections:
        return "No objects detected."
    parts = [f"{d.label} ({d.confidence:.2f})" for d in detections]
    return f"Detected {len(detections)} object(s): " + ", ".join(parts)


def process_frame(frame: np.ndarray, model: Any, confidence_threshold: float = 0.5) -> DetectionResponse:
    """
    Core processing function.
    Accepts a BGR frame, runs detection, returns structured response.
    """
    if frame is None or frame.size == 0:
        raise ValueError("Empty or invalid frame")

    # Run inference (adapt to model API)
    # raw = model(frame)  # YOLO example
    # detections = decode_detections(raw, confidence_threshold)

    detections = []  # placeholder
    text_summary = format_detections_as_text(detections)

    return DetectionResponse(
        text_summary=text_summary,
        detections=detections,
        frame_shape=list(frame.shape[:2]),
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect", response_model=DetectionResponse)
def detect_from_camera(camera_index: int = 0, confidence: float = 0.5):
    """
    Capture a single frame from the specified camera and run object detection.
    For continuous streams prefer WebSocket or StreamingResponse endpoints.
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise HTTPException(status_code=503, detail=f"Cannot open camera {camera_index}")

    try:
        ret, frame = cap.read()
        if not ret:
            raise HTTPException(status_code=500, detail="Failed to capture frame")

        model = load_detector()  # Consider caching the model at app startup
        result = process_frame(frame, model, confidence_threshold=confidence)
        return result
    finally:
        cap.release()


if __name__ == "__main__":
    # Development only. Use a proper ASGI server in production.
    uvicorn.run(app, host="0.0.0.0", port=8000)
