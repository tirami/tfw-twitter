import extract

lines = tuple(open("text_tweets.txt", 'r'))
for l in lines:
    print ""
    print l
    print extract.process_status(l)

