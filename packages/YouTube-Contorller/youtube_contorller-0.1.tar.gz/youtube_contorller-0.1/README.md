
# YouTube Controller

**YouTube Controller** — это Python-библиотека для управления воспроизведением видео на YouTube с использованием Selenium WebDriver.

## Установка

Для установки YouTube Controller, выполните следующую команду:

```bash
pip install YouTube_Controller
```

## Зависимости

- Selenium 4.0.0 и выше
- Chrome WebDriver

## Использование

Пример использования библиотеки для поиска и воспроизведения видео на YouTube:

```python
from youtube_controller import YouTubePlayer

# Создаём объект для управления видео
player = YouTubePlayer()

# Ищем видео по запросу
player.play_video("Python tutorial")

# Пауза
player.pause()

# Перемотка назад на 10 секунд
player.rewind_backward(10)

# Перемотка вперёд на 10 секунд
player.rewind_forward(10)

# Увеличение громкости
player.volume_up()

# Закрытие браузера
player.close()
```

## Лицензия

Этот проект лицензирован по лицензии MIT. Подробнее см. файл [LICENSE](LICENSE).
