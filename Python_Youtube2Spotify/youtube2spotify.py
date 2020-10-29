''' 
Youtube to spotify importer

script that converts your youtube playlist into a spotify playlist
at the time of writing this worked awesomely!

the tedious functionality here is that plenty of the songs i had on youtube
had incredibly obnoxious titles, and so that large bulk of this script
is me just cleaning those titles so that they can be passed to spotify

this was just for practive interacting with APIs and such

Requires a bit of setup, such as having an api key for both youtube and 
spotify

youtube-dl has been taken down for violating copyright codes and 
so for now this does not work

for this script to work:
    youtube playlist and spotify playlist must both be public

TODO
implement a way to briefly make a playlist public then back to private for 
both spotify and youtube

TODO
implement a way to check if the secret keys are working before beginning the import

TODO
Implement a UI that takes in the users values so that nothing is stored permanenly, instead of 
reading from a .env file

'''
# imports 
import os
from dotenv import load_dotenv

# imports for youtube handling
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl

# spotify handling
import spotipy
import spotipy.util as util


######################################################################################################
## Core functions
## these should be in a class, which ill do in the future
######################################################################################################
# input: youtube api key
# output: youtube client object
def get_youtube_client(youtube_api_key):
    # Disable OAuthlib's HTTPS verification when running locally
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    
    # request youtube client
    youtube_client = googleapiclient.discovery.build(
        api_service_name,
        api_version,
        developerKey = youtube_api_key
        )
    
    return youtube_client

# input: youtube client and the youtube playist id to be scraped. Note must be public
# output: list of youtube video urls for all the items in the playlist
def get_youtube_playlist(client, playlist_id):
    q_property = "contentDetails"
    q_fields = "nextPageToken,items.contentDetails.videoId"
    youtube_song_urls  = []
    max_results = 50
    next_page = True
    
    request = client.playlistItems().list(
        part = q_property,
        maxResults = max_results,
        playlistId = playlist_id,
        fields = q_fields,
        )
        
    # query response in json format
    response = request.execute()
    youtube_song_urls.extend(youtube_url_list_creator(response))
    
    # check if the response returned a token for the next page
    try:
        next_page_token = response['nextPageToken']
    except KeyError:
        next_page=False
    
    # if there is a next page, loop through and check
    while (next_page):
        
        response = client.playlistItems().list(
            part = q_property,
            maxResults = max_results,
            pageToken = next_page_token,
            playlistId = playlist_id,
            fields = q_fields,
            )
        youtube_song_urls.extend(youtube_url_list_creator(response))
        
        # attempt to retrieve a nextpage token
        try:
            next_page_token = response['nextPageToken']
        except KeyError:
            break
    
    return youtube_song_urls

# input: list of urls for videos on youtube
# output: two lists:
#       list of tracks and artists names for videos that have song information via youtube-dl
#       list of video titles that didn't have song information via youtube-dl

def grab_track_info(youtube_song_urls):
    matched, not_matched = [], []
    youtubedl_options = {'ignoreerrors': True}
    
    # using the list of urls, we want to grab the track info
    # iterate through the urls and grab the track info one at at time
    for url in youtube_song_urls:
        try:
            track = youtube_dl.YoutubeDL(youtubedl_options).extract_info(url, download=False)
        except youtube_dl.utils.ExtractorError:
            print("Extractor Error")
            continue
        # attempt to extract information from the video
        try:
            track_name, artist, video_title = track['track'], track['artist'],track['title']
        except TypeError:
            continue
        except KeyError:
            continue
        # if there is a match
        if track_name != None and artist !=None:
            matched.append([track_name,artist])
        else:
            not_matched.append(video_title)
    
    return (matched, not_matched)

# input: spotify username
# output: spotify client
def get_spotify_client(spotify_username):
    token = util.prompt_for_user_token(spotify_username)
    return spotipy.Spotify(auth=token)

