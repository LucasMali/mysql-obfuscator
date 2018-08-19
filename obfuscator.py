#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
* Python 2.7 or higher (Note: If Python 3 or higher, print statements need to be changed)
* Installed python libs: random


Use of script
-------------
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

_INPUT_FILE = "console" # by default, this script expects console such that it can be used in a bash pipe oneliner
_OUTPUT_FILE = "output.sql"
_SETTINGS_FILE = "obfuscator_settings.txt"
_NULL_STAYS_NULL = True # Do not force a new value on NULL values
_PRINT_FEEDBACK = False

# obfuscation variables (In this case, comic book companies and (Belgian) comic book characters)
_fnamelist = ["Admiraal","Agent","Ali","Allan","Alley","Angelfood","Ankie","Annemarie","Appie","Archibald","Archie","Arend","Averell","Axel","Baba","Bamm","Barend","Barney","Baron","Bart","Benjamin","Bennie","Benny","Bernard","Bert","Bertje","Bessie","Betty","Bibi","Billie","Birre","Bob","Bolle","Boo","Boris","Bram","Brammetje","Brigadier","Bruno","Buck","Bugs","Bulle","Buster","Buurman","Calamity","Carl","Carmella","Charles","Charlie","Charlotte","Chick","Clarabella","Clark","Clo","Commandant","Commissaris","Cornelis","Cornelius","Corto","Daffy","Dagobert","Dan","Dees","Dick","Diederik","Dikke","Dirk","Dog","Dokter","Donald","Doortje","Doris","Douwe","Driftige","Dumbella","Elodie","Elroy","Enid","Estella","Evert","Fanny","Fernand","Fester","Flakey","Flapoor","Flip","Flippie","Fokkie","Fone","Foxy","Fred","Froefroe","Gaby","Garmt","Generaal","Geniale","George","Gerard","Gerrit","Gertje","Gezusters","Gijs","Gijsje","Gomez","Govert","Groene","Grote","Guus","Guust","Haagse","Hamster","Harry","Hiep","Hilarius","Hippe","Homer","Howard","Huckleberry","Ian","Ingenieur","Iron","Isabelle","Jack","Jacques","Jan","Jane","Jans","Jean","Jef","Jerome","Jerry","Jess","Jessica","Joachim","Jody","Joe","Joeksel","John","Jolan","Jolly","Julius","Kabouter","Kapitein","Kari","Kid","Klaartje","Kolonel","Koning","Konstantinopel","Krazy","Kriss","Kroesje","Lady","Largo","Leo","Leon","Leonard","Lex","Lieven","Linke","Lisa","Lois","Luc","Magilla","Majoor","Malle","Marcel","Marie","Martin","Mary ","Mic","Michel","Mick","Mickey","Mighty","Mijnheer","Minnie","Modesty","Moe","Moeder","Moemoe","Morticia","Motoko","Muten","Neef","Nick","Ninja","Nonkel","Octaaf","Officer","Olaf","Oma","Opa","Oscar","Ouwe","Pastuiven","Pat","Pebbles","Pee","Peppermint","Perry","Phil","Phineas","Phony","Piet","Pinkie","Porky","Potige","Prince","Prins","Professor","Pugsley","Rebecca","Richie","Rik","Rip","Roberto","Roel","Rooie","Roy","Roze","Sailor","Sally","Sam","Sarah","Schraalhans","Serafijn","Signor","Silver","Simon","Sjakie","Sloeber","Son","Sonny","Spekkie","Stan","Stef","Steve","Steven","Sus","Svein","taan","Taka","Tante","Teenage","Thea","Theo","Theodoor","Theofiel","Thomas","Tijl","Timothea","Tinus","Tokkie","Tom","Vader","Vittorio","Wal","Walt","Wammes","Wayne","Wednesday","Wendy","Wieske","William","Willie","Wilma","Wimpie","Wolvin","Yogi","Yoko","James","Mary","John","Patricia","Robert","Linda","Michael","Barbara","William","Elizabeth","David","Jennifer","Richard","Maria","Charles","Susan","Joseph","Margaret","Thomas","Dorothy","Christopher","Lisa","Daniel","Nancy","Paul","Karen","Mark","Betty","Donald","Helen","George","Sandra","Kenneth","Donna","Steven","Carol","Edward","Ruth","Brian","Sharon","Ronald","Michelle","Anthony","Laura","Kevin","Sarah","Jason","Kimberly","Matthew","Deborah","Gary","Jessica","Timothy","Shirley","Jose","Cynthia","Larry","Angela","Jeffrey","Melissa","Frank","Brenda","Scott","Amy","Eric","Anna","Stephen","Rebecca","Andrew","Virginia","Raymond","Kathleen","Gregory","Pamela","Joshua","Martha","Jerry","Debra","Dennis","Amanda","Walter","Stephanie","Patrick","Carolyn","Peter","Christine","Harold","Marie","Douglas","Janet","Henry","Catherine","Carl","Frances","Arthur","Ann","Ryan","Joyce","Roger","Diane"]
_lnamelist = ["Abraham","Addams","Adolphine","Akelig","Amos","Antigoon","Ardoba","Avondrood","Baardemakers","Bailey","Bamba","Barabas","Barton","Bas","Bear","Beer","Bibber","Biereco","Big","Bill","Blaaskop","Bladerdeeg","Blaise","Blandy","Bloks","Blunder","Boef","Boemerang","Bolderbast","Bone","Boop","Bos","Bram","Braun","Brazil","Brecht","Brekel","Brown","Bunny","Caesar","Canyon","Carrington","Carter","Cash","Castafiore","Chesterfield","Cleysters","Coleslaw","Cooper","Dabbert","Dalton","Danny","Diamond","Dickerdack","DiFool","Dijkstra","Doddel","Doorzon","Doppelmeyer","Dragon","Dredd","Dubbel","Duck","Dust","Edelweiss","Eppie","Faccioni","Fillemon","Flater","Flink","Flintstone","Flitser","Fluwijn","Flynn","Foont","Fury","Gans","Gaston","Gator","Geluk","Gijs","Gobelijn","Goedbloed","Goedzak","Goegebuer","Gohan","Goku","Goochem","Goodbye","Gorilla","Goten","Goudglans","Grandpa","Grootgrut","Haddock","Happie","Har","Haring","Harry","Henk","Herman","Hieper","Hoed","Hortensia","Hound","IJzerdraad","Jager","Jane","Janssen","Jetson","Jim","Joekie","Jorgen","Joviaal","Jumper","Kaledine","Kapoen","Kat","Kent","Keunink","Kiekeboe","Kip","Kitty","Klepzeiker","Kloris","Knobbel","Koe","Kordaat","Krelis","Kreuvett","Kumulus","Kusanagi","Kweepeer","Kwel","Kwok","Lampion","Lane","Langtand","Lawina","Lente","Loden","Loetje","Loewie","Long","Luke","Lumeij","Lupardi","Luthor","Mac","MacDingeling","Maltese","Man","Mataboe","McDuck","McSpade","Melody","Meulemans","Mie","Mikmak","Milaan","Moderato","Moon","Moonshine","Morane","Mouse","Mus","Mutant","Natuur","Nero","Niek","Noord","Oliepul","Olifant","Olivier","Oop","Ordinn","Orient","Otto","Paddle","panter","Pastinakel","Patat","Patty","Pedal","Pepermunt","Perry","Peuk","Pezzo","Pheip","Phreak","Pienter","Pieps","Pig","Pips","Pleksy","Poedel","Poes","Poker","Pollewop","Pralin","Prikkebeen","Prince","Prul","Psylocibide","Pup","Pyr","Rae","Ralph","Rastapopoulos","Rich","Rijkers","Ringers","Rob","Rockerduck","Rogers","Rommelgem","Roshi","Rubble","Rus","Sapperdeboere","Saprinetta","Schlomo","Schneesicht","Schulmeister","Shelton","Sheridan","Shin","Sickbock","Sidonia","Simpson","Slim","Smurf","Snoek","Snor","Snorkel","Snuf","Snuffel","Sonja","Springmuis","Stans","Stark","Steenvreter","Sterk","Steur","Stokvis","Surfer","Takata","Taks","Tangy","Teljora","Terzijde","Thompson","Thorgaldotr","Thorgalsson","Tieter","Tijd","Tijn","Tloc","Tor","Traal","Tracy","Triangl","Tromp","Trotyl","Tsuno","Tuckson","Tumbler","Turbo","Turf","Turtles","Uilenspiegel","Vaillant","Valiant","Van Der Neffe","Verhagen","Verkwil","Vermeire","Violette","Vital","Vondelaar","Voorzichtig","Waggel","Wallet","Wargaren","Warwinkel","Welp","Wentelteefje","Wesley","Wezel","Whitebread","Wiebeling","Winch","Winkle","Woman","Woodpecker","Wortel","Worth","Yves","Zigomar","Zita","Smith","Johnson","Williams","Jones","Brown","Davis","Miller","Wilson","Moore","Taylor","Anderson","Thomas","Jackson","White","Harris","Martin","Thompson","Garcia","Martinez","Robinson","Clark","Rodriguez","Lewis","Lee","Walker","Hall","Allen","Young","Hernandez","King","Wright","Lopez","Hill","Scott","Green","Adams","Baker","Gonzalez","Nelson","Carter","Mitchell","Perez","Roberts","Turner","Phillips","Campbell","Parker","Evans","Edwards","Collins","Stewart","Sanchez","Morris","Rogers","Reed","Cook","Morgan","Bell","Murphy","Bailey","Rivera","Cooper","Richardson","Cox","Howard","Ward","Torres","Peterson","Gray","Ramirez","James","Watson","Brooks","Kelly","Sanders","Price","Bennett","Wood","Barnes","Ross","Henderson","Coleman","Jenkins","Perry","Powell","Long","Patterson","Hughes","Flores","Washington","Butler","Simmons","Foster","Gonzales","Bryant","Alexander","Russell","Griffin","Diaz","Hayes"]
_companylist = ["12 bis","12-Gauge Comics","1First Comics","215 Ink","451 Media Group","4th Wall Productions","Aardvark-Vanaheim","Abacus Comics","About Comics","AC Comics","Actes Sud/l\'AN 2","Action Lab Entertainment","Action Lab Comics Signature Series","AdHouse Books","After Hours Press","Aftershock Comics","AiT/Planet Lar","Akita Shoten","Alterna Comics","Alternative Comics","Angry Viking Press","Ankama Editions","Antarctic Press","Ape Entertainment","Approbation Comics","Arcana Studio","Arch Enemy Entertainment","Archaia Studios Press","Archie Comic Publications","Ardden Entertainment","Ark Vindicta Development and Publishing, LLC","Arktinen Banaani - Arctic Banana","Arrow Comics","Arrow Manga","Asahi Sonorama","ASCII Media Works","Asgardian Comics","Aspen MLT","L'Association","Asuka","Atlas Unleashed","Atomic Book Company","avant verlag","Avatar Press","Azteca Productions","Bedside Press","Bel-Ami edizioni","Beta 3 Comics","Beyond Comics","Big Bang Comics","Bitterkomix Pulp","Black Fairy Press","Black Hearted Press","Blank Slate Books","Boneyard Press","Bongo Comics","Boom! Studios","Boundless Comics","Brain Scan Studios","BroadSword Comics","Bubble Comics","Burlyman Entertainment","Bluewater Productions","Buru Lan Ediciones","Calvary Comics","Carlsen Comics","Cartoon Books","Casterman","Champion City Comics","Checker Book Publishing Group","Clap Comix","Class Comics","Classical Comics","Coamix","Coconino Press","comicplus+","Com.x","Conrad","Cool Comics","Core Magazine","Cross Culture","Cult Comics","Curtis Publishing Company","Daak Comics","DAPshow Press","Dare Comics","Dargaud","Dark Horse Comics","Dark Horse Manga","DC Comics","D. C. Thomson & Co. Ltd","The Dead Timez Magazine","Deimos Comics","Delcourt","Desperado Publishing","Devil\'s Due Publishing","Devil\'s Due Digital","DieGo Comics Publishing","Drawn and Quarterly","Dupuis","DWAP Productions","Dynamite Entertainment","EATComics","Edicions de Ponent","Edition 52","E.F.edizioni","eigoMANGA","Emet Comics","Eureka! Comic Labs","Evil Ink Comics","Evil Twin Comics","Fan-Atic Press","Fantagraphics Books","Fierce Comics","Finix Comics","Fluid Friction Comics","Front Froid","Fremok","Full Bleed Studios","Futabasha","Futuropolis","Gemstone Publishing","Gentosha","Gestalt Publishing","Glenat","Glucklicher Montag","Grim Crew Comics","Guild Publications","Guild Works Publications","Hakusensha","Heaven Sent Gaming","Heeby Jeeby Comix","Hero Comics","Hero Graphics","Heroic Publishing","Hexagon Comics","Hirntot Comix","Houbunsha","Hound Comics","Humanoids Publishing","Human Comics Independent Publishing","Current Books","Huuda Huuda","Ichijinsha","Icon","Idaho Comics Group","Ideenschmiede Paul & Paul - IPP","IDW Publishing","Image Comics","Imperium Comics","InterVerse Comics","Imagine Worlds Comics","Jademan Comics","JBC","JC Comics","Jitsugyo no Nihon Sha","Johnny DC","JMFcomics","Kadokawa Shoten","Kana","Kasakura Shuppansha aka Kasakura Publishing","Katzenjammer Comics","Kaze","Ki-oon","Kobunsha","Kodansha","Koyama Press","Laizen Comics","LAMP PoST Publications","La Pasteque","Laska Comix","Last Gasp","Comix & Stories","Legioncomix","Le Lombard","Les 400 coups","Les Humanoides Associes","Liquid Comics","Lonely Robot Comics","Ludovico Technique LLC","Lucha Comics","Mag Garden","Mam Tor Publishing","Manuscript Press","Maple Leaf Publishing","Markosia","Marvel Comics","Max Comics aka MAX","Media Factory","Mille-Iles","Milk Shadow Books","MiniKomix","Mirage Studios","Mirror Comics","Moonstone Books","MOSAIK Steinchen fur Steinchen Verlag","M Press","MyInkComics.com","NBM Publishing","Neko Press","New Baby Productions","New England Comics","Nifty Comics","Nihon Bungeisha","No Comprendo Press","NPC Comics","Omega Dream Distillery Publications - Oddpubs","Off Shoot Comics","Ohzora Publishing","Oni Press","Oog & Blik","Oogachtend","Outpouring Comics","Paper Crane Factory","Perro Muerto Producciones","Penny-Farthing Press","Phi3 COMICS","Pika edition","Piredda Verlag","Planet Random Creative","Plem Plem Productions!","Pocket Watch Books","Pow Pow Press","Print Media","Prism Comics","Radical Comics","Radio Comix","Raj Comics","Reasonably Priced Comics","Rebellion Developments","Red 5 Comics","Red Giant Entertainment","Reprodukt","Retrofit Comics","Revil Comics","Rip Off Press","Robot Comics","RoninComics","Rolf Kauka Comics","Rough Cut Comics","schreiber & leser","Schwarzer Turm","Seoulmunhwasa","Sequential Pulp Comics","Seven Seas Entertainment","ShadowLine","Shanda Fantasy Arts","Shinshokan","Shinchosha","Shodensha","Shogakukan","Shonen Gahosha","Shueisha","Shuppan Manga","Silverline","Slave Labor Graphics","So Cherry Studios","Soleil Productions","Spectrum Comics","Spilt Ink","Square Enix","Studio 407","Takeshobo","Terminal Press","Teshkeel Comics","Timeless Journey Comics","THENEXTART","Titan Books","Todd McFarlane Productions","Tokuma Shoten","Top Cow Productions","Top Shelf Comics","UDON","Ultimate Marvel","UPN-Volksverlag","Valiant Comics","Verotik","Vertigo Comics","Vimanika Comics","Vimanika Comics UK","Viper Comics","VIZ Media","Frankenstein's Daughter[321]","Warp Graphics","Weildarum-Verlag","Weissblech Comics","Yaoi Press","Zenescope Entertainment","ZETABELLA Publishing","Zeta Comics","Zwerchfell Verlag","Mythopoeia","American Mythology Productions","NBM Publishing","Neko Press","New Baby Productions","New England Comics","Nifty Comics","Nihon Bungeisha","No Comprendo Press","NPC Comics","Omega Dream Distillery Publications - Oddpubs","Off Shoot Comics","Ohzora Publishing","Oni Press","Oog & Blik","Oogachtend","Outpouring Comics","Paper Crane Factory","Perro Muerto Producciones","Penny-Farthing Press","Phi3 COMICS","Pika edition","Piredda Verlag","Planet Random Creative","Plem Plem Productions!","Pocket Watch Books","Pow Pow Press","Print Media","Prism Comics","Radical Comics","Radio Comix","Raj Comics","Reasonably Priced Comics","Rebellion Developments","Red 5 Comics","Red Giant Entertainment","Reprodukt","Retrofit Comics","Revil Comics","Rip Off Press","Robot Comics","RoninComics","Rolf Kauka Comics","Rough Cut Comics","schreiber & leser","Schwarzer Turm","Seoulmunhwasa","Sequential Pulp Comics","Seven Seas Entertainment","ShadowLine","Shanda Fantasy Arts","Shinshokan","Shinchosha","Shodensha","Shogakukan","Shueisha","Shuppan Manga","Silverline","Slave Labor Graphics","So Cherry Studios","Soleil Productions","Spectrum Comics","Spilt Ink","Square Enix","Stratum Comics","Studio 407","Takeshobo","Terminal Press","Teshkeel Comics","Timeless Journey Comics","THENEXTART","Titan Books","Todd McFarlane Productions","Tokuma Shoten","Top Cow Productions","Top Shelf Comics","UDON","Ultimate Marvel","UPN-Volksverlag","Valiant Comics","Verotik","Vertigo Comics","Vimanika Comics","Vimanika Comics UK","Viper Comics","VIZ Media","Frankenstein's Daughter","Warp Graphics","Weildarum-Verlag","Weissblech Comics","Yaoi Press","Zenescope Entertainment","ZETABELLA Publishing","Zeta Comics","Zwerchfell Verlag"]
_utf8_fix_dict = {'\x00': 'NULL', 'NULL': 'NULL', '00':'\'00\'' ,'\'\'': '\'\''}


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
        float(s) # for int, long and float - not complex as complex also allows 'J' as number or unit
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
        return ''.join(['\'',new,'\''])
    return new

