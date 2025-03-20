#full text to slang words
import string
import re
from pytoslang.fullToSlang import fullToSlang
from pytoslang.slangToEmoji import slangToEmoji
from pytoslang.SlangToFull import SlangToFull

def remove_punctuation(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)


def full_to_slang(words):
    words = words.lower()
    for phrase, slang in fullToSlang.items():
        pattern = r'\b{}\b'.format(re.escape(phrase))
        #words = words.replace(phrase, slang)
        words = re.sub(pattern, slang, words)
    
    return words

def slang_to_full(words):
    words = words.lower()
    for slang, phrase in SlangToFull.items():
        pattern = r'\b{}\b'.format(re.escape(slang))
        words = re.sub(pattern, phrase, words)
    return words


##slang to emojis
def slang_to_emoji(words):
    words = str(words).lower()
    for slang, emoji in slangToEmoji.items():
        pattern = r'\b{}\b'.format(re.escape(slang))
        #words = words.replace(slang, emoji)
        words = re.sub(pattern, emoji, words)
    return words



def remove_slang(words):
    words = words.lower()

    for slang in SlangToFull.keys():
        words = re.sub(r'\b{}\b'.format(re.escape(slang)), '', words)

    return " ".join(words.split())

def main():
    #example text for all the necessary conversions 

    text = "I love software engineering, omg , I don't know though I really need to stop procrastinating lol! #stem"

    print("Orginal Text:")
    print(text)


    #full text to slang 

    slang_text = full_to_slang(text)
    print("\nConverted to slang:")
    print(slang_text)

    #slang to full text 

    full_text = slang_to_full(text)
    print("\nConverted to full:")
    print(full_text)

    #slang to emojis 
    emoji_version =slang_to_emoji(text)
    print("\nConverted to emoji:")
    print(emoji_version)

    #removes slang
    remove_slang_from_text = remove_slang(text)
    print("\nRemoving all slang:")
    print(remove_slang_from_text)

if __name__ == "__main__":
    main()

