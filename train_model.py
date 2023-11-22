# Import Libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib

# Prepare Dataset with provided data
data = {
    "domain_name": [
        # Productive sites
        "canvas.tamu.edu", "github.com", "stackoverflow.com", "leetcode.com",
        "coursera.org", "udemy.com", "pluralsight.com", "kaggle.com", "jira.com",
        "asana.com", "trello.com", "google.com", "drive.google.com", "scholar.google.com",
        "pubmed.ncbi.nlm.nih.gov", "ieee.org", "acm.org", "jupyter.org", "w3schools.com",
        "mdn.io", "developer.mozilla.org", "docs.python.org", "medium.com", "dev.to",
        "freecodecamp.org", "hackerrank.com", "codecademy.com", "microsoft.com",
        "apple.com", "oracle.com", "www.linkedin.com", "indeed.com", "glassdoor.com",
        "chat.openai.com",
        
        # Unproductive sites
        "espn.com", "goal.com", "bleacherreport.com", "facebook.com",
        "instagram.com", "twitter.com", "tiktok.com", "9gag.com", "reddit.com", "4chan.org",
        "buzzfeed.com", "mashable.com", "imgur.com", "netflix.com", "hulu.com", "disneyplus.com",
        "youtube.com", "vimeo.com", "dailymotion.com", "twitch.tv", "steam.com", "epicgames.com",
        "battle.net", "pinterest.com", "snapchat.com", "whatsapp.com", "telegram.org", "messenger.com",
        "bing.com", "yahoo.com", "craigslist.org", "spotify.com", "soundcloud.com", "last.fm",
        "pandora.com", "hbomax.com"
    ],
    "is_productive": [
        # Labels for productive (1) and unproductive (0) sites
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ],
}

# Create DataFrame
df = pd.DataFrame(data)

# Encode the domain_name column
encoder = LabelEncoder()
df['domain_encoded'] = encoder.fit_transform(df['domain_name'])

# Separate features and labels
X = df[['domain_encoded']]
y = df['is_productive']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Logistic Regression model
clf = LogisticRegression(verbose=1)
clf.fit(X_train, y_train)

# Predict on the test set
y_pred = clf.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)

# Save the model and encoder
joblib.dump(clf, 'trained_logistic_model.pkl')
joblib.dump(encoder, 'domain_encoder.pkl')

print("Logistic Regression model and encoder saved.")
