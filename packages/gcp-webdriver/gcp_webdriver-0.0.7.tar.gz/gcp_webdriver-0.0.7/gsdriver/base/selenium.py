from __future__ import annotations
from gsdriver.base.abstract import SESSION_CONTEXT
from gsdriver.base.session import Info, Schema, Field, Flow, Process
from gsdriver.base.session import ITER_INDEX, PAGE_ITERATOR, iter_task
from gsdriver.base.gcloud import GoogleQueryList, GoogleUploadList

from gsdriver.base.spider import Spider, AsyncSpider, EncryptedSpider, EncryptedAsyncSpider
from gsdriver.base.spider import LoginSpider, LoginCookie, RangeFilter, SPIDER_KILL, ENCRYPTED_SPIDER_KILL
from gsdriver.base.spider import MAX_ASYNC_TASK_LIMIT, MAX_REDIRECT_LIMIT, RETRY, RETURN
from gsdriver.base.spider import ACTION, WHERE, WHICH, DRIVER_UNIQUE

from gsdriver.base.types import LogLevel, TypeHint, EncryptedKey, DecryptedKey
from gsdriver.base.types import IndexLabel, Keyword, Unit, Range, Timedelta, Timezone, JsonData

from gsdriver.utils.alert import AlertInfo
from gsdriver.utils.logs import log_messages
from gsdriver.utils.map import notna_dict, search_keyword, get_scala
from gsdriver.utils.request import get_headers, encode_params

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from seleniumwire import webdriver as webdriver_wire
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from seleniumwire.request import Request

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

import abc
import asyncio
import functools
import pyperclip
import requests
import time
import os
import subprocess

from typing import Any, Callable, Dict, List, Literal, Optional, Sequence, Tuple, Union
from numbers import Real
from bs4 import BeautifulSoup, Tag
from gzip import GzipFile
from io import BytesIO
import json
import re


SOURCE, BYTES, TEXT, JSON, HTML = "source", "bytes", "text", "json", "html"
REFRESH, REOPEN = 2, 3

class DriverError(NameError):
    def __init__(self, enableWire=False):
        message = f"Selenium{'-Wire' if enableWire else ''} WebDriver does not exist."
        super().__init__(message)

SELENIUM_SPIDER_KILL = (*SPIDER_KILL, DriverError)
SELENIUM_ENCRYPTED_SPIDER_KILL = (*ENCRYPTED_SPIDER_KILL, DriverError)


###################################################################
############################# Selenium ############################
###################################################################

def wait_element(func):
    @functools.wraps(func)
    def wrapper(element: WebElement, *args, delay=0.1, retry=0, **kwargs):
        for _ in range(retry):
            try: return func(element, *args, **kwargs)
            except NoSuchElementException:
                if delay: time.sleep(delay)
        return func(element, *args, **kwargs)
    return wrapper


@wait_element
def select_element(element: WebElement, selector: str, delay=0.1, retry=0) -> WebElement:
    return element.find_element(By.CSS_SELECTOR, selector)


@wait_element
def select_elements(element: WebElement, selector: str, if_null: Literal["pass","error"]="pass",
                    delay=0.1, retry=0) -> List[WebElement]:
    elements = element.find_elements(By.CSS_SELECTOR, selector)
    if (if_null == "error") and (len(elements) == 0):
        _raise_no_such_element_exception(selector)
    else: return elements


@wait_element
def click_text(element: WebElement, selector: str, value: str, if_null: Literal["pass","error"]="pass",
                exact=True, delay=0.1, retry=0):
    elements = element.find_elements(By.CSS_SELECTOR, selector)
    for __element in elements:
        if (__element.text.strip() == value) if exact else (value in __element.text):
            return __element.click()
    if if_null == "error":
        _raise_no_such_element_exception(selector)


def _raise_no_such_element_exception(selector: str):
    context = '{"method":"css selector","selector":"'+selector+'"}'
    raise NoSuchElementException("Message: no such element: Unable to locate element: "+context)


@wait_element
def input_text(element: WebElement, selector: str, value: str, clear=True, delay=0.1, retry=0):
    input = element.find_element(By.CSS_SELECTOR, selector)
    if clear: input.clear()
    input.send_keys(value)


@wait_element
def paste_text(element: WebElement, selector: str, value: str, delay=0.1, retry=0):
    input = element.find_element(By.CSS_SELECTOR, selector)
    input.click()
    pyperclip.copy(value)
    input.send_keys(Keys.CONTROL, 'v')


def wait_exists(element: WebElement, selector: str, delay=0.1):
    def select_element(element: WebElement, selector: str) -> bool:
        try: return isinstance(element.find_element(By.CSS_SELECTOR, selector), WebElement)
        except: return False
    while select_element(element, selector):
        time.sleep(delay)


def move_to_element(driver: webdriver.Chrome, element: Optional[WebElement]=None, selector=str(), delay=0.1, retry=0):
    actions = ActionChains(driver)
    if selector:
        element = select_element(driver, selector, delay=delay, retry=retry)
    actions.move_to_element(element).perform()


def scroll_to_bottom(driver: webdriver.Chrome):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def refresh_hard(driver: webdriver.Chrome):
    driver.execute_script("location.reload(true);")


def open_window(driver: webdriver.Chrome):
    driver.execute_script("window.open('');")


def switch_window(driver: webdriver.Chrome, index: int):
    driver.switch_to.window(driver.window_handles[index])


###################################################################
########################## Selenium-Wire ##########################
###################################################################

ResponseBody = Union[bytes, str, JsonData, Tag]
ResponseData = Union[ResponseBody, List[ResponseBody]]

