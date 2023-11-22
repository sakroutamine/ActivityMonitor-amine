from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import joblib

# Sample data: replace with your actual training data
data = {
    'domain_name': [
        # Productive sites (added 'arxiv.org')
        'canvas.tamu.edu', 'github.com', 'stackoverflow.com', 'leetcode.com',
        'coursera.org', 'udemy.com', 'pluralsight.com', 'kaggle.com', 'jira.com',
        'asana.com', 'trello.com', 'google.com', 'drive.google.com', 'scholar.google.com',
        'pubmed.ncbi.nlm.nih.gov', 'ieee.org', 'acm.org', 'jupyter.org', 'w3schools.com',
        'mdn.io', 'developer.mozilla.org', 'docs.python.org', 'medium.com', 'dev.to',
        'freecodecamp.org', 'hackerrank.com', 'codecademy.com', 'microsoft.com',
        'apple.com', 'oracle.com', 'www.linkedin.com', 'indeed.com', 'glassdoor.com', 'chat.openai.com',

        # Unproductive sites
        'espn.com', 'goal.com', 'bleacherreport.com', 'facebook.com', 'instagram.com',
        'twitter.com', 'tiktok.com', '9gag.com', 'reddit.com', '4chan.org',
        'buzzfeed.com', 'mashable.com', 'imgur.com', 'netflix.com', 'hulu.com',
        'disneyplus.com', 'youtube.com', 'vimeo.com', 'dailymotion.com', 'twitch.tv',
        'steam.com', 'epicgames.com', 'battle.net', 'pinterest.com', 'snapchat.com',
        'whatsapp.com', 'telegram.org', 'messenger.com', 'bing.com', 'yahoo.com',
        'craigslist.org', 'spotify.com', 'soundcloud.com', 'last.fm', 'pandora.com', 'hbomax.com'
    ],
    'is_productive': [
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  

        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ]
}

df = pd.DataFrame(data)

# Encoding the domain_name column
encoder = LabelEncoder()
df['domain_encoded'] = encoder.fit_transform(df['domain_name'])

# Separating features and labels
X = df[['domain_encoded']]
y = df['is_productive']

# Train the model
clf = DecisionTreeClassifier()
clf.fit(X, y)

# Save the model and encoder
joblib.dump(clf, 'trained_model.pkl')
joblib.dump(encoder, 'domain_encoder.pkl')

print("Model and encoder saved.")