def number_with_check(number, checkmod=97, quotes=True, newgen=False):
    """
    Typical numerical check for bank numbers (97 is largest prime under 100)
    """
    if newgen: # people born in or after 2000
        check_no = checkmod - (number + 2000000000) % checkmod
    else:
        check_no = checkmod - number % checkmod
    if quotes:
        return ''.join(['\'',str(number),str(check_no).zfill(2),'\''])
    return ''.join([str(number),str(check_no).zfill(2)])

def print_to_file(file, value='', format=True):
    """
    Print to file and adds newline if needed
    """
    if format:
        value = ''.join([value.strip(), '\r\n'])
    file.write(value.decode('utf-8'))

_print_statements = set()
def single_print_statment(prnt):
    """
    Prevent printing double statements
    """
    global _print_statements
    if prnt not in _print_statements:
        _print_statements.add(prnt)
        print prnt


# Obfuscation options
# *******************

_parameters = {'nullcheck': ['orig', 'new'], 'numbers': ['min_no', 'max_no'], 'short': ['max_no'], 'date': ['min_year','max_year'], 'static_string': ['msg']}
# keep last generated values from current table columns (such that first-name, last-name and full contains the same names)
_last_gen = dict()
# set required for the method "set_replace"
_replace_set = dict()

def names(quotes=True,v=True):
    if 'names' not in _last_gen:
        _last_gen['names'] = random.choice(_fnamelist)
    return nullcheck(v, _last_gen['names'], quotes=quotes)
