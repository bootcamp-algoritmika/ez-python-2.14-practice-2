# Для этого задания необходимо установить внешнюю зависимость
# pip install spotipy
# Так же необходимо зайти на https://developer.spotify.com/dashboard/applications
# создать свое приложение и получить client_id и client_secret
import spotipy


"""
Изучать API Spotify не нужно, ровно как и переделывать способ получения данных оттуда
"""


class Spotify:
	def __init__(self):
		self.spotify = spotipy.Spotify(auth_manager=spotipy.SpotifyClientCredentials(
			client_id='CLIENT_ID',
			client_secret='CLIENT_SECRET'
		))
	
	def get_artist_info(self, name: str):
		tracks_by_popularity = self.get_song_by_popularity(name)
		average_song_popularity = self.get_average_popularity(tracks_by_popularity)
		most_popular_album = self.get_most_popular_album(tracks_by_popularity)
		top20_tracks = tracks_by_popularity[:20]
		print(f'Most popular album is {most_popular_album}')
		print(f'Average song popularity {average_song_popularity}')
		top20_tracks_pretty_string = ''
		for track, track_num in zip(top20_tracks, range(len(top20_tracks))):
			track_pretty_string = f"{track_num+1}. {', '.join(track[0])} - {track[1]}, album {track[2]} \n"
			top20_tracks_pretty_string += track_pretty_string
		print(f'Top20 track by popularity: \n{top20_tracks_pretty_string}')
		
	def get_song_by_popularity(self, name: str):
		response: dict = self.spotify.search(q=name, limit=1)
		artist_uri: str = response['tracks']['items'][0]['artists'][0]['uri']
		
		albums = self.spotify.artist_albums(artist_id=artist_uri)
		albums_uri = []
		for album in albums['items']:
			albums_uri.append(album['uri'])
			
		albums_tracks = []
		for album_uri in albums_uri:
			album_tracks = self.spotify.album_tracks(album_uri)
			albums_tracks.append(album_tracks['items'])
		
		tracks_uri = []
		for album in albums_tracks:
			for track in album:
				tracks_uri.append(track['uri'])
			
		detailed_tracks = []
		for track_uri in tracks_uri:
			detailed_track = self.spotify.track(track_id=track_uri)
			detailed_tracks.append(detailed_track)
		
		tracks_with_full_information = []
		for detailed_track in detailed_tracks:
			track_name = detailed_track['name']
			popularity = detailed_track['popularity']
			album_name = detailed_track['album']['name']
			artists = [artist['name'] for artist in detailed_track['artists']]
			track_with_popularity = (artists, track_name, album_name, popularity)
			tracks_with_full_information.append(track_with_popularity)
		
		tracks_with_full_information.sort(key=lambda track_info: track_info[3], reverse=True)
		
		return tracks_with_full_information
	
	def get_average_popularity(self, tracks_by_popularity) -> float:
		popularity_sum = 0
		for track in tracks_by_popularity:
			popularity_sum += track[3]
		average_popularity = popularity_sum/len(tracks_by_popularity)
		return average_popularity
	
	def get_most_popular_album(self, tracks_by_popularity) -> str:
		albums_with_popularity = {}
		
		for track in tracks_by_popularity:
			if track[1] in albums_with_popularity:
				albums_with_popularity[track[1]] += track[3]
			else:
				albums_with_popularity[track[1]] = track[3]
		
		most_popular_album = max(albums_with_popularity, key=albums_with_popularity.get)
		return most_popular_album
		

def main():
	s = Spotify()
	name = input('Enter artist name: ')
	s.get_artist_info(name=name)
	

if __name__ == '__main__':
	main()