# input: spotify client and a trackitem which is a tuple of track,artist
# output:
#       uri if there is a match
#       None if there is no match 
def get_single_spotify_uri(client,trackitem):
    track,artist = trackitem
    spot_query = f'track:{track} artist:{artist}'
    spot_response = client.search(
        spot_query,
        limit=5,
        offset=0,
        type='track',
        market=None
        )
    # extract the songs list from the response
    songs = spot_response["tracks"]["items"]
    try:
        uri = songs[0]["uri"]      # further extract the uri from the first element of the reponse
    except IndexError:
        return None                 # if we cannot get a URI, return None, so we know that we were not able to
    return uri



# input: list of tuples containing the (track,artist)
# output:2 lists:
#               list of uris
#               list of tuples containing the (track,artist)
def get_spotify_uri(username,tracks):
    uri_list,uri_fail = [],[]
    client = get_spotify_client(username)
    for track in tracks:
        current_track = get_single_spotify_uri(client,track)
        if current_track != None:
            uri_list.append(current_track)
        else:
            uri_fail.append(track)
    
    return (uri_list,uri_fail)

def get_spotify_uri_dirty(username,tracks):
    uri_list,uri_fail = [],[]
    spotify_client = get_spotify_client(username)
    for track in tracks:
        query = f'{track}'
        spot_response = spotify_client.search(
            query,
            limit=5,
            offset=0,
            type='track',
            market=None
            )
        
        # extract the songs list from the response
        songs = spot_response["tracks"]["items"]
        try:
            # further extract the uri from the first element of the reponse
            uri = songs[0]["uri"]
        except IndexError:
            # if we cannot get a URI, return None, so we know that we were not able to
            uri_fail.append(track)
            continue
        uri_list.append(uri)
    
    return (uri_list,uri_fail)


def add_tracks_to_spotify(playlist_id,username,tracks):
    spotify_client = get_spotify_client(username)
    spotify_client.trace = False
    block_size = 99
    uri_blocks = [tracks[x:x+block_size] for x in range(0,len(tracks), block_size)]
    for uri_list in uri_blocks:
        print(uri_list)
        spotify_client.user_playlist_add_tracks(
            username,
            playlist_id,
            uri_list
            )
    return print("Tracks Added")




######################################################################################################
## Helper functions
######################################################################################################
# Function that returns the youtube videos URL id which is easier for 
# youtubedl to parse
#   input: json data from a youtube query for playlist items
#   output: list of urls for the videos in the given playlist
def youtube_url_list_creator(response):
    yt_video_ids = [item['contentDetails']['videoId'] for item in response['items']]
    return [f"https://www.youtube.com/watch?v={_}" for _ in yt_video_ids]


# input: track name, first brack, second bracket
# output: list of urls for the videos in the given playlist
def bracket_remover(track):
    open_pairs, close_pairs = ['(', '[', '{'], [')', ']', '}']
    
    for first,second in zip(open_pairs,close_pairs):
        # use a try except to find the bracket pairs
        try:
            first_pos, second_pos = track.find(first), track.find(second)
        except ValueError:
            continue
        
        substring = track[first_pos:second_pos+1].lower()
        # if the substring within the brackets has remix, we skip this
        if substring.find('remix') == -1:
            # retrn the track without the bracketed elements
            track = track[0:first_pos]+track[second_pos+1:]
            track.strip()
        else:
            continue
    print(f'[bracket_remover] {track}')
    return track.strip()

# remove weird symbole form the artist name, and strip leading whitespace ,
# which seemed like  a problem 
def artist_cleaner(artist):
    garbage, artist = ['"', "(", ")", ",", "&", "|", "/"], list(artist)
    clean_artist = "".join([_ for _ in artist if _ not in garbage])
    return clean_artist.lstrip().lower()


# remove features, as features can clutter up a spotify search
def feature_remover(track):
    garbage = ['ft.','feat.','feat','featuring']
    # iterate through the garbage and check if any of those are 
    # in the track name
    for feature in garbage:
        try:
            # find returns -1 if the value we are looking for does not exist 
            openbracket = track.index(feature)
        except ValueError:
            continue
        
        track = track[0:openbracket]
        
        return track
    return track

