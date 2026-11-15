"""
Trafficdetection.py
================================================================================
A complete traffic-object detection system in Python.

Built on Ultralytics YOLOv8 (a pre-trained COCO checkpoint) and OpenCV, this
program detects everything relevant to a traffic scene and works on three
kinds of input:

    * a single image  (e.g. a traffic-camera snapshot)
    * a video file    (e.g. CCTV / dashcam footage)
    * a live webcam / USB camera stream (index-based)

Detectable traffic classes (subset of the COCO-80 label set used by YOLO):
    Vehicles : car, truck, bus, motorcycle, bicycle
    People   : person                (pedestrians, cyclists, riders)
    Signals  : traffic light, stop sign

Features
--------
* Colour-coded, softly glowing bounding boxes with rounded corners
* Class label + confidence rendered on a modern label chip
* Live glass-style HUD dashboard (per-category counters, FPS meter)
  overlaid on the feed
* Optional CSV export of every single detection (frame, class, conf, box)
* Annotated image / video saving
* Pre-trained YOLO weights are downloaded automatically on first run
* Confidence threshold and IoU (NMS) threshold configurable from the CLI
* Runs on CPU or GPU (CUDA/MPS auto-detected, override with --device)

Quick start
-----------
1) Install the dependencies:

       python -m pip install ultralytics opencv-python numpy

2) Run it:

       python Trafficdetection.py --source street.jpg --save     # image
       python Trafficdetection.py --source traffic.mp4 --save    # video
       python Trafficdetection.py --source 0                     # webcam

Useful options
--------------
       --conf 0.5      raise the confidence threshold (fewer, surer boxes)
       --model yolov8s.pt   use a bigger / more accurate model
       --csv detlog.csv     log every detection to CSV
       --no-show            disable the preview window (headless mode)

Author : traffic-vision demo
--------------------------------------------------------------------------------
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import cv2
import numpy as np

try:  # optional import so that the CLI help still works without the package
    from ultralytics import YOLO
except ImportError:  # pragma: no cover - simple guard for first-time users
    print(
        "\n[ERROR] The 'ultralytics' package is required.\n"
        "        Install everything with:\n"
        "            python -m pip install ultralytics opencv-python numpy\n"
    )
    sys.exit(1)


# ------------------------------------------------------------------------------
# Traffic class definitions  (subset of the COCO-80 labels YOLO is trained on)
# ------------------------------------------------------------------------------
VEHICLE_CLASSES = {"car", "truck", "bus", "motorcycle", "bicycle"}
PERSON_CLASSES = {"person"}
SIGNAL_CLASSES = {"traffic light", "stop sign"}

# BGR colours used for drawing (modern, high-contrast HUD palette)
COLOR_VEHICLE = (96, 214, 104)     # emerald
COLOR_PERSON = (255, 175, 64)      # amber
COLOR_SIGNAL = (88, 66, 255)       # red
COLOR_OTHER = (150, 150, 150)      # grey

# glass-style HUD palette
COLOR_PANEL = (30, 36, 52)         # translucent card background
COLOR_PANEL_BORDER = (92, 104, 136)
COLOR_TITLE = (255, 255, 255)      # card title / chip text
COLOR_ROW_TEXT = (215, 215, 215)   # card body text
COLOR_DIVIDER = (70, 78, 100)      # thin card separators
COLOR_ACCENT = (255, 184, 52)      # amber accent underline
COLOR_FPS = (96, 214, 104)         # emerald FPS meter
COLOR_CHIP_BG = (24, 26, 36)       # label-chip background

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v", ".wmv"}

# ------------------------------------------------------------------------------
# Small drawing helpers
# ------------------------------------------------------------------------------
def _rounded_rectangle(img, p1, p2, radius=10, color=(255, 255, 255),
                       thickness=-1, line_type=cv2.LINE_AA):
    """Draw a rounded rectangle onto *img* in place.

    ``thickness`` = -1 fills the shape, a positive value draws only the
    outline.  ``radius`` is the corner radius in pixels and is reduced
    automatically if the rectangle is too small to fit it.
    """
    x1, y1 = p1
    x2, y2 = p2
    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))
    radius = max(1, min(radius, (x2 - x1) // 2, (y2 - y1) // 2))

    cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2),
                  color, thickness, line_type)
    cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius),
                  color, thickness, line_type)
    cv2.circle(img, (x1 + radius, y1 + radius), radius,
               color, thickness, line_type)
    cv2.circle(img, (x2 - radius, y1 + radius), radius,
               color, thickness, line_type)
    cv2.circle(img, (x1 + radius, y2 - radius), radius,
               color, thickness, line_type)
    cv2.circle(img, (x2 - radius, y2 - radius), radius,
               color, thickness, line_type)

# ------------------------------------------------------------------------------
# TrafficDetector : YOLO wrapper with traffic-aware post-processing and drawing
# ------------------------------------------------------------------------------
class TrafficDetector:
    """Detects traffic objects in frames coming from images / videos / webcam."""

    def __init__(self, model_path="yolov8n.pt", conf_thresh=0.35,
                 iou_thresh=0.45, device="auto"):
        self.model_path = model_path
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        self.device = device
        self.model = None
        self.class_names = None
        self.load_model()

    # -- model loading -----------------------------------------------------
    def load_model(self):
        """Load the YOLO checkpoint, downloading it the first time it is used."""
        try:
            self.model = YOLO(self.model_path)
        except Exception as exc:  # network failure, bad path, wrong format...
            raise RuntimeError(
                f"Could not load model '{self.model_path}'.\n"
                f"Make sure the path is valid and you have internet access "
                f"on first run so the weights can be downloaded.\nOriginal "
                f"error: {exc}"
            ) from exc
        self.class_names = self.model.names
        try:
            n_params = sum(p.numel() for p in self.model.model.parameters())
            label = Path(self.model_path).name
            print(f"[+] Model loaded: {label} ({n_params / 1e6:.1f}M params) "
                  f"| conf={self.conf_thresh} iou={self.iou_thresh} "
                  f"device={self.device}")
        except Exception:
            print(f"[+] Model loaded: {self.model_path}")

    # -- inference -----------------------------------------------------------
    def detect(self, frame):
        """Run detection on one BGR frame.

        Parameters
        ----------
        frame : numpy.ndarray
            A single, raw BGR image.

        Returns
        -------
        list of tuples
            Every detection is ``(x1, y1, x2, y2, label, confidence)`` where
            ``(x1, y1)`` is the top-left and ``(x2, y2)`` the bottom-right
            corner of the bounding box.
        """
        # Ultralytics' internal select_device() does not understand the literal
        # string "auto", so translate it to None (its native auto-selection).
        device = None if str(self.device).lower() == "auto" else self.device
        results = self.model.predict(
            source=frame,
            conf=self.conf_thresh,
            iou=self.iou_thresh,
            device=device,
            verbose=False,
        )
        detections = []
        result = results[0]
        if result.boxes is None:
            return detections
        for box in result.boxes:
            x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].tolist())
            conf = float(box.conf[0])
            label = result.names[int(box.cls[0])]
            detections.append((x1, y1, x2, y2, label, conf))
        return detections

# -- drawing ----------------------------------------------------------------
    def annotate(self, frame, detections):
        """Draw premium boxes: soft glow, rounded corners, label chips."""
        frame_h, frame_w = frame.shape[:2]

        # 1) soft glow pass
        glow = frame.copy()
        for x1, y1, x2, y2, label, conf in detections:
            cv2.rectangle(glow, (x1, y1), (x2, y2),
                          self.label_color(label), 6)
        cv2.addWeighted(glow, 0.35, frame, 0.65, 0, dst=frame)

        # 2) rounded outlines + 3) label chips
        for x1, y1, x2, y2, label, conf in detections:
            color = self.label_color(label)
            _rounded_rectangle(frame, (x1, y1), (x2, y2), radius=6,
                               color=color, thickness=2)
            x1, y1, x2, y2 = (max(0, v) for v in (x1, y1, x2, y2))
            x2 = min(x2, frame_w - 1)
            y2 = min(y2, frame_h - 1)
            self._draw_label_chip(frame, (x1, y1), (x2, y2),
                                  label, conf, color)
        return frame

    def _draw_label_chip(self, frame, p1, p2, label, conf, color):
        """Draw a compact rounded label chip (label + confidence)."""
        x1, y1 = p1
        x2, y2 = p2
        text = f"{label} {conf:.0%}"
        font = cv2.FONT_HERSHEY_DUPLEX
        scale, thick = 0.45, 1
        (tw, th), _b = cv2.getTextSize(text, font, scale, thick)

        chip_w = tw + 18
        chip_h = th + 12
        frame_w = frame.shape[1]

        if y1 - chip_h - 4 >= 0:
            cy1 = y1 - chip_h - 4
        else:
            cy1 = y1 + 4
        cx1 = min(max(x1, 4), frame_w - chip_w - 4)
        cy2 = cy1 + chip_h
        cx2 = cx1 + chip_w

        _rounded_rectangle(frame, (cx1, cy1), (cx2, cy2), radius=6,
                           color=COLOR_CHIP_BG, thickness=-1)
        _rounded_rectangle(frame, (cx1, cy1), (cx2, cy2), radius=6,
                           color=color, thickness=1)
        cv2.line(frame, (cx1 + 3, cy1 + 3), (cx1 + 3, cy2 - 3),
                 color, 2, cv2.LINE_AA)
        cv2.putText(frame, text, (cx1 + 12, cy2 - 7), font, scale,
                    COLOR_TITLE, thick, cv2.LINE_AA)

    def label_color(self, label):
        """Return the colour used to draw a box for the given class label."""
        if label in VEHICLE_CLASSES:
            return COLOR_VEHICLE
        if label in PERSON_CLASSES:
            return COLOR_PERSON
        if label in SIGNAL_CLASSES:
            return COLOR_SIGNAL
        return COLOR_OTHER

    def count_labels(self, detections):
        """Count detections per traffic category.

        Returns a dict with the keys used by ``draw_stats`` / ``summarize``:
        ``vehicles``, ``people``, ``signals`` and ``other``.
        """
        counters = {"vehicles": 0, "people": 0, "signals": 0, "other": 0}
        for _x1, _y1, _x2, _y2, label, _conf in detections:
            if label in VEHICLE_CLASSES:
                counters["vehicles"] += 1
            elif label in PERSON_CLASSES:
                counters["people"] += 1
            elif label in SIGNAL_CLASSES:
                counters["signals"] += 1
            else:
                counters["other"] += 1
        return counters

    def draw_stats(self, frame, counters, fps=None):
        """Overlay a glass-style HUD card: traffic counters + FPS meter."""
        height, width = frame.shape[:2]
        pad = 14
        panel_w = min(280, max(220, width - 2 * pad))
        panel_h = 182
        x1, y1 = pad, pad
        x2, y2 = x1 + panel_w, y1 + panel_h

        # 1) translucent rounded card + thin outline
        overlay = frame.copy()
        _rounded_rectangle(overlay, (x1, y1), (x2, y2), radius=14,
                           color=COLOR_PANEL, thickness=-1)
        cv2.addWeighted(overlay, 0.72, frame, 0.28, 0, dst=frame)
        _rounded_rectangle(frame, (x1, y1), (x2, y2), radius=14,
                           color=COLOR_PANEL_BORDER, thickness=1)

        # 2) header with amber accent underline
        tx, ty = x1 + 18, y1 + 24
        cv2.putText(frame, "TRAFFIC MONITOR", (tx, ty),
                    cv2.FONT_HERSHEY_DUPLEX, 0.55, COLOR_TITLE, 1,
                    cv2.LINE_AA)
        cv2.rectangle(frame, (tx, ty + 7), (tx + 134, ty + 9),
                      COLOR_ACCENT, -1)

        # 3) category rows: colour dot + label + right-aligned count
        rows = (("vehicles", COLOR_VEHICLE, "Vehicles"),
                ("people", COLOR_PERSON, "People"),
                ("signals", COLOR_SIGNAL, "Signals"))
        for i, (key, color, title) in enumerate(rows):
            baseline = y1 + 48 + 18 + i * 30
            cv2.circle(frame, (x1 + 24, baseline - 4), 5, color, -1)
            cv2.putText(frame, title, (x1 + 40, baseline),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_ROW_TEXT, 1,
                        cv2.LINE_AA)
            count = str(counters.get(key, 0))
            (cw, _ch), _m = cv2.getTextSize(count, cv2.FONT_HERSHEY_DUPLEX,
                                            0.7, 2)
            cv2.putText(frame, count, (x2 - 22 - cw, baseline),
                        cv2.FONT_HERSHEY_DUPLEX, 0.7, color, 2,
                        cv2.LINE_AA)

        # 4) divider line
        dy = y1 + 48 + 90 + 4
        cv2.line(frame, (x1 + 18, dy), (x2 - 18, dy),
                 COLOR_DIVIDER, 1, cv2.LINE_AA)

        # 5) FPS footer with mini meter bar
        if fps is not None:
            fy = dy + 26
            cv2.putText(frame, "FPS", (x1 + 18, fy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_ROW_TEXT, 1,
                        cv2.LINE_AA)
            bar_x1, bar_x2 = x1 + 50, x2 - 58
            bar_y1, bar_y2 = fy - 10, fy - 6
            ratio = min(max(fps / 60.0, 0.0), 1.0)
            cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x2, bar_y2),
                          COLOR_DIVIDER, -1)
            fill = int(bar_x1 + (bar_x2 - bar_x1) * ratio)
            if fill > bar_x1:
                cv2.rectangle(frame, (bar_x1, bar_y1), (fill, bar_y2),
                              COLOR_FPS, -1)
            txt = f"{fps:.1f}"
            (tw, _th2), _m2 = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX,
                                              0.5, 1)
            cv2.putText(frame, txt, (bar_x2 + 8, fy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_FPS, 1,
                        cv2.LINE_AA)
        return frame

    @staticmethod
    def summarize(counters):
        """Human-readable one-liner of the latest frame statistics."""
        return (f"{counters['vehicles']} vehicle(s), "
                f"{counters['people']} person(s), "
                f"{counters['signals']} signal(s), "
                f"{counters['other']} other")

# ------------------------------------------------------------------------------
# Source-processing functions
# ------------------------------------------------------------------------------
def process_image(detector, image_path, out_path=None, show=True, csv_path=None):
    """Run detection on a single image file."""
    frame = cv2.imread(str(image_path))
    if frame is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    print(f"[i] Analysing image: {image_path}")

    detections = detector.detect(frame)
    counters = detector.count_labels(detections)

    for _x1, _y1, _x2, _y2, label, conf in detections:
        print(f"    - {label:<16} conf={conf:.3f} box=({_x1},{_y1})-({_x2},{_y2})")
    print(f"[i] Frame stats -> {TrafficDetector.summarize(counters)}")

    if csv_path:
        Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
        with open(csv_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["frame", "class", "confidence",
                             "x1", "y1", "x2", "y2"])
            for x1, y1, x2, y2, label, conf in detections:
                writer.writerow([1, label, f"{conf:.4f}", x1, y1, x2, y2])
        print(f"[i] Detection log written -> {csv_path}")

    detector.annotate(frame, detections)
    detector.draw_stats(frame, counters)

    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        ok = cv2.imwrite(str(out_path), frame)
        status = "saved" if ok else "FAILED"
        print(f"[i] Annotated image {status} -> {out_path}")

    if show:
        cv2.imshow("TrafficVision - Image", frame)
        print("[i] Press any key in the preview window to close it...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return counters


def process_video(detector, source, out_path=None, show=True, csv_path=None):
    """Run detection on a video file (or webcam index) and stream results."""
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video source: {source}")

    is_webcam = isinstance(source, int) or str(source).isdigit()
    fps_in = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    source_name = f"webcam #{int(source)}" if is_webcam else str(source)
    print(f"[+] Processing: {source_name} "
          f"({width}x{height} @ {fps_in:.1f} fps)"
          + (f", {total_frames} frames" if total_frames > 0 else ""))

    # optional annotated-video writer
    writer = None
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(out_path), fourcc, fps_in, (width, height))
        if not writer.isOpened():
            print(f"[!] VideoWriter failed for {out_path}; output disabled")
            writer = None
        else:
            print(f"[i] Annotated video will be saved -> {out_path}")

    # --- optional CSV detection log
    csv_handle = None
    csv_writer = None
    if csv_path:
        Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
        csv_handle = open(csv_path, "w", newline="", encoding="utf-8")
        csv_writer = csv.writer(csv_handle)
        csv_writer.writerow(["frame", "class", "confidence",
                             "x1", "y1", "x2", "y2"])
        print(f"[i] Detection log will be written -> {csv_path}")

    frame_idx = 0
    prev_time = time.time()
    fps = 0.0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame_idx += 1

            detections = detector.detect(frame)
            counters = detector.count_labels(detections)
            detector.annotate(frame, detections)

            # rolling FPS estimate
            now = time.time()
            fps = 0.9 * fps + 0.1 * (1.0 / max(now - prev_time, 1e-6))
            prev_time = now
            detector.draw_stats(frame, counters, fps=fps)

            if csv_writer is not None:
                for x1, y1, x2, y2, label, conf in detections:
                    csv_writer.writerow([frame_idx, label, f"{conf:.4f}",
                                         x1, y1, x2, y2])

            if writer is not None:
                writer.write(frame)

            if show:
                cv2.imshow("TrafficVision", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("[i] 'q' pressed - stopping early")
                    break

            if frame_idx % 30 == 0 or frame_idx == 1:
                progress = (frame_idx / total_frames * 100) if total_frames > 0 else 0
                where = f"{frame_idx}/{total_frames} ({progress:.0f}%)" if total_frames else f"{frame_idx}"
                print(f"    frame {where:<16} "
                      f"{TrafficDetector.summarize(counters)}")
    except KeyboardInterrupt:
        print("\n[i] Interrupted by user")
    finally:
        cap.release()
        if writer is not None:
            writer.release()
        if csv_handle is not None:
            csv_handle.close()
        if show:
            cv2.destroyAllWindows()

    print(f"[i] Finished ({frame_idx} frames processed)")
    return frame_idx

# ------------------------------------------------------------------------------
# Command-line interface
# ------------------------------------------------------------------------------
def build_parser():
    parser = argparse.ArgumentParser(
        prog="Trafficdetection.py",
        description=("Traffic-detection system: detects vehicles, pedestrians "
                     "and traffic signals in images, videos or webcam feeds "
                     "using Ultralytics YOLO + OpenCV."),
        epilog=("Examples:\n"
                "  python Trafficdetection.py --source street.jpg --save\n"
                "  python Trafficdetection.py --source traffic.mp4 --save --csv log.csv\n"
                "  python Trafficdetection.py --source 0\n"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--source", default="0",
        help="Input: image/video file path, or webcam index (default: 0)",
    )
    parser.add_argument(
        "--model", default="yolov8n.pt",
        help="YOLO weights. One of yolov8n/s/m/l/x.pt or a custom .pt path "
             "(downloaded automatically on first use)",
    )
    parser.add_argument(
        "--conf", type=float, default=0.35,
        help="Detection confidence threshold, 0..1 (default: 0.35)",
    )
    parser.add_argument(
        "--iou", type=float, default=0.45,
        help="Non-max-suppression IoU threshold, 0..1 (default: 0.45)",
    )
    parser.add_argument(
        "--device", default="auto",
        help="Inference device: auto, cpu, or cuda index e.g. 0 (default: auto)",
    )
    parser.add_argument(
        "--no-show", action="store_true",
        help="Disable the interactive preview window (headless operation)",
    )
    parser.add_argument(
        "--save", action="store_true",
        help="Save the annotated image/video into the output folder",
    )
    parser.add_argument(
        "--out", default=None,
        help="Explicit output path (overrides the default output folder)",
    )
    parser.add_argument(
        "--csv", default=None, metavar="PATH",
        help="Path of a CSV file that logs every detection",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    # decide the source type
    source = args.source
    if str(source).isdigit():
        src_is_image = False
        src_is_video = False
    else:
        src_path = Path(source)
        src_is_image = src_path.suffix.lower() in IMAGE_EXTENSIONS
        src_is_video = src_path.suffix.lower() in VIDEO_EXTENSIONS

    # build the detector (downloads weights on first run)
    detector = TrafficDetector(
        model_path=args.model,
        conf_thresh=args.conf,
        iou_thresh=args.iou,
        device=args.device,
    )

    # default output paths
    if args.save:
        if args.out:
            out_target = args.out
        elif src_is_image:
            out_target = f"output/annotated_{Path(source).name}"
        elif src_is_video or str(source).isdigit():
            stem = Path(source).stem if not str(source).isdigit() else "webcam"
            out_target = f"output/annotated_{stem}.mp4"
        else:
            out_target = None
    else:
        out_target = None

    show = not args.no_show

    try:
        if src_is_image:
            if not Path(source).is_file():
                raise FileNotFoundError(f"Image not found: {source}")
            process_image(detector, source, out_path=out_target,
                          show=show, csv_path=args.csv)
        elif src_is_video or str(source).isdigit():
            # pass webcam indices as int so VideoCapture treats them as cameras
            video_source = int(source) if str(source).isdigit() else source
            process_video(detector, video_source, out_path=out_target,
                          show=show, csv_path=args.csv)
        else:
            print(f"[!] Unrecognised source '{source}'. Expected an image "
                  f"({', '.join(sorted(IMAGE_EXTENSIONS))}) or a video "
                  f"({', '.join(sorted(VIDEO_EXTENSIONS))}) file, or a webcam "
                  f"index (integer).")
            return 2
    except Exception as exc:
        print(f"\n[ERROR] {exc}")
        return 1

    print("[+] Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
