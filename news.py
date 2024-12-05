#https://github.com/codelucas/newspaper
#pip3 install newspaper3k

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

print(article.keywords)

print(article.summary)

print(article.text)

print(article.authors)
print(article.publish_date)
