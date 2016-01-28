#encoding: utf-8
import json
import urllib
import urllib2

from settings_local import bing_api_key


def get_images(query=""):
    queryBingFor = "'" + query + "'" # the apostrophe's required as that is the format the API Url expects.
    quoted_query = urllib.quote(queryBingFor)
    rootURL = "https://api.datamarket.azure.com/Bing/Search/v1/Image"
    searchURL = rootURL + "?$format=json&$top=20&Query=" + quoted_query
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, searchURL, None , bing_api_key)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    return json.loads(urllib2.urlopen(searchURL).read())