# Import Libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

# Read dataset from CSV file
file_path = 'productivity_data.csv'
df = pd.read_csv(file_path)

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

# Calculate evaluation metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

# Print metrics
print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)
print("Confusion Matrix:\n", conf_matrix)

# Save the model and encoder
joblib.dump(clf, 'trained_logistic_model.pkl')
joblib.dump(encoder, 'domain_encoder.pkl')

print("Logistic Regression model and encoder saved.")