RequestAttr = Union[Request, Dict[str,str], ResponseBody]
RequestData = Union[RequestAttr, List[RequestAttr]]

class NoSuchRequestException(NoSuchElementException):
    ...


def wait_request(func):
    @functools.wraps(func)
    def wrapper(driver: webdriver_wire.Chrome, *args, empty=True, delay=0.1, retry=0, **kwargs):
        for _ in range(retry):
            try: return func(driver, *args, empty=False, **kwargs)
            except NoSuchRequestException:
                if delay: time.sleep(delay)
        return func(driver, *args, empty=empty, **kwargs)
    return wrapper


def clear_request(func):
    @functools.wraps(func)
    def wrapper(driver: webdriver_wire.Chrome, *args, clear_requests=False, **kwargs):
        results = func(driver, *args, **kwargs)
        if clear_requests: del driver.requests
        return results
    return wrapper


def parse_safe(func):
    @functools.wraps(func)
    def wrapper(*args, safe=True, default=None, **kwargs):
        if safe:
            try: return func(*args, **kwargs)
            except: return default
        else: return func(*args, **kwargs)
    return wrapper


@wait_request
@clear_request
def get_requests(driver: webdriver_wire.Chrome, match: Dict[str,Any]=dict(), how: Literal["and","or"]="and", index: Optional[int]=None, attr=None,
                parse: Optional[Literal["bytes","text","json","html"]]=None, decoder: Optional[Callable[[bytes],bytes]]=None,
                safe=True, with_index=False, with_url=False, empty=True, delay=0.1, retry=0, clear_requests=False) -> RequestData:
    results = list()
    for __index, __request in enumerate(driver.requests):
        if _match_request(__request, match, how, parse=parse, decoder=decoder, safe=safe):
            __result = parse_request(__request, attr, parse=parse, decoder=decoder, safe=safe)
            if __result is not None:
                if with_index: results.append((__index, __result))
                elif with_url: results.append((__request.url, __result))
                else: results.append(__result)
    if not (empty or results):
        raise NoSuchRequestException("Message: no such request")
    elif isinstance(index, int):
        return get_scala(results, index, default=((None, None) if with_index or with_url else None))
    else: return results


def _match_request(request: Request, match: Dict[str,Any], how: Literal["and","or"]="and", safe=True, **kwargs) -> bool:
    if not match: return True
    elif how == "and": return _match_request_and(request, match, safe=safe, **kwargs)
    elif how == "or": return _match_request_or(request, match, safe=safe, **kwargs)
    else: return False


def _match_request_and(request: Request, match: Dict[str,Any], safe=True, **kwargs) -> bool:
    __match = True
    for __attr, __func in match.items():
        try:
            if __attr == "response":
                for __attr, __func in (__func if isinstance(__func, Dict) else dict()).items():
                    if __attr == "body": __match &= _match_response_body(request, __func, safe=safe, default=False, **kwargs)
                    else: __match &= _match_attr(getattr(request.response, __attr), __func, safe=safe, default=False)
            else: __match &= _match_attr(getattr(request, __attr), __func, safe=safe, default=False)
        except: return False
    return __match


def _match_request_or(request: Request, match: Dict[str,Any], safe=True, **kwargs) -> bool:
    for __attr, __func in match.items():
        try:
            if __attr == "response":
                for __attr, __func in (__func if isinstance(__func, Dict) else dict()).items():
                    if __attr == "body":
                        if _match_response_body(request, __func, safe=safe, default=False, **kwargs): return True
                        else: pass
                    elif _match_attr(getattr(request.response, __attr), __func, safe=safe, default=False): return True
                    else: pass
            elif _match_attr(getattr(request, __attr), __func, safe=safe, default=False): return True
            else: pass
        except: pass
    return False


@parse_safe
def _match_attr(attr: Any, match: Any, safe=True, default=None) -> bool:
    if isinstance(match, Callable): return match(attr)
    elif isinstance(match, re.Pattern): return bool(match.search(_decode_attr(attr)))
    elif isinstance(match, Sequence): return search_keyword(_decode_attr(attr), match)
    else: return False


@parse_safe
def _match_response_body(request: Request, match: Any, parse: Optional[Literal["bytes","text","json","html"]]=None,
                    decoder: Optional[Callable[[bytes],bytes]]=None, safe=True, default=None) -> bool:
    if isinstance(match, Callable):
        return match(parse_request(request, None, parse, decoder, safe=False))
    elif isinstance(match, re.Pattern):
        return bool(match.search(parse_request(request, parse=TEXT, decoder=decoder, safe=False, default=str())))
    elif isinstance(match, Sequence):
        return search_keyword(parse_request(request, parse=TEXT, decoder=decoder), match, safe=False, default=str())
    else: return False


@parse_safe
def parse_request(request: Request, attr=None, parse: Optional[Literal["bytes","text","json","html"]]=None,
                decoder: Optional[Callable[[bytes],bytes]]=None, safe=True, default=None) -> RequestAttr:
    if attr or parse:
        __attr = getattr(request, attr) if attr else _get_response_body(request, decoder)
        if parse == BYTES: return _encode_attr(__attr)
        elif parse == TEXT: return _decode_attr(__attr)
        elif parse == JSON: return json.loads(__attr)
        elif parse == HTML: return BeautifulSoup(__attr, "html.parser")
        else: return __attr
    else: return request


def _get_response_body(request: Request, decoder: Optional[Callable[[bytes],bytes]]=None) -> bytes:
    decoder = gzip_decoder if isinstance(decoder, str) and decoder == "gzip" else decoder
    return decoder(request.response.body) if isinstance(decoder, Callable) else request.response.body


