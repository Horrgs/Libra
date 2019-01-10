from photos.photos import PhotoConnect, Album

photos = PhotoConnect()

session = photos.get_authorized_session()
album_id = Album(session, "Libra")
cache_photos = photos.cache_photos(session, album_id, None)