"""
Music Search Module — поиск музыки через YouTube Music
Бесплатно, без API-ключа
"""

from ytmusicapi import YTMusic
import re

def search_music(query: str, limit: int = 5) -> list:
    """
    Ищет музыку на YouTube Music
    
    Args:
        query: поисковый запрос (например, "Imagine Dragons Believer")
        limit: количество результатов (по умолчанию 5)
    
    Returns:
        list: список найденных песен с названием, артистом и ссылкой
    """
    try:
        # Инициализация клиента (без авторизации — достаточно для поиска)
        ytmusic = YTMusic()
        
        # Поиск песен
        results = ytmusic.search(query, filter="songs", limit=limit)
        
        songs = []
        for item in results:
            # Извлекаем название и артиста
            title = item.get('title', 'Без названия')
            
            # Получаем имя артиста
            artist = 'Неизвестен'
            if item.get('artists') and len(item['artists']) > 0:
                artist = item['artists'][0].get('name', 'Неизвестен')
            
            # Получаем длительность
            duration = item.get('duration', '')
            if duration:
                # Преобразуем секунды в мм:сс если нужно
                if isinstance(duration, int) and duration > 0:
                    minutes = duration // 60
                    seconds = duration % 60
                    duration = f"{minutes}:{seconds:02d}"
            
            songs.append({
                'title': title,
                'artist': artist,
                'video_id': item.get('videoId', ''),
                'url': f"https://music.youtube.com/watch?v={item.get('videoId', '')}" if item.get('videoId') else '',
                'duration': duration,
                'year': item.get('year', ''),
                'thumbnails': item.get('thumbnails', [])
            })
        
        return songs
    except Exception as e:
        return [{'error': f'Ошибка поиска: {str(e)}'}]


def format_search_results(songs: list, query: str) -> str:
    """Форматирует результаты поиска для ответа Анны"""
    if not songs:
        return f"😔 Не удалось найти музыку по запросу '{query}'. Попробуйте другие слова."
    
    if songs[0].get('error'):
        return songs[0]['error']
    
    # Фильтруем только успешные результаты
    valid_songs = [s for s in songs if not s.get('error') and s.get('url')]
    
    if not valid_songs:
        return f"😔 Не удалось найти музыку по запросу '{query}'. Попробуйте другие слова."
    
    result_text = f"🎵 **Вот что я нашла по запросу '{query}':**\n\n"
    for i, song in enumerate(valid_songs, 1):
        result_text += f"{i}. **{song['title']}** — {song['artist']}\n"
        if song.get('duration'):
            result_text += f"   ⏱️ Длительность: {song['duration']}\n"
        if song.get('year'):
            result_text += f"   📅 Год: {song['year']}\n"
        result_text += f"   🔗 [Слушать на YouTube Music]({song['url']})\n\n"
    
    result_text += "💡 *Нажмите на ссылку, чтобы открыть в браузере*"
    
    return result_text


def get_song_info(song_id: str) -> dict:
    """Получает детальную информацию о песне по ID"""
    try:
        ytmusic = YTMusic()
        watch_playlist = ytmusic.get_watch_playlist(song_id, limit=1)
        if watch_playlist and watch_playlist.get('tracks'):
            track = watch_playlist['tracks'][0]
            return {
                'title': track.get('title', ''),
                'artist': track.get('artists', [{}])[0].get('name', ''),
                'album': track.get('album', {}).get('name', ''),
                'duration': track.get('duration', ''),
                'url': f"https://music.youtube.com/watch?v={song_id}"
            }
        return {'error': 'Не удалось получить информацию'}
    except Exception as e:
        return {'error': f'Ошибка: {str(e)}'}


def search_artist(artist_name: str, limit: int = 5) -> list:
    """Ищет популярные песни артиста"""
    try:
        ytmusic = YTMusic()
        results = ytmusic.search(artist_name, filter="artists", limit=1)
        
        if results and results[0].get('browseId'):
            # Получаем песни артиста
            artist_id = results[0]['browseId']
            songs_data = ytmusic.get_artist(artist_id)
            
            songs = []
            # Берём популярные песни
            top_songs = songs_data.get('songs', [])[:limit]
            for song in top_songs:
                songs.append({
                    'title': song.get('title', ''),
                    'artist': artist_name,
                    'video_id': song.get('videoId', ''),
                    'url': f"https://music.youtube.com/watch?v={song.get('videoId', '')}",
                    'duration': song.get('duration', '')
                })
            return songs
        return []
    except Exception as e:
        return [{'error': f'Ошибка: {str(e)}'}]


def search_mood(mood: str, limit: int = 5) -> list:
    """
    Ищет музыку по настроению
    Примеры: 'happy', 'sad', 'relax', 'workout', 'party'
    """
    try:
        ytmusic = YTMusic()
        # Используем поиск по плейлистам настроения
        results = ytmusic.search(f"{mood} music", filter="playlists", limit=limit)
        
        songs = []
        for playlist in results:
            playlist_id = playlist.get('browseId')
            if playlist_id:
                playlist_info = ytmusic.get_playlist(playlist_id, limit=5)
                for track in playlist_info.get('tracks', []):
                    songs.append({
                        'title': track.get('title', ''),
                        'artist': track.get('artists', [{}])[0].get('name', ''),
                        'video_id': track.get('videoId', ''),
                        'url': f"https://music.youtube.com/watch?v={track.get('videoId', '')}",
                        'duration': track.get('duration', '')
                    })
                    if len(songs) >= limit:
                        break
                if len(songs) >= limit:
                    break
        return songs
    except Exception as e:
        return [{'error': f'Ошибка: {str(e)}'}]


# Простой тест
if __name__ == "__main__":
    print("Тест поиска музыки...")
    results = search_music("Imagine Dragons Believer", limit=3)
    for r in results:
        print(f"- {r.get('title')} by {r.get('artist')}: {r.get('url')}")