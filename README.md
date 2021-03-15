# animal-name-scrapper
Time it took to write the code:
approx an hour for a basic working version, Approx. 2-2.5 more hours for handling the edge cases 
(especially with the data edge cases and the synonyms list)
Another hour for writing the unit tests and parsing it into an html file

Time Complexity approximation - O(n) where n is the number of animals in the table
For each animal there are a few collateral_adjectives, but this num < C for some constant.
Searching for values in the dict(hashtable) is done in O(1), as is adding values to the table.

Notes:
1. Regarding Animal Synonyms, (some animals have "See X") reference, this is because they are not unique animals,
but rather another name for this animal,  They will appear in the dictionary under the empty "" key,  
but also, they will appear in a synonyms list, which is printed afterwards.

2. Given more time, I might have looked into using more beautiful soup functionality 
to refactor the function _parse_animal_name().
This will be instead some of the regex, I believe this can make the code more bug proof by future possible changes to 
the wiki page. Currently the format is very dependent on the current state and format of the page.
I have no guarantee it will stay this way.
