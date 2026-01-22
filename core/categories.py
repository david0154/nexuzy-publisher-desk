"""
News Categories Configuration
Comprehensive list of news categories for RSS feeds and articles
"""

# Complete list of news categories
NEWS_CATEGORIES = [
    # General
    'General',
    'Top Stories',
    'Breaking News',
    'Latest News',
    
    # Politics & Government
    'Politics',
    'Government',
    'Elections',
    'International Relations',
    'Diplomacy',
    'Policy',
    
    # Business & Economy
    'Business',
    'Economy',
    'Finance',
    'Markets',
    'Stock Market',
    'Cryptocurrency',
    'Startups',
    'Entrepreneurship',
    'Real Estate',
    'Banking',
    
    # Technology
    'Technology',
    'AI & Machine Learning',
    'Gadgets',
    'Software',
    'Hardware',
    'Mobile',
    'Apps',
    'Cybersecurity',
    'Cloud Computing',
    'Internet',
    'Programming',
    'Gaming',
    
    # Science & Health
    'Science',
    'Health',
    'Medicine',
    'Research',
    'Space',
    'Environment',
    'Climate Change',
    'Biology',
    'Physics',
    'Chemistry',
    'Mental Health',
    'Fitness',
    'Nutrition',
    
    # Sports
    'Sports',
    'Football',
    'Cricket',
    'Basketball',
    'Tennis',
    'Baseball',
    'Hockey',
    'Olympics',
    'Motor Sports',
    'Extreme Sports',
    'Esports',
    
    # Entertainment
    'Entertainment',
    'Movies',
    'TV Shows',
    'Music',
    'Celebrities',
    'Hollywood',
    'Bollywood',
    'Streaming',
    'Theater',
    'Awards',
    
    # Lifestyle & Culture
    'Lifestyle',
    'Culture',
    'Fashion',
    'Beauty',
    'Travel',
    'Food',
    'Cooking',
    'Home & Garden',
    'Parenting',
    'Relationships',
    'Weddings',
    
    # Education & Career
    'Education',
    'Career',
    'Jobs',
    'Skills',
    'Universities',
    'Online Learning',
    
    # World & Regional
    'World News',
    'Asia',
    'Europe',
    'Americas',
    'Africa',
    'Middle East',
    'Australia',
    'India',
    'USA',
    'UK',
    'China',
    
    # Social & Opinion
    'Opinion',
    'Editorial',
    'Analysis',
    'Commentary',
    'Blogs',
    
    # Crime & Law
    'Crime',
    'Law',
    'Legal',
    'Court',
    'Investigation',
    
    # Environment & Nature
    'Wildlife',
    'Conservation',
    'Sustainability',
    'Renewable Energy',
    
    # Automotive
    'Automotive',
    'Cars',
    'Electric Vehicles',
    'Auto Reviews',
    
    # Religion & Spirituality
    'Religion',
    'Spirituality',
    
    # Other
    'Weather',
    'Disasters',
    'Odd News',
    'Human Interest',
    'Obituaries',
    'Local News'
]

# Category groups for organization
CATEGORY_GROUPS = {
    'News': ['General', 'Top Stories', 'Breaking News', 'Latest News', 'World News'],
    'Politics': ['Politics', 'Government', 'Elections', 'International Relations', 'Diplomacy', 'Policy'],
    'Business': ['Business', 'Economy', 'Finance', 'Markets', 'Stock Market', 'Cryptocurrency', 'Startups', 'Real Estate', 'Banking'],
    'Technology': ['Technology', 'AI & Machine Learning', 'Gadgets', 'Software', 'Hardware', 'Mobile', 'Apps', 'Cybersecurity', 'Gaming'],
    'Science & Health': ['Science', 'Health', 'Medicine', 'Research', 'Space', 'Environment', 'Climate Change', 'Mental Health', 'Fitness'],
    'Sports': ['Sports', 'Football', 'Cricket', 'Basketball', 'Tennis', 'Baseball', 'Hockey', 'Olympics', 'Esports'],
    'Entertainment': ['Entertainment', 'Movies', 'TV Shows', 'Music', 'Celebrities', 'Hollywood', 'Bollywood', 'Streaming'],
    'Lifestyle': ['Lifestyle', 'Culture', 'Fashion', 'Beauty', 'Travel', 'Food', 'Cooking', 'Home & Garden', 'Parenting'],
    'World': ['Asia', 'Europe', 'Americas', 'Africa', 'Middle East', 'Australia', 'India', 'USA', 'UK', 'China'],
    'Other': ['Education', 'Career', 'Crime', 'Law', 'Weather', 'Automotive', 'Religion', 'Opinion']
}

# Popular RSS feed suggestions by category
POPULAR_FEEDS = {
    'Technology': [
        ('TechCrunch', 'https://techcrunch.com/feed/'),
        ('The Verge', 'https://www.theverge.com/rss/index.xml'),
        ('Ars Technica', 'http://feeds.arstechnica.com/arstechnica/index'),
        ('Wired', 'https://www.wired.com/feed/rss'),
    ],
    'Business': [
        ('Reuters Business', 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best'),
        ('Bloomberg', 'https://www.bloomberg.com/feed/podcast/bloomberg-brief.xml'),
        ('Forbes', 'https://www.forbes.com/real-time/feed2/'),
    ],
    'Science': [
        ('Scientific American', 'http://rss.sciam.com/ScientificAmerican-Global'),
        ('Nature', 'http://feeds.nature.com/nature/rss/current'),
        ('Science Daily', 'https://www.sciencedaily.com/rss/all.xml'),
    ],
    'Sports': [
        ('ESPN', 'https://www.espn.com/espn/rss/news'),
        ('BBC Sport', 'http://feeds.bbci.co.uk/sport/rss.xml'),
    ],
    'General': [
        ('BBC News', 'http://feeds.bbci.co.uk/news/rss.xml'),
        ('CNN', 'http://rss.cnn.com/rss/edition.rss'),
        ('Reuters', 'https://www.reutersagency.com/feed/?best-topics=tech'),
    ]
}

def get_all_categories():
    """Get all available categories"""
    return sorted(NEWS_CATEGORIES)

def get_category_groups():
    """Get categories organized by groups"""
    return CATEGORY_GROUPS

def get_popular_feeds(category=None):
    """Get popular RSS feeds for a category"""
    if category:
        return POPULAR_FEEDS.get(category, [])
    return POPULAR_FEEDS
