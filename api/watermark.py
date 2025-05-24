from PIL import Image

def add_image_watermark(input_image_path, output_image_path, watermark_path, position=(10, 10), opacity=100, watermark_scale=0.25):
    """
    Добавляет графическую вотермарку на изображение.
    :param input_image_path: путь к исходному изображению
    :param output_image_path: путь для сохранения изображения с вотермаркой
    :param watermark_path: путь к png/jpg-файлу вотермарки (можно указать любой файл)
    :param position: кортеж (x, y) — позиция вотермарки
    :param opacity: прозрачность вотермарки (0-255)
    :param watermark_scale: масштаб вотермарки относительно ширины исходного изображения (например, 0.2 для 20%)
    """
    base = Image.open(input_image_path).convert('RGBA')
    watermark = Image.open(watermark_path).convert('RGBA')

    if watermark_scale:
        base_w, base_h = base.size
        wm_w, wm_h = watermark.size
        new_wm_w = int(base_w * watermark_scale)
        new_wm_h = int(wm_h * (new_wm_w / wm_w))
        watermark = watermark.resize((new_wm_w, new_wm_h), Image.Resampling.LANCZOS)

    alpha = watermark.split()[3]
    alpha = alpha.point(lambda p: p * opacity // 255)
    watermark.putalpha(alpha)
    base.paste(watermark, position, watermark)
    base = base.convert('RGB')
    base.save(output_image_path)
    return output_image_path 