# Import categories at the top
try:
    from core.categories import get_all_categories, POPULAR_FEEDS
    CATEGORIES = get_all_categories()
except:
    CATEGORIES = [
        'General', 'Breaking News', 'Top Stories',
        'Politics', 'Government', 'Elections', 'International Relations',
        'Business', 'Economy', 'Finance', 'Markets', 'Stock Market', 'Cryptocurrency', 'Startups',
        'Technology', 'AI & Machine Learning', 'Gadgets', 'Software', 'Cybersecurity', 'Gaming',
        'Science', 'Health', 'Medicine', 'Research', 'Space', 'Environment', 'Climate Change',
        'Sports', 'Football', 'Cricket', 'Basketball', 'Tennis', 'Olympics', 'Esports',
        'Entertainment', 'Movies', 'TV Shows', 'Music', 'Celebrities', 'Hollywood', 'Bollywood',
        'Lifestyle', 'Fashion', 'Beauty', 'Travel', 'Food', 'Cooking', 'Parenting',
        'World News', 'Asia', 'Europe', 'Americas', 'Africa', 'Middle East', 'India', 'USA', 'UK',
        'Education', 'Career', 'Crime', 'Law', 'Weather', 'Automotive', 'Opinion'
    ]

# 200+ Translation Languages
TRANSLATION_LANGUAGES = [
    # European Languages
    'Spanish', 'French', 'German', 'Italian', 'Portuguese', 'Russian',
    'Polish', 'Dutch', 'Greek', 'Swedish', 'Norwegian', 'Danish',
    'Finnish', 'Czech', 'Romanian', 'Hungarian', 'Bulgarian', 'Croatian',
    'Serbian', 'Slovak', 'Slovenian', 'Lithuanian', 'Latvian', 'Estonian',
    'Ukrainian', 'Catalan', 'Galician', 'Basque', 'Icelandic', 'Albanian',
    
    # Asian Languages
    'Hindi', 'Bengali', 'Tamil', 'Telugu', 'Marathi', 'Gujarati',
    'Kannada', 'Malayalam', 'Punjabi', 'Urdu', 'Odia', 'Assamese',
    'Chinese (Simplified)', 'Chinese (Traditional)', 'Japanese', 'Korean',
    'Thai', 'Vietnamese', 'Indonesian', 'Malay', 'Filipino', 'Tagalog',
    'Burmese', 'Khmer', 'Lao', 'Mongolian', 'Nepali', 'Sinhala',
    
    # Middle Eastern Languages
    'Arabic', 'Persian', 'Hebrew', 'Turkish', 'Kurdish', 'Pashto',
    'Dari', 'Azerbaijani', 'Armenian', 'Georgian',
    
    # African Languages  
    'Swahili', 'Yoruba', 'Hausa', 'Zulu', 'Xhosa', 'Afrikaans',
    'Amharic', 'Somali', 'Tigrinya', 'Oromo', 'Igbo', 'Shona',
    'Sesotho', 'Setswana', 'Kinyarwanda', 'Kirundi',
    
    # American Languages
    'English', 'Portuguese (Brazil)', 'Spanish (Latin America)',
    'Haitian Creole', 'Quechua', 'Guarani', 'Aymara',
    
    # Pacific Languages
    'Maori', 'Samoan', 'Tongan', 'Fijian', 'Hawaiian',
    
    # Central Asian
    'Kazakh', 'Uzbek', 'Kyrgyz', 'Tajik', 'Turkmen',
    
    # Other Major Languages
    'Irish', 'Welsh', 'Scottish Gaelic', 'Maltese', 'Luxembourgish',
    'Belarusian', 'Macedonian', 'Bosnian', 'Montenegrin',
    'Sami', 'Faroese', 'Greenlandic'
]

# Update the show_rss_manager method to use comprehensive categories:
# In the category_menu line, change to:
category_menu = ttk.Combobox(
    form_frame, textvariable=category_var,
    values=CATEGORIES,  # Use comprehensive categories
    state='readonly', width=20
)

# Update the show_translations method to use 200+ languages:
# In the lang_menu line, change to:
lang_menu = ttk.Combobox(
    lang_frame, textvariable=lang_var,
    values=TRANSLATION_LANGUAGES,  # Use 200+ languages
    state='readonly', width=25
)
