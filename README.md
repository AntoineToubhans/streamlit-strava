Strava-Data
===

Install: `poetry install` (requires python>=3.11)

Run app: `poetry run streamlit run app.py`

### Steps to get my tokens

1. Go to url `https://www.strava.com/oauth/authorize?client_id=114166&redirect_uri=http://localhost&response_type=code&scope=activity:read_all`
2. Authorize and get the code from the URL (don't care if there is an error)
3. run `curl -X POST https://www.strava.com/oauth/token\?client_id\=114166\&client_secret\=e8ad5dd8c1d1f9a6e6fc458d05e4c47d12c71534\&code\=56704285702ef7f84e1bb51e6f96abcf9d05de2a\&grant_type\=authorization_code | jq`
4. Get tokens from the JSON response e.g.:

```json
{
  "token_type": "Bearer",
  "expires_at": 1695601986,
  "expires_in": 21600,
  "refresh_token": "171e69ed7fb03ab75014d1f6abbd293398a903dc",
  "access_token": "1ab45dc027eb54b7ccf8ef79d3d7807344ef42b3",
  "athlete": {
    "id": 66893629,
    "username": "atoubhans",
    "resource_state": 2,
    "firstname": "Antoine",
    "lastname": "Toubhans",
    "bio": null,
    "city": null,
    "state": null,
    "country": null,
    "sex": "M",
    "premium": true,
    "summit": true,
    "created_at": "2020-08-24T11:07:40Z",
    "updated_at": "2023-09-15T12:29:39Z",
    "badge_type_id": 1,
    "weight": 75,
    "profile_medium": "https://dgalywyr863hv.cloudfront.net/pictures/athletes/66893629/16628470/1/medium.jpg",
    "profile": "https://dgalywyr863hv.cloudfront.net/pictures/athletes/66893629/16628470/1/large.jpg",
    "friend": null,
    "follower": null
  }
}```