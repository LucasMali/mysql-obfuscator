#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SEE https://github.com/LucasMali/mysql-obfuscator

###############################################################
#
# Warning
#
# This script will change the values of the given SQL file
# It will make an obfuscated copy of the original
# It is NOT possible to reverse the process on a file
#
# Disclaimer
# This script with NO GUARANTEE
# Though it has been thoroughly tested, results may vary
# Use at own risk
###############################################################


"""
Requirements
------------
* Python 3.0

Use of script
-------------
python obfuscator.py [-i input_filename] [-o output_filename] [-s settings_filename]

The SQL script must contain either a CREATE statement for tables that need to be altered
or the table columns must be added after the INSERT statements.

The script expects a settings file. This file (settings.txt by default) needs to contain 
the column names and obfuscation type according the the format below.
It is possible to add a "general" rule to obfuscate a specific column in all tables that 
contain it. Otherwise a column must be part of one or multiple table(s).
To define a table, write "table" followed by a semicolon ":" and the tablename(s).
When the to-be-obfuscated columns are entered, close the table definition with "end".
Anything after a hashtag "#" will be ignored.
Example:

general
    name :names
    streetname :street_name
end

# Comment that will be ignored by this script
table :table-name-1
    row-name :custom-function #to be added at the top of this script
end

table :table-name-2 :table-name-3 :table-name-4
    row-name :names
    row-name-2 :numbers :10 :18
    row-name-3 :date
end
"""

###############################################################
# Default variables
# Note: most can also be given as parameters when running script

_INPUT_FILE = "console"  # by default, this script expects console such that it can be used in a bash pipe oneliner
_OUTPUT_FILE = "output.sql"
_SETTINGS_FILE = "obfuscator_settings.txt"
_NULL_STAYS_NULL = True  # Do not force a new value on NULL values
_PRINT_FEEDBACK = False

_fnamelist = ["John", "Jane"]
_lnamelist = ["Doe"]
_companylist = ["somecompany"]
_email_list = ["someemail.us"]
_utf8_fix_dict = {'\x00': 'NULL', 'NULL': 'NULL', '00': '\'00\'', '\'\'': '\'\''}

# No need to change anything after this point
# Modify or add custom functions at own risk
###############################################################

# Imports
import sys
import random
import os.path
import getopt
import time
import csv
import codecs


# Helper functions
# ****************

def is_number(s):
    """
    Small function to check if a value is numeric
    """
    try:
        float(s)  # for int, long and float - not complex as complex also allows 'J' as number or unit
    except ValueError:
        return False
    return True


def nullcheck(orig, new, quotes=True):
    """
    returns quotes string (such that quotes are printed to file) 
    and ensures that NULL (or similar entry - utf8 fixes) stays NULL
    """
    if _NULL_STAYS_NULL:
        if orig == '' or not orig:
            return '\'\''
        elif orig in _utf8_fix_dict:
            return _utf8_fix_dict[orig]
    if quotes:
        return ''.join(['\'', new, '\''])
    return new


def number_with_check(number, checkmod=97, quotes=True, newgen=False):
    """
    Typical numerical check for bank numbers (97 is largest prime under 100)
    """
    if newgen:  # people born in or after 2000
        check_no = checkmod - (number + 2000000000) % checkmod
    else:
        check_no = checkmod - number % checkmod
    if quotes:
        return ''.join(['\'', str(number), str(check_no).zfill(2), '\''])
    return ''.join([str(number), str(check_no).zfill(2)])


def print_to_terminus(file, value='', format=True):
    """
    Print to terminus and adds newline if needed
    """
    if format:
        value = ''.join([value.strip(), '\r\n'])

    if not file:
        sys.stdout.write(value)
    else:
        file.write(value)

_print_statements = set()


def single_print_statment(prnt):
    """
    Prevent printing double statements
    """
    global _print_statements
    if prnt not in _print_statements:
        _print_statements.add(prnt)
        print(prnt)


# Obfuscation options
# *******************

_parameters = {'nullcheck': ['orig', 'new'], 'numbers': ['min_no', 'max_no'], 'short': ['max_no'],
               'date': ['min_year', 'max_year'], 'static_string': ['msg']}
