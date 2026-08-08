# Intrachat 
    - (!!!) Add router server code
    - (!!) Fix offline mode
        - Remove incognito mode and change any code which may depend on it
        - Remove any images and remove favicons

# StudyNet BACKEND
    ## Security.py
        - Make JWT key permanant ("# TODO: make the secret permanent via os.getenv")

    ## Database.py
        - "in db, code so that using the given exp, autoexpire the jti once the time is up. This will also be useful for "Log me out on all devices" (security.py)

# StudyNet FRONTEND
    ## Login.html
        - Send the form results to server
        - Force a HCaptcha on 3+ failed attempts

- Fill out procfile