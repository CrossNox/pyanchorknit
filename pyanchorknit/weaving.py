"""Weaving code."""
import json
from pathlib import Path
from typing import Dict, Tuple
from multiprocessing import Pool

import tqdm
import numpy as np
from cv2 import cv2
from skimage.measure import profile_line

from pyanchorknit.utils import config_logger

logger = config_logger(__name__)

BLACK = 0
WHITE = 255


def whitest(intensities):
    return np.argmax(intensities)


def blackest(intensities):
    return np.argmin(intensities)


def create_circular_mask(h, w):
    center = (int(w / 2), int(h / 2))
    radius = min(center[0], center[1], w - center[0], h - center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)

    mask = dist_from_center <= radius
    return mask


def line_intensity(ps, points, bw_img):
    p1, p2 = ps
    return profile_line(bw_img.T, points[p1], points[p2], mode="constant").sum()


def weaving(
    img_path: Path,
    img_out: Path = Path("./weaved.png"),
    traces_out: Path = Path("./traces.json"),
    n_edges: int = 512,
    maxlines: int = 2000,
    n_jobs: int = 8,
):
    logger.info(f"image path: {img_path}")
    logger.info(f"number of edges: {n_edges}")
    logger.info(f"max lines: {maxlines}")
    logger.info(f"n_jobs: {n_jobs}")

    img = cv2.imread(str(img_path.resolve()))
    bw_img = 255 - cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    centerx = img.shape[0] // 2
    centery = img.shape[1] // 2

    points = []

    for theta in np.linspace(0, 2 * np.pi, n_edges + 1)[:-1]:
        x = min(int(centerx * np.cos(theta) + centerx), img.shape[0] - 1)
        y = min(int(centery * np.sin(theta) + centery), img.shape[1] - 1)
        points.append(np.array([x, y], dtype=np.int32))

    white_img: np.typing.ArrayLike = np.ones(img.shape[:2], dtype=np.uint8) * WHITE

    traces: Dict[Tuple[int, int], float] = dict()
    thread_length = 0

    p = 0
    max_intensity = None

    for _ in tqdm.tqdm(range(maxlines)):
        plines = [(p, j) for j in range(len(points)) if j != p]

        with Pool(n_jobs) as pool:
            intensities = pool.starmap(
                line_intensity, [(ps, points, bw_img) for ps in plines]
            )

        poi = whitest(intensities)
        p, pprime = plines[poi]
        intensity = intensities[poi]

        max_intensity = max(max_intensity or 0, intensity)  # flip by color

        if len(traces) > 0 and (intensity / max_intensity) < 0.10:
            logger.debug("Intensity below threshold")
            break

        if (p, pprime) in traces or (pprime, p) in traces:
            logger.debug("Repeated trace")
            break

        p1, p2 = tuple(points[p]), tuple(points[pprime])

        bw_img = cv2.line(bw_img, p1, p2, BLACK, 1)
        white_img = cv2.line(white_img, p1, p2, BLACK, 1)

        thread_length += np.linalg.norm(points[p] - points[pprime])
        traces[(p, pprime)] = intensity
        p = pprime

    logger.info(f"Thread used: {thread_length:.2f}")

    circular_mask = create_circular_mask(*img.shape[:2]) * 255

    rgba_img = cv2.merge(np.array([white_img, white_img, white_img, circular_mask]))
    cv2.imwrite(str(img_out.resolve()), rgba_img)

    points_json = {i: tuple(map(int, point)) for i, point in enumerate(points)}
    traces_json = [((x, y), trace_len) for (x, y), trace_len in traces.items()]
    with open(traces_out, "w") as fp:
        json.dump({"points": points_json, "traces_json": traces_json}, fp)
