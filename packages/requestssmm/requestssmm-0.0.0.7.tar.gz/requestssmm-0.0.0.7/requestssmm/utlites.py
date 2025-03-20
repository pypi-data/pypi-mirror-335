from requests import get,post
class Botgp:
    def __init__(self):
        pass
    def share_facebook_post_EAAAAU(self,token, post_url,privacy='SELF'):
        try:
            """
            Share a post on Facebook using the Facebook Graph API.
            :param token: Facebook access token [EAAAAUaZA8...........]
            :param post_url: URL of the post to share
            :param privacy: Privacy setting for the post (default: SELF)
            Returns:
                Grapg api respone
            """
            fb_url = 'https://graph.facebook.com/v13.0/me/feed'
            data = {'link': post_url, 'published': '0', 'privacy': '{"value":"%s"}'%(privacy), 'access_token': token}
            response = post(fb_url, data=data).json()
            if 'id' in response:
                return (True,response)
        except Exception as e:
            return (False,e)
        
    def share_facebook_post_EAAGN(self,token, id_share,cookie,privacy='0'):
        try:
            """
            Share a post on Facebook using the Facebook Graph API.
            :param token: Facebook access token [EAAGNO...........]
            :param post_url: URL of the post to share
            :param privacy: Privacy setting for the post (default: SELF)
            Returns:
                Grapg api respone
            """
            he = {
                'accept': '*/*',
                'accept-encoding': 'gzip, deflate',
                'connection': 'keep-alive',
                'content-length': '0',
                'cookie': cookie,
                'host': 'graph.facebook.com'
            }
            response = post(f'https://graph.facebook.com/me/feed?link=https://m.facebook.com/{id_share}&published={privacy}&access_token={token}', headers=he).json()
            if 'id' in response:
                return (True,response)
        except Exception as e:
            return (False,e)
    def comment_post_EAAGN(self,post_id='9000855519965854',message='ma4D1',token=None,cookes=None):
        try:
            """
            Comment on a post on Facebook using the Facebook Graph API.
            :param token: Facebook access token [EAAGNO...........]
            :param post_url: URL of the post to share
            :param privacy: Privacy setting for the post (default: SELF)
            Returns:
            Grapg api respone
            """
            if token and cookes :
                response=post(f"https://graph.facebook.com/{post_id}/comments/?message={message}&access_token={token}", headers = {"cookie":cookes}).json()
                if 'id' in response:
                    return (True,response)
        except Exception as e:
            return (False,e)
        