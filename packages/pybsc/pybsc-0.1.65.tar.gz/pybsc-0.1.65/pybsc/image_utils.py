
import base64
from enum import Enum
import math
from pathlib import Path

import cv2
import numpy as np
import PIL
from PIL.Image import Image as PILImage
from shapely.geometry import Polygon

from pybsc.tile import squared_tile

try:
    from turbojpeg import TurboJPEG
    jpeg = TurboJPEG()
except Exception:
    jpeg = None


class ReturnType(Enum):
    BYTES = 0
    PILLOW = 1
    NDARRAY = 2


def str_to_pil_interpolation(interpolation):
    if interpolation == 'nearest':
        return PIL.Image.NEAREST
    elif interpolation == 'bilinear':
        return PIL.Image.BILINEAR
    elif interpolation == 'bicubic':
        return PIL.Image.BICUBIC
    elif interpolation == 'lanczos':
        return PIL.Image.LANCZOS
    else:
        raise ValueError(
            'Not valid Interpolation. '
            + 'Valid interpolation methods are '
            + 'nearest, bilinear, bicubic and lanczos.')


def pil_to_cv2_interpolation(interpolation):
    if isinstance(interpolation, str):
        interpolation = interpolation.lower()
        if interpolation == 'nearest':
            cv_interpolation = cv2.INTER_NEAREST
        elif interpolation == 'bilinear':
            cv_interpolation = cv2.INTER_LINEAR
        elif interpolation == 'bicubic':
            cv_interpolation = cv2.INTER_CUBIC
        elif interpolation == 'lanczos':
            cv_interpolation = cv2.INTER_LANCZOS4
        else:
            raise ValueError(
                'Not valid Interpolation. '
                + 'Valid interpolation methods are '
                + 'nearest, bilinear, bicubic and lanczos.')
    else:
        if interpolation == PIL.Image.NEAREST:
            cv_interpolation = cv2.INTER_NEAREST
        elif interpolation == PIL.Image.BILINEAR:
            cv_interpolation = cv2.INTER_LINEAR
        elif interpolation == PIL.Image.BICUBIC:
            cv_interpolation = cv2.INTER_CUBIC
        elif interpolation == PIL.Image.LANCZOS:
            cv_interpolation = cv2.INTER_LANCZOS4
        else:
            raise ValueError(
                'Not valid Interpolation. '
                + 'Valid interpolation methods are '
                + 'PIL.Image.NEAREST, PIL.Image.BILINEAR, '
                + 'PIL.Image.BICUBIC and PIL.Image.LANCZOS.')
    return cv_interpolation


def convert_to_numpy(input_data):
    """Convert the input data into a numpy.ndarray object.

    Parameters
    ----------
    input_data : str, Path, np.ndarray, or PIL.Image
        The input data to be converted. This can be a string or Path
        object representing a file path, a np.ndarray representing an image,
        or a PIL.Image object.

    Returns
    -------
    np.ndarray
        The converted np.ndarray object.

    Raises
    ------
    TypeError
        If the input_data is not of type str, Path, np.ndarray, or PIL.Image.
    """
    if isinstance(input_data, (str, Path)):
        return np.array(PIL.Image.open(str(input_data)))
    elif isinstance(input_data, np.ndarray):
        return input_data
    elif isinstance(input_data, PILImage.Image):
        return np.array(input_data)
    else:
        raise TypeError(
            "Invalid input type. Expected filepath, np.ndarray, or PIL.Image")


def convert_to_pil(input_data):
    """Convert the input data into a PIL.Image object.

    Parameters
    ----------
    input_data : str, Path, np.ndarray, or PIL.Image
        The input data to be converted.
        This can be a string or Path object representing a file path,
        a np.ndarray representing an image, or a PIL.Image object.

    Returns
    -------
    PIL.Image
        The converted PIL.Image object.

    Raises
    ------
    TypeError
        If the input_data is not of type str, Path, np.ndarray, or PIL.Image.
    """
    if isinstance(input_data, (str, Path)):
        return PIL.Image.open(str(input_data))
    elif isinstance(input_data, np.ndarray):
        return PIL.Image.fromarray(input_data)
    elif isinstance(input_data, PIL.Image):
        return input_data
    else:
        raise TypeError(
            "Invalid input type. Expected filepath, np.ndarray, or PIL.Image")


