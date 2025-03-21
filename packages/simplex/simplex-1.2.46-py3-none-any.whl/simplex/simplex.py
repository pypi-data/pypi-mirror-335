import requests 
import atexit
from typing import Optional
from playwright.sync_api import sync_playwright
import os
import json

BASE_URL = "https://api.simplex.sh"

class Playwright:
    def __init__(self, simplex_instance):
        self.simplex = simplex_instance
        
    def click(self, locator: str, locator_type: str, exact: Optional[bool] = False, 
              element_index: Optional[str] = None, nth_index: Optional[int] = None, 
              locator_options: Optional[dict] = None):
        
        if element_index and element_index not in ["first", "last", "nth"]:
            raise ValueError("element_index must be 'first', 'last', or 'nth'")
        
        if element_index=="nth" and not nth_index:
            raise ValueError("nth_index is required when element_index is 'nth'")
        
        data = {
            'session_id': self.simplex.session_id,
            'locator': locator,
            'locator_type': locator_type,
        }     
        
        if element_index:
            data['element_index'] = element_index
            data['nth_index'] = nth_index

        if exact:
            data['exact'] = exact
            
        if locator_options:
            data['locator_options'] = json.dumps(locator_options)

        response = requests.post(
            f"{BASE_URL}/playwright/click",
            headers={
                'x-api-key': self.simplex.api_key
            },
            data=data
        )

        if 'succeeded' not in response.json():
            print(response.json())
            raise ValueError(f"It looks like the click action with playwright failed to return a response. Did you set your api_key when creating the Simplex class?")
        
        if response.json()["succeeded"]:
            return
        else:
            raise ValueError(f"Failed to click element: {response.json()['error']}")

