import pandas as pd

from app import log
from app.parsers.base_parser import BaseParser
from app.utils.constants import (CSES_AC_PROBLEM_CLASS,
                                 CSES_ACCOUNT_ANCHOR_CLASS, CSES_BASE_URL,
                                 CSES_CSRF_TOKEN_FORM_NAME, CSES_LOGIN_URL,
                                 CSES_PASSWORD_FORM_NAME,
                                 CSES_PASSWORD_YAML_NAME, CSES_PROBLEMS_URL, CSES_PROBLEM_RESULTS_URL,
                                 CSES_USERNAME_FORM_NAME,
                                 CSES_USERNAME_YAML_NAME, CSES_YAML_REL_PATH)
from app.utils.io_utils import (get_abs_path, get_all_data_from_yaml,
                                validate_keys)
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

        # get user id from response
        post_login_content = parse(response.text)
        self.user_id = post_login_content.find(
            "a", attrs={"class": CSES_ACCOUNT_ANCHOR_CLASS})["href"]

    def process(self, session, *args, **kwargs):
        # extract list of all solved problems
        CSES_ACCOUNT_URL = CSES_PROBLEMS_URL + self.user_id
        response = http_get(session, CSES_ACCOUNT_URL, self.headers, True)

        user_statistics_content = parse(response.text)
        _list_ac_problem_tags = user_statistics_content.findAll(
            "a", attrs={"class": CSES_AC_PROBLEM_CLASS})

        list_ac_problem_links = [CSES_PROBLEM_RESULTS_URL + "/" + link["href"].strip(
            "/").split("/")[-1] for link in _list_ac_problem_tags]

        iters = 0
        for link in list_ac_problem_links:
            response = http_get(session, link, self.headers, True)
            ac_problem_content = parse(response.text)
            _list_page_anchor_tags = ac_problem_content.find("div", attrs={"class": "pager wide"}).findAll(
                "a", class_=lambda val: val not in ["next", "prev"])
            list_page_links = [CSES_BASE_URL + anchor_tag["href"]
                               for anchor_tag in _list_page_anchor_tags]

            # iterate through each page
            list_submission_data = []
            _header_cells = []

            for page_link in list_page_links:
                response = http_get(session, page_link, self.headers, True)
                current_page_content = parse(response.text)
                _table_element = current_page_content.find(
                    "table", attrs={"class": "wide"})

                # find header if not found already
                if not _header_cells:
                    _header_row_element = _table_element.find(
                        "thead").find("tr")
                    _header_cells = [cell.text if cell.text else "submission"
                                     for cell in _header_row_element.findAll("th")]

                # find valid submissions
                for row in _table_element.findAll("tr")[1:]:
                    _curr_dict = dict(zip(_header_cells, row.findAll("td")))

                    # ignore unaccepted submissions
                    if _curr_dict.get("result").get("class") != CSES_AC_PROBLEM_CLASS:
                        continue

                    for key in _curr_dict:
                        if key not in ["result", "submission"]:
                            _curr_dict[key] = _curr_dict.get(key).text.lower()

                    # handle submission column
                    _curr_dict["submission"] = CSES_BASE_URL + _curr_dict.get(
                        "submission").find("a").get("href")
                    list_submission_data.append(_curr_dict)

            df = pd.DataFrame(list_submission_data)

            # clean up the dataframe
            # 1. drop unnecessary columns
            df.drop(["time", "result"], inplace=True, axis=1)

            # 2. remove 's' and 'ch' from 'code time' and 'code size' cols resp.
            df[["code time", "code size"]] = df[["code time", "code size"]
                                                ].applymap(lambda x: x.split(" ")[0])

            print(df)

            # TODO : remove the break (testing few problem links for now)
            iters += 1
            if iters > 4:
                break