def _imread(image_path, color_type='bgr'):
    img = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)

    if img is None:
        raise ValueError(f'Image not found at path: {image_path}')

    if color_type.lower() == 'gray':
        converted_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif color_type.lower() == 'rgba':
        if img.shape[2] == 3:
            converted_img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        elif img.shape[2] == 4:
            converted_img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    elif color_type.lower() == 'bgra':
        if img.shape[2] == 3:
            converted_img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        elif img.shape[2] == 4:
            converted_img = img
    elif color_type.lower() == 'bgr':
        if img.shape[2] == 3:
            converted_img = img
        elif img.shape[2] == 4:
            converted_img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    elif color_type.lower() == 'rgb':
        converted_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        raise ValueError(f'Unsupported color type: {color_type}')
    return np.array(converted_img)


def imread(img_path, color_type='bgr',
           size_keeping_aspect_ratio_wrt_longside=None,
           clear_alpha=False):
    img = _imread(img_path, color_type=color_type)
    if size_keeping_aspect_ratio_wrt_longside:
        if color_type == 'bgra' or color_type == 'rgba':
            bgr = img[..., :3]
            alpha_img = img[..., 3]
            alpha_img = resize_keeping_aspect_ratio_wrt_longside(
                alpha_img, size_keeping_aspect_ratio_wrt_longside,
                interpolation='nearest')
            bgr = resize_keeping_aspect_ratio_wrt_longside(
                bgr, size_keeping_aspect_ratio_wrt_longside,
                interpolation='bilinear')
            img = np.dstack(
                [np.array(bgr, dtype=np.uint8),
                 np.array(alpha_img, dtype=np.uint8)[..., None]])
            if clear_alpha:
                img[..., 3] = 0
        else:
            img = resize_keeping_aspect_ratio_wrt_longside(
                img, size_keeping_aspect_ratio_wrt_longside,
                interpolation='bilinear')
    return img


def imwrite(image_path, img, color_type='bgr'):
    if color_type.lower() == 'gray':
        converted_img = PIL.Image.fromarray(img, 'L')
    elif color_type.lower() == 'rgba':
        converted_img = PIL.Image.fromarray(img, 'RGBA')
    elif color_type.lower() == 'bgra':
        b, g, r, a = img.split()
        converted_img = PIL.Image.merge("RGBA", (r, g, b, a))
    elif color_type.lower() == 'bgr':
        b, g, r = np.split(img, 3, axis=2)
        converted_img = PIL.Image.fromarray(
            np.concatenate((r, g, b), axis=2), 'RGB')
    elif color_type.lower() == 'rgb':
        converted_img = PIL.Image.fromarray(img, 'RGB')
    else:
        raise ValueError(f'Unsupported color type: {color_type}')

    converted_img.save(image_path)


def decode_image_cv2(b64encoded):
    bin = b64encoded.split(",")[-1]
    bin = base64.b64decode(bin)
    bin = np.frombuffer(bin, np.uint8)
    img = cv2.imdecode(bin, cv2.IMREAD_COLOR)
    return img


def decode_image_turbojpeg(b64encoded):
    bin = b64encoded.split(",")[-1]
    bin = base64.b64decode(bin)
    img = jpeg.decode(bin)
    return img


def decode_image(b64encoded):
    if jpeg is not None:
        img = decode_image_turbojpeg(b64encoded)
    else:
        img = decode_image_cv2(b64encoded)
    return img


def encode_image_turbojpeg(img):
    bin = jpeg.encode(img)
    b64encoded = base64.b64encode(bin).decode('ascii')
    return b64encoded


def encode_image_cv2(img, quality=90):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    result, encimg = cv2.imencode('.jpg', img, encode_param)
    b64encoded = base64.b64encode(encimg).decode('ascii')
    return b64encoded


def encode_image(img):
    if jpeg is not None:
        img = encode_image_turbojpeg(img)
    else:
        img = encode_image_cv2(img)
    return img


def get_size(img):
    if isinstance(img, PILImage):
        return img.size
    elif isinstance(img, np.ndarray):
        return (img.shape[1], img.shape[0])
    else:
        raise RuntimeError(
            'input img should be PILImage or numpy.ndarray'
            + f', get {type(img)}')


