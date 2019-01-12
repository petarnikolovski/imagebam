# ImageBam

This project is not affiliated with the `imagebam.com`. This is wrapper library around their [official API][1]. This is only a proof of concept project, and not a full library. It only implements verification (which is usually the hardest part of the library), and one function (to fetch all images from own gallery).

## How to use this library?

Here is the example usage:

from imagebam.imagebam import ImageBam

```python
consumer_key = 'REGISTER_YOUR_APP_TO_OBTAIN_THIS'
consumer_secret = 'REGISTER_YOUR_APP_TO_OBTAIN_THIS'

ib = ImageBam(consumer_key, consumer_secret)
ib.set_fake_user_agent()  # If you don't want to appear as robot

# This is workflow to obtain the token
token, secret = ib.obtain_unathorized_token()
ib.authorize_token(token)  # Opens up a browser, asking for permission and giving authorization code
access_token, access_token_secret = ib.obtain_access_token(
  token,
  secret,
  'AUTHORIZATION_CODE_OBTAINED_FROM_BROWSER'
)

# Now use some API methods
ib.fetch_list_of_images_from_gallery(access_token, access_token_secret, 'YOUR_GALLERY_ID')
```

[1]: https://code.google.com/archive/p/imagebam-api/
