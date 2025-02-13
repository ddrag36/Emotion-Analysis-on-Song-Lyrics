

# Emotion Analysis on Song Lyrics Dataset

## Import Necessary Packages
"""

from google.colab import output
output.enable_custom_widget_manager()

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
from nltk.tokenize import word_tokenize
import string
from transformers import pipeline
import nltk
import plotly.express as px
from tqdm.notebook import tqdm

# Download NLTK resources
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

"""## Load Dataset"""

from google.colab import drive
drive.mount('/content/drive')

df = pd.read_csv('/content/drive/MyDrive/TMA-Assignment-2/Song_Lyrics.csv', delimiter=";")

df

"""## Dataset Overview"""

df.info()

"""## Summary Statistics"""

df.describe(include='all')

"""## Missing Values"""

df.isnull().sum()

"""## Clean Dataset"""

## Drop column unnamed: 0
df = df.drop(columns=['Unnamed: 0'], errors='ignore')

"""## Analyses of Genre Column"""

df["genre"].value_counts()

df["genre"].nunique()

df["genre"].unique()

"""## Visualizations

### Year Distribution
"""

pip install -U kaleido

fig = px.histogram(
    data_frame=df,
    x='year',
    nbins=len(df['year'].unique()),  # Ensure each year gets its own bin
    title="Year Distribution",
    labels={'year': 'Year', 'count': 'Count'}
)
fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Count",
    xaxis=dict(tickmode='linear'),  # Show all years on x-axis
    bargap=0.1  # Add spacing between bars
)
fig.update_traces(
    marker_line_color='black',  # Add borders to bars
    marker_line_width=1.5,  # Make borders more visible
    texttemplate='%{y}',  # Show count on top of each bar
    textposition='outside'  # Position text above bars
)
fig.write_image("year_distribution.png", width=1200, height=800, scale=2)
fig.show()

"""### Genre Distributions"""

genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['Genre', 'Count']
genre_counts = genre_counts.sort_values(by='Count', ascending=True)
fig = px.bar(
    genre_counts,
    x='Count',
    y='Genre',
    orientation='h',
    title="Genre Distribution",
    labels={'Count': 'Count', 'Genre': 'Genre'}
)
fig.update_traces(
    marker_line_color='black',  # Add borders to bars
    marker_line_width=1.5,  # Make borders more visible
    texttemplate='%{x}',  # Show count on the bars
    textposition='outside'  # Position text beside bars
)
fig.write_image("genre_distribution.png", width=1200, height=800, scale=2)
fig.show()

"""### Most Frequent Artists"""

top_artists = df['artist'].value_counts().head(10)
top_artists_reset = top_artists.reset_index()
top_artists_reset.columns = ['Artist', 'Number of Songs']
top_artists_reset = top_artists_reset.sort_values(by='Number of Songs', ascending=True)
fig = px.bar(
    top_artists_reset,
    x='Number of Songs',
    y='Artist',
    orientation='h',
    title='Top 10 Artists by Number of Songs',
    labels={'Number of Songs': 'Number of Songs', 'Artist': 'Artist'}
)
fig.update_traces(
    marker_line_color='black',  # Add borders to bars
    marker_line_width=1.5,  # Make borders more visible
    texttemplate='%{x}',  # Show count on the bars
    textposition='outside'  # Position text beside bars
)
fig.write_image("most_frequent_artists.png", width=1200, height=800, scale=2)
fig.show()

"""### Artist's Number of Songs Per Genre"""

# 1. Identify the top 10 artists (by number of songs)
top_artists = df['artist'].value_counts().head(20).index

# 2. Filter the dataframe to only these top 10 artists
df_top_artists = df[df['artist'].isin(top_artists)]

# 3. Group by artist and genre, and count the number of songs
artist_genre_counts = (
    df_top_artists
    .groupby(['artist', 'genre'])
    .size()
    .reset_index(name='Number of Songs')
    .sort_values(by='Number of Songs', ascending=True)
)

# 4. Create a horizontal stacked bar chart
fig = px.bar(
    artist_genre_counts,
    x='Number of Songs',
    y='artist',
    color='genre',
    orientation='h',               # Horizontal bars
    title="Top 20 Artists' Number of Songs Per Genre",
    labels={
        'Number of Songs': 'Number of Songs',
        'artist': 'Artist',
        'genre': 'Genre'
    },
)