def resize_keeping_aspect_ratio(img, width=None, height=None,
                                interpolation='bilinear',
                                return_scale=False):
    if (width and height) or (width is None and height is None):
        raise ValueError('Only width or height should be specified.')
    if isinstance(img, PILImage):
        if width == img.size[0] and height == img.size[1]:
            return img
        if width:
            scale = width / img.size[0]
            height = scale * img.size[1]
        else:
            scale = height / img.size[1]
            width = scale * img.size[0]
        height = int(height)
        width = int(width)
        resized_img = img.resize(
            (width, height),
            resample=str_to_pil_interpolation(interpolation))
    elif isinstance(img, np.ndarray):
        if width == img.shape[1] and height == img.shape[0]:
            return img
        if width:
            scale = width / img.shape[1]
            height = scale * img.shape[0]
        else:
            scale = height / img.shape[0]
            width = scale * img.shape[1]
        height = int(height)
        width = int(width)
        cv_interpolation = pil_to_cv2_interpolation(interpolation)
        resized_img = cv2.resize(img, (width, height),
                                 interpolation=cv_interpolation)
    else:
        raise ValueError(
            f"Input type {type(img)} is not supported.")
    if return_scale:
        return resized_img, scale
    else:
        return resized_img


def resize_keeping_aspect_ratio_wrt_longside(img, length,
                                             interpolation='bilinear',
                                             return_scale=False):
    if isinstance(img, PILImage):
        W, H = img.size
        aspect = W / H
        if H > W:
            width = length * aspect
            scale = length / H
            resized_img = img.resize(
                (int(width), int(length)),
                resample=str_to_pil_interpolation(interpolation))
        else:
            height = length / aspect
            scale = length / W
            resized_img = img.resize(
                (int(length), int(height)),
                resample=str_to_pil_interpolation(interpolation))
    elif isinstance(img, np.ndarray):
        cv_interpolation = pil_to_cv2_interpolation(interpolation)
        H, W = img.shape[:2]
        aspect = W / H
        if H > W:
            width = length * aspect
            scale = length / H
            resized_img = cv2.resize(
                img, (int(width), int(length)),
                interpolation=cv_interpolation)
        else:
            height = length / aspect
            scale = length / W
            resized_img = cv2.resize(
                img, (int(length), int(height)),
                interpolation=cv_interpolation)
    else:
        raise ValueError(
            f"Input type {type(img)} is not supported.")
    if return_scale:
        return resized_img, scale
    else:
        return resized_img


def _resize_keeping_aspect_ratio_wrt_longside_rgba(img, image_width):
    img = convert_to_numpy(img)
    try:
        img, mask = img[..., :3], img[..., 3]
    except IndexError:
        height = img.shape[0]
        width = img.shape[1]
        mask = 255 * np.ones(
            (height, width),
            dtype=np.uint8)
    pil_mask = PIL.Image.fromarray(mask)
    pil_mask = resize_keeping_aspect_ratio_wrt_longside(
        pil_mask, image_width,
        interpolation='nearest')
    pil_img = PIL.Image.fromarray(img)
    pil_img = resize_keeping_aspect_ratio_wrt_longside(
        pil_img, image_width,
        interpolation='bilinear')
    return np.concatenate(
        [np.array(pil_img, dtype=np.uint8),
         np.array(pil_mask, dtype=np.uint8).reshape(
             pil_mask.size[1],
             pil_mask.size[0],
             1)],
        axis=2)


def resize_keeping_aspect_ratio_wrt_target_size(
        img, width, height, interpolation='bilinear',
        background_color=(0, 0, 0)):
    if width == img.shape[1] and height == img.shape[0]:
        return img
    H, W, _ = img.shape
    ratio = min(float(height) / H, float(width) / W)
    M = np.array([[ratio, 0, 0],
                  [0, ratio, 0]], dtype=np.float32)
    dst = np.zeros((int(height), int(width), 3), dtype=img.dtype)
    return cv2.warpAffine(
        img, M,
        (int(width), int(height)),
        dst,
        cv2.INTER_CUBIC, cv2.BORDER_CONSTANT,
        background_color)


