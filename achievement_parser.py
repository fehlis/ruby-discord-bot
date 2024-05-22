import datetime
import json, requests

def preprocess_json(json_string):
    # Replace invalid escape sequences with valid ones
    json_string = json_string.replace('\\\\', '\\')
    json_string = json_string.replace('\\', '')

    return json_string[:-2]

def get_exophase_html() -> str:
    # Step 1: Fetch the webpage content
    url = 'https://www.exophase.com/user/PureRuby87/'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to load page: {response.status_code}")
    return response.text

def parse_exophase() -> list:
    ret = []
    
    # TODO: get exophase html
    html = get_exophase_html()
    # TODO: parse playerGames text from htmk
    for line in html.split("\n"):
        if "window.playerGames = " in line:
            escaped_string = line
            break
        
    # Remove the leading part
    escaped_string = escaped_string.replace("window.playerGames = '", "").rstrip(",'")

    # Decode the escaped sequences
    decoded_string = bytes(escaped_string, "utf-8").decode("unicode_escape")

    decoded_string = preprocess_json(decoded_string)

    with open('decoded.json', 'w') as f:
        f.write(decoded_string)

    # Parse the JSON content
    try:
        data = json.loads(decoded_string)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        data = None

    # Print the parsed data (for demonstration purposes)
    #if data is not None:
    #    print(json.dumps(data, indent=2))

    # Step 5: Process and print details of the games
    for game in data.get('games', []):
        entry = { 'title': None, 'link': None, 'last_played': None }
        meta = game['meta']
        #title = meta.get('title_original', 'Unknown title')
        #last_played = meta.get('lastupdated', 'Unknown date')
        entry['title'] = meta['title_original']
        entry['link'] = meta['links'][0]['endpoint'] 
        entry['last_played'] = game['lastplayed']
        entry['completion_date'] = datetime.datetime.fromtimestamp(game['completion_date'], datetime.UTC)
        entry['earned_awards'] = game['earned_awards']
        entry['total_awards'] = game['total_awards']
        entry['percent'] = game['percent']
        #print(f"Game: {title}, Last Played: {last_played}")
        
        ret.append(entry)

        # Sort the dictionary by the 'timestamp' field
        #sorted_data = sorted(ret, key=lambda x: x['last_played'])
        sorted_data = ret

    return sorted_data

def get_completed(games, timestamp):
    completed_games = [item for item in games if item["completion_date"] > timestamp]
    return completed_games
    
def generate_message(games):
    # TODO: Generate a message for the given list of games
    current_games = []
    current_completes = []

    # Current timestamp
    now = datetime.datetime.now(datetime.UTC).timestamp()

    # Calculate the cutoff timestamp for 5 days ago
    cutoff_timestamp = now - (5 * 24 * 60 * 60)

    # Filter the list to include only items not older than 5 days
    recent_games = [item for item in games if item["last_played"] >= cutoff_timestamp]
    
    # get the most recent finished game and 2 current in progress games
    for game in recent_games:
        if len(current_games) < 2:
            if game['percent'] < 100:
                current_games.append(game)
        if len(current_completes) < 1:
            if game['percent'] == 100:
                current_completes.append(game)
    
    #print(current_games)
    #print(current_completes)
    
    str = "Recently completed:\n"
    for game in current_completes:
        str += '- [{}]({}) completed on {}\n'.format(game['title'], game['link'], game['completion_date'].strftime('%d %B'))
    str += "Currently hunting:\n"
    for game in current_games:
        str += '- [{}]({}) - Progress {}/{}\n'.format(game['title'], game['link'], game['earned_awards'], game['total_awards'])

    return str
 
if __name__ == '__main__':
    # first: parse ruby's games from exophase
    ruby_games = parse_exophase()
    #print(ruby_games)
    # second: generate message to post on Discord
    postmsg = generate_message(ruby_games)
    print(postmsg)