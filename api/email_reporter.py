from analytics_fetcher import analytics_summary

def build_weekly_report_html(platform=None):
    s = analytics_summary(platform)
    rows = "".join([f"<tr><td>{p['post_id']}</td><td>{p['platform']}</td><td>{p['likes']}</td><td>{p['comments']}</td><td>{p['shares']}</td><td>{p['engagement_rate']}</td></tr>" for p in s["top_posts"]])
    return f"""
    <h2>Weekly Social Media Report</h2>
    <p>Total reach: {s['total_reach']}</p>
    <p>Average engagement rate: {s['avg_engagement_rate']}</p>
    <table border='1'><tr><th>Post</th><th>Platform</th><th>Likes</th><th>Comments</th><th>Shares</th><th>Engagement</th></tr>{rows}</table>
    """

if __name__ == "__main__":
    print(build_weekly_report_html())