def _encode_attr(attr: Any) -> bytes:
    if isinstance(attr, bytes): return attr
    elif isinstance(attr, (List,Dict)):
        return json.dumps(attr, ensure_ascii=False).encode("utf-8")
    else: return str(attr).encode("utf-8")


def _decode_attr(attr: Any) -> str:
    return attr.decode("utf-8") if isinstance(attr, bytes) else str(attr)


def gzip_decoder(body: bytes) -> bytes:
    with GzipFile(fileobj=BytesIO(body)) as f:
        return f.read()


###################################################################
########################## Selenium Base ##########################
###################################################################

Port = Union[str,int]

class SeleniumBase(webdriver.Chrome):
    process = None

    def set_service(self, chromePath=str(), debuggingPort: Optional[Port]=None, debuggingDir=str(),
                    proxyPort: Optional[Port]=None, incognito=False) -> Service:
        if chromePath:
            if self.validate_port(debuggingPort) and debuggingDir:
                self.run_debugging(chromePath, debuggingPort, debuggingDir, proxyPort, incognito)
            else: return Service(executable_path=chromePath)
        try: return Service(executable_path=ChromeDriverManager().install())
        except: return Service(executable_path=r".\chromedriver.exe")

    def set_options(self, downloadPath=str(), headless=False, incognito=False, loadImages=True, disableProxy=False, ignoreCert=False,
                    extensions: List[str]=list(), debuggingPort: Optional[Port]=None, proxyPort: Optional[Port]=None) -> Options:
        options = Options()
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-blink-features=AutomationControlled")
        if headless: self._add_headless_options(options)
        if incognito: options.add_argument("--incognito")
        if disableProxy: options.add_argument("--disable-proxy-certificate-handler")
        if ignoreCert: options.add_argument("--ignore-certificate-errors")
        if extensions: self._add_extensions(options, extensions)
        if self.validate_port(proxyPort): options.add_argument(f"--proxy-server=http://localhost:{proxyPort}")
        self._add_experimental_options(options, downloadPath, loadImages, debuggingPort)
        return options

    def _add_headless_options(self, options: Options, gpu=False, windowSize="1920x1080"):
        options.add_argument("--headless")
        if not gpu: options.add_argument("--disable-gpu")
        if windowSize: options.add_argument(f"--window-size={windowSize}")
        options.add_argument("user-agent="+get_headers()["User-Agent"])

    def _add_extensions(self, options: Options, extensions: List[str]):
        for __extension in extensions:
            if os.path.exists(__extension): options.add_extension(__extension)

    def _add_experimental_options(self, options: Options, downloadPath=str(), loadImages=True, debuggingPort: Optional[Port]=None):
        prefs = dict()
        if downloadPath:
            prefs["download.default_directory"] = os.path.abspath(downloadPath)
            prefs["download.prompt_for_download"] = False
            prefs["download.directory_upgrade"] = True
        if not loadImages: prefs["profile.managed_default_content_settings.images"] = 2
        if prefs: options.add_experimental_option("prefs", prefs)
        if self.validate_port(debuggingPort): options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debuggingPort}")

    def set_timeout_and_wait(self, loadTimeout: Optional[float]=None, implicitlyWait: Optional[float]=None):
        if isinstance(loadTimeout, (float,int)) and (loadTimeout > 0.):
            self.set_page_load_timeout(loadTimeout)
        if isinstance(implicitlyWait, (float,int)) and (implicitlyWait > 0.):
            self.implicitly_wait(implicitlyWait)

    ###################################################################
    ########################### Debug Driver ##########################
    ###################################################################

    def run_debugging(self, chromePath: str, debuggingPort: int, debuggingDir: str, proxyPort: Optional[Port]=None, incognito=False) -> Service:
        command = f'"{chromePath}" --remote-debugging-port={debuggingPort} --user-data-dir="{debuggingDir}"'
        if self.validate_port(proxyPort): command += f" --proxy-server=localhost:{proxyPort}"
        if incognito: command = command + " --incognito"
        self.process = subprocess.Popen(command)

    def exit_debugging(self):
        try:
            if isinstance(self.process, subprocess.Popen) and (self.process.poll() is None):
                self.process.terminate()
        except: return

    def validate_port(self, port: Optional[Port]=None) -> bool:
        if port is None: return False
        elif isinstance(port, int): return True
        else: return str(port).isdecimal()

    ###################################################################
    ########################## Request Driver #########################
    ###################################################################

    def catch_exception(func):
        @functools.wraps(func)
        def wrapper(self: SeleniumBase, *args, ignore_exception=False, **context):
            if ignore_exception:
                try: return func(self, *args, **context)
                except: return None
            else: return func(self, *args, **context)
        return wrapper

    @catch_exception
    def get(self, url: str, params=None, headers=None, parse: Optional[Literal["text","json","html"]]=None,
            delay: Optional[Real]=None, ignore_exception=False) -> Union[str,JsonData,Tag]:
        super().get(encode_params(url, params) if isinstance(params, (Dict,Sequence)) and params else url)
        if isinstance(delay, (float,int)) and delay:
            time.sleep(delay)
        return self.get_page_source(parse)

    @catch_exception
    def get_page_source(self, parse: Optional[Literal["text","json","html"]]=None, ignore_exception=False) -> Union[str,JsonData,Tag]:
        if parse == TEXT: return BeautifulSoup(self.page_source, "html.parser").text
        elif parse == JSON: return json.loads(BeautifulSoup(self.page_source, "html.parser").text)
        elif parse == HTML: return BeautifulSoup(self.page_source, "html.parser")
        else: return self.page_source

    ###################################################################
    ######################### Selenium Method #########################
    ###################################################################

    def select_element(self, selector: str, delay=0.1, retry=0) -> WebElement:
        return select_element(self, selector, delay=delay, retry=retry)

    def select_elements(self, selector: str, if_null: Literal["pass","error"]="pass",
                        delay=0.1, retry=0) -> List[WebElement]:
        return select_elements(self, selector, if_null=if_null, delay=delay, retry=retry)

    def click_text(self, selector: str, value: str, if_null: Literal["pass","error"]="pass",
                    exact=True, delay=0.1, retry=0):
        click_text(self, selector, value, if_null=if_null, exact=exact, delay=delay, retry=retry)

    def input_text(self, selector: str, value: str, clear=True, delay=0.1, retry=0):
        input_text(self, selector, value, clear=clear, delay=delay, retry=retry)

    def paste_text(self, selector: str, value: str, delay=0.1, retry=0):
        paste_text(self, selector, value, delay=delay, retry=retry)

    def wait_exists(self, selector: str, delay=0.1):
        wait_exists(self, selector, delay)

    def move_to_element(self, element: Optional[WebElement]=None, selector=str(), delay=0.1, retry=0):
        move_to_element(self, element, selector, delay=delay, retry=retry)

    def scroll_to_bottom(self, delay=0.):
        scroll_to_bottom(self)
        if delay: time.sleep(delay)

    def refresh_hard(self, delay=0.):
        refresh_hard(self)
        if delay: time.sleep(delay)

    def open_window(self, delay=0.):
        open_window(self)
        if delay: time.sleep(delay)

    def switch_window(self, index: int, delay=0.):
        switch_window(self, index)
        if delay: time.sleep(delay)


