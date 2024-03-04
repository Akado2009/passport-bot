# passport-bot
Just a bot to track passport slots in the russian consulat.



<!-- drill -->
1. allow multiple subscriptions and the ability to cancel one (/subscribe and that prompt thing)
2. allow viewing of active running subscriptions


1. ask for a link and parse it using regexp
x = re.search(r'[0-9]{5}', txt) (Filters.Regexp - take from there)
2. some consulats have different text (no Извините)
3. install chromedriver... https://skolo.online/documents/webscrapping/#step-2-install-chromedriver