# 5. (Optional) Add styling to match your original figure
fig.update_traces(
    marker_line_color='black',
    marker_line_width=1.5,
    texttemplate='%{x}',  # Show count on the bars
    textposition='outside'  # Position text beside bars
)
fig.write_image("artist_songs_per_genre.png", width=1200, height=800, scale=2)
fig.show()

"""### Average Lyrics Length Per Genre"""

df['lyrics_length'] = df['lyrics'].apply(lambda x: len(str(x).split()))
avg_length_per_genre = df.groupby('genre')['lyrics_length'].mean()
avg_length_per_genre_reset = avg_length_per_genre.reset_index().sort_values(by='lyrics_length', ascending=True)
fig = px.bar(
    avg_length_per_genre_reset,
    x='lyrics_length',
    y='genre',
    orientation='h',
    title='Average Lyrics Length per Genre',
    labels={'lyrics_length': 'Average Length', 'genre': 'Genre'}
)
fig.update_traces(
    marker_line_color='black',  # Add borders to bars
    marker_line_width=1.5,  # Make borders more visible
    texttemplate='%{x}',  # Show count on the bars
    textposition='outside'  # Position text beside bars
)
fig.write_image("average_lyrics_length_per_genre.png", width=1200, height=800, scale=2)
fig.show()

"""### Word Cloud for Lyrics"""

lyrics_text = " ".join(str(lyric) for lyric in df['lyrics'])
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(lyrics_text)
plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title("Word Cloud of Lyrics")
plt.savefig("wordcloud_lyrics.png", dpi=300, bbox_inches='tight')
plt.show()

"""## Emotion Analyses Model on Song Lyrics Per Genre

### Preprocessing Song Lyrics
"""

# Preprocessing Lyrics using NLTK
def preprocess_lyrics_nltk(lyrics):
    words = word_tokenize(str(lyrics).lower())
    filtered_words = [word for word in words if word.isalpha()]
    return " ".join(filtered_words)

df['cleaned_lyrics'] = df['lyrics'].apply(preprocess_lyrics_nltk)

df["cleaned_lyrics"]

"""## Model Training and Analysis

### Model Training
"""

# Load the emotion model
emotion_analyzer = pipeline("text-classification", model="j-hartmann/emotion-english-roberta-large")

def analyze_emotions(lyrics):
    try:
        emotions = emotion_analyzer(lyrics, truncation=True)
        return emotions[0]['label']
    except:
        return None

# Use tqdm with Jupyter Notebook
tqdm.pandas(desc="Analyzing Emotions in Notebook")
df['dominant_emotion'] = df['cleaned_lyrics'].progress_apply(analyze_emotions)

"""### Training Result Analysis"""

# Find the highest proportion of emotions for each genre
emotion_counts = df.groupby('genre')['dominant_emotion'].value_counts(normalize=True).unstack()
highest_emotion_per_genre = emotion_counts.idxmax(axis=1)
highest_proportion_per_genre = emotion_counts.max(axis=1)
print("\nHighest Emotion Proportion per Genre:")
print(pd.DataFrame({"Dominant Emotion": highest_emotion_per_genre, "Proportion": highest_proportion_per_genre}))

emotion_counts

"""### Training Results Visualisation"""

# Plotly visualization for Emotion Distribution by Genre
emotion_counts_reset = emotion_counts.reset_index()
emotion_counts_melted = emotion_counts_reset.melt(id_vars='genre', var_name='Emotion', value_name='Proportion')
fig = px.bar(
    emotion_counts_melted,
    x='genre',
    y='Proportion',
    color='Emotion',
    title='Emotion Distribution by Genre',
    barmode='stack',
    labels={'genre': 'Genre', 'Proportion': 'Emotion Proportion'}
)
fig.write_image("Emotion_Distribution_by_Genre.png", width=1200, height=800, scale=2)
fig.show()

# 1. Group by year and emotion, and count occurrences
emotion_year_counts = df.groupby(['year', 'dominant_emotion']).size().reset_index(name='count')

# 2. Calculate the total songs per year to get proportion
year_totals = emotion_year_counts.groupby('year')['count'].sum().reset_index(name='year_total')
emotion_year_counts = emotion_year_counts.merge(year_totals, on='year', how='left')
emotion_year_counts['proportion'] = emotion_year_counts['count'] / emotion_year_counts['year_total']

# 3. Create a line chart showing emotion trends over time
fig_line = px.line(
    emotion_year_counts,
    x='year',
    y='proportion',
    color='dominant_emotion',
    title='Emotion Change in Song Lyrics Over the Years'
)
fig.write_image("Emotion_Change_per_year.png", width=1200, height=800, scale=2)
fig_line.show()
