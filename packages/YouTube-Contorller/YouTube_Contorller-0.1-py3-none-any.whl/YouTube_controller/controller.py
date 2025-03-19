import time
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

class YouTubePlayer:
    def __init__(self):
        options = Options()
        options.add_argument("--autoplay-policy=no-user-gesture-required")  # Разрешаем автовоспроизведение
        options.add_argument("--disable-popup-blocking")  # Отключаем блокировку всплывающих окон
        options.add_argument("--disable-blink-features=AutomationControlled")  # Маскируем Selenium
        self.driver = webdriver.Chrome(options=options)
        
        self.video_loaded = False

    def play_video(self, query):
        """Ищет и запускает видео на YouTube"""
        self.driver.get(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
        time.sleep(3)
        
        # Кликаем на первое видео
        video = self.driver.find_element(By.ID, "video-title")
        video.click()
        
        time.sleep(5)  # Ждём загрузки видео
        self.video_loaded = True

    def _execute_js(self, script):
        """Выполняет JavaScript в браузере"""
        return self.driver.execute_script(script)

    def pause(self):
        """Ставит видео на паузу или снимает с паузы"""
        if self.video_loaded:
            self.driver.find_element(By.TAG_NAME, "body").send_keys("k")

    def rewind_forward(self, seconds=10):
        """Перематывает видео вперёд"""
        if self.video_loaded:
            for _ in range(seconds // 10):  # "l" перематывает на 5 секунд вперёд
                self.driver.find_element(By.TAG_NAME, "body").send_keys("l")

    def rewind_backward(self, seconds=10):
        """Перематывает видео назад"""
        if self.video_loaded:
            for _ in range(seconds // 10):  # "j" перематывает на 5 секунд назад
                self.driver.find_element(By.TAG_NAME, "body").send_keys("j")

    def volume_up(self):
        """Увеличивает громкость на 5%"""
        if self.video_loaded:
            video_player = self.driver.find_element(By.CSS_SELECTOR, "video")
            ActionChains(self.driver).move_to_element(video_player).send_keys(Keys.ARROW_UP).perform()

    def volume_down(self):
        """Уменьшает громкость на 5%"""
        if self.video_loaded:
            video_player = self.driver.find_element(By.CSS_SELECTOR, "video")
            ActionChains(self.driver).move_to_element(video_player).send_keys(Keys.ARROW_DOWN).perform()


    def close(self):
        """Закрывает браузер"""
        self.driver.quit()
        self.video_loaded = False