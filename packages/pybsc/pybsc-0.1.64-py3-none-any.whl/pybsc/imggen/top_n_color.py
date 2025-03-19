import numpy as np
import scipy
import scipy.cluster


def pillow_image_to_simple_bitmap(pillow_image, mask=None):
    if mask is not None:
        bitmap = np.array(pillow_image, dtype=np.int16)[np.array(mask) > 150]
    else:
        bitmap = np.array(pillow_image, dtype=np.int16)
        shape = bitmap.shape
        bitmap = bitmap.reshape(scipy.product(shape[:2]), shape[2])
    bitmap = bitmap.astype(np.float)
    return bitmap


def top_n_colors(pillow_image, top_n, num_of_clusters, mask=None):
    clustering = scipy.cluster.vq.kmeans
    bitmap = pillow_image_to_simple_bitmap(pillow_image, mask)
    clusters, _ = clustering(bitmap, num_of_clusters)
    quntized, _ = scipy.cluster.vq.vq(bitmap, clusters)
    histgrams, _ = scipy.histogram(quntized, len(clusters))
    order = np.argsort(histgrams)[::-1][:top_n]
    for idx in range(min(top_n, len(order))):
        rgb = clusters.astype(int)[order[idx]].tolist()
        yield rgb
