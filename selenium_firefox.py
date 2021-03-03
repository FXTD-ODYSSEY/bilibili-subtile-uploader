
from typing import DefaultDict, Optional

from collections import defaultdict
import json
import time
from pathlib import Path
import logging

from typing import Optional, Dict

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By as by
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from fake_useragent import UserAgent
import tldextract

By = by
Keys = Keys

import pickle, os, time

RANDOM_USERAGENT = 'random'

class Firefox:
    def __init__(
        self,
        cookies_folder_path: str,
        extensions_folder_path: str,
        host: str = None,
        port: int = None,
        private: bool = False,
        full_screen: bool = True,
        headless: bool = False,
        language: str = 'en-us',
        manual_set_timezone: bool = False,
        user_agent: str = None,
        load_proxy_checker_website: bool = False
    ):
        self.cookies_folder_path = cookies_folder_path
        profile = webdriver.FirefoxProfile()

        if user_agent is not None:
            if user_agent == RANDOM_USERAGENT:
                user_agent_path = os.path.join(cookies_folder_path, 'user_agent.txt')

                if os.path.exists(user_agent_path):
                    with open(user_agent_path, 'r') as file:
                        user_agent = file.read().strip()
                else:
                    user_agent = self.__random_firefox_user_agent(min_version=60.0)
                    
                    with open(user_agent_path, 'w') as file:
                        file.write(user_agent)

            profile.set_preference("general.useragent.override", user_agent)
        
        if language is not None:
            profile.set_preference('intl.accept_languages', language)

        if private:
            profile.set_preference("browser.privatebrowsing.autostart", True)
        
        if host is not None and port is not None:
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.http", host)
            profile.set_preference("network.proxy.http_port", port)
            profile.set_preference("network.proxy.ssl", host)
            profile.set_preference("network.proxy.ssl_port", port)
            profile.set_preference("network.proxy.ftp", host)
            profile.set_preference("network.proxy.ftp_port", port)
            profile.set_preference("network.proxy.socks", host)
            profile.set_preference("network.proxy.socks_port", port)
            profile.set_preference("network.proxy.socks_version", 5)
            profile.set_preference("signon.autologin.proxy", True)
        
        profile.set_preference("marionatte", False)
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference("media.peerconnection.enabled", False)
        profile.set_preference('useAutomationExtension', False)

        profile.set_preference("general.warnOnAboutConfig", False)

        profile.update_preferences()

        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")

        self.driver = webdriver.Firefox(firefox_profile=profile, firefox_options=options)

        if full_screen:
            self.driver.fullscreen_window()
        
        try:
            change_timezone_id = None
            for (dirpath, _, filenames) in os.walk(extensions_folder_path):
                for filename in filenames:
                    if filename.endswith('.xpi') or filename.endswith('.zip'):
                        addon_id = self.driver.install_addon(os.path.join(dirpath, filename), temporary=False)

                        if 'change_timezone' in filename:
                            change_timezone_id = addon_id

            # self.driver.get("about:addons")
            # self.driver.find_element_by_id("category-extension").click()
            # self.driver.execute_script("""
            #     let hb = document.getElementById("html-view-browser");
            #     let al = hb.contentWindow.window.document.getElementsByTagName("addon-list")[0];
            #     let cards = al.getElementsByTagName("addon-card");
            #     for(let card of cards){
            #         card.addon.disable();
            #         card.addon.enable();
            #     }
            # """)

            while len(self.driver.window_handles) > 1:
                time.sleep(0.5)
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.close()
            
            self.driver.switch_to.window(self.driver.window_handles[0])

            if change_timezone_id is not None and manual_set_timezone:
                if host is not None and port is not None:
                    self.open_new_tab('https://whatismyipaddress.com/')
                    time.sleep(0.25)

                self.open_new_tab('https://www.google.com/search?client=firefox-b-d&q=my+timezone')
                time.sleep(0.25)

                self.driver.switch_to.window(self.driver.window_handles[0])
                
                input('\n\n\nSet timezone.\n\nPress ENTER, when finished. ')
            
                while len(self.driver.window_handles) > 1:
                    time.sleep(0.5)
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.close()
                
                self.driver.switch_to.window(self.driver.window_handles[0])
            elif load_proxy_checker_website and host is not None and port is not None:
                self.driver.get('https://whatismyipaddress.com/')
        except:
            while len(self.driver.window_handles) > 1:
                time.sleep(0.5)
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.close()

    def get(
        self,
        url: str
    ) -> bool:
        clean_current = self.driver.current_url.replace('https://', '').replace('www.', '').strip('/')
        clean_new = url.replace('https://', '').replace('www.', '').strip('/')

        if clean_current == clean_new:
            return False
        
        self.driver.get(url)

        return True

    def refresh(self) -> None:
        self.driver.refresh()

    def find(
        self,
        by: By,
        key: str,
        element: Optional = None,
        timeout: int = 15
    ) -> Optional:
        if element is None:
            element = self.driver
        
        try:
            e = WebDriverWait(element, timeout).until(
                EC.presence_of_element_located((by, key))
            )

            return e
        except:        
            return None

    def find_all(
        self,
        by: By,
        key: str,
        element: Optional = None,
        timeout: int = 15
    ) -> Optional:
        if element is None:
            element = self.driver

        try:
            es = WebDriverWait(element, timeout).until(
                EC.presence_of_all_elements_located((by, key))
            )

            return es
        except:
            return None
    
    def get_attribute(self, element, key: str) -> Optional[str]:
        try:
            return element.get_attribute(key)
        except:
            return None

    def get_attributes(self, element) -> Optional[Dict[str, str]]:
        try:
            return json.loads(
                self.browser.driver.execute_script(
                    'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return JSON.stringify(items);',
                    element
                )
            )
        except:
            return None

    def save_cookies(self) -> None:
        pickle.dump(
            self.driver.get_cookies(),
            open(self.__cookies_path(), "wb")
        )

    def load_cookies(self) -> None:
        if not self.has_cookies_for_current_website():
            self.save_cookies()

            return

        cookies = pickle.load(open(self.__cookies_path(), "rb"))

        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def has_cookies_for_current_website(self, create_folder_if_not_exists: bool = True) -> bool:
        return os.path.exists(
            self.__cookies_path(
                create_folder_if_not_exists=create_folder_if_not_exists
            )
        )

    def send_keys_delay_random(
        self,
        element: object,
        keys: str,
        min_delay: float = 0.025,
        max_delay: float = 0.25
    ) -> None:
        import random

        for key in keys:
            element.send_keys(key)
            time.sleep(random.uniform(min_delay,max_delay))

    def scroll(self, amount: int) -> None:
        self.driver.execute_script("window.scrollTo(0,"+str(self.current_page_offset_y()+amount)+");")

    def current_page_offset_y(self) -> float:
        return self.driver.execute_script("return window.pageYOffset;")

    def open_new_tab(self, url: str) -> None:
        if url is None:
            url = ""

        cmd = 'window.open("'+url+'","_blank");'
        self.driver.execute_script(cmd)
        self.driver.switch_to.window(self.driver.window_handles[-1])



    # LEGACY
    def scroll_to_bottom(self) -> None:
        MAX_TRIES = 25
        SCROLL_PAUSE_TIME = 0.5
        SCROLL_STEP_PIXELS = 5000
        current_tries = 1

        while True:
            last_height = self.current_page_offset_y()
            self.scroll(last_height+SCROLL_STEP_PIXELS)
            time.sleep(SCROLL_PAUSE_TIME)
            current_height = self.current_page_offset_y()

            if last_height == current_height:
                current_tries += 1

                if current_tries == MAX_TRIES:
                    break
            else:
                current_tries = 1



    # PRIVATE
    def __random_firefox_user_agent(self, min_version: float = 60.0) -> str:
        while True:
            agent = UserAgent().firefox

            try:
                version_str_comps = agent.split('/')[-1].strip().split('.', 1)
                version = float(version_str_comps[0] + '.' + version_str_comps[1].replace('.', ''))

                if version >= min_version:
                    return agent
            except:
                pass

    def __cookies_path(self, create_folder_if_not_exists: bool = True) -> str:
        url_comps = tldextract.extract(self.driver.current_url)
        formatted_url = url_comps.domain + '.' + url_comps.suffix

        return os.path.join(
            self.cookies_folder_path,
            formatted_url + '.pkl'
        )

        
