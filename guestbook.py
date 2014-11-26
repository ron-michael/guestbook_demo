import base64
import json
import uuid

from flask import Flask
from flask import request


app = Flask(__name__)



##-- Route Methods --##

@app.route('/guests/', methods=['GET', 'POST'])
def process_guests():
    """Processes guests requests.

    Performs processing for the REST requests or access to the guests
    collection resource.

    Args:
        N/A; there are no method parameters.

        However, for POST requests, it is expected that the FORM field "guest"
        will contain JSON-formatted new-guest information:

            {
                "name": "Wilkins Distilled",
                "age": "16",
                "photo": ""                
            }


    Returns:
        For GET request, JSON formatted list of guest information is returned:

            {
                "1231238080AAA":
                    {
                        "id": "1231238080AAA",
                        "name": "Wilkins Distilled",
                        "age": "16",
                        "photo": ""                
                    },

                "1123ABCD099DF":
                    {
                        "id": "1123ABCD099DF",
                        "name": "Xperia Phone",
                        "age": "26",
                        "photo": ""                
                    }
            }
                    
            The photo field will hold base64encoded contents.

        For POST requests, operations status is returned:
            
            {
                "result": "success"
            }

            The result field will either have a value of "success" or "fail".

    Raises:
        N/A
    """

    method = request.method

    output = ''
    if method == 'GET':
        output = process_guests_fetch(request)

    elif method == 'POST':
        output = process_guests_add(request)

    if output == None:
        output = ''

    return output


@app.route('/guests/<guest_id>', methods=['GET'])
def process_guest(guest_id):
    """Processes fetch single guest requests.

    Performs processing for the REST requests for a single guest entry from the 
    guests collection resource.

    Args:
        N/A; there are no method parameters.


    Returns:
        If the id is a valud guest entry ID, JSON formatted guest information:

            {
                "name": "Wilkins Distilled",
                "age": "16",
                "photo": ""                
            }

            The photo field will hold base64encoded contents.

    Raises:
        N/A
    """

    output = process_guests_fetch(request, guest_id)

    if output == None:
        output = ''

    return output



##-- Non-Route Methods --##

def process_guests_fetch(request ,guest_id = None):
    """Processes guests listing requests.

    Performs processing for listing requests for the guests collection resource.

    Args:
        request: web request object

    Returns:
        If no id value is specified, JSON formatted list of guest information:

            {
                "1231238080AAA":
                    {
                        "id": "1231238080AAA",
                        "name": "Wilkins Distilled",
                        "age": "16",
                        "photo": ""                
                    },

                "1123ABCD099DF":
                    {
                        "id": "1123ABCD099DF",
                        "name": "Xperia Phone",
                        "age": "26",
                        "photo": ""                
                    }
            }

        If a valid guest ID is specified, JSON-formatted guest information
            
            {
                "id": "1231238080AAA",
                "name": "Wilkins Distilled",
                "age": "16",
                "photo": ""                
            }

        Note: The photo field will hold base64encoded contents.

    """
    guests = load_guests_data();
    data = None
    if guest_id != None and len(guest_id.strip()) > 0:
        if guests.has_key(guest_id):
            data = guests[guest_id]

    if data == None:    
        data = guests

    data = json.dumps(data)

    return data


def process_guests_add(request):
    """Processes guests add requests.

    Performs processing for addition or modification requests for the guests 
    collection resource.

    Args:
        request: web request object

        The request object' form attribute is checked for the field "guest"
        to contain JSON-formatted new-guest information:

            {
                "name": "Wilkins Distilled",
                "age": "16",
                "photo": ""                
            }

    Returns:

        Operation result in a JSON-formatted structure:

            {
                "result": "success"
            }

            The result field will either have a value of "success" or "fail".
    """
    resp = create_response('fail')

    # Check if there is guest info passed
    if request.form == None or len(request.form['guest']) == 0:
        resp['reason'] = 'no_data'
        return json.dumps(resp)

    # Fetch guest info and use as JSON data
    argInfo = request.form['guest']
    try:
        argInfo = argInfo.strip()
        argInfo = json.loads(argInfo)
    except:
        resp['reason'] = 'invalid_data'
        return json.dumps(resp)

    guests = load_guests_data()
    guestInfo = None

    # Check if guest ID exists (update-mode)
    if argInfo.has_key('id'):
        guestId = argInfo['id']

        if guests.has_key(guestId):
            guestInfo = guests[guestId]


    # If not update mode
    if guestInfo == None:

        #print guests

        # Traverse guest list and compare against submitted data
        for key, guest in guests.iteritems():
            # If name matches, consider as update-mode
            if guest['name'] == argInfo['name']:
                #print guest
                #print argInfo

                guestId = guest['id']
                guestInfo = argInfo
                break 

    # Check if it's a new entry
    if guestInfo == None:
        guestId = str(uuid.uuid4())
        guestInfo = argInfo

    guestInfo['id'] = guestId
    guests[guestId] = guestInfo

    try:
        save_guests_data(guests)
        resp['result'] = 'success'
        resp['id'] = guestId
    except:
        resp['reason'] = 'failed_saving'

    return json.dumps(resp)

def load_guests_data():
    """Loads guests data.

    Reads/deserializes JSON object from the JSON file, guests.json.

    Args:
        N/A

    Returns:
        N/A

    Raises:
        Exception when loading fails
    """
    data = None
    try:
        with open('guests.json') as datafile:
            data = json.load(datafile)
    except:
        data = None

    if data == None:
        data = json.loads('{}')
    
    return data

def save_guests_data(guests):
    """Saves guests data.

    Saves/serializes the specified guests data to a file, guests.json.

    Args:
        guests: guests information to be saved

    Returns:
        N/A

    Raises:
        Exception when saving fails
    """
    with open('guests.json', 'w') as datafile:
        json.dump(guests, datafile)


def create_response(result):
    """Creates response data.

    Creates a JSON object intended to be used as response data.

    Args:
        result: string to be the value of the result field

    Returns:
        For POST requests, operations status is returned:
            
            {
                "result": "success"
            }

    Raises:
        N/A
    """
    obj = json.loads("""
        {
            "result": "success"
        }
        """)

    obj["result"] = result
    return obj

if __name__ == '__main__':
    app.run(debug=True)
