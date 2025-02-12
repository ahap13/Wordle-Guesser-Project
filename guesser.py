import wordy
import PIL
from PIL import Image, ImageDraw, ImageFilter
import pytesseract
import random

class Letter:
    """Each instance is a single letter from a guess.
    
    Attributes:
        name: str
        in_correct_place: bool = False
        in_word: bool = False"""
    
    def __init__(self, name: str, in_correct_place = False, in_word = False) -> None:
        """Constructor for the Letter class"""
        self.name = name
        self.in_correct_place = in_correct_place
        self.in_word = in_word
        self.letter = name
    
    def is_in_correct_place(self) -> bool:
        """Checks whether the letter is in the correct place"""
        return self.in_correct_place
    
    def is_in_word(self) -> bool:
        """Checks whether the letter is in the word"""
        return self.in_word

def prep_image(img: Image) -> Image:
    """Preprocesses image for OCR"""
    img_copy = img.copy()
    img_copy = img.convert("L") # Turn to grayscale
    img_copy = img_copy.resize((img_copy.width * 4, img_copy.height * 4)) # Enlarge
    
    new_img = bytearray(img_copy.tobytes()) # Convert to bytearray to enumerate
    
    # Convert to b&w max contrast
    for location, value in enumerate(new_img):
        if value == 255:
            new_img[location] = 0
        else:
            new_img[location] = 255
            
    new_image = PIL.Image.frombytes(img_copy.mode, img_copy.size, bytes(new_img))
    new_image = new_image.filter(ImageFilter.DETAIL)
    
    return new_image