logging.basicConfig()

class Constant:
    """A class for storing constants for YoutubeUploader class"""
    BILIBILI_URL = 'https://www.bilibili.com/'
    
    
    YOUTUBE_URL = 'https://www.youtube.com'
    YOUTUBE_STUDIO_URL = 'https://studio.youtube.com'
    YOUTUBE_UPLOAD_URL = 'https://www.youtube.com/upload'
    USER_WAITING_TIME = 1
    VIDEO_TITLE = 'title'
    VIDEO_DESCRIPTION = 'description'
    DESCRIPTION_CONTAINER = '/html/body/ytcp-uploads-dialog/paper-dialog/div/ytcp-animatable[1]/' \
                            'ytcp-uploads-details/div/ytcp-uploads-basics/ytcp-mention-textbox[2]'
    MORE_OPTIONS_CONTAINER = '/html/body/ytcp-uploads-dialog/paper-dialog/div/ytcp-animatable[1]/' \
                             'ytcp-uploads-details/div/div/ytcp-button/div'
    TEXTBOX = 'textbox'
    TEXT_INPUT = 'text-input'
    RADIO_LABEL = 'radioLabel'
    # STATUS_CONTAINER = '/html/body/ytcp-uploads-dialog/paper-dialog/div/ytcp-animatable[2]/' \
    #                    'div/div[1]/ytcp-video-upload-progress/span'
    STATUS_CONTAINER = '//*[@id="dialog"]/div/ytcp-animatable[2]/div/div[1]/ytcp-video-upload-progress/span'
    NOT_MADE_FOR_KIDS_LABEL = 'NOT_MADE_FOR_KIDS'
    NEXT_BUTTON = 'next-button'
    PUBLIC_BUTTON = 'PUBLIC'
    PRIVATE_BUTTON = 'PRIVATE'
    VIDEO_URL_CONTAINER = "//span[@class='video-url-fadeable style-scope ytcp-video-info']"
    VIDEO_URL_ELEMENT = "//a[@class='style-scope ytcp-video-info']"
    HREF = 'href'
    UPLOADED = 'uploaded'
    ERROR_CONTAINER = '//*[@id="error-message"]'
    VIDEO_NOT_FOUND_ERROR = 'Could not find video_id'
    DONE_BUTTON = 'done-button'
    INPUT_FILE_VIDEO = "//input[@type='file']"
    