###################################################################
######################### Selenium Driver #########################
###################################################################

class SeleniumDriver(SeleniumBase):
    def __init__(self, chromePath=str(), downloadPath=str(), headless=False, incognito=False, loadImages=True, disableProxy=False,
                ignoreCert=False, loadTimeout: Optional[float]=None, implicitlyWait: Optional[float]=None, extensions: List[str]=list(),
                debuggingPort: Optional[Port]=None, debuggingDir=str(), proxyPort: Optional[Port]=None, **kwargs):
        service = self.set_service(chromePath, debuggingPort, debuggingDir, proxyPort, incognito)
        options = self.set_options(downloadPath, headless, incognito, loadImages, disableProxy, ignoreCert, extensions, debuggingPort, proxyPort)
        super().__init__(service=service, options=options)
        self.set_timeout_and_wait(loadTimeout, implicitlyWait)

    def __exit__(self, exc_type, exe, traceback):
        super().__exit__(exc_type, exe, traceback) # quit()
        self.exit_debugging()

    def close(self):
        super().close()
        self.exit_debugging()

    def quit(self):
        super().quit()
        self.exit_debugging()

    def get_cookies(self, encode=True, raw=False) -> Union[str,Dict,List]:
        if raw: return super().get_cookies()
        elif encode: return '; '.join([f'{cookie["name"]}={cookie["value"]}' for cookie in super().get_cookies()])
        else: return {cookie["name"]: cookie["value"] for cookie in super().get_cookies()}

    def set_cookies(self, session: requests.Session):
        for cookie in self.get_cookies(raw=True):
            kwargs = dict(domain=cookie.get("domain"), path=cookie.get("path"), secure=cookie.get("secure",False), expires=cookie.get("expiry"))
            session.cookies.set(cookie["name"], cookie["value"], **kwargs)


###################################################################
########################## Selenium Wire ##########################
###################################################################

class SeleniumWireDriver(webdriver_wire.Chrome, SeleniumBase):
    def __init__(self, chromePath=str(), downloadPath=str(), headless=False, incognito=False, loadImages=True, disableProxy=False,
                ignoreCert=False, loadTimeout: Optional[float]=None, implicitlyWait: Optional[float]=None, extensions: List[str]=list(),
                debuggingPort: Optional[Port]=None, debuggingDir=str(), proxyPort: Optional[Port]=None, **kwargs):
        service = self.set_service(chromePath, debuggingPort, debuggingDir, proxyPort, incognito)
        options = self.set_options(downloadPath, headless, incognito, loadImages, disableProxy, ignoreCert, extensions, debuggingPort, proxyPort)
        seleniumwire_options = dict(port=int(proxyPort)) if self.validate_port(proxyPort) else None
        webdriver_wire.Chrome.__init__(self, service=service, options=options, seleniumwire_options=seleniumwire_options)
        self.set_timeout_and_wait(loadTimeout, implicitlyWait)

    def __exit__(self, exc_type, exe, traceback):
        webdriver_wire.Chrome.__exit__(self, exc_type, exe, traceback) # quit()
        self.exit_debugging()

    def close(self):
        webdriver_wire.Chrome.close(self)
        self.exit_debugging()

    def quit(self):
        webdriver_wire.Chrome.quit(self)
        self.exit_debugging()

    @SeleniumBase.catch_exception
    def get(self, url: str, params=None, headers=None, parse: Optional[Literal["text","json","html"]]=None,
                delay: Optional[Real]=None, ignore_exception=False) -> Union[str,JsonData,Tag]:
        if isinstance(headers, Dict):
            self.set_headers(headers)
        webdriver_wire.Chrome.get(self, encode_params(url, params) if isinstance(params, (Dict,Sequence)) and params else url)
        if isinstance(delay, (float,int)) and delay:
            time.sleep(delay)
        return self.get_page_source(parse)

    def get_cookies(self, encode=True, raw=False) -> Union[str,Dict,List]:
        if raw: return super().get_cookies()
        elif encode: return '; '.join([cookie["name"]+'='+cookie["value"] for cookie in super().get_cookies()])
        else: return {cookie["name"]: cookie["value"] for cookie in super().get_cookies()}

    def set_cookies(self, session: requests.Session):
        for cookie in self.get_cookies(raw=True):
            kwargs = dict(domain=cookie.get("domain"), path=cookie.get("path"), secure=cookie.get("secure",False), expires=cookie.get("expiry"))
            session.cookies.set(cookie["name"], cookie["value"], **kwargs)

    def set_headers(self, headers: Dict[str,str]):
        def interceptor(request: Request):
            for __key, __value in headers.items():
                request.headers[__key] = __value
        self.request_interceptor = interceptor

    def get_requests(self, match: Dict[str,Any]=dict(), how: Literal["and","or"]="and", index: Optional[int]=None, attr=None,
                    parse: Optional[Literal["bytes","text","json","html"]]=None, decoder: Optional[Callable[[bytes],bytes]]=None,
                    safe=True, with_index=False, with_url=False, empty=True, delay=0.1, retry=0, clear_requests=False) -> RequestData:
        kwargs = dict(empty=empty, delay=delay, retry=retry, clear_requests=clear_requests)
        return get_requests(self, match, how, index, attr, parse, decoder, safe, with_index, with_url, **kwargs)