def first_name(v = True):
    return names(v)
def last_name(quotes=True,v=True,force=False):
    if 'last_name' not in _last_gen or force:
        _last_gen['last_name'] = random.choice(_lnamelist)
    return nullcheck(v, _last_gen['last_name'], quotes=quotes)
def search_name(quotes=True,v=True):
    return nullcheck(v,"".join(''.join([last_name(False), first_name(False)]).split()), quotes=quotes)
def full_name(v = True):
    return nullcheck(v,''.join([first_name(False), ' ', last_name(False)]))
def street_name(v = True):
    return nullcheck(v,''.join([last_name(False, force=True), "straat"]))
def niscode(v=True):
    return nullcheck(v,str(random.randint(100,4000)).zfill(4))
def numbers(min_no=0, max_no=100,v=True):
    return nullcheck(v,random.randint(int(min_no), int(max_no)), quotes=False)
def static_string(msg="An important remark", v=True):
    return nullcheck(v, msg)
def short(max_no=5, v=''):
    max_no = int(max_no)
    if v:
        v = ''.join(e for e in v if e.isalnum())
    if not v:
        return '\'\''
    return nullcheck(v, v[:max_no])
def date(min_year=1945, max_year=2017,v=True):
    return nullcheck(v,''.join([str(random.randint(min_year, max_year)).zfill(4),
                                '-',str(random.randint(1, 12)).zfill(2),
                                '-', str(random.randint(1, 28)).zfill(2)]))