# to be used on youtube video titles to clean them up
def track_cleaner(track):
    replacements = [' - ', ' & ', '-', '&']
    garbage = ['Official Music Video','LYRICS','Original Motion Picture Soundtrack',
                  'Official Music Video HD','Official Lyrics','Full Version','Official Video',
                  'Lyric Video','full track','Short Version',]
    
    for _ in replacements:
        track = track.replace(_, " ")
        
    for _ in garbage:
        try:
            check = track.index(_)
        except ValueError:
            continue
        
        track = track.replace(_,"")
    
    return track

# Splits a track title into the artist and the track name
# this is generic splitter and assumes the artist precedes
# the track name in the given string
def track_splitter(title):
    if len(title.split('-'))==2:
        artist,track = title.split('-')
        return (artist.strip(),track.strip())
    else:
        return (None,None)

######################################################################################################
## main 
######################################################################################################
def main():
    # load the environment file
    load_dotenv()
    # load required user info
    youtube_playlist_id = os.getenv("YOUTUBE_PLAYLIST_ID")
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    spotify_username = os.getenv("SPOTIFY_USERNAME")
    spotify_playlist_id = os.getenv("SPOTIFY_PLAYLIST_ID")
    
    # get youtube client
    youtube_client = get_youtube_client(youtube_api_key)
    
    # pull urls for each video on youtube
    youtube_song_urls = get_youtube_playlist(youtube_client,youtube_playlist_id)
    
    # use youtube-dl to extract song info
        # if match: create list of matches                      youtubedl_passed = (track,artist)
        # no match: keep video title, for retrucutring          youtubedl_failed = (videotitle)
    youtubedl_passed, youtubedl_failed = grab_track_info(youtube_song_urls)
    
    # structure song info into spotipy query
    # despite returning the track and artist, the return values are cluterred and dirty , with weird brackets 
    # that make it hard for the spotipy api to parse
    first_clean = [(bracket_remover(track),bracket_remover(artist)) for track,artist in youtubedl_passed]
    track_list = [(track,artist_cleaner(artist)) for track,artist in first_clean]
    
    # search spotipy for song matches
        # if match: grab uri (uri)
        # no match: add to secondPass list (track,artist)
    spotify_uri_pass, spotify_uri_fail = get_spotify_uri(spotify_username,track_list)
    
    # add matched songs to spotify playlist
    add_tracks_to_spotify(spotify_playlist_id,spotify_username, spotify_uri_pass)
    
    # take youtube-dl fails and spotipy fails and restructure them
    # clean them up 
    # for spotify_uri_fail: remove features, remove track junk, join together
    # for youtubedl_failed: remove bracketed stuff, attempt to split, remove title junk, remove features
    # search spotipy again
        # if match: extract uri, add to list
        # if no match: add to fail list
    third_clean = [bracket_remover(item) for item in youtubedl_failed]
    fourth_clean = []
    
    # if we can split the tracks and clean them separately then better
    for trackitem in third_clean:
        first, second = track_splitter(trackitem)
        if first != None and second != None:
            first_x = track_cleaner(first)
            second_x = track_cleaner(second)
            fourth_clean.append("{} {}".format(feature_remover(first_x),feature_remover(second_x)))
        else:
            fourth_clean.append("{}".format(track_cleaner(trackitem)))
    
    
    for track,artist in spotify_uri_fail:
        track_x, artist_x  = feature_remover(track), feature_remover(artist)
        fourth_clean.append("{} {}".format(track_cleaner(track_x), track_cleaner(artist_x)))
    
    spotify_uri_pass, spotify_uri_fail = get_spotify_uri_dirty(spotify_username,fourth_clean)
    
    add_tracks_to_spotify(spotify_playlist_id,spotify_username, spotify_uri_pass)
    print(spotify_uri_fail)
    print("Done!")

if __name__ == "__main__":
    main()