# turbotape

A modern utility library for easily using the Tape (https://tapeapp.com/) API with Python.

## How to install

```
pip install turbotape
```

## the 'tpod' command

Get your client ID und client secret from https://podio.com/settings/api

Then run the following command:

```
tpod init --client-id=<Tape-client-id> --client-secret=<Tape-client-secret>
```

This will create a hidden file called `.turbotape_credentials.json` in the
current working directory. The access token is valid for some hours.

## Accessing single Tape items

You can find die `item_id` of any Tape item by opening a Tape item detail view
in the Webbrowser and then clicking on 'Actions' and 'Developer info':

![Click on Actions](docs/developer-info01.png)

This will display among other things the item_id and the app_id:

![Click on dwActions](docs/developer-info02.png)

Using the item_id you can now write a simple python programm that will read the details
of one single item. Create file named `get_record_data.py` that contains the following Python code:

```python
from turbotape.session import create_tape_session

ITEM_ID=123456789 # <- Replace with your own record_id.


def get_tape_record(record_id):
    # reads the access token from .turbotape_credentials.json
    Tape = create_Tape_session()

    # see https://developers.podio.com/doc/items/get-item-22360
    record_url = f'https://api.tapeapp.com/v1/record/{record_id}'

    # podio.get() works almost the same way that requests.get() works
    resp = podio.get(record_url)
    resp.raise_for_status()
    item_data = resp.json()
    return item_data


if __name__ == '__main__':
    item_data = get_tape_record(ITEM_ID)
    # print something from the item_data, then exit
    print(f"Record ID: {item_data['item_id']}")
    print(f"Record title: {item_data['title']}")

```

Now run the program. The output should look like this:

```bash
$ python ./get_record_data.py
Record ID: 123456789
Record title: Bow of boat
$ _ 
```

## Working with higher number of Tape items

Tape has very strict API limits. Because of this, turbotape includes an option to
create a 'robust' session. If you create Tape session with the `robust` parameter,
turbotape will wait when the API limit is reached and it will also retry the request
when Tape returns a '504 Gateway timeout' error.

```python
from turbotape.session import create_podio_session

podio = create_podio_session(robust=True)
```

Another hurdle is pagination. To download the data of a whole Tape app, we need to
get the Tape items in smaller chunks:

```python
from turbotape.session import create_podio_session
from turbotape.helpers import iterate_resource

app_id = 987654321 # <- Enter your own app_id here.

podio = create_podio_session(robust=True)
url = f'https://api.podio.com/item/app/{app_id}/filter/'

for item in iterate_resource(client, url, 'POST', limit=250):
    print(item['item_id'])
```

(The `limit` parameter can be anything from 1 to 500. On larger Tape apps it is wise to stay below
300 and reduce the limit if you see that the Tape API returns a lot of HTTP 504 Errors.

See https://developers.podio.com/doc/items/filter-items-4496747 for more info on the
filter API endpoint.

## Turning a whole Tape app into a Pandas dataframe

For this example to work [Pandas](https://pandas.pydata.org/) needs to be installed already. 
Often you want to get __all__ the data from one Tape app.

```python
import turbotape.dataframe
from turbotape.session import create_podio_session

podio = create_podio_session(robust=True)
app_id = 987654321 # <- Replace with your own app_id here.

# You need to list the fields that should be included in the dataframe
df = turbotape.dataframe.load_from_app(podio, app_id, labels=['Title', 'Description'])

# But you can also use the external_ids of the fields
df = turbotape.dataframe.load_from_app(podio, app_id, external_ids=['title‘, 'description'])
```


## Useful links
+ https://github.com/finklabs/whaaaaat
+ http://click.pocoo.org/5/
+ https://github.com/asweigart/pyperclip
+ http://urwid.org/
+ http://npyscreen.readthedocs.io/introduction.html
+ https://help.podio.com/hc/en-us/community/posts/206886967-Updating-a-Calculation-Field-Script-via-the-API
+ https://requests-oauthlib.readthedocs.io/en/latest/
+ https://sedimental.org/glom_restructured_data.html
+ https://flit.readthedocs.io/en/latest/