def squared_padding_image(img, length=None,
                          return_offset=None):
    H, W = img.shape[:2]
    if H > W:
        if length is not None:
            img = resize_keeping_aspect_ratio_wrt_longside(img, length)
        margin = img.shape[0] - img.shape[1]
        offset = (margin // 2, 0)
        img = np.pad(img,
                     [(0, 0),
                      (margin // 2, margin - margin // 2),
                      (0, 0)], 'constant')
    else:
        if length is not None:
            img = resize_keeping_aspect_ratio_wrt_longside(img, length)
        margin = img.shape[1] - img.shape[0]
        offset = (0, margin // 2)
        img = np.pad(img,
                     [(margin // 2, margin - margin // 2),
                      (0, 0), (0, 0)], 'constant')
    if return_offset:
        return img, offset
    else:
        return img


def concat_with_keeping_aspect(
        imgs, width, height,
        tile_shape=None):
    if len(imgs) == 0:
        raise ValueError
    if tile_shape is None:
        tile_x, tile_y = squared_tile(len(imgs))
    else:
        tile_x, tile_y = tile_shape

    w = width // tile_x
    h = height // tile_y

    ret = []
    max_height = h
    max_width = w
    for img in imgs:
        if img.shape[1] / w > img.shape[0] / h:
            tmp_img = resize_keeping_aspect_ratio(img, width=w, height=None)
        else:
            tmp_img = resize_keeping_aspect_ratio(img, width=None, height=h)
        ret.append(tmp_img)

    canvas = np.zeros((height, width, 3),
                      dtype=np.uint8)

    i = 0
    for y in range(tile_y):
        for x in range(tile_x):
            lh = (max_height - ret[i].shape[0]) // 2
            rh = (max_height - ret[i].shape[0]) - lh
            lw = (max_width - ret[i].shape[1]) // 2
            rw = (max_width - ret[i].shape[1]) - lw
            img = np.pad(ret[i],
                         [(lh, rh),
                          (lw, rw),
                          (0, 0)], 'constant')
            canvas[y * max_height:(y + 1) * max_height,
                   x * max_width:(x + 1) * max_width] = img
            i += 1
            if i >= len(imgs):
                break
        if i >= len(imgs):
            break
    return canvas


def mask_to_bbox(mask, threshold=0):
    if isinstance(mask, PILImage):
        mask = np.array(mask)
    elif isinstance(mask, np.ndarray):
        pass
    else:
        raise TypeError(f'Invalid input image type, {type(mask)}')
    mask = mask > threshold
    mask_indexes = np.where(mask)
    y_min = np.min(mask_indexes[0])
    y_max = np.max(mask_indexes[0])
    x_min = np.min(mask_indexes[1])
    x_max = np.max(mask_indexes[1])
    return (y_min, x_min, y_max, x_max)


def masks_to_bboxes(mask):
    R, _, _ = mask.shape
    instance_index, ys, xs = np.nonzero(mask)
    bboxes = np.zeros((R, 4), dtype=np.float32)
    for i in range(R):
        ys_i = ys[instance_index == i]
        xs_i = xs[instance_index == i]
        if len(ys_i) == 0:
            continue
        y_min = ys_i.min()
        x_min = xs_i.min()
        y_max = ys_i.max() + 1
        x_max = xs_i.max() + 1
        bboxes[i] = np.array(
            [x_min, y_min, x_max, y_max],
            dtype=np.float32)
    return bboxes


def alpha_blend(a_img, b_img, alpha=0.5):
    viz = cv2.addWeighted(a_img, alpha, b_img, 1 - alpha, 0)
    return viz


def zoom(img, ratio=1.0, interpolation='bilinear'):
    """zoom function resize and crop images.

    Parameters
    ----------
    img : np.ndarray
        input image (C, H, W)
    ration : float
        zoom ratio
        should be greater than 1.0.
    Returns
    -------
    cropped_img : np.ndarray
        zoomed image
    """
    if ratio < 1.0:
        raise ValueError(f'ratio should be greater than 1.0, but given {ratio}')
    w, h = get_size(img)
    H = int(h * ratio)
    W = int(w * ratio)
    resized_img = resize_keeping_aspect_ratio(
        img, height=H,
        interpolation=interpolation)
    cropped_img = resized_img[(H - h) // 2:(H - h) // 2 + h,
                              (W - w) // 2:(W - w) // 2 + w,
                              :]
    return cropped_img


def tile_image(wh_size, tile_size_wh, window_size=None):
    w, h = wh_size
    if isinstance(tile_size_wh, tuple) or isinstance(tile_size_wh, list):
        tile_width, tile_height = tile_size_wh
    else:
        tile_width, tile_height = tile_size_wh, tile_size_wh

    if window_size is None:
        window_h = tile_height
        window_w = tile_width
    else:
        if isinstance(window_size, tuple) or isinstance(window_size, list):
            window_w, window_h = window_size
        else:
            window_w = window_size
            window_h = window_size

    tile_w = tile_width
    tile_h = tile_height

    x = np.arange(0, w - tile_w, window_w)
    if (w - tile_w) % tile_w != 0:
        x = np.concatenate([x, np.array([w - tile_w])])
    y = np.arange(0, h - tile_h, window_h)
    if (h - tile_h) % tile_h != 0:
        y = np.concatenate([y, np.array([h - tile_h])])

    sx, sy = np.meshgrid(x, y)
    sx = sx.reshape(-1)
    ex = sx + tile_w
    sy = sy.reshape(-1)
    ey = sy + tile_h

    return np.array(
        [((sx[i], sy[i], ex[i] - sx[i], ey[i] - sy[i]))
         for i in range(len(sx))])


def create_tile_image(image_list,
                      image_size=300,
                      num_tiles_per_row=10,
                      background_color=(255, 255, 255)):
    """Create a tiled image from a list of images.

    Parameters
    ----------
    image_list : list
        A list of images to be tiled. Each image can be a filepath
        (str or Path), np.ndarray, or PIL.Image.
    image_size : int
        The size for each individual image tile. Defaults to 300.
    num_tiles_per_row : int, optional
        The number of image tiles per row in the output image.
        Defaults to 10.
    background_color : tuple, optional
        The background color for the output image in (R, G, B).
        Defaults to (255, 255, 255).

    Returns
    -------
    PIL.Image
        The created tiled image.

    Raises
    ------
    ValueError
        If any of the images in image_list cannot be opened or read.
    """
    num_images = len(image_list)
    num_rows = math.ceil(num_images / num_tiles_per_row)

    tile_width = image_size * num_tiles_per_row
    tile_height = image_size * num_rows
    tile_image = PIL.Image.new(
        'RGBA', (tile_width, tile_height),
        tuple(list(background_color) + [0]))

    for i, image in enumerate(image_list):
        tile_x = (i % num_tiles_per_row) * image_size
        tile_y = (i // num_tiles_per_row) * image_size
        pil_img = convert_to_pil(
            _resize_keeping_aspect_ratio_wrt_longside_rgba(
                image, image_size))
        tile_image.paste(pil_img, (tile_x, tile_y))
    return tile_image


def get_bboxes_from_tile(bboxes, tile):
    new_bboxes = []
    for y1, x1, y2, x2 in bboxes:
        new_bboxes.append(Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)]))
    bboxes = new_bboxes
    x1, y1, w, h = tile
    x2, y2 = x1 + w, y1 + h
    pol = Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])
    sliced_bboxes = []
    indices = []
    for box_idx, box in enumerate(bboxes):
        if pol.intersects(box):
            inter = pol.intersection(box)
            # get the smallest polygon
            # (with sides parallel to the coordinate axes)
            # that contains the intersection
            new_box = inter.envelope

            # get coordinates of polygon vertices
            x, y = new_box.exterior.coords.xy
            x = x - x1
            y = y - y1

            sliced_bboxes.append([min(y), min(x), max(y), max(x)])
            indices.append(box_idx)
    return sliced_bboxes, indices