###################################################################
######################### Selenium Spider #########################
###################################################################

ChromeDriver = Union[SeleniumDriver,SeleniumWireDriver]

class SeleniumSpider(Spider):
    __metaclass__ = abc.ABCMeta
    asyncio = False
    operation = "spider"
    host = str()
    where = WHERE
    which = WHICH
    verb = ACTION
    by = str()
    fields = list()
    ranges = list()
    iterateArgs = list()
    iterateCount = dict()
    iterateProduct = list()
    iterateUnit = 1
    redirectUnit = 1
    pagination = False
    pageFrom = 1
    offsetFrom = 1
    pageUnit = 0
    pageLimit = 0
    interval = None
    fromNow = None
    timeout = None
    ssl = None
    numRetries = 0
    delay = 1.
    interruptType = tuple()
    killType = tuple()
    errorType = tuple()
    responseType = "records"
    returnType = "records"
    mappedReturn = False
    root = list()
    groupby = list()
    groupSize = dict()
    countby = str()
    driver = None
    enableWire = False
    info = Info()
    flow = Flow()

    def __init__(self, fields: Optional[IndexLabel]=None, ranges: Optional[RangeFilter]=None, returnType: Optional[TypeHint]=None,
                tzinfo: Optional[Timezone]=None, countryCode=str(), datetimeUnit: Optional[Literal["second","minute","hour","day"]]=None,
                logName: Optional[str]=None, logLevel: LogLevel="WARN", logFile: Optional[str]=None, localSave=False,
                debugPoint: Optional[Keyword]=None, killPoint: Optional[Keyword]=None, extraSave: Optional[Keyword]=None,
                numRetries: Optional[int]=None, delay: Range=1., cookies: Optional[str]=None,
                fromNow: Optional[Unit]=None, discard=True, progress=True, where=str(), which=str(), by=str(), message=str(),
                iterateUnit: Optional[int]=None, interval: Optional[Timedelta]=None, apiRedirect=False, redirectUnit: Optional[int]=None,
                queryList: GoogleQueryList=list(), uploadList: GoogleUploadList=list(), alertInfo: AlertInfo=dict(),
                driverOptions: Optional[Dict]=None, reopenDelay: Range=30., **context):
        Spider.__init__(self, **self.from_locals(locals(), drop=DRIVER_UNIQUE))
        self.set_driver_options(driverOptions, reopenDelay)

    def find_driver(self, driver: Optional[ChromeDriver]=None, **context) -> ChromeDriver:
        __class = SeleniumWireDriver if self.enableWire else SeleniumDriver
        if isinstance(driver, __class): return driver
        elif isinstance(self.driver, __class): return self.driver
        else: raise DriverError(self.enableWire)

    def get_driver_options(self, driverOptions: Optional[Dict]=None, **context) -> Dict:
        return driverOptions if isinstance(driverOptions, Dict) else dict()

    def set_driver_options(self, driverOptions: Optional[Dict]=None, reopenDelay: Range=30.):
        if isinstance(driverOptions, Dict) and driverOptions:
            options = dict(driverOptions=driverOptions, reopenDelay=reopenDelay)
        else: options = dict(reopenDelay=reopenDelay)
        self.update(options)

    ###################################################################
    ######################### Driver Managers #########################
    ###################################################################

    def init_driver(func):
        @functools.wraps(func)
        def wrapper(self: SeleniumSpider, *args, self_var=True, **context):
            args, context = self.init_context(args, context, self_var=self_var)
            self.run_driver(**self.get_driver_options(**context))
            try: data = func(self, *args, **SESSION_CONTEXT(**context))
            finally: self.quit_driver()
            self.with_data(data, func=func.__name__, **context)
            return data
        return wrapper

    def with_driver(func):
        @functools.wraps(func)
        def wrapper(self: SeleniumSpider, *args, **context):
            self.run_driver(**self.get_driver_options(**context))
            try: data = func(self, *args, **context)
            finally: self.quit_driver()
            return data
        return wrapper

    def is_kill(self, exception: Exception) -> bool:
        return isinstance(exception, SELENIUM_SPIDER_KILL) or isinstance(exception, self.killType)

    ###################################################################
    ############################ Run Driver ###########################
    ###################################################################

    def run_driver(self, **options):
        self.driver = SeleniumWireDriver(**options) if self.enableWire else SeleniumDriver(**options)

    @Spider.ignore_exception
    def quit_driver(self, clear=False, delay=0.25):
        if clear: self.driver.delete_all_cookies()
        self.driver.quit()
        self.sleep(delay)

    def reopen_driver(self, driverOptions: Dict=dict(), reopenDelay: Range=30.):
        self.quit_driver(clear=True, delay=0.)
        self.sleep(reopenDelay, minimum=1.)
        self.run_driver(**driverOptions)

    @Spider.ignore_exception
    def refresh_driver(self, how: Literal["normal","hard"]="normal", delay: Optional[Range]=None):
        if how == "hard": self.driver.refresh_hard()
        else: self.driver.refresh()
        self.sleep(delay)

    def interrupt(self, *args, exception: Exception, func: Callable, retryCount=0, reopenDelay: Range=30., **context) -> Tuple[int,Any]:
        if self.driver is not None:
            self.reopen_driver(self.get_driver_options(**context), reopenDelay)
            return super().interrupt(*args, exception=exception, func=func, retryCount=retryCount, **context)
        else: raise exception

    def interrupt_by_count(self, numRetries=0, retryCount=0, reopenDelay=30., delay: Optional[Range]=None,
                            refresh: Literal["auto","normal","hard"]="auto", **context) -> int:
        if (numRetries > 1) and (retryCount == 0):
            self.reopen_driver(self.get_driver_options(**context), reopenDelay)
            return REOPEN
        elif (numRetries != retryCount) and (retryCount > 0):
            if refresh == "auto":
                refresh = "normal" if ((numRetries-1) == retryCount) and (retryCount > 0) else "hard"
            self.refresh_driver(delay=delay, how=refresh)
            return REFRESH
        else: RETURN

    ###################################################################
    ########################## Request Driver #########################
    ###################################################################

    def driver_required(func):
        @functools.wraps(func)
        def wrapper(self: SeleniumSpider, *args, driver: Optional[ChromeDriver]=None, **context):
            return func(self, *args, driver=self.find_driver(driver), **context)
        return wrapper

    @driver_required
    def request_driver(self, how: Literal["source","text","json","html"], url: str, params=None, headers=None,
                        delay: Optional[Range]=None, ignore_exception=False, *args,
                        driver: ChromeDriver, **context) -> Union[str,JsonData,Tag]:
        messages = notna_dict(params=params, headers=headers)
        self.logger.debug(log_messages(**notna_dict({ITER_INDEX: context.get(ITER_INDEX)}), url=url, params=params, dump=self.logJson))
        self.checkpoint(iter_task(context, "request"), where="request_driver", msg=dict(url=url, **messages))
        response = driver.get(url, **messages, parse=None, delay=self.get_delay(delay), ignore_exception=ignore_exception)
        self.logger.info(dict(url=url, **{"contents-length":len(response)}, **self.get_iterator(**context, _index=True)))
        self.checkpoint(iter_task(context, "response"), where="request_driver", msg={"response":response}, save=response)
        return driver.get_page_source(how, ignore_exception=ignore_exception) if how != SOURCE else response

    @driver_required
    def get_page_source(self, parse: Optional[Literal["text","json","html"]]=None, ignore_exception=False, *args,
                        driver: ChromeDriver, **context) -> Union[str,JsonData,Tag]:
        return driver.get_page_source(parse, ignore_exception=ignore_exception)

    ###################################################################
    ########################## Selenium Wire ##########################
    ###################################################################

    def wire_required(func):
        @functools.wraps(func)
        def wrapper(self: SeleniumSpider, *args, driver: Optional[SeleniumWireDriver]=None, **context):
            if self.enableWire:
                return func(self, *args, driver=self.find_driver(driver), **context)
            else: raise DriverError(enableWire=True)
        return wrapper

    @wire_required
    def get_driver_response(self, match: Dict[str,Any]=dict(), how: Literal["and","or"]="and", index: Optional[int]=None,
                            parse: Optional[Literal["bytes","text","json","html"]]=None, decoder: Optional[Callable[[bytes],bytes]]=None,
                            safe=True, empty=True, delay=0.1, retry=0, clear_requests=False, *args,
                            driver: Optional[SeleniumWireDriver]=None, **context) -> ResponseData:
        kwargs = dict(empty=empty, delay=delay, retry=retry, clear_requests=clear_requests)
        response = driver.get_requests(match, how, index, None, parse, decoder, safe, with_url=True, **kwargs)
        for __url, __response in ([response] if isinstance(index, int) else response):
            self.checkpoint(iter_task(context, "driver"), where="get_response", msg={"response":__response}, save=__response)
            self.logger.debug(log_messages(url=__url, match=match, dump=self.logJson))
        return response[1] if isinstance(index, int) else [__response[1] for __response in response]

    ###################################################################
    ######################### Selenium Method #########################
    ###################################################################

    def select_element(self, element: WebElement, selector: str, delay=0.1, retry=0) -> WebElement:
        return select_element(element, selector, delay=delay, retry=retry)

    def select_elements(self, element: WebElement, selector: str, if_null: Literal["pass","error"]="pass",
                        delay=0.1, retry=0) -> List[WebElement]:
        return select_elements(element, selector, if_null=if_null, delay=delay, retry=retry)

    def click_text(self, element: WebElement, selector: str, value: str, if_null: Literal["pass","error"]="pass",
                    exact=True, delay=0.1, retry=0):
        click_text(element, selector, value, if_null=if_null, exact=exact, delay=delay, retry=retry)

    def input_text(self, element: WebElement, selector: str, value: str, clear=True, delay=0.1, retry=0):
        input_text(element, selector, value, clear=clear, delay=delay, retry=retry)

    def paste_text(self, element: WebElement, selector: str, value: str, delay=0.1, retry=0):
        paste_text(element, selector, value, delay=delay, retry=retry)

    def wait_exists(self, element: WebElement, selector: str, delay=0.1):
        wait_exists(element, selector, delay)

    def move_to_element(self, driver: webdriver.Chrome, element: Optional[WebElement]=None, selector=str(), delay=0.1, retry=0):
        move_to_element(driver, element, selector, delay=delay, retry=retry)


