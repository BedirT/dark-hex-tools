# https://stackoverflow.com/a/39225272/15269364

from pathlib import Path
import requests

def missing_in_file():
    print('Please pick a pre-run game data to work on;')        
    print('\t1) 3x3 First Player')
    print('\t2) 4x3 First Player (Long edge)')
    game_type = -1
    while game_type <= 0 or game_type > 2:
        try:
            game_type = int(input('Please enter the item number only (i.e. 1): ').strip())
        except KeyboardInterrupt:
            exit()
        except:
            game_type = -1
            print('Invalid input, please try again.')
    if game_type == 1:
        Path('Exp_Results/pONE/3x3/').mkdir(parents=True, exist_ok=True)
        in_file = 'Exp_Results/pONE/3x3/default_file.pkl'
        download_file_from_google_drive('1oNl4UZAB6SxjA-aUi0M9oUiqlpIdXnwk', in_file)
    elif game_type == 2:
        Path('Exp_Results/pONE/4x3/').mkdir(parents=True, exist_ok=True)
        in_file = 'Exp_Results/pONE/4x3/default_file.pkl'
        download_file_from_google_drive('1MpMn8Gf0a8tCWeb8Ag276FlLGX6tBCD9', in_file)
    return in_file

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)