def non_maximum_suppression(bbox, thresh, score=None, limit=None):
    if len(bbox) == 0:
        return np.zeros((0,), dtype=np.int32)

    if score is not None:
        order = score.argsort()[::-1]
        bbox = bbox[order]
    bbox_area = np.prod(bbox[:, 2:] - bbox[:, :2], axis=1)

    indices = np.zeros(bbox.shape[0], dtype=bool)
    for i, b in enumerate(bbox):
        tl = np.maximum(b[:2], bbox[indices, :2])
        br = np.minimum(b[2:], bbox[indices, 2:])
        area = np.prod(br - tl, axis=1) * (tl < br).all(axis=1)

        iou = area / (bbox_area[i] + bbox_area[indices] - area)
        if (iou >= thresh).any():
            continue

        indices[i] = True
        if limit is not None and np.count_nonzero(indices) >= limit:
            break

    indices = np.where(indices)[0]
    if score is not None:
        indices = order[indices]
    return indices.astype(np.int32)


def rotate(pil_img, mask=None, angle=360):
    return_np = False
    concat = False
    if isinstance(pil_img, np.ndarray):
        if pil_img.shape[2] == 4:
            concat = True
            pil_img, mask = PIL.Image.fromarray(pil_img[..., :3]), \
                PIL.Image.fromarray(pil_img[..., 3])
        else:
            pil_img = PIL.Image.fromarray(pil_img)
            if mask is not None:
                mask = PIL.Image.fromarray(mask)
        return_np = True

    rot_img = pil_img.rotate(angle, resample=PIL.Image.BILINEAR,
                             expand=True)
    if mask is not None:
        if return_np:
            if concat:
                rgb = np.array(rot_img)
                mask = np.array(mask.rotate(
                    angle,
                    resample=PIL.Image.NEAREST,
                    expand=True), dtype=np.uint8)
                return np.concatenate(
                    [rgb, mask[..., None]], axis=2)
            return np.array(rot_img), np.array(mask.rotate(
                angle,
                resample=PIL.Image.NEAREST,
                expand=True), dtype=np.uint8)
        else:
            return rot_img, mask.rotate(
                angle,
                resample=PIL.Image.NEAREST,
                expand=True)
    if return_np:
        return np.array(rot_img)
    return rot_img