# keep last generated values from current table columns (such that first-name, last-name and full contains the same
# names)
_last_gen = dict()
# set required for the method "set_replace"
_replace_set = dict()


def names(quotes=True, v=True):
    if 'names' not in _last_gen:
        _last_gen['names'] = random.choice(_fnamelist)
    return nullcheck(v, _last_gen['names'], quotes=quotes)


def first_name(v=True):
    return names(v)


def last_name(quotes=True, v=True, force=False):
    if 'last_name' not in _last_gen or force:
        _last_gen['last_name'] = random.choice(_lnamelist)
    return nullcheck(v, _last_gen['last_name'], quotes=quotes)


def search_name(quotes=True, v=True):
    return nullcheck(v, "".join(''.join([last_name(False), first_name(False)]).split()), quotes=quotes)


def full_name(v=True):
    return nullcheck(v, ''.join([first_name(False), ' ', last_name(False)]))


def street_name(v=True):
    return nullcheck(v, ''.join([last_name(False, force=True), "straat"]))


def niscode(v=True):
    return nullcheck(v, str(random.randint(100, 4000)).zfill(4))


def numbers(min_no=0, max_no=100, v=True):
    return nullcheck(v, random.randint(int(min_no), int(max_no)), quotes=False)


def static_string(msg="An important remark", v=True):
    return nullcheck(v, msg)


def short(max_no=5, v=''):
    max_no = int(max_no)
    if v:
        v = ''.join(e for e in v if e.isalnum())
    if not v:
        return '\'\''
    return nullcheck(v, v[:max_no])


def date(min_year=1945, max_year=2017, v=True):
    return nullcheck(v, ''.join([str(random.randint(min_year, max_year)).zfill(4),
                                 '-', str(random.randint(1, 12)).zfill(2),
                                 '-', str(random.randint(1, 28)).zfill(2)]))


def ip(v=False):
    return nullcheck(v, ".".join(map(str, (random.randint(0, 255) for _ in range(4)))))


def email(v=False):
    return nullcheck(v, ''.join([first_name(False).lower(), '@', random.choice(_email_list)]))


def company(v=True):
    return nullcheck(v, random.choice(_companylist))


def company_no(v=True):
    return nullcheck(v, number_with_check(random.randint(1000000, 9998999), quotes=False))


def company_rsz(v=True):
    return nullcheck(v, number_with_check(random.randint(1000000, 9998999), quotes=False))


def iban(v=True):
    return iban_be(v)


def iban_be(v=True):
    random_no = random.randint(631000000, 639000000)
    check_no = str(random_no % 97).zfill(2)
    belgian_bank_account = ''.join([str(random_no), str(check_no)])
    check_no = 98 - int(''.join([belgian_bank_account, "111400"])) % 97
    return nullcheck(v, ''.join(["BE", str(check_no).zfill(2), "0", belgian_bank_account]))


_unique_insz = set()


def insz(v=False, birthdate=False, sex=False):
    birth = random.randint(5, 995)
    newgen = False
    if v and v != '' and v != 'NULL':
        if number_with_check(int(v[:9]), quotes=False) != str(v):
            newgen = True
        birthdate = v[:6]
        sex = 'F'
        if int(v[6:9]) % 2 == 0:
            sex = 'M'
    else:
        if _NULL_STAYS_NULL:
            return 'NULL'
        sex = random.choice(['M', 'F'])
    if sex == 'M':
        if birth % 2 != 0:
            birth += 1
    elif birth % 2 == 0:
        birth += 1
    if not birthdate:
        birthdate = date()
        birthdate = birthdate.replace('-', '')[2:]
    random_no = ''.join([str(birthdate), str(birth).zfill(3)])
    new_insz = number_with_check(int(random_no), quotes=False, newgen=newgen).zfill(11)
    global _unique_insz
    if new_insz in _unique_insz:
        return insz(v=v)
    _unique_insz.add(new_insz)
    return ''.join(['\'', new_insz, '\''])


def inter_phone_no(v=True):
    return nullcheck(v, ''.join(['+1', str(1), str(5555555555)]))