def load_metadata(metadata_json_path: Optional[str] = None) -> DefaultDict[str, str]:
    if metadata_json_path is None:
        return defaultdict(str)
    with open(metadata_json_path) as metadata_json_file:
        return defaultdict(str, json.load(metadata_json_file))


class YouTubeUploader:
    """A class for uploading videos on YouTube via Selenium using metadata JSON file
    to extract its title, description etc"""

    def __init__(self, video_path: str, metadata_json_path: Optional[str] = None) -> None:
        self.video_path = video_path
        self.metadata_dict = load_metadata(metadata_json_path)
        current_working_dir = str(Path.cwd())
        self.browser = Firefox(current_working_dir, current_working_dir,full_screen=False)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # self.__validate_inputs()
        self.username = ""
        self.password = ""

    def __validate_inputs(self):
        if not self.metadata_dict[Constant.VIDEO_TITLE]:
            self.logger.warning("The video title was not found in a metadata file")
            self.metadata_dict[Constant.VIDEO_TITLE] = Path(self.video_path).stem
            self.logger.warning("The video title was set to {}".format(Path(self.video_path).stem))
        if not self.metadata_dict[Constant.VIDEO_DESCRIPTION]:
            self.logger.warning("The video description was not found in a metadata file")

    # def upload_bilibili(self):
    #     try:
    #         self.bilibili_login()
    #         return self.youtube_upload()
    #     except Exception as e:
    #         print(e)
    #         self.quit()
    #         raise

    def bilibili_login(self):
        self.browser.get(Constant.BILIBILI_URL)
        time.sleep(Constant.USER_WAITING_TIME)

        if self.browser.has_cookies_for_current_website():
            self.browser.load_cookies()
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.refresh()
        else:
            self.logger.info('Please sign in and then press enter')
            input()
            self.browser.get(Constant.BILIBILI_URL)
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.save_cookies()

    
    def bilibili_upload(self,bvid,cid,bcc_path,zh=False):
        self.browser.get(f"https://account.bilibili.com/subtitle/edit/#/editor?bvid={bvid}&cid={cid}")
        time.sleep(Constant.USER_WAITING_TIME)
        # NOTE 语言点击
        path = f"//body/div[@id='app']/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[1]/ul[1]/li[{1 if zh else 6}]"
        self.browser.find(By.XPATH,path).click()
        time.sleep(Constant.USER_WAITING_TIME)
        # NOTE 点击编辑按钮
        path = "//body/div[@id='app']/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/button[1]"
        self.browser.find(By.XPATH,path).click()
        # NOTE 上传 input
        path = "//body/div[@id='app']/div[1]/div[1]/div[2]/div[1]/div[2]/label[1]/input[1]"
        self.browser.find(By.XPATH,path).send_keys(bcc_path)
        time.sleep(Constant.USER_WAITING_TIME)
        
        # NOTE 点击上传按钮
        path = "//body/div[@id='app']/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/button[1]"
        self.browser.find(By.XPATH,path).click()
        time.sleep(Constant.USER_WAITING_TIME)
        # self.browser.get(Constant.BILIBILI_URL)
        
        # elem = self.browser.driver.find_elements_by_xpath("//*[contains(text(), '中文')]")
        # print(elem)
        # typ = self.browser.find(By.NAME, "中文（中国）" if zh else "英语（美国）") 
        # self.browser.driver.execute_script("$('.el-select-dropdown__list').children()[0].click()") 
        # time.sleep(Constant.USER_WAITING_TIME)
        # self.browser.driver.execute_script("$('button').children()[1].click()") 
        # time.sleep(Constant.USER_WAITING_TIME)

    
    def upload_yotube(self):
        try:
            self.youtube_login()
            return self.youtube_upload()
        except Exception as e:
            print(e)
            self.quit()
            raise
        
    def youtube_login(self,username="",password=""):
        username = username if username else self.username
        password = password if password else self.password

        self.browser.get(Constant.YOUTUBE_URL)
        time.sleep(Constant.USER_WAITING_TIME)

        if self.browser.has_cookies_for_current_website():
            self.browser.load_cookies()
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.refresh()
        else:
            self.browser.get('https://stackoverflow.com/users/signup?ssrc=head&returnurl=%2fusers%2fstory%2fcurrent%27')
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.find(By.XPATH,'//*[@id="openid-buttons"]/button[1]').click()
            self.browser.find(By.XPATH,'//input[@type="email"]').send_keys(username)
            self.browser.find(By.XPATH,'//*[@id="identifierNext"]').click()
            time.sleep(Constant.USER_WAITING_TIME*2)
            self.browser.find(By.XPATH,'//input[@type="password"]').send_keys(password)
            self.browser.find(By.XPATH,'//*[@id="passwordNext"]').click()
            time.sleep(Constant.USER_WAITING_TIME)
            
            # self.logger.info('Please sign in and then press enter')
            # input()
            self.browser.get(Constant.YOUTUBE_URL)
            time.sleep(Constant.USER_WAITING_TIME)
            self.browser.save_cookies()

    def youtube_upload(self) -> (bool, Optional[str]):
        # self.browser.get(Constant.YOUTUBE_URL)
        # time.sleep(Constant.USER_WAITING_TIME)
        self.browser.get(Constant.YOUTUBE_UPLOAD_URL)
        time.sleep(Constant.USER_WAITING_TIME)
        absolute_video_path = str(Path.cwd() / self.video_path)
        self.browser.find(By.XPATH, Constant.INPUT_FILE_VIDEO).send_keys(absolute_video_path)
        self.logger.debug('Attached video {}'.format(self.video_path))
        title_field = self.browser.find(By.ID, Constant.TEXTBOX)
        title_field.click()
        time.sleep(Constant.USER_WAITING_TIME)
        title_field.clear()
        time.sleep(Constant.USER_WAITING_TIME)
        title_field.send_keys(Keys.COMMAND + 'a')
        time.sleep(Constant.USER_WAITING_TIME)
        title_field.send_keys(self.metadata_dict[Constant.VIDEO_TITLE])
        self.logger.debug('The video title was set to \"{}\"'.format(self.metadata_dict[Constant.VIDEO_TITLE]))

        video_description = self.metadata_dict[Constant.VIDEO_DESCRIPTION]
        if video_description:
            description_container = self.browser.find(By.XPATH,
                                                      Constant.DESCRIPTION_CONTAINER)
            description_field = self.browser.find(By.ID, Constant.TEXTBOX, element=description_container)
            description_field.click()
            time.sleep(Constant.USER_WAITING_TIME)
            description_field.clear()
            time.sleep(Constant.USER_WAITING_TIME)
            description_field.send_keys(self.metadata_dict[Constant.VIDEO_DESCRIPTION])
            self.logger.debug(
                'The video description was set to \"{}\"'.format(self.metadata_dict[Constant.VIDEO_DESCRIPTION]))

        kids_section = self.browser.find(By.NAME, Constant.NOT_MADE_FOR_KIDS_LABEL)
        self.browser.find(By.ID, Constant.RADIO_LABEL, kids_section).click()
        self.logger.debug('Selected \"{}\"'.format(Constant.NOT_MADE_FOR_KIDS_LABEL))

        self.browser.find(By.ID, Constant.NEXT_BUTTON).click()
        self.logger.debug('Clicked {}'.format(Constant.NEXT_BUTTON))

        self.browser.find(By.ID, Constant.NEXT_BUTTON).click()
        self.logger.debug('Clicked another {}'.format(Constant.NEXT_BUTTON))

        public_main_button = self.browser.find(By.NAME, Constant.PRIVATE_BUTTON)
        self.browser.find(By.ID, Constant.RADIO_LABEL, public_main_button).click()
        self.logger.debug('Made the video {}'.format(Constant.PRIVATE_BUTTON))

        video_id = self.__get_video_id()

        status_container = self.browser.find(By.XPATH,
                                             Constant.STATUS_CONTAINER)
        while True:
            in_process = status_container.text.find(Constant.UPLOADED) != -1
            if in_process:
                time.sleep(Constant.USER_WAITING_TIME)
            else:
                break

        done_button = self.browser.find(By.ID, Constant.DONE_BUTTON)

        # Catch such error as
        # "File is a duplicate of a video you have already uploaded"
        if done_button.get_attribute('aria-disabled') == 'true':
            error_message = self.browser.find(By.XPATH,
                                              Constant.ERROR_CONTAINER).text
            self.logger.error(error_message)
            return False, None

        done_button.click()
        self.logger.debug("Published the video with video_id = {}".format(video_id))
        return True, video_id

    def __get_video_id(self) -> Optional[str]:
        video_id = None
        try:
            video_url_container = self.browser.find(By.XPATH, Constant.VIDEO_URL_CONTAINER)
            video_url_element = self.browser.find(By.XPATH, Constant.VIDEO_URL_ELEMENT,
                                                  element=video_url_container)
            video_id = video_url_element.get_attribute(Constant.HREF).split('/')[-1]
        except:
            self.logger.warning(Constant.VIDEO_NOT_FOUND_ERROR)
            pass
        return video_id

    def quit(self):
        self.browser.driver.quit()
