from app import log
from app.parsers.base_parser import BaseParser
from app.utils.constants import CSES_YAML_REL_PATH, CSES_LOGIN_URL, CSES_PROBLEMS_URL, CSES_USERNAME_YAML_NAME, CSES_PASSWORD_YAML_NAME, CSES_USERNAME_FORM_NAME, CSES_PASSWORD_FORM_NAME, CSES_CSRF_TOKEN_FORM_NAME
from app.utils.io_utils import get_abs_path, get_all_data_from_yaml, validate_keys
from app.utils.web_utils import http_get, http_post, parse

_cses_config_abs_path = get_abs_path(
    rel_path=CSES_YAML_REL_PATH,
    caller_script_directory=__file__
)


class CsesParser(BaseParser):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"}

    def __init__(self) -> None:
        self.local_context = get_all_data_from_yaml(_cses_config_abs_path)

    def preprocess(self, session, *args, **kwargs):
        # validate username/password present in context
        validate_keys(self.local_context, [
                      CSES_USERNAME_YAML_NAME, CSES_PASSWORD_YAML_NAME], to_prompt=True)

        # log in
        response = http_get(
            session, CSES_LOGIN_URL, self.headers, True)

        # extract csrf token
        content = parse(response.text)
        csrfToken = content.find(
            "input", attrs={"name": CSES_CSRF_TOKEN_FORM_NAME})["value"]

        # create payload
        payload = {
            CSES_USERNAME_FORM_NAME: self.local_context[CSES_USERNAME_YAML_NAME],
            CSES_PASSWORD_FORM_NAME: self.local_context[CSES_PASSWORD_YAML_NAME],
            CSES_CSRF_TOKEN_FORM_NAME: csrfToken,
        }

        # post
        response = http_post(
            session, CSES_LOGIN_URL, payload, self.headers)

        # verify login successful
        assert self.local_context[CSES_USERNAME_YAML_NAME] in response.text
        log.info("Successfully logged in.")

    def process(self, session, *args, **kwargs):
        # TODO: Fetch submissions from problems page
        pass