def phone_no(v=True):
    return nullcheck(v, ''.join(['03', str(random.randint(1000000, 9000000))]))


def cell_phone_no(v=True):
    return nullcheck(v, ''.join(['0478 ', str(random.randint(100000, 900000))]))


def registration_number(v=True):
    return nullcheck(v, str(random.randint(10000000, 98888888)))


# Settings - parser object
# ************************

# Note: no specific reason why this is in an object

class SettingsTable(object):
    # Variables
    tables = dict()
    parse_tables = dict()
    prepare_tables = dict()
    general_columns_list = list()
    skiplist = set()

    # Class constructor / initializer
    def __init__(self, tables):
        self.tables = tables;
        if 'general_table_columns' in self.tables:
            self.general_columns_list = [item[0] for item in self.tables['general_table_columns']]

    def prepare_parse_table(self, table, line):
        """
        Add table to the preparation list, waiting for found columns
        """
        if table not in self.prepare_tables:
            self.prepare_tables[table] = list()
        self.prepare_tables[table].append(line.strip()[1:].partition("`")[0])

    def finalize_parse_table(self, table):
        """
        add_parse_table wrapper
        """
        if table not in self.prepare_tables:
            return False
        return self.add_parse_table(table, self.prepare_tables[table])

    def add_parse_table(self, table, columns):
        """
        Add parse table with the correct amount of columns (from CREATE) accompanied by the obfuscation action
        This will add "do_nothing" for everything that was not mentioned in the settings file
        """
        if table in self.parse_tables:
            return False
        if table in self.skiplist:
            self.skiplist.remove(table)
        self.parse_tables[table] = dict()
        table_column_names = []
        if table in self.tables and len(self.tables[table]) > 0:
            table_column_names = [item[0] for item in self.tables[table]]
        for i, row in enumerate(columns):
            if row in table_column_names:
                self.parse_tables[table][i] = self.tables[table][table_column_names.index(row)][1:]
            elif row in self.general_columns_list:
                self.parse_tables[table][i] = self.tables["general_table_columns"][
                                                  self.general_columns_list.index(row)][1:]
            else:
                self.parse_tables[table][i] = ['do_nothing']
        if len(set([item[0] for item in self.parse_tables[table].values() if item[0] != "do_nothing"])) == 0:
            del self.parse_tables[table]
            self.skiplist.add(table)
        return True

    def check_table_known(self, table, line=""):
        """
        Check if a CREATE statement was found and the table requires alternation (see settings file)
        """
        if table in self.skiplist:
            return False
        # if table not found with create statement, give another attempt before adding to skiplist
        if table not in self.parse_tables and line:
            return self.get_columns_from_insert(table, line)
        return True

    def get_table(self, line):
        """
        Returns table name of the current INSERT statement
        """
        return line.partition('`')[2].partition('`')[0]

    def get_values(self, line):
        """
        Get the values of an SQL insert statement (both mysqldump and mysqldump -c)
        """
        values = line.partition('` VALUES ')[2]
        if not values:
            return "(" + line.partition(') VALUES (')[2]
        return values

    def values_sanity_check(self, values):
        """
        Ensures that values from the INSERT statement meet basic checks.
        """
        assert values
        assert values[0] == '('
        return True  # Assertions have not been raised

    def set_replace(self, original_value, function, arguments=[]):
        """
        Obfuscates with a limited set of values according to the original values
        Each replaced value is placed in a set which is reused for replacing
        """
        global _replace_set
        if function not in _replace_set:
            _replace_set[function] = dict()
        if original_value in _replace_set[function]:
            return _replace_set[function][original_value]
        else:
            new_value = self.obfuscate(original_value, function, arguments)
            _replace_set[function][original_value] = new_value
            return new_value

    def obfuscate(self, original_value, function, arguments=[]):
        """
        Obfuscates a given value by calling the corresponding function by its string name
        """
        params = dict()
        if function in _parameters:  # if function is known to have parameters
            for i, p in enumerate(arguments):
                params[_parameters[function][i]] = p
        params['v'] = original_value
        return globals()[function](**params)

    def parse_values(self, table, values):  # , outfile):
        """
        Parse the given values to an obfuscated INSERT statement
        """
        # if self.values_sanity_check(values):
        global _last_gen
        reader = csv.reader([values[:-1]],
                            delimiter=',',
                            doublequote=False,
                            escapechar='\\',
                            quotechar="'",
                            strict=True
                            )
        latest_row = list()
        returnstring = "INSERT INTO `{0}` VALUES ".format(table)
        t = self.parse_tables[table]
        func_change_dict = {'cond_remove': 1, 'cond_replace': 2}
        for reader_row in reader:
            last = False
            remove = False
            replace = dict()
            for column in reader_row:
                # If our current string is empty...
                if len(column) == 0:
                    latest_row.append(chr(0))
                    continue

                # Remove parentheses at start or end
                if len(latest_row) < 1 and column[0] == "(":
                    column = column[1:]
                elif len(t) - 1 == len(latest_row):
                    column = column[:-1]
                    last = True

                # Change / Obfuscate the values according to defitition in settings file
                func = t[len(latest_row)]
                if func[0] in func_change_dict:
                    if func[0] == 'cond_replace' and column not in _utf8_fix_dict:
                        replace[len(latest_row)] = func[1:]
                    elif column == func[1]:  # already certain cond_remove
                        remove = True
                    column = nullcheck(column, column)
                elif func[0] == 'set_replace':
                    column = self.set_replace(column, func[1], func[2:])
                elif func[0] != 'do_nothing':
                    column = self.obfuscate(column, func[0], func[1:])
                elif column in _utf8_fix_dict:
                    column = _utf8_fix_dict[column]
                elif not column:
                    column = '\'\''
                elif not is_number(column):
                    column = ''.join(['\'', column, '\''])
                if str(column).count('\'') > 2:
                    column = ''.join(['\'', column[1:].replace("\'", "\\\'", column.count('\'') - 2)])
                latest_row.append(str(column))

                # If a datarow is completed
                if last:
                    if len(replace) > 0:
                        for key in replace.keys():
                            # Get the function id if the accompanied word occurs
                            occurences = [replace[key][0].split(',').index(item) for item in replace[key][0].split(',')
                                          if ''.join(['\'', item, '\'']) in latest_row]
                            if len(occurences) > 0:
                                latest_row[key] = str(
                                    self.obfuscate(latest_row[key], replace[key][1].split(',')[occurences[0]], []))
                        replace = dict()
                    if not remove:
                        returnstring = ''.join([returnstring, "(", ','.join(latest_row).replace('\x00', '\'\''), "),"])
                    last = False
                    remove = False
                    latest_row = list()
                    _last_gen = dict()

        if returnstring[-7:] == 'VALUES ':
            return ''
        return ''.join([returnstring[:-1], ';'])

    def get_columns_from_insert(self, table, line):
        """
        Get the column names from the INSERT statement if exported using mysqldump -c
        """
        if not table or table not in line:
            return False
        stripped_line = line.strip().partition(table)[2][1:].strip()
        if stripped_line[0] == "(":
            return self.add_parse_table(table, stripped_line[1:].partition(")")[0].split("`, `"))
        return False


