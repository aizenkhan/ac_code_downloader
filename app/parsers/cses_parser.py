from app import log
from app.parsers.base_parser import BaseParser
from app.utils.io_utils import get_abs_path, get_all_data_from_yaml, validate_keys
from app.utils.web_utils import http_get, http_post, parse

_cses_config_abs_path = get_abs_path(
    rel_path="../../files/cses.yaml",
    caller_script_directory=__file__
)


class CsesParser(BaseParser):
    dict_urls = {
        "LOGIN_URL": "https://cses.fi/login",
        "PROBLEMS_URL": "https://cses.fi/problemset"
    }

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"}

    def __init__(self) -> None:
        super().__init__(self.dict_urls)
        self.local_context = get_all_data_from_yaml(_cses_config_abs_path)

    def preprocess(self, session, *args, **kwargs):
        # validate username/password present in context
        validate_keys(self.local_context, [
                      "username", "password"], to_prompt=True)

        # log in
        response = http_get(
            session, self.dict_urls["LOGIN_URL"], self.headers, True)

        # extract csrf token
        content = parse(response.text)
        csrfToken = content.find(
            "input", attrs={"name": "csrf_token"})["value"]

        # create payload
        payload = {
            "nick": self.local_context["username"],
            "pass": self.local_context["password"],
            "csrf_token": csrfToken,
        }

        # post
        response = http_post(
            session, self.dict_urls["LOGIN_URL"], payload, self.headers)

        # verify login successful
        assert self.local_context["username"] in response.text
        log.info("Successfully logged in.")

    def process(self, session, *args, **kwargs):
        # TODO: Fetch submissions from problems page
        pass
