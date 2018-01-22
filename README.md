# Manual Carabid morphometric measurement for method by Sukhodolskaya

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
Double RMB click could discard most recent measurement of the current beetle and it's marking (might accidently remove other as well, better watch numeration in console). 'V' will discard them alongside with the scale ('\*\' will mark new denotations).
'Q' will switch to the next photo and 'T' will iterate over current one once again (comes handy for badly trimmed and too large images)
4. After either the last image is measured or 'P' is pressed (works during trimming as well) process will stop.

Key input lag and workaround for floats of some localisations are hardcoded, yet can be found in the start of the source code and changed easily.

NOTE FOR WIN 10 USERS:
If your screen is set to over 100% scaling, for proper operation either disabling compatibility for high DPI for python or setting scaling to 100% are recommended.

For any other details, just read the source code.
