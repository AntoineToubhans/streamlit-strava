Strava-Data
===

Install: `poetry install` (requires python>=3.11)

Run app: `poetry run streamlit run app.py`


### Update data cache from Strava

First, get your Strava code:

1. Go to url `https://www.strava.com/oauth/authorize?client_id=114166&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fauthorization&approval_prompt=auto&scope=read%2Cactivity%3Aread&response_type=code`
2. Get the code from the URL
3. Paste code to file [update_data_cache.py](./update_data_cache.py) script

Then run: `poetry run python update_data_cache.py`


### Backog

- Use [timeunits](https://altair-viz.github.io/user_guide/transform/timeunit.html#user-guide-timeunit-transform) to group by periods. :warning: not use it will work for weeks