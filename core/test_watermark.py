import os
from api.watermark import add_image_watermark
from PIL import Image

def test_add_image_watermark():
    input_image = os.path.join('images', 'schneider_electric_kompleksnye_resheniya_dlya_avtomatizacii_i_energoeffektivnosti', '000FBXZSGLK50LXY-C461-F4.jpg')
    watermark_path = os.path.join('images', 'watermarks', 'watermark_itexport.png')
    output_image = os.path.join('images', 'schneider_electric_kompleksnye_resheniya_dlya_avtomatizacii_i_energoeffektivnosti', 'test_watermarked3.jpg')
    # Получаем размеры исходного изображения
    with Image.open(input_image) as im:
        w, h = im.size
    # Задаем масштаб вотермарки (например, 20% от ширины исходного изображения)
    watermark_scale = 0.25
    # Временно открываем вотермарк, чтобы получить его исходные пропорции
    try:
        with Image.open(watermark_path) as wm_img:
            wm_w_orig, wm_h_orig = wm_img.size
        # Рассчитываем новый размер на основе масштаба
        wm_w_scaled = int(w * watermark_scale)
        wm_h_scaled = int(wm_h_orig * (wm_w_scaled / wm_w_orig))
        # Рассчитываем позицию для центрирования scaled вотермарки
        pos = ((w - wm_w_scaled) // 2, (h - wm_h_scaled) // 2)
        add_image_watermark(input_image, output_image, watermark_path, position=pos, opacity=100, watermark_scale=watermark_scale)
        assert os.path.exists(output_image)
        print('Тест успешно: изображение с вотермаркой сохранено как', output_image)
    except FileNotFoundError:
        print(f'Ошибка: файл вотермарки не найден по пути {watermark_path}')
    except Exception as e:
        print(f'Ошибка при обработке вотермарки: {e}')

if __name__ == '__main__':
    test_add_image_watermark() 