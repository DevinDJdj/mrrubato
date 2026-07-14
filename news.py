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
#pip install lxml_html_clean

import newspaper
import extensions.trey.qdrantz as qdrantz


allarticles = [] #{title, url, category, text, authors, publish_date, summary, keywords}


def get_news(source_url):
    paper = newspaper.build(source_url, memoize_articles=False)
    print(f'Found {len(paper.articles)} articles in {source_url}')
    sarticles = []
    for idx,article in enumerate(paper.articles):
        try:
            if (idx < 10): #limit for now
                print(f'Processing article {idx}: {article.url}')
                print(article)
                article.download()
                article.parse()
                article.nlp()
                a = {'paper': source_url, 'title': article.title, 'url': article.url, 'text': article.text, 'authors': article.authors, 'publish_date': article.publish_date, 'summary': article.summary, 'keywords': article.keywords}
                sarticles.append(a)
#                allarticles.append(a)
        except Exception as e:
            print(f'Error processing article {article.url}: {e}')
    return sarticles


if (__name__ == "__main__"):
    # Build a newspaper for CNN

    cnn = get_news('http://cnn.com')
    allarticles.extend(cnn)
    bbc = get_news('http://bbc.com')
    allarticles.extend(bbc)
#    get_news('http://nytimes.com')
#    get_news('http://reuters.com')
#    get_news('http://theguardian.com')
#    get_news('http://washingtonpost.com')
#    get_news('http://wsj.com')
    fox = get_news('http://foxnews.com')
    allarticles.extend(fox)

    qdrantz.init_qdrant()
    mynews = qdrantz.get_collection("news")
    texts = [a['text'] for a in allarticles]
    ids = [i for i in range(len(texts))]
    payloads = [allarticles[i] for i in range(len(texts))]
    qdrantz.add_vectors("news", texts, ids, payloads)

    for a in allarticles:
        print(f"Title: {a['title']}")
        print(f"URL: {a['url']}")
#        print(f"Category: {a['category']}")
        print(f"Authors: {a['authors']}")
        print(f"Publish Date: {a['publish_date']}")
        print(f"Summary: {a['summary']}")
        print(f"Keywords: {a['keywords']}")
        print(f"Text: {a['text'][:200]}...")  # Print first 200 characters of the article text
        print("\n---\n")
        #add to local vector DB.  
        #for each sentence in article text.
        #find similar item with different source. 
        #if none found, not verified. 
        #each sentence will be ranked with verification score.




"""
    cnn_paper = newspaper.build('http://cnn.com')
    cnn_article = cnn_paper.articles[0]
    cnn_article.download()
    cnn_article.parse()
    cnn_article.nlp()

    print(cnn_article.keywords)

    print(cnn_article.summary)

    print(cnn_article.text)

    print(cnn_article.authors)
    print(cnn_article.publish_date)
"""