def ip(v = False):
    return nullcheck(v,".".join(map(str, (random.randint(0, 255) for _ in range(4)))))
def email(v = False):
    providerlist = ['mozilla.com', 'provider.be']
    return nullcheck(v,''.join([first_name(False).lower(), '@', random.choice(providerlist)]))
def company(v=True):
    return nullcheck(v,random.choice(_companylist))
def company_no(v=True):
    return nullcheck(v,number_with_check(random.randint(1000000,9998999), quotes=False))
def company_rsz(v=True):
    return nullcheck(v,number_with_check(random.randint(1000000,9998999), quotes=False))
def iban(v=True):
    return iban_be(v)
def iban_be(v=True):
    random_no = random.randint(631000000,639000000)
    check_no = str(random_no % 97).zfill(2)
    belgian_bank_account = ''.join([str(random_no), str(check_no)])
    check_no = 98 - int(''.join([belgian_bank_account, "111400"])) % 97
    return nullcheck(v,''.join(["BE", str(check_no).zfill(2),"0", belgian_bank_account]))
_unique_insz = set()
def insz(v=False, birthdate=False, sex=False):
    birth = random.randint(5,995)
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
            birth+=1
    elif birth % 2 == 0:
        birth+=1
    if not birthdate:
        birthdate = date()
        birthdate = birthdate.replace('-', '')[2:]
    random_no = ''.join([str(birthdate),str(birth).zfill(3)])
    new_insz = number_with_check(int(random_no), quotes=False, newgen=newgen).zfill(11)
    global _unique_insz
    if new_insz in _unique_insz:
        return insz(v=v)
    _unique_insz.add(new_insz)
    return ''.join(['\'',new_insz,'\''])
