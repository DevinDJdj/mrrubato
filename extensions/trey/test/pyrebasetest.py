#> pip install pyrebase4
import pyrebase
import sys
sys.path.insert(0, 'c:/devinpiano/') #config.json path
sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path
import config 

def login():
    email = config.cfg["trey"]["user"]
    password = config.cfg["trey"]["pwd"]
    auth = firebase.auth()
    try:
                # Generate the email verification link
        #link = auth.generate_email_verification_link(email) #, action_code_settings=action_code_settings)
        #return link
        #auth.create_user_with_email_and_password(login, password)
        # Sign in the user
        user = auth.sign_in_with_email_and_password(email, password)

        # Extract the UID (localId) from the user object
        uid = user.get("localId") 

        print(f"Successfully signed in. User UID: {uid}")

        # You can also get other user info if needed
        # id_token = user.get("idToken")

    except Exception as e:
        print(f"Login failed: {e}")


if __name__ == '__main__':
     # Firebase configuration
    databaseURL = config.cfg["firebase"]["fbconfig"]["databaseURL"]
        # Init firebase with your credentials
    #auth.current_user['localId']

    firebase = pyrebase.initialize_app({'apiKey': config.cfg["firebase"]["fbconfig"]["apiKey"], 'authDomain': config.cfg["firebase"]["fbconfig"]["authDomain"], 'databaseURL':databaseURL, 'storageBucket': config.cfg["firebase"]["fbconfig"]["storageBucket"]})    
    login()

