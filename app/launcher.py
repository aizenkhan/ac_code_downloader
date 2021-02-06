""" launcher file for the application """

# imports
from app import log
from app.parsers.cses_parser import CsesParser


if __name__ == "__main__":
    # test log in
    csesParser = CsesParser()
    csesParser.run()
    log.info("Done")