def phone_no(v=True):
    return nullcheck(v,''.join(['03', str(random.randint(1000000,9000000))]))
def cell_phone_no(v=True):
    return nullcheck(v,''.join(['0478 ', str(random.randint(100000,900000))]))
def registration_number(v=True):
    return nullcheck(v,str(random.randint(10000000,98888888)))


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
        for i,row in enumerate(columns):
            if row in table_column_names:
                self.parse_tables[table][i] = self.tables[table][table_column_names.index(row)][1:]
            elif row in self.general_columns_list:
                self.parse_tables[table][i] = self.tables["general_table_columns"][self.general_columns_list.index(row)][1:]
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
        values=line.partition('` VALUES ')[2]
        if not values:
            return "(" + line.partition(') VALUES (')[2]
        return values

    def values_sanity_check(self, values):
        """
        Ensures that values from the INSERT statement meet basic checks.
        """
        assert values
        assert values[0] == '('
        return True # Assertions have not been raised

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
        if function in _parameters: #if function is known to have parameters
            for i,p in enumerate(arguments):
                params[_parameters[function][i]] = p
        params['v'] = original_value
        return globals()[function](**params)

    def parse_values(self, table, values): #, outfile):
        """
        Parse the given values to an obfuscated INSERT statement
        """
        #if self.values_sanity_check(values):
        global _last_gen
        reader = csv.reader([values[:-1]],  
                    delimiter=',',
                    doublequote=False,
                    escapechar='\\',
                    quotechar="'",
                    strict=True
        )
        latest_row=list()
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
                elif len(t)-1 == len(latest_row):
                    column = column[:-1]
                    last = True

                # Change / Obfuscate the values according to defitition in settings file
                func = t[len(latest_row)]
                if func[0] in func_change_dict:
                    if func[0] == 'cond_replace' and column not in _utf8_fix_dict:
                        replace[len(latest_row)] = func[1:]
                    elif column == func[1]: # already certain cond_remove
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
                    column = ''.join(['\'',column[1:].replace("\'","\\\'",column.count('\'') - 2)])
                latest_row.append(str(column))

                # If a datarow is completed
                if last:
                    if len(replace) > 0:
                        for key in replace.keys():
                            # Get the function id if the accompanied word occurs
                            occurences = [replace[key][0].split(',').index(item) for item in replace[key][0].split(',') if ''.join(['\'',item,'\'']) in latest_row]
                            if len(occurences) > 0:
                                latest_row[key] = str(self.obfuscate(latest_row[key], replace[key][1].split(',')[occurences[0]], []))
                        replace = dict()
                    if not remove:
                        returnstring = ''.join([returnstring, "(", ','.join(latest_row).replace('\x00', '\'\''), "),"])
                    last = False
                    remove = False
                    latest_row=list()
                    _last_gen=dict()

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
            print_to_file(output, line)
        elif t in truncates: # truncate in settings file means delete line
            if not_silent:
                single_print_statment("Table {0} truncated".format(t))
        elif not tables.check_table_known(t, line):
            if not_silent:
                single_print_statment("Skipped inserts for table {0}".format(t))
            print_to_file(output, line)
        else:
            values = tables.parse_values(t, tables.get_values(line))
            if values and values != '': # Fix for empty lines (INSERT INTO tblname VALUES;)
                print_to_file(output, values)
            if not_silent:
                print "Insert statement for table {0} written (Elapsed time: {1:.2f})".format(t, time.time() - start_time)
        return table
    elif line.startswith('CREATE'):
        table = tables.get_table(line)
    print_to_file(output, l, False)
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
    scriptname = sys.argv[0]    # makes it easy to rename the file

    # Get and set optional parameters
    try:
        opts, args = getopt.getopt(argv,"h:i:o:s:",["ifile=","ofile=","sfile="])
    except getopt.GetoptError:
        print '{0} [-i <inputfile>] [-o <outputfile>] [-s <settingsfile>]'.format(scriptname)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print '{0} -i <inputfile> -o <outputfile> -s <settingsfile>'.format(scriptname)
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
            print "Input file \"{0}\" doesn't exist.".format(inputfile)
            print 'Format: {0} [-i <inputfile>] [-o <outputfile>] [-s <settingsfile>]'.format(scriptname)
            sys.exit(0)
        # Check if the output file already exists
        if os.path.isfile(outputfile):
            if raw_input("Outputfile \"{0}\" already exists. Overwrite? [y/n] ".format(outputfile))[0] != 'y':
                sys.exit(0)
    else:
        global _PRINT_FEEDBACK
        _PRINT_FEEDBACK = False

    # Obfuscate the given input file with the settings to the given output file
    output=codecs.open(outputfile, "w",encoding="utf-8", buffering=0)
    if _PRINT_FEEDBACK:
        print "Reading settings..."
    try:
        # Read in configuration file
        tables = dict()
        truncates = set()
        if os.path.isfile(settingsfile):
            with codecs.open(settingsfile, encoding="utf-8") as f:
                t = False
                g = False
                for l in [x.strip().replace("\t", " ").split("#")[0] for x in f.readlines() if x.split("#")[0] and x[0] not in ['#', '/']]:
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
            print "No settings file"
            sys.exit()
        if 'tables' not in locals() or type(tables) is not dict:
            print "Please define a tables variable as tables = dict()"
            sys.exit()
        if len(tables) < 1:
            print "No table profiles in settings file"
            sys.exit()

        # Parse file and obfuscate the tables according to settings file
        table = False
        tables = SettingsTable(tables)
        start_time = time.time()
        
        if inputfile == "console":
            for line in sys.stdin:
                table = read_sql_by_line(line, tables, table, truncates, start_time, output, not_silent=_PRINT_FEEDBACK)
                sys.stdout.write(line)
        else:
            with open(inputfile, 'r') as f:
                for line in f:
                    table = read_sql_by_line(line, tables, table, truncates, start_time, output, not_silent=_PRINT_FEEDBACK)

        print_to_file(output)
        output.close()
        if _PRINT_FEEDBACK:
            print "Finished (Elapsed time: {0:.2f})".format(time.time() - start_time)

    except KeyboardInterrupt:
        output.close()
        sys.exit(0)


# Start actual program
# ************************

if __name__ == "__main__":
    main(sys.argv[1:])