class Simplex:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session_id = None
        atexit.register(self.close_session)
        self.playwright = Playwright(self)
        self.pw_browser = None
        self.pw = None
        
    def close_session(self):
        if self.pw_browser:
            try:
                self.pw_browser.close()
                self.pw_browser = None
            except Exception as e:
                print(f"Failed to close pw_browser: {e}")
        if self.pw:
            try:
                self.pw.stop()
                self.pw = None
            except Exception as e:
                print(f"Failed to stop pw: {e}")
        if not self.session_id:
            return
        response = requests.post(
            f"{BASE_URL}/close_session",
            headers={
                'x-api-key': self.api_key
            },
            data={'session_id': self.session_id}
        )
        self.session_id = None
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the close_session action failed to return a response. Did you set your api_key when creating the Simplex class?")
        if response.json()["succeeded"]:
            return
        else:
            raise ValueError(f"Failed to close session: {response.json()['error']}")

    def create_session(self, show_in_console: Optional[bool] = True, proxies: Optional[bool] = True, session_data: Optional[dict | str] = None):
        if session_data:
            if isinstance(session_data, dict):
                session_data_dict = session_data
            else:
                try:
                    # Try to parse as JSON string first
                    session_data_dict = json.loads(session_data)
                except json.JSONDecodeError:
                    # If parsing fails, treat as file path
                    try:
                        with open(session_data, 'r') as f:
                            session_data_dict = json.load(f)
                    except Exception as e:
                        raise ValueError(f"Failed to load session data. Input must be valid JSON string, dictionary, or path to JSON file. Error: {str(e)}")
            response = requests.post(
                f"{BASE_URL}/create_session",
                headers={
                    'x-api-key': self.api_key
                },
                data={'proxies': proxies, 'session_data': json.dumps(session_data_dict)}
            )
        else:
            response = requests.post(
                f"{BASE_URL}/create_session",
                headers={
                    'x-api-key': self.api_key
                },
                data={'proxies': proxies}
            )
        # Check for non-200 status code
        if response.status_code != 200:
            raise ValueError(f"Create session request failed with status code {response.status_code}: {response.text}")

        response_json = response.json()
        if 'session_id' not in response_json:
            raise ValueError(f"It looks like the session wasn't created successfully. Did you set your api_key when creating the Simplex class?")
        self.session_id = response_json['session_id']
        livestream_url = response_json['livestream_url']
        
        # Start Playwright without using context manager
        self.pw = sync_playwright().start()
        self.connect_url = response_json['connect_url']
        # self.pw_browser = self.pw.chromium.connect_over_cdp(response_json['connect_url'])

        if show_in_console:
            print(f"Livestream URL: {livestream_url}")

        return self.session_id, livestream_url

    def goto(self, url: str, cdp_url: str = None):
        if not cdp_url and not self.session_id:
            raise ValueError(f"Must call create_session before calling action goto with url='{url}'")
        
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url

        data = {'url': url}

        if cdp_url:
            data['cdp_url'] = cdp_url
        else:
            data['session_id'] = self.session_id

        response = requests.post(
            f"{BASE_URL}/goto",
            headers={
                'x-api-key': self.api_key
            },
            data=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the goto action failed to return a response. Did you set your api_key when creating the Simplex class?")
    
        if response.json()["succeeded"]:
            return
        else:
            raise ValueError(f"Failed to goto url: {response.json()['error']}")

    def click(self, element_description: str, cdp_url: str = None):
        if not cdp_url and not self.session_id:
            raise ValueError(f"Must call create_session before calling action click with element_description='{element_description}'")

        data = {'element_description': element_description}

        if cdp_url:
            data['cdp_url'] = cdp_url
        else:
            data['session_id'] = self.session_id

        response = requests.post(
            f"{BASE_URL}/click",
            headers={
                'x-api-key': self.api_key
            },
            data=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the click action failed to return a response. Did you set your api_key when creating the Simplex class?")
        if response.json()["succeeded"]:
            return response.json()["element_clicked"]
        else:
            raise ValueError(f"Failed to click element: {response.json()['error']}")

    def type(self, text: str, cdp_url: str = None):
        if not cdp_url and not self.session_id:
            raise ValueError(f"Must call create_session before calling action type with text='{text}'")

        data = {'text': text}

        if cdp_url:
            data['cdp_url'] = cdp_url
        else:
            data['session_id'] = self.session_id

        response = requests.post(
            f"{BASE_URL}/type",
            headers={
                'x-api-key': self.api_key
            },
            data=data
        )
        if response.json()["succeeded"]:
            return
        else:
            raise ValueError(f"Failed to type text: {response.json()['error']}")

    def press_enter(self, cdp_url: str = None):
        if not cdp_url and not self.session_id:
            raise ValueError("Must call create_session before calling action press_enter")

        data = {}

        if cdp_url:
            data['cdp_url'] = cdp_url
        else:
            data['session_id'] = self.session_id

        response = requests.post(
            f"{BASE_URL}/press_enter",
            headers={
                'x-api-key': self.api_key
            },
            data=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the press_enter action failed to return a response. Did you set your api_key when creating the Simplex class?")
        if response.json()["succeeded"]:
            return
        else:
            raise ValueError(f"Failed to press enter: {response.json()['error']}")
        
    def press_tab(self, cdp_url: str = None):
        if not cdp_url and not self.session_id:
            raise ValueError("Must call create_session before calling action press_tab")

        data = {}

        if cdp_url:
            data['cdp_url'] = cdp_url
        else:
            data['session_id'] = self.session_id

        response = requests.post(
            f"{BASE_URL}/press_tab",
            headers={
                'x-api-key': self.api_key
            },
            data=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the press_tab action failed to return a response. Did you set your api_key when creating the Simplex class?")
        if response.json()["succeeded"]:
            return
        else:
            raise ValueError(f"Failed to press tab: {response.json()['error']}")
        
    def delete_text(self, cdp_url: str = None):
        if not cdp_url and not self.session_id:
            raise ValueError("Must call create_session before calling action delete_text")

        data = {}

        if cdp_url:
            data['cdp_url'] = cdp_url
        else:
            data['session_id'] = self.session_id

        response = requests.post(
            f"{BASE_URL}/delete_text",
            headers={
                'x-api-key': self.api_key
            },
            data=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the delete_text action failed to return a response. Did you set your api_key when creating the Simplex class?")
        if response.json()["succeeded"]:
            return
        else:
            raise ValueError(f"Failed to delete text: {response.json()['error']}")

    def extract_bbox(self, element_description: str, cdp_url: str = None):
        if not cdp_url and not self.session_id:
            raise ValueError(f"Must call create_session before calling action extract_bbox with element_description='{element_description}'")

        data = {'element_description': element_description}

        if cdp_url:
            data['cdp_url'] = cdp_url
        else:
            data['session_id'] = self.session_id

        response = requests.get(
            f"{BASE_URL}/extract-bbox",
            headers={
                'x-api-key': self.api_key
            },
            params=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the extract_bbox action failed to return a response. Did you set your api_key when creating the Simplex class?")
        if response.json()["succeeded"]:
            return response.json()["bbox"]
        else:
            raise ValueError(f"Failed to extract bbox: {response.json()['error']}")

    def extract_text(self, element_description: str, cdp_url: str = None):
        if not cdp_url and not self.session_id:
            raise ValueError(f"Must call create_session before calling action extract_text with element_description='{element_description}'")

        data = {'element_description': element_description}

        if cdp_url:
            data['cdp_url'] = cdp_url
        else:
            data['session_id'] = self.session_id

        response = requests.post(
            f"{BASE_URL}/extract-text",
            headers={
                'x-api-key': self.api_key
            },
            data=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the extract_text action failed to return a response. Did you set your api_key when creating the Simplex class?")
        if response.json()["succeeded"]:
            return response.json()["text"]
        else:
            raise ValueError(f"Failed to extract text: {response.json()['error']}")

    def extract_image(self, element_description: str, cdp_url: str = None):
        if not cdp_url and not self.session_id:
            raise ValueError(f"Must call create_session before calling action extract_image with element_description='{element_description}'")

        data = {'element_description': element_description}

        if cdp_url:
            data['cdp_url'] = cdp_url
        else:
            data['session_id'] = self.session_id

        response = requests.get(
            f"{BASE_URL}/extract-image",
            headers={
                'x-api-key': self.api_key
            },
            params=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the extract_image action failed to return a response. Did you set your api_key when creating the Simplex class?")
        if response.json()["succeeded"]:
            return response.json()["image"]
        else:
            raise ValueError(f"Failed to extract image: {response.json()['error']}")

    def scroll(self, pixels: float, cdp_url: str = None):
        if not cdp_url and not self.session_id:
            raise ValueError(f"Must call create_session before calling action scroll with pixels={pixels}")

        data = {'pixels': pixels}

        if cdp_url:
            data['cdp_url'] = cdp_url
        else:
            data['session_id'] = self.session_id

        response = requests.post(
            f"{BASE_URL}/scroll",
            headers={
                'x-api-key': self.api_key
            },
            data=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the scroll action failed to return a response. Did you set your api_key when creating the Simplex class?")
        if response.json()["succeeded"]:
            return
        else:
            raise ValueError(f"Failed to scroll: {response.json()['error']}")

    def wait(self, milliseconds: int, cdp_url: str = None):
        if not cdp_url and not self.session_id:
            raise ValueError(f"Must call create_session before calling action wait with milliseconds={milliseconds}")

        data = {'milliseconds': milliseconds}

        if cdp_url:
            data['cdp_url'] = cdp_url
        else:
            data['session_id'] = self.session_id

        response = requests.post(
            f"{BASE_URL}/wait",
            headers={
                'x-api-key': self.api_key
            },
            data=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the wait action failed to return a response. Did you set your api_key when creating the Simplex class?")
        if response.json()["succeeded"]:
            return
        else:
            raise ValueError(f"Failed to wait: {response.json()['error']}")
    
    def create_login_session(self, url: str, save_directory: Optional[str] = None):
        def get_website_name(url: str) -> str:
            """Extract website name from URL"""
            from urllib.parse import urlparse
            netloc = urlparse(url).netloc
            # Remove www. if present
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            return netloc.replace(".", "_")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                channel="chrome",  
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-automation',
                ],
                ignore_default_args=['--enable-automation']
            )
            
            # Create context and pages
            context = browser.new_context()
            main_page = context.new_page()
            main_page.goto(url)
            
            # Create control page in same context
            control_page = context.new_page()
            control_page.set_content("""
                <html>
                <body style="display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f5f5f5;">
                    <button id="capture-btn" style="
                        padding: 20px 40px;
                        font-size: 18px;
                        cursor: pointer;
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    ">Click here when logged in to capture session</button>
                </body>
                </html>
            """)
            
            # Wait for button click using Playwright's wait_for_event
            control_page.wait_for_selector('#capture-btn')
            control_page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        document.getElementById('capture-btn').onclick = () => {
                            resolve(true);
                        }
                    });
                }
            """)
            
            # Use context.storage_state() instead of browser.storage_state()
            storage = context.storage_state()
            if save_directory:
                filename = os.path.join(save_directory, get_website_name(url) + "_session_data.json")
            else:
                filename = get_website_name(url) + "_session_data.json"
            
            with open(filename, 'w') as f:
                json.dump(storage, f, indent=2)
                
            print(f"Session data saved to '{filename}'")
            
            browser.close()

        return filename
    
    def restore_login_session(self, session_data: str, cdp_url: str = None):
        """
        Restore a login session from either a file path or a JSON string.
        
        Args:
            session_data: Either a file path to JSON file or a JSON string
            cdp_url: Optional CDP URL for remote debugging
        """
        try:
            # Try to parse as JSON string first
            session_data_dict = json.loads(session_data)
        except json.JSONDecodeError:
            # If parsing fails, treat as file path
            try:
                with open(session_data, 'r') as f:
                    session_data_dict = json.load(f)
            except Exception as e:
                raise ValueError(f"Failed to load session data. Input must be valid JSON string or path to JSON file. Error: {str(e)}")
        
        data = {
            'session_data': json.dumps(session_data_dict)
        }
        if cdp_url:
            data['cdp_url'] = cdp_url
        else:
            data['session_id'] = self.session_id
        
        response = requests.post(
            f"{BASE_URL}/restore_login_session",
            headers={
                'x-api-key': self.api_key
            },
            data=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the restore_login_session action failed to return a response. Did you set your api_key when creating the Simplex class?")
        if response.json()["succeeded"]:
            return
        else:
            raise ValueError(f"Failed to restore login session: {response.json()['error']}")

    def click_and_upload(self, element_description: str, file_path: str):
        if not self.session_id:
            raise ValueError(f"Must call create_session before calling action click_and_upload with element_description='{element_description}'")

        files = {
            'file': open(file_path, 'rb')
        }
        
        data = {
            'element_description': element_description
        }

        data['session_id'] = self.session_id

        response = requests.post(
            f"{BASE_URL}/click_and_upload",
            headers={
                'x-api-key': self.api_key
            },
            files=files,
            data=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the click_and_upload action failed to return a response. Did you set your api_key when creating the Simplex class?")
        if response.json()["succeeded"]:
            return
        else:
            raise ValueError(f"Failed to click and upload: {response.json()['error']}")
    
    def click_and_download(self, element_description: str):
        if not self.session_id:
            raise ValueError(f"Must call create_session before calling action click_and_download with element_description='{element_description}'")
        
        data = {
            'element_description': element_description
        }

        data['session_id'] = self.session_id

        response = requests.post(
            f"{BASE_URL}/click_and_download",
            headers={
                'x-api-key': self.api_key
            },
            data=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the click_and_download action failed to return a response. Did you set your api_key when creating the Simplex class?")
        if response.json()["succeeded"]:
            return response.json()["b64"], response.json()["filename"]
        else:
            raise ValueError(f"Failed to click and download: {response.json()['error']}")
    
    def exists(self, element_description: str, cdp_url: str = None):
        if not cdp_url and not self.session_id:
            raise ValueError(f"Must call create_session before calling action exists with element_description='{element_description}'")

        data = {'element_description': element_description}

        if cdp_url:
            data['cdp_url'] = cdp_url
        else:
            data['session_id'] = self.session_id

        response = requests.post(
            f"{BASE_URL}/exists",
            headers={
                'x-api-key': self.api_key
            },
            data=data
        )
        if 'succeeded' not in response.json():
            raise ValueError(f"It looks like the exists action failed to return a response. Did you set your api_key when creating the Simplex class?")
        response_json = response.json()
        if response_json['succeeded']:
            return response_json['exists'], response_json['reasoning']
        else:
            raise ValueError(f"Failed to check if element exists: {response_json['error']}")