def solution(board: PIL.Image) -> str:
    """The student solution to the problem.
    
    Query wordy module to get board state. Use ocr and colors to make a best next guess
    Re-use logic code from other assignments (make new functions?)
    pytesseract module for ocr. Look into docs
    
    Get colors from photo first to see whats right, then turn it gray or do whatever needed for ocr

    Returns:
        str: guess.
    """
    new_guess = ""
    
    new_image = board.copy()
    new_image = prep_image(new_image)
    old_image = board.copy()
    old_image = old_image.resize((old_image.width * 4, old_image.height * 4))
    width, height = new_image.size
    section_width = width // 5 # Section is 20% of width so there's one for each letter
    section_height = 240 # This is the height of each section, hardcoded because each image will be different heights
    
    str_letters = []
    feedback = []
    for i in range(0, height, section_height): # Loop through the image and crop to create sections
        for j in range(0, width, section_width):
            left = j
            top = i
            right = min(j + section_width, width)
            bottom = min(i + section_height, height)
            
            feedback_section = old_image.crop((left+20, top, right-15, bottom))
            ocr_section = new_image.crop((left+20, top, right-15, bottom))
            
            colors = {(0, 39, 76): "in_place", (255, 203, 5): "in_word", (211, 211, 211): "wrong"}
            colorsample = feedback_section.getpixel((10, 10))
            feedback.append(colors[colorsample])
            
            # Run OCR on each section/letter
            config = '--psm 10 -l eng -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ' # English and characters to
            ocr_res = pytesseract.image_to_string(ocr_section, config=config)
            if len(ocr_res) == 0:
                config = '--psm 13 -l eng -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                ocr_res = pytesseract.image_to_string(ocr_section, config=config)
                str_letters.append(ocr_res.strip())
            else:
                str_letters.append(ocr_res.strip())
    
    # Clean up OCR, make letter objects 
    guesses_with_feedback = [x for x in zip(str_letters, feedback)] # Every letter guessed with result
    letters = []
    for guess in guesses_with_feedback:
        name = guess[0]
        result = guess[1]
        if name == "LL":
            name = "I"
        if result == "in_place":
            new_letter = Letter(name, in_correct_place = True, in_word = True)
            letters.append(new_letter)
        elif result == "in_word":
            new_letter = Letter(name, in_word = True)
            letters.append(new_letter)
        else:
            new_letter = Letter(name)
            letters.append(new_letter)
            
    with open("words.txt") as fwords:
        words = fwords.readlines()
    
    words = [word[:5] for word in words] # Stripping words.txt and putting into list
    
    # Vars for letter/word processing
    current_word = []
    current_word_str = ""
    count = 0
    # Vars for building guess
    bad_letters = set() # Letters that aren't in word at all
    letters_in_word = set() # Letters with in_word
    working_guess = [None, None, None, None, None] # Fill this in with letters in_correct_place
    for letter in letters:
        # Remove word from words if exists, reset current word at 5
        # Process letters to find good/bad letters
        if letter.in_correct_place:
            working_guess[count] = letter.name
            letters_in_word.add(letter.name)
        elif letter.in_word:
            letters_in_word.add(letter.name)
        else:
            bad_letters.add(letter.name)
        
        current_word.append(letter)
        current_word_str = current_word_str + letter.name
        count += 1
        
        # If it's the 5th letter, remove from word list to eliminate future guess and reset word
        # If not in word list then check for common errors
        if len(current_word) == 5:
            current_word_backup = current_word 
            current_word_str_backup = current_word_str
            count = 0
            if current_word_str in words: # Best case scenario
                words.remove(current_word_str)
                # Now reset current word
                current_word = [] 
                current_word_str = ""
            else: # Test for common errors: C in place of O, T in place of I
                i = 0
                all_changed_copy = current_word
                for letter in current_word: # Go through letter by letter
                    if letter.name == "C" and not letter.in_correct_place: # If C replace with O
                        letter.name = "O"
                        try:
                            current_word_str = f"{current_word[:i]}O{current_word[i+1:]}"
                            all_changed_copy = f"{current_word[:i]}O{current_word[i+1:]}"
                        except:
                            current_word_str = f"{current_word[:i]}O"
                            all_changed_copy = f"{current_word[:i]}O"
                    if letter.name == "T" and not letter.in_correct_place:
                        letter.name = "I"
                        try:
                            current_word_str = f"{current_word[:i]}I{current_word[i+1:]}"
                            all_changed_copy = f"{current_word[:i]}I{current_word[i+1:]}"
                        except:
                            current_word_str = f"{current_word[:i]}I"
                            all_changed_copy = f"{current_word[:i]}I"
                    if current_word_str in words or all_changed_copy in words:
                        try:
                            words.remove(current_word_str)
                        except:
                            words.remove(all_changed_copy)
                        # Now reset current word
                        current_word = [] 
                        current_word_str = ""
                        break
                    else:
                        current_word = current_word_backup # Change it back
                        current_word_str = current_word_str_backup # Change it back
                if all_changed_copy in words:
                    try:
                        words.remove(current_word_str)
                    except:
                        words.remove(all_changed_copy)
                # Now reset current word
                current_word = [] 
                current_word_str = ""
                
    # Now pick an educated guess from remaining words in words based on working guess, bad_letters, letters_in_word
    best_choices = {} # Words that have letters in the correct spot, {word: count_in_place}
    alt_choices = {} # Words that just have the right letters somewhere {word: count_in_word}
        
    # If choice dicts are empty, return random choice (occurs if first guess or prev guesses yielded nothing)
    # Remove choice from word_list after guessing
    if len(best_choices) == 0 and len(alt_choices) == 0 and len(bad_letters) == 0 and len(letters_in_word) == 0:
        choice = random.choice(words)
        words.remove(choice) # Removes guess from remaining available words
        return choice
        
    # After the first guess, make smart guesses
    # Pick a remaining word that has the most correct letters in place
    # Break tie with count of letters in word
    # Remove guess from word_list
    # Iterate through each available word, compare to working_guess
    for word in words:
            
        # Change to true if you remove.(word) and then continue before next loop
        remove = False
            
        # Check each word for any bad letters
        for letter in bad_letters:
            if letter in word: 
                words.remove(word)
                remove = True
                break
            
        if remove: continue
            
        # Disqual if letter doesn't match same position in working guess (not None)
        for i in range(5):
            if word[i] != working_guess[i] and working_guess[i] != None:
                words.remove(word)
                remove = True
                break
                    
        if remove: continue
                
        # Add to appropriate dicts for good matches
        for i in range(len(word)):
            if word[i] == working_guess[i]: # If there is a positional match
                if word not in best_choices:
                    best_choices[word] = 0
                    alt_choices[word] = 0
                best_choices[word] += 1 
                alt_choices[word] += 1
                    
    # If neither list populates then just pull a random word
    if len(best_choices) == 0 and len(alt_choices) == 0:
        choice = random.choice(words)
        words.remove(choice)
        return choice
            
        
    # Iterate through best_choices to get best choice, if empty then go through alt_choice
    bchoices_sorted = dict(sorted(best_choices.items(), key=lambda key: key[1], reverse=True))
    achoices_sorted = dict(sorted(alt_choices.items(), key=lambda key: key[1], reverse=True))
        
    # Go through sorted dicts, pick the first word that meets criteria 
    # Has to use known correct letters in correct spots
    choice = None
    for key in bchoices_sorted.keys():
        for i in range(len(key)):
            if working_guess[i] == None: continue # No need to check unknown spaces
            elif working_guess[i] != key[i]: break
        choice = key
        
    if choice != None:
        words.remove(choice)
        return choice
        
    for key in achoices_sorted.keys():
        for i in range(len(key)):
            if working_guess[i] == None: continue
            elif working_guess[i] != key[i]: break
        choice = key
        
    if choice == None:
        print(best_choices, alt_choices)
        print(bchoices_sorted, achoices_sorted)
        return choice  
        

img = wordy.get_board_state()
choice = solution(img)
print(f"Choice: {choice}")