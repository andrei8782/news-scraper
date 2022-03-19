from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

def remove_stop_words(tokens):
    stop_words_list = stopwords.words()
    return [token for token in tokens if token not in stop_words_list]

def to_space(c):
    if c.isalpha():
        return c
    else:
        return ' '

def tokenize(text):
    text = text.lower()
    modified_text = "".join(map(to_space, text))
    return modified_text.split()

def porter_stemming(str):
    porter_stemmer = PorterStemmer()
    return [porter_stemmer.stem(word) for word in str]

def stem(token):
    porter_stemmer = PorterStemmer()
    return porter_stemmer.stem(token)

def preprocess(text):
    tokenized_text = tokenize(text)
    filtered_text = remove_stop_words(tokenized_text)
    stems = porter_stemming(filtered_text)
    return stems