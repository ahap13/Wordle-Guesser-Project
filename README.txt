This is a script for a Coursera course project that provides an educated guess for the game Wordle, given a screenshot of a current game board. The game board can have anywhere between one and five guesses.

The script will process the image by using color recognition to figure out which letters are in the correct position, in the word, and not in the word at all. Then I used pytesseract to do optical character recognition (OCR) to create the guesses themselves.

Then it was just a matter of keeping track of the letters, a working guess, and then finding a word in the available words file that matches my criteria. 

The bot may not be able to win the game, but it should provide an educated guess that does not include letters that should not be there, includes letters that are in the word, and has all known positional matches.

Note: The course was developed by the staff at the University of Michigan, so the colors in the screenshot are Blue and Maize, not yellow and green. The display specifications can be modified in the wordy.py file.

*** The only python file I wrote is guesser.py; The rest were provided to do the project