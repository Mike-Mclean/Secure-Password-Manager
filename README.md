# OSUSecurePasswordManager

## Development

#### prerequisites

- docker compose
- python >=3.12 (+ pyenv for easier version management)

### set up

#### database

start the local dev PgSQL database in docker

```sh
docker compose up database
```

#### python

install [pyenv](https://4geeks.com/how-to/what-is-pyenv-and-how-to-install-pyenv)
for example, on MacOS, with brew:

```sh
# install some dependencies first
brew install openssl readline sqlite3 xz zlib
brew install pyenv
```

install and use python version in pyenv

```sh
pyenv install 3.12.7
pyenv local 3.12.7
```

install and set up a virtual environment and app dependencies

```sh
# create a virtual environment to keep this app's python libraries segregated from your system
python --version # 3.12.7
python -m venv .venv # creates a virtual environment in ./.venv
source ./.venv/bin/activate
(.venv) pip install -r passwordmanager/requirements.txt
```

copy the `env-example` to `.env` and make any changes you need, then run migrations and start the app

```sh
cp env-example .env
# ...
cd passwordmanager
python manage.py migrate && python manage.py runserver
```

then the app should be running on localhost:8000

to build and inject the frontend React app:

```sh
cd frontend
npm run build
```

vite will output the build assets and manifest into the django static directory. The directory is hardcoded in the vite config, and is the same one referenced in `passwordmanager/settings.py` as `FRONTEND_MANIFEST_PATH`

### Testing the API with Postman

included is a Postman colelction JSON file that has tests for all the API endpoints. In order to simulate a authed/logged in session, there is a special endpoint that only runs when in development mode for getting a valid CSRF token and a sessionid to use in subsequent Postman requests. the sessionid corresponds to an auth session in Django once the login exchange happens.

### Email provider

Currently this repo is set up to use free gmail account as the SMTP provider. (See slack for credentials)

### MFA

Vault routes are optinoally MFA protected. If the user is MFA enrolled, then MFA verification will be required to access hose endpoints, based on the `MFARequiredIfOptedIn` permissions class

#### Email MFA

Email-based MFA sends a verification code to the user's email address during login or enrollment.
Configure SMTP settings in your `.env` file (a free Gmail account is currently configured using an app password, see [google app passwords](https://support.google.com/accounts/answer/185833?hl=en))

**Enrollment Flow:**

1. User requests email MFA enrollment via `/api/accounts/mfa/email/enroll/`
2. System sends verification email with time-limited code
3. User enters code via `/api/accounts/mfa/email/verify/` to complete enrollment
4. Email MFA is enabled for subsequent logins

**Login Flow:**

1. User completes username/password authentication
2. System sends MFA challenge code to user's email
3. User enters code to complete authentication

#### TOTP (Time-based One-Time Password) MFA

TOTP MFA uses authenticator apps like Google Authenticator, Microsoft Authenticator, etc. to generate time-based codes. The code is based on a random secret that is stored in the user profile, and can be checked subsequently to ensure the user's auth app has the original code

**Enrollment Flow:**

1. User initiates TOTP enrollment via `/api/accounts/mfa/totp/enroll/`
2. System generates a random secret key and buolds a QR code from it
3. User can scan the QR code with their authenticator app or potentically use the random secret directly if their authenticator app uses it
4. The app will then generate a code that canbe used to verify the original secret
5. User enters the code via `/api/accounts/mfa/totp/verify/`
6. System validates code and enables TOTP for the account secret

**Login Flow:**

1. User completes username/password authentication
2. System prompts for current 6-digit TOTP code
3. User enters code from their authenticator app
4. System validates time-based code and grants access
