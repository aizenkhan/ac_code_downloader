import pandas as pd
from app import log
from app.parsers.base_parser import BaseParser
from app.utils.constants import (CSES_AC_PROBLEM_CLASS,
                                 CSES_ACCOUNT_ANCHOR_CLASS, CSES_BASE_URL,
                                 CSES_CSRF_TOKEN_FORM_NAME, CSES_LOGIN_URL,
                                 CSES_NEXT_PAGE_CLASS, CSES_PAGE_SPAN_CLASS,
                                 CSES_PASSWORD_FORM_NAME,
                                 CSES_PASSWORD_YAML_NAME, CSES_PREV_PAGE_CLASS,
                                 CSES_PROBLEM_RESULTS_URL, CSES_PROBLEMS_URL,
                                 CSES_TABLE_CLASS, CSES_TABLE_CODE_LANG_COL,
                                 CSES_TABLE_CODE_SIZE_COL,
                                 CSES_TABLE_CODE_TIME_COL,
                                 CSES_TABLE_SUBMISSION_COL,
                                 CSES_TABLE_TIMESTAMP_COL,
                                 CSES_TABLE_VERDICT_COL,
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
        # get the profile page
        CSES_ACCOUNT_URL = CSES_PROBLEMS_URL + self.user_id
        response = http_get(session, CSES_ACCOUNT_URL, self.headers, True)

        # get all the solved problem tags from profile page
        user_statistics_content = parse(response.text)
        _list_ac_problem_tags = user_statistics_content.findAll(
            "a", attrs={"class": CSES_AC_PROBLEM_CLASS})

        # get actual links of the solved problems
        list_ac_problem_links = [CSES_PROBLEM_RESULTS_URL + "/" + link["href"].strip(
            "/").split("/")[-1] for link in _list_ac_problem_tags]

        iters = 0
        # go through each solved problem link and fetch AC submissions
        for link in list_ac_problem_links:
            # get the problem page
            response = http_get(session, link, self.headers, True)
            ac_problem_content = parse(response.text)

            # submissions can span across multiple sub-pages, so get links of all sub-pages
            _list_page_anchor_tags = ac_problem_content.find("div", attrs={"class": CSES_PAGE_SPAN_CLASS}).findAll(
                "a", class_=lambda val: val not in [CSES_NEXT_PAGE_CLASS, CSES_PREV_PAGE_CLASS])
            list_page_links = [CSES_BASE_URL + anchor_tag["href"]
                               for anchor_tag in _list_page_anchor_tags]

            list_submission_data = []  # table rows
            _header_cells = []  # table header

            # iterate through each sub-page
            for page_link in list_page_links:
                # get the sub-page
                response = http_get(session, page_link, self.headers, True)
                current_page_content = parse(response.text)

                # submissions are stored in a table element, so capture that
                _table_element = current_page_content.find(
                    "table", attrs={"class": CSES_TABLE_CLASS})

                # find header if not found already
                if not _header_cells:
                    _header_row_element = _table_element.find(
                        "thead").find("tr")
                    # column containing links to code has no name i.e '', so assigning it a name
                    _header_cells = [cell.text if cell.text else CSES_TABLE_SUBMISSION_COL
                                     for cell in _header_row_element.findAll("th")]

                # find valid submissions from table
                for row in _table_element.findAll("tr")[1:]:
                    _curr_dict = dict(zip(_header_cells, row.findAll("td")))

                    # ignore unaccepted submissions
                    if _curr_dict.get(CSES_TABLE_VERDICT_COL).get("class") != CSES_AC_PROBLEM_CLASS:
                        continue

                    # get text from cells except for verdict and submission columns
                    # verdict column contains no text, whereas submission column links to code page
                    for key in _curr_dict:
                        if key not in [CSES_TABLE_VERDICT_COL, CSES_TABLE_SUBMISSION_COL]:
                            _curr_dict[key] = _curr_dict.get(key).text.lower()

                    # extract code page link from submission column
                    _curr_dict[CSES_TABLE_SUBMISSION_COL] = CSES_BASE_URL + _curr_dict.get(
                        CSES_TABLE_SUBMISSION_COL).find("a").get("href")

                    # add the row to our list of rows
                    list_submission_data.append(_curr_dict)

            # make dataframe from our list of (dict) rows
            df = pd.DataFrame(list_submission_data)

            # clean up the dataframe
            # 1. drop unnecessary columns
            df.drop([CSES_TABLE_TIMESTAMP_COL, CSES_TABLE_VERDICT_COL],
                    inplace=True, axis=1)

            # 2. remove 's' and 'ch' from 'code time' and 'code size' columns resp. and make them numeric
            df[[CSES_TABLE_CODE_TIME_COL, CSES_TABLE_CODE_SIZE_COL]] = df[[CSES_TABLE_CODE_TIME_COL, CSES_TABLE_CODE_SIZE_COL]
                                                                          ].applymap(lambda x: x.split(" ")[0]).astype(float)

            # 3. group by language and get rows having minimum code time
            df = df.loc[df.groupby(CSES_TABLE_CODE_LANG_COL)[CSES_TABLE_CODE_TIME_COL].idxmin()].reset_index(
                drop=True)
            
            # TODO : parse dataframe and fetch actual code from code page

            # TODO : remove the break (testing few problem links for now)
            iters += 1
            if iters > 4:
                break
