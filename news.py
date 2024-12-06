#https://github.com/codelucas/newspaper
#pip3 install newspaper3k
#too many runs will make the newspaper block.  
#create UI to manage paper/input sources.  
# then have aggregation settings.  
#and feedback loop.  
#not simple like/dislike though.  Need much more nuanced feedback.  
#why not just provide human language feedback.  
#"I would like to read about ...."
#"What happened in Tampa today?"
#"Find some heartwarming story for me.."
# Then provide feedback
#"Give me the headlines"
#"Read that story"
# Need decent TTS for this.  


import newspaper

cnn_paper = newspaper.build('http://cnn.com')

for article in cnn_paper.articles:
    print(article.url)

for category in cnn_paper.category_urls():
    print(category)


cnn_article = cnn_paper.articles[0]
cnn_article.download()
cnn_article.parse()
cnn_article.nlp()

print(cnn_article.keywords)

print(cnn_article.summary)

print(cnn_article.text)

print(cnn_article.authors)
print(cnn_article.publish_date)
