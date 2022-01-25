import os, re

STATEMENT_INIT = """BINLOG '"""
STATEMENT_END = """'/*!*/;"""
TEST_FILE = 'data/parsed_binlog'
DATABASE = 'db_test'

TABLES = ['images']
RE_MATCH = ['UPDATE', 'INSERT', 'DELETE', 'REPLACE']

def match_line(line):
    re_tables = '|'.join(TABLES)
    re_match = '|'.join(RE_MATCH)
    test_line = """### (?:{}).*`{}`.`(?:{})`""".format( 
            re_match,
            DATABASE,
            re_tables,
        )
    test = re.compile(test_line, re.IGNORECASE)
    if re.search(test, line):
        return True
    return False

def parse_file():
    binglog_file = open(TEST_FILE, 'r')
    TMP_STATEMENT_LIST = []
    STATEMENTS = []
    append = False
    for line_ in binglog_file:
        line = line_.strip()
        if line == STATEMENT_END:
            TMP_STATEMENT_LIST.append(line)
            append = False
            FULL_STATEMENT = '\n'.join(TMP_STATEMENT_LIST)
            TMP_STATEMENT_LIST = []
            STATEMENTS.append(FULL_STATEMENT)
        elif line == STATEMENT_INIT:
            TMP_STATEMENT_LIST.append(line)
            append = True
        elif append:
            TMP_STATEMENT_LIST.append(line)

        if match_line(line) and STATEMENTS:
            print(STATEMENTS[-1])
            STATEMENTS = []

if __name__ == '__main__':
    parse_file()
    # re_tables = '|'.join(TABLES)
    # re_match = '|'.join(RE_MATCH)
    # line = """### INSERT INTO `db_test`.`images`"""
    # test_line = """### (?:{}).*`{}`.`(?:{})`""".format( 
    #         re_match,
    #         DATABASE,
    #         re_tables,
    #     )
    # test = re.compile(test_line)
    # print(test)
    # res = re.search(test, line)
    # print(res)    
