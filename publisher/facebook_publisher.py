from publisher_manager import publish_post

def publish(caption, media_url=None):
    return publish_post("Facebook", caption, media_url)
