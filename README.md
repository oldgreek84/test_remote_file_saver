# Remote file saver


Test application implements REST API which allows
upload, save and download user files using http requests.


## Using application

For woking application you need installed MongoDb database:

[link to install MongoDb](https://docs.mongodb.com/manual/installation/)


- download app from repository:

```bash
git clone https://github.com/oldgreek84/test_remote_file_saver.git
```

- open working directory:

```bash
cd test_remote_file_saver
```

- install python enviroment and pip requirements:

```bash
virualenv env
source env/bin/activate
pip install -r requirements.txt
```

- run test web server:

```bash
python app/app.py
```

- application is available at URL:

```vim
http://localhost:5000/api
```

## Working with REST API

main_url = http://localhost:5000

#### API endpoints:

- Create new user in the db

  {main_url}/api/auth/users/

- Get user authentification token

  {main_url}/api/auth/token/

- download or upload user files

  {main__url}/api/values/