###################################################################
###################### Selenium Async Spider ######################
###################################################################

class SeleniumAsyncSpider(AsyncSpider, SeleniumSpider):
    __metaclass__ = abc.ABCMeta
    asyncio = True
    operation = "spider"
    host = str()
    where = WHERE
    which = WHICH
    verb = ACTION
    by = str()
    fields = list()
    ranges = list()
    iterateArgs = list()
    iterateCount = dict()
    iterateProduct = list()
    iterateUnit = 1
    maxLimit = MAX_ASYNC_TASK_LIMIT
    redirectUnit = 1
    redirectLimit = MAX_REDIRECT_LIMIT
    pagination = False
    pageFrom = 1
    offsetFrom = 1
    pageUnit = 0
    pageLimit = 0
    interval = None
    fromNow = None
    timeout = None
    ssl = None
    numRetries = 0
    delay = 1.
    interruptType = tuple()
    killType = tuple()
    errorType = tuple()
    responseType = "records"
    returnType = "records"
    mappedReturn = False
    root = list()
    groupby = list()
    groupSize = dict()
    countby = str()
    driver = None
    enableWire = False
    info = Info()
    flow = Flow()

    def __init__(self, fields: Optional[IndexLabel]=None, ranges: Optional[RangeFilter]=None, returnType: Optional[TypeHint]=None,
                tzinfo: Optional[Timezone]=None, countryCode=str(), datetimeUnit: Optional[Literal["second","minute","hour","day"]]=None,
                logName: Optional[str]=None, logLevel: LogLevel="WARN", logFile: Optional[str]=None, localSave=False,
                debugPoint: Optional[Keyword]=None, killPoint: Optional[Keyword]=None, extraSave: Optional[Keyword]=None,
                numRetries: Optional[int]=None, delay: Range=1., cookies: Optional[str]=None, numTasks=100,
                fromNow: Optional[Unit]=None, discard=True, progress=True, where=str(), which=str(), by=str(), message=str(),
                iterateUnit: Optional[int]=None, interval: Optional[Timedelta]=None, apiRedirect=False, redirectUnit: Optional[int]=None,
                queryList: GoogleQueryList=list(), uploadList: GoogleUploadList=list(), alertInfo: AlertInfo=dict(),
                driverOptions: Optional[Dict]=None, reopenDelay: Range=30., **context):
        AsyncSpider.__init__(self, **self.from_locals(locals(), drop=DRIVER_UNIQUE))
        self.set_driver_options(driverOptions, reopenDelay)

    def init_driver(func):
        @functools.wraps(func)
        async def wrapper(self: SeleniumSpider, *args, self_var=True, **context):
            args, context = self.init_context(args, context, self_var=self_var)
            self.run_driver(**self.get_driver_options(**context))
            try: data = await func(self, *args, **SESSION_CONTEXT(**context))
            finally: self.quit_driver()
            self.with_data(data, func=func.__name__, **context)
            return data
        return wrapper

    def with_driver(func):
        @functools.wraps(func)
        async def wrapper(self: SeleniumSpider, *args, **context):
            self.run_driver(**self.get_driver_options(**context))
            try: data = await func(self, *args, **context)
            finally: self.quit_driver()
            return data
        return wrapper

    async def interrupt(self, *args, exception: Exception, func: Callable, retryCount=0, reopenDelay: Range=30., **context) -> Tuple[int,Any]:
        if self.driver is not None:
            self.reopen_driver(self.get_driver_options(**context), reopenDelay)
            return await super().interrupt(*args, exception=exception, func=func, retryCount=retryCount, **context)
        else: raise exception

    def is_kill(self, exception: Exception) -> bool:
        return isinstance(exception, SELENIUM_SPIDER_KILL) or isinstance(exception, self.killType)


