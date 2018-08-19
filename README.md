# mysql-obfuscator
This python script will obfuscate / anonymise your database dump.

It will obfuscate the file, not the database, which means it can be done after a backup has been created to create a new backup for testing purposes that is ready-to-use for developers.

Currently the script uses hard-coded comic book character names for obfuscation of names (first name, last name, street name, company name, etc.)

## Requirements
* Python 2.7 or higher (Note: If Python 3 or higher, print statements need to be changed)
* Installed python libs: random


## Use of script
python anonymiser.py [-i input_filename] [-o output_filename] [-s settings_filename]

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

```bash
general
    name :names
    streetname :street_name
    remark :static_string :an important remark
end

# Comment that will be ignored by this script
table :table-name-1
    row-name :custom-function #to be added at the top of this script
end

table :table-name-2 :table-name-3 :table-name-4
    row-name :names
    row-name-2 :numbers :10 :18
    row-name-3 :date
    contact-row :cond_replace :GSM,TEL,EMAIL :cell_phone_no,phone_no,email
end
```
