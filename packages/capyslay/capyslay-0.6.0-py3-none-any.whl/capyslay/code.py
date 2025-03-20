from IPython.display import Javascript, display

from .tokenizer import tokenize
from .wordcount import wordcount
from .corpus import corpus
from .grams import grams
from .smoothing import smoothing
from .pos import pos
from .stopwords import stopwords
from .stemming import stemming

from .studData import studData
from .visitingCard import visitingCard
from calculator import calculator
from .signin import signin
from .wallpaper import wallpaper
from .counter import counter
from .text2speech import text2speech
from .caller import caller
from .mediaplayer import mediaplayer
from .database1 import database1
from .quiz import quiz
from .currencyConverter import currencyConverter
from .unitsConverter import unitsConverter

def print_codes(codes):
    codes = codes[::-1]

    for code in codes:
        js_code = f'''
        var cell = Jupyter.notebook.insert_cell_below('code');
        cell.set_text(`{code}`);
        '''
        display(Javascript(js_code))



def hail(program):
    if program == "studData":
        codes = studData()
    elif program == "visitingCard":
        codes = visitingCard()
    elif program == "calculator":
        codes = calculator()
    elif program == "signin":
        codes = signin()    
    elif program == "wallpaper":
        codes = wallpaper()
    elif program == "counter":
        codes = counter()
    elif program == 'text2speech':
        codes = text2speech()
    elif program == 'caller':
        codes = caller()
    elif program == 'mediaplayer':
        codes = mediaplayer()
    elif program == 'database1':
        codes = database1()
    elif program == 'unitsconverter':
        codes = unitsConverter()
    elif program == 'currencyConverter':
        codes = currencyConverter()
    elif program == 'quiz':
        codes = quiz()
    else:
        codes = [
            """
            Available studData, visitingCard, calculator, signin,wallpaper, counter, text2speech, caller, mediplayer, database1,
            unitsConverter, currencyConverter, quiz
            """
        ]

    print_codes(codes)


def code(program):
    if (1 == 1):
        codes = []
    elif program == "tokenize":
        codes = tokenize()
    elif program == "wordcount":
        codes = wordcount()
    elif program == "corpus":
        codes = corpus()
    elif program == "grams":
        codes = grams()
    elif program == "smoothing":
        codes = smoothing()
    elif program == "pos":
        codes = pos()
    elif program == "stopwords":
        codes = stopwords()
    elif program == "stemming":
        codes = stemming()
    else:
        codes = []

    print_codes(codes)