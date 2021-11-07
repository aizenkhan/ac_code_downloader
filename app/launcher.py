""" launcher file for the application """

if __name__ == "__main__":
    # imports
    from app import log
    from app.parsers.cses_parser import CsesParser

    csesParser = CsesParser()
    csesParser.run()
    log.info("Done")
