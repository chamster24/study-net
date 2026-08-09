# Intrachat 
    - (!!!) Add router server code
    - (!!) Fix offline mode
        - Remove incognito mode and change any code which may depend on it
        - Remove any images and remove favicons
    - (!!!) FIX INTRACHAT SCRIPTS, BOTH ONLINE AND OFFLINE
    
    Planned features:
    - slash commands (https://github.com/chamster24/IntrAChat/issues/3)
    - better ui, maybe not for offline mode (https://github.com/chamster24/IntrAChat/issues/4)
    - change room/user dict to a global dict so it can be processed by MANY workers instead of 1 (https://github.com/chamster24/IntrAChat/issues/9)
    - Emoji selector (https://github.com/chamster24/IntrAChat/issues/14)
    - Rate limiting to prevent DDOS (https://github.com/chamster24/IntrAChat/issues/18)
    - ratelimit join requests to 1/sec (https://github.com/chamster24/IntrAChat/issues/19)
    - msg/roomcode/user char limits serverside (https://github.com/chamster24/IntrAChat/issues/20)


# StudyNet BACKEND
    ## Security.py
        - Make JWT key permanant ("# TODO: make the secret permanent via os.getenv")

    ## Database.py
        - "in db, code so that using the given exp, autoexpire the jti once the time is up. This will also be useful for "Log me out on all devices" (security.py)
        - "# TODO: Initialize SQLModel"

# StudyNet FRONTEND
    ## Login.html
        - Send the form results to server
        - Force a HCaptcha on 3+ failed attempts

- (!!) Fill out procfile (root)