def rescale(pil_img, mask=None, scale=1.0):
    if isinstance(pil_img, np.ndarray):
        concat = False
        if pil_img.shape[2] == 4:
            concat = True
            pil_img, mask = PIL.Image.fromarray(
                pil_img[..., :3]), \
                PIL.Image.fromarray(pil_img[..., 3])
        else:
            pil_img = PIL.Image.fromarray(pil_img)
            if mask is not None:
                mask = PIL.Image.fromarray(mask)
        w, h = pil_img.size
        w = int(np.ceil(scale * pil_img.size[0]))
        h = int(np.ceil(scale * pil_img.size[1]))
        pil_img = pil_img.resize((w, h), PIL.Image.BILINEAR)
        rgb = np.array(pil_img, dtype=np.uint8)
        if mask is not None:
            mask = mask.resize((w, h), PIL.Image.NEAREST)
            mask = np.array(mask, dtype=np.uint8)
            if concat:
                np.concatenate(
                    [rgb, mask[..., None]], axis=2)
            else:
                return rgb, mask
        return rgb

    else:
        w, h = pil_img.size
        w = int(np.ceil(scale * pil_img.size[0]))
        h = int(np.ceil(scale * pil_img.size[1]))
        pil_img = pil_img.resize((w, h), PIL.Image.BILINEAR)
        if mask is not None:
            mask = mask.resize((w, h), PIL.Image.NEAREST)
            return pil_img, mask
        return pil_img


def apply_mask(bgr_img, mask, fill_value=255, alpha=255,
               use_alpha=False):
    """Apply a mask to an image.

    This function applies a mask to an image, with an optional fill value
    for unmasked areas. If the fill value is a list or tuple, it's assumed
    to represent RGB values.

    Parameters
    ----------
    bgr_img : ndarray
        An input image in BGR format.
    mask : ndarray
        The mask to apply. Any areas where the mask is 0 will be filled
        with the fill_value.
    fill_value : int or list/tuple of int, optional
        The value to fill unmasked areas with. If a list or tuple, it should
        represent BGR values. Defaults to 255.
    alpha : int, optional
        Not used in this function. Defaults to 255.

    Returns
    -------
    img : ndarray
        The image with the mask applied.
    """
    img = bgr_img.copy()
    if len(img.shape) == 3:
        img = img[..., :3]
    if isinstance(fill_value, (list, tuple)):
        fill_value = np.array(fill_value, dtype=np.uint8)
    else:
        fill_value = np.array(
            [fill_value, fill_value, fill_value],
            dtype=np.uint8)
    img[mask == 0] = fill_value
    if use_alpha:
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.GRAY2BGR)
        return np.dstack([img, mask])
    return img


def add_alpha_channel(img, alpha=255):
    """Add an alpha channel to an image.

    If the image already has an alpha channel, the image is returned as is.
    If the image has three channels (BGR), a fourth alpha channel is added.

    Parameters
    ----------
    img : ndarray
        The input image. Should have either 3 (BGR) or 4 (BGRA) channels.
    alpha : int, optional
        The alpha value to set for the new channel. Defaults to 255.

    Returns
    -------
    img_rgba : ndarray
        The image with an added alpha channel.

    Raises
    ------
    ValueError
        If the input image does not have either 3 (BGR) or 4 (BGRA) channels.
    """
    # Checking if the image has 3 channels (Red, Green, Blue)
    if img.shape[2] == 3:
        h, w, _ = img.shape
        # Create a new image with 4 channels
        img_rgba = np.zeros((h, w, 4), dtype=img.dtype)
        img_rgba[:, :, :3] = img
        img_rgba[:, :, 3] = alpha
        return img_rgba
    elif img.shape[2] == 4:  # If the image already has an alpha channel
        return img
    else:
        raise ValueError(
            "Invalid number of channels. "
            + "The image should either have 3 (BGR) or 4 (BGRA) channels.")
