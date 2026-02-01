import requests
from datetime import date
from pprint import pprint

API_TOKEN = "wDUNbwdxSYrwoDxEV1gDbxcRKLqDByDRA426ZJ7y"  # replace with your Marketaux key

# Target companies
symbols_list = ["TSLA", "AMZN", "NVDA"]
url = "https://api.marketaux.com/v1/news/all"

ARTICLES_PER_SYMBOL = 3
OUTPUT_FILE = "sentiment.txt"

def fetch_marketaux_news(symbol: str, limit: int = ARTICLES_PER_SYMBOL):
    """Fetch news for a single symbol from Marketaux."""
    params = {
        "api_token": API_TOKEN,
        "symbols": symbol,
        "language": "en",
        "filter_entities": "true",
        "limit": limit
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def structure_marketaux_response(api_response: dict):
    """Convert Marketaux API response into clean structured format."""
    structured = []

    for article in api_response.get("data", []):
        article_obj = {
            "id": article.get("uuid"),
            "title": article.get("title"),
            "summary": article.get("description") or article.get("snippet"),
            "source": article.get("source"),
            "url": article.get("url"),
            "published_at": article.get("published_at"),
            "companies": []
        }

        for entity in article.get("entities", []):
            company_obj = {
                "symbol": entity.get("symbol"),
                "name": entity.get("name"),
                "industry": entity.get("industry"),
                "sentiment_score": entity.get("sentiment_score"),
                "sentiment_label": (
                    "Positive" if entity.get("sentiment_score", 0) > 0.05 else
                    "Negative" if entity.get("sentiment_score", 0) < -0.05 else
                    "Neutral"
                )
            }
            article_obj["companies"].append(company_obj)

        structured.append(article_obj)

    return structured

def save_articles_to_file(articles, filename=OUTPUT_FILE):
    """Save structured articles to a text file for Watson ingestion."""
    with open("sentiment.txt", "w", encoding="utf-8") as f:
        f.write(f"Sentiment Analysis Articles - Date: {date.today()}\n\n")
        for i, article in enumerate(articles, 1):
            f.write(f"Article {i}:\n")
            f.write(f"Title: {article['title']}\n")
            f.write(f"Summary: {article['summary']}\n")
            f.write(f"Source: {article['source']}\n")
            f.write(f"URL: {article['url']}\n")
            f.write(f"Published At: {article['published_at']}\n")
            f.write("Companies:\n")
            for company in article['companies']:
                f.write(f"  - {company['name']} ({company['symbol']}, {company['industry']}), "
                        f"Sentiment: {company['sentiment_label']} ({company['sentiment_score']})\n")
            f.write("\n" + "-"*80 + "\n\n")
    print(f"All articles saved to 'sentiment.txt'")

def main():
    all_articles = []

    for symbol in symbols_list:
        try:
            data = fetch_marketaux_news(symbol)
            structured = structure_marketaux_response(data)
            all_articles.extend(structured)
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error for {symbol}: {err}")
        except Exception as e:
            print(f"Error for {symbol}: {e}")

    # Save structured articles to text file
    save_articles_to_file(all_articles)

    # Optional: also pretty-print summary
    pprint({
        "meta": {
            "symbols": symbols_list,
            "total_articles": len(all_articles),
            "date_fetched": str(date.today())
        },
        "articles_count": len(all_articles)
    })

if __name__ == "__main__":
    main()
