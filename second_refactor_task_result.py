import spotipy
from dataclasses import dataclass


# Выносим трэк в отдельный датакласс для удобства, так же определяем метод repr для него
@dataclass
class DetailedTrack:
	name: str
	authors: list[str]
	popularity: int
	album: str
	
	def __repr__(self):
		return f"{', '.join(self.authors)} - {self.name}, album {self.album}"


# Выносим всю работу с API спотифая в отдельный класс, чтобы в случае изменения API или
# добавления функционала избежать дублирования кода, а в случае изменения методов менять их атомарно.
# Намного проще изменить одну функцию, соблюдая контракты, чем разбираться в простыне кода и пытаться
# ничего не сломать. Так же, обозначаем все методы для работы с апи напрямую как приватные
class Spotify:
	def __init__(self, client_id: str, client_secret: str):
		self.spotify_client = spotipy.Spotify(auth_manager=spotipy.SpotifyClientCredentials(
			client_id=client_id,
			client_secret=client_secret
		))
	
	def _get_artist_uri(self, artist_name: str) -> str:
		response: dict = self.spotify_client.search(q=artist_name, limit=1)
		artist_uri: str = response['tracks']['items'][0]['artists'][0]['uri']
		return artist_uri
	
	def _get_artist_albums_uri(self, artist_uri: str) -> list[str]:
		albums: dict = self.spotify_client.artist_albums(artist_id=artist_uri)
		albums_uri: list[str] = []
		for album in albums['items']:
			albums_uri.append(album['uri'])
		return albums_uri
	
	def _get_tracks_uri_from_albums(self, albums_uri: list[str]) -> list[str]:
		albums_tracks: list[list[dict]] = []
		for album_uri in albums_uri:
			album_tracks = self.spotify_client.album_tracks(album_uri)
			albums_tracks.append(album_tracks['items'])
		
		tracks_uri: list[str] = []
		for album in albums_tracks:
			for track in album:
				tracks_uri.append(track['uri'])
		
		return tracks_uri
	
	def _get_detailed_tracks_info(self, tracks_uri: list[str]) -> list[DetailedTrack]:
		detailed_tracks: list[dict] = []
		for track_uri in tracks_uri:
			detailed_track = self.spotify_client.track(track_id=track_uri)
			detailed_tracks.append(detailed_track)
		
		tracks_with_full_information: list[DetailedTrack] = []
		for detailed_track in detailed_tracks:
			track_name = detailed_track['name']
			popularity = detailed_track['popularity']
			album_name = detailed_track['album']['name']
			artists = [artist['name'] for artist in detailed_track['artists']]
			track_with_popularity = DetailedTrack(
				name=track_name,
				album=album_name,
				popularity=popularity,
				authors=artists
			)
			tracks_with_full_information.append(track_with_popularity)
		
		return tracks_with_full_information
	
	def get_all_artist_tracks(self, artist_name: str) -> list[DetailedTrack]:
		artist_uri: str = self._get_artist_uri(artist_name=artist_name)
		artist_albums_uri: list[str] = self._get_artist_albums_uri(artist_uri=artist_uri)
		tracks_uri: list[str] = self._get_tracks_uri_from_albums(albums_uri=artist_albums_uri)
		detailed_tracks: list[DetailedTrack] = self._get_detailed_tracks_info(tracks_uri=tracks_uri)
		return detailed_tracks
		

# Выносим всю работу по анализу тржков в отдельный класс. Причины те же, что для
# выноса API спотифая в отдельный класс
class ArtistAnalyzer:
	def __init__(self, artist_tracks: list[DetailedTrack]):
		self.tracks = artist_tracks
	
	def get_most_popular_album(self) -> str:
		albums_with_popularity = {}
		
		for track in self.tracks:
			if track.name in albums_with_popularity:
				albums_with_popularity[track.name] += track.popularity
			else:
				albums_with_popularity[track.name] = track.popularity
		
		most_popular_album = max(albums_with_popularity, key=albums_with_popularity.get)
		return most_popular_album

	def get_average_popularity(self) -> float:
		popularity_sum = 0
		for track in self.tracks:
			popularity_sum += track.popularity
		average_popularity = popularity_sum/len(self.tracks)
		return average_popularity
	
	def get_top20_tracks_by_popularity(self) -> list[DetailedTrack]:
		self.tracks.sort(key=lambda track: track.popularity, reverse=True)
		return self.tracks[:20]
		

# По итогу, у нас есть функция, которая содержит только логику вывода полученной информации на
# экран, вся остальная логика инкапуслирована в отдельные классы.
def get_artist_info(client_id: str, client_secret: str, artist_name: str):
	spotify_client = Spotify(client_id=client_id, client_secret=client_secret)
	artist_tracks: list[DetailedTrack] = spotify_client.get_all_artist_tracks(artist_name=artist_name)
	
	artist_analyzer = ArtistAnalyzer(artist_tracks=artist_tracks)
	most_popular_album: str = artist_analyzer.get_most_popular_album()
	average_song_popularity: float = artist_analyzer.get_average_popularity()
	top20_tracks: list[DetailedTrack] = artist_analyzer.get_top20_tracks_by_popularity()
	
	top20_tracks_pretty_string = ''
	for track, track_num in zip(top20_tracks, range(len(top20_tracks))):
		top20_tracks_pretty_string += f'{track_num+1}. {track} \n'
	print(f'Most popular album is {most_popular_album}')
	print(f'Average song popularity {average_song_popularity}')
	print(f'Top20 song by popularity: \n{top20_tracks_pretty_string}')


def main():
	client_secret = 'CLIENT_SECRET'
	client_id = 'CLIENT_ID'
	name = input('Enter artist name: ')
	get_artist_info(artist_name=name, client_secret=client_secret, client_id=client_id)


if __name__ == '__main__':
	main()