###################################################################
#################### Selenium Encrypted Spider ####################
###################################################################

class SeleniumEncryptedSpider(SeleniumSpider, EncryptedSpider):
    __metaclass__ = abc.ABCMeta
    asyncio = False
    operation = "spider"
    host = str()
    where = WHERE
    which = WHICH
    verb = ACTION
    by = str()
    fields = list()
    ranges = list()
    iterateArgs = list()
    iterateCount = dict()
    iterateProduct = list()
    iterateUnit = 1
    redirectUnit = 1
    pagination = False
    pageFrom = 1
    offsetFrom = 1
    pageUnit = 0
    pageLimit = 0
    interval = None
    fromNow = None
    timeout = None
    ssl = None
    numRetries = 0
    delay = 1.
    interruptType = tuple()
    killType = tuple()
    errorType = tuple()
    responseType = "records"
    returnType = "records"
    mappedReturn = False
    root = list()
    groupby = list()
    groupSize = dict()
    countby = str()
    auth = LoginSpider
    authKey = list()
    decryptedKey = dict()
    driver = None
    enableWire = False
    info = Info()
    flow = Flow()

    def __init__(self, fields: Optional[IndexLabel]=None, ranges: Optional[RangeFilter]=None, returnType: Optional[TypeHint]=None,
                tzinfo: Optional[Timezone]=None, countryCode=str(), datetimeUnit: Optional[Literal["second","minute","hour","day"]]=None,
                logName: Optional[str]=None, logLevel: LogLevel="WARN", logFile: Optional[str]=None, localSave=False,
                debugPoint: Optional[Keyword]=None, killPoint: Optional[Keyword]=None, extraSave: Optional[Keyword]=None,
                numRetries: Optional[int]=None, delay: Range=1., cookies: Optional[str]=None,
                fromNow: Optional[Unit]=None, discard=True, progress=True, where=str(), which=str(), by=str(), message=str(),
                iterateUnit: Optional[int]=None, interval: Optional[Timedelta]=None, apiRedirect=False, redirectUnit: Optional[int]=None,
                queryList: GoogleQueryList=list(), uploadList: GoogleUploadList=list(), alertInfo: AlertInfo=dict(),
                encryptedKey: Optional[EncryptedKey]=None, decryptedKey: Optional[DecryptedKey]=None,
                driverOptions: Optional[Dict]=None, reopenDelay: Range=30., **context):
        EncryptedSpider.__init__(self, **self.from_locals(locals(), drop=DRIVER_UNIQUE))
        self.set_driver_options(driverOptions, reopenDelay)

    def login_driver(func):
        @functools.wraps(func)
        def wrapper(self: SeleniumEncryptedSpider, *args, self_var=True, **context):
            args, context = self.init_context(args, context, self_var=self_var)
            options = self.get_driver_options(**context)
            with SeleniumWireDriver(**options) if self.enableWire else SeleniumDriver(**options) as driver:
                self.login(driver, **self.get_auth_key(update=True, **context))
                data = func(self, *args, driver=driver, **SESSION_CONTEXT(**self.set_auth_info(driver, **context)))
            time.sleep(.25)
            self.with_data(data, func=func.__name__, **context)
            return data
        return wrapper

    def is_kill(self, exception: Exception) -> bool:
        return isinstance(exception, SELENIUM_ENCRYPTED_SPIDER_KILL) or isinstance(exception, self.killType)


