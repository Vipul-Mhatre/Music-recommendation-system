from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
import numpy as np

app = Flask(__name__)

music_info_path = 'Music Info.csv'
history_path = 'User Listening History.csv'

music_df = pd.read_csv(music_info_path)
history_df = pd.read_csv(history_path)

history_df_cleaned = history_df.drop_duplicates(subset=["track_id", "user_id"]).dropna(subset=["track_id", "user_id"])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/statistics', methods=['GET'])
def get_user_statistics():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user_history = history_df_cleaned[history_df_cleaned['user_id'] == user_id]

    if user_history.empty:
        return jsonify({"error": f"No listening history found for User ID {user_id}"}), 404

    total_tracks_listened = user_history['track_id'].nunique()
    total_playcount = user_history['playcount'].sum()
    average_playcount = user_history['playcount'].mean()
    unique_tracks = total_tracks_listened

    return jsonify({
        "total_tracks_listened": int(total_tracks_listened),  
        "total_playcount": int(total_playcount), 
        "average_playcount": float(average_playcount), 
        "unique_tracks": int(unique_tracks)  
    })

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user_history = history_df_cleaned[history_df_cleaned['user_id'] == user_id]

    if user_history.empty:
        return jsonify({"error": f"No listening history found for User ID {user_id}"}), 404

    user_data = pd.merge(user_history, music_df, on='track_id', how='inner')

    feature_columns = ['danceability', 'energy', 'loudness', 'tempo']
    X = user_data[feature_columns].values
    y = user_data['playcount'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    knn_model = NearestNeighbors(n_neighbors=10, metric='euclidean')
    knn_model.fit(X_train)

    distances, indices = knn_model.kneighbors(X_test)

    recommendations_list = []

    for i, idx in enumerate(indices):
        recommended_track = music_df.iloc[idx[0]]  
        recommendations_list.append({
            "track_id": recommended_track['track_id'],
            "name": recommended_track['name'],
            "artist": recommended_track['artist']
        })

    return jsonify(recommendations_list)

if __name__ == '__main__':
    app.run(debug=True)