def read_sql_by_line(l, tables, table, truncates, start_time, output, not_silent=True):
    line = l.strip()
    if table:
        if line.startswith("`"):
            tables.prepare_parse_table(table, line)
        else:
            tables.finalize_parse_table(table)
            table = False

    # Look for an INSERT statement and parse it.
    elif line.startswith('INSERT'):
        t = tables.get_table(line)
        if not t:
            print_to_terminus(output, line)
        elif t in truncates:  # truncate in settings file means delete line
            if not_silent:
                single_print_statment("Table {0} truncated".format(t))
        elif not tables.check_table_known(t, line):
            if not_silent:
                single_print_statment("Skipped inserts for table {0}".format(t))
            print_to_terminus(output, line)
        else:
            values = tables.parse_values(t, tables.get_values(line))
            if values and values != '':  # Fix for empty lines (INSERT INTO tblname VALUES;)
                print_to_terminus(output, values)
            if not_silent:
                print("Insert statement for table {0} written (Elapsed time: {1:.2f})".format(t,
                                                                                              time.time() - start_time))
        return table
    elif line.startswith('CREATE'):
        table = tables.get_table(line)
    print_to_terminus(output, l, False)
    return table


# Main - init & run script
# ************************

def main(argv):
    """
    Parse arguments and start the program
    """
    # Set default values
    outputfile = _OUTPUT_FILE
    inputfile = _INPUT_FILE
    settingsfile = _SETTINGS_FILE
    scriptname = sys.argv[0]  # makes it easy to rename the file

    # Get and set optional parameters
    try:
        opts, args = getopt.getopt(argv, "h:i:o:s:", ["ifile=", "ofile=", "sfile="])
    except getopt.GetoptError:
        print('{0} [-i <inputfile>] [-o <outputfile>] [-s <settingsfile>]'.format(scriptname))
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('{0} -i <inputfile> -o <outputfile> -s <settingsfile>'.format(scriptname))
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-s", "--sfile"):
            settingsfile = arg

    if inputfile != "console":
        # Check if the input file exists
        if not os.path.isfile(inputfile):
            print("Input file \"{0}\" doesn't exist.".format(inputfile))
            print('Format: {0} [-i <inputfile>] [-o <outputfile>] [-s <settingsfile>]'.format(scriptname))
            sys.exit(0)
        # Check if the output file already exists
        if os.path.isfile(outputfile):
            if input("Outputfile \"{0}\" already exists. Overwrite? [y/n] ".format(outputfile))[0] != 'y':
                sys.exit(0)
    else:
        global _PRINT_FEEDBACK
        _PRINT_FEEDBACK = False

    # Obfuscate the given input file with the settings to the given output file
    if inputfile != "console":
        output = codecs.open(outputfile, "w", encoding="utf-8", buffering=0)
    else:
        output = False

    if _PRINT_FEEDBACK:
        print("Reading settings...")
    try:
        # Read in configuration file
        tables = dict()
        truncates = set()
        if os.path.isfile(settingsfile):
            with codecs.open(settingsfile, encoding="utf-8") as f:
                t = False
                g = False
                for l in [x.strip().replace("\t", " ").split("#")[0] for x in f.readlines() if
                          x.split("#")[0] and x[0] not in ['#', '/']]:
                    if t:
                        if l.startswith("end"):
                            for tab in t[1:]:
                                tables[tab] = tables[t[0]]
                            t = False
                            continue
                        tables[t[0]].append(l.split(" :"))
                    elif l.startswith("table"):
                        t = l.split(" :")[1:]
                        tables[t[0]] = list()
                    elif l.startswith("truncate"):
                        truncates.add(l.split(" :")[1])
                    elif l.startswith("general"):
                        t = ["general_table_columns"]
                        tables[t[0]] = list()
        else:
            print("No settings file")
            sys.exit()
        if 'tables' not in locals() or type(tables) is not dict:
            print("Please define a tables variable as tables = dict()")
            sys.exit()
        if len(tables) < 1:
            print("No table profiles in settings file")
            sys.exit()

        # Parse file and obfuscate the tables according to settings file
        table = False
        tables = SettingsTable(tables)
        start_time = time.time()

        if inputfile == "console":
            for line in sys.stdin:
                table = read_sql_by_line(line, tables, table, truncates, start_time, output, not_silent=_PRINT_FEEDBACK)
                # This isn't doing anything but outputting the same thing coming in. See read_sql_by_line.
                # sys.stdout.write(line)
        else:
            with open(inputfile, 'r') as f:
                for line in f:
                    table = read_sql_by_line(line, tables, table, truncates, start_time, output,
                                             not_silent=_PRINT_FEEDBACK)

        if inputfile != "console":
            print_to_terminus(output)
            output.close()

        if _PRINT_FEEDBACK:
            print("Finished (Elapsed time: {0:.2f})".format(time.time() - start_time))

    except KeyboardInterrupt:
        output.close()
        sys.exit(0)


# Start actual program
# ************************

if __name__ == "__main__":
    main(sys.argv[1:])
