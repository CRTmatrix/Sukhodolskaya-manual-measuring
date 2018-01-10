# Manual Carabid morphometric measurement for method by Sukhodolskay

This is a tool for morphometric beetle measurement. It's purposed for manual measuring input simplification.

For more detailed description read (Russian):
http://www.dissercat.com/content/dinamika-ekologicheskoi-struktury-populyatsii-zhuzhelits-zonalnykh-i-intrazonalnykh-ekosiste
http://old.kpfu.ru/uni/sank/db/filebase/files/871

It was made to run and tested on Python 2.7.13 with numpy 1.11.3 and openCV 3.1. Proper operation on other versions is not granted, yet expected.

Measuring process is composed of subsequent steps:

1. Input directory of folder with photos (Having unicode symbols in not supported).
2. Trimming of photo with double LMB click for top-left corner marking, double RMB for bottom-right. 'R' button for 90 degree rotation (rotate before setting corners) and 'c' for retrieval of trimmed image.
3. Setting 10 mm scale on fiducials.
Measure distance placement in order of 'A','B','V','G','D' and 'E' (Cyrillic transliteration) mit double LMB click, having 14 LM (including scale) saved. Landmark order is not significant. Results in output table will have rows and anterior/leftmost put first.
'S' button is utilized for calling current animal's sex input and writing results down into the table thereafter. 
Double RMB click could discard measurements of the current beetle. 'V' will discard them alongside with the scale ('\*\' will mark new signings).
'Q' will swith to the next photo and 'T' will iterate over current photo once again (comes handy for badly trimmed and too large images)
4. After either the last image is measured or 'P' is pressed (works during trimming as well), results are saved in the same directory as two separate tables (for landmarks and measured distances accordingly).

Screen resolution, key input lag and workaround for floats of some localisations are hardcoded, yet can be found in the start of the source code and changed easily.

For any other details, reading the source code is recommended.
