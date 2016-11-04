'''
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def trends_default(path):
    #List of counrties with google trends
    geo_hottrends=country_list()
    # Country of trends
    country_of_trends=country_map("US")
    #List of trends google trends
    trends, trend_date, trend_date_url=google_trends(country="US",dayP=0)
    return render_template("index.html", 
        geo_hottrends=geo_hottrends, 
        country_of_trends=country_of_trends, 
        trends=trends,
        trend_date=trend_date,
        trend_date_url=trend_date_url,
        tweet_id='451399393850052610')
'''