###################################################################
################# Selenium Encrypted Async Spider #################
###################################################################

class SeleniumEncryptedAsyncSpider(SeleniumAsyncSpider, EncryptedAsyncSpider):
    __metaclass__ = abc.ABCMeta
    asyncio = True
    operation = "spider"
    host = str()
    where = WHERE
    which = WHICH
    verb = ACTION
    by = str()
    fields = list()
    ranges = list()
    iterateArgs = list()
    iterateCount = dict()
    iterateProduct = list()
    iterateUnit = 1
    maxLimit = MAX_ASYNC_TASK_LIMIT
    redirectUnit = 1
    redirectLimit = MAX_REDIRECT_LIMIT
    pagination = False
    pageFrom = 1
    offsetFrom = 1
    pageUnit = 0
    pageLimit = 0
    interval = None
    fromNow = None
    timeout = None
    ssl = None
    numRetries = 0
    delay = 1.
    interruptType = tuple()
    killType = tuple()
    errorType = tuple()
    responseType = "records"
    returnType = "records"
    mappedReturn = False
    root = list()
    groupby = list()
    groupSize = dict()
    countby = str()
    auth = LoginSpider
    authKey = list()
    decryptedKey = dict()
    driver = None
    enableWire = False
    info = Info()
    flow = Flow()

    def __init__(self, fields: Optional[IndexLabel]=None, ranges: Optional[RangeFilter]=None, returnType: Optional[TypeHint]=None,
                tzinfo: Optional[Timezone]=None, countryCode=str(), datetimeUnit: Optional[Literal["second","minute","hour","day"]]=None,
                logName: Optional[str]=None, logLevel: LogLevel="WARN", logFile: Optional[str]=None, localSave=False,
                debugPoint: Optional[Keyword]=None, killPoint: Optional[Keyword]=None, extraSave: Optional[Keyword]=None,
                numRetries: Optional[int]=None, delay: Range=1., cookies: Optional[str]=None,
                fromNow: Optional[Unit]=None, discard=True, progress=True, where=str(), which=str(), by=str(), message=str(),
                iterateUnit: Optional[int]=None, interval: Optional[Timedelta]=None, apiRedirect=False, redirectUnit: Optional[int]=None,
                queryList: GoogleQueryList=list(), uploadList: GoogleUploadList=list(), alertInfo: AlertInfo=dict(),
                encryptedKey: Optional[EncryptedKey]=None, decryptedKey: Optional[DecryptedKey]=None,
                driverOptions: Optional[Dict]=None, reopenDelay: Range=30., **context):
        EncryptedAsyncSpider.__init__(self, **self.from_locals(locals(), drop=DRIVER_UNIQUE))
        self.set_driver_options(driverOptions, reopenDelay)

    def login_driver(func):
        @functools.wraps(func)
        async def wrapper(self: SeleniumEncryptedSpider, *args, self_var=True, **context):
            args, context = self.init_context(args, context, self_var=self_var)
            options = self.get_driver_options(**context)
            with SeleniumWireDriver(**options) if self.enableWire else SeleniumDriver(**options) as driver:
                self.login(driver, **self.get_auth_key(update=True, **context))
                data = await func(self, *args, driver=driver, **SESSION_CONTEXT(**self.set_auth_info(driver, **context)))
            await asyncio.sleep(.25)
            self.with_data(data, func=func.__name__, **context)
            return data
        return wrapper

    def is_kill(self, exception: Exception) -> bool:
        return isinstance(exception, SELENIUM_ENCRYPTED_SPIDER_KILL) or isinstance(exception, self.killType)
