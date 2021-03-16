# animal-name-scrapper
Getting Started:
Run "Main.py"
If you wish to also download the images you can add
```
Main.py --d
```

To use an image download path different then "/tmp" use:
```
Main.py --d --path "YOURPATH"
```

**Time it took to write the code:**

Approx an hour for a basic working version, Approx. 2-2.5 more hours for handling the edge cases 
(especially with the data edge cases and the synonyms dict)
Another hour for writing the unit tests and parsing it into an html file.
A few hours for the image download mechanism. some code refactoring and documentation.
Adding thread support for downloading images was simpler then expected.

**Time Complexity approximation:**

O(n) where n is the number of animals in the table
For each animal there are a few collateral_adjectives, but this num < C, for some constant C (We can assume C<=5)
Searching for values in the dict(hashtable) is done in O(1), as is adding values to the table.

Main bottleneck of the application is the images, It has 2 parts: getting the image url and downloading the image. 
Both can take a long time (Around a sec for each image). To overpass this I used threading, it fits great with this IO 
use case and it shortens the run time by a large margin.

**Notes:**

1. Regarding Animal Synonyms, (some animals have "See X") reference, this is because they are not unique animals,
but rather another name for this animal.  They will not appear in the dictionary.
Instead, they will appear in a synonyms dict, which is printed afterwards. (not shown in the html)

2. Given more time, I might have looked into using more beautiful soup functionality 
to refactor the function _parse_animal_name().
This will be used instead some of the regex, I believe this can make the code more bug proof by future possible 
changes to the wiki page. Currently the format is very dependent on the current state and format of the page.
As I have no guarantee the format won't change even slightly.

3. More Unit tests can be added, ideally a test for each independent function, and for more edge cases and exceptions.

4. I am aware that the method of retrieving the images can miss some images, 
but I think the method I chose to take the image from the infobox has a pretty high chance overall of being correct.
A better solution might be to address another site where the pictures are tagged and present for all animals.
I thought it was the case for wikipedia, but apparently it isn't.

