def verify_credentials(username):
    # allowable = ["dk", "moae", "20dk01", "20dk01l", "dk01", "321dk123",]
    allowable = ["20dk01l"]
    return username.lower().replace(".", "") in allowable


def get_creds(username):
    return {
        "identifier": "20DK01L",
        "name": "DK"
    }


def auth(username):
    if verify_credentials(username):
        return get_creds(username)
    else:
        return None
