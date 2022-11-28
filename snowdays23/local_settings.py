STATIC_ROOT = '/app/static/'

# Reconfigure databases using DATABASE_URL environment variable
DATABASES['default'] = dj_database_url.config(conn_max_age=600)

# PayPal creds
PAYPAL_CLIENT_ID = "ASviHC7eUli4wcDKphrreCoJVtht9Hxr2_y3VLKK6zcDSy8SHw20MKcf78BLrfXwS3pjTNuJps46gAjP"
PAYPAL_SECRET = "EHhz1zIhCjUGiqjZqyo0_0X-6Wznx0w3kZ4P7JMtNO4hvJCW2Z3cypbI02OLCMnA1ew2U6Oi8cWy4u9v"