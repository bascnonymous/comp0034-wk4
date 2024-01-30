def test_print_response_params(client):
    """
    This is just so you can see what type of detail you get in a response object.
    Don't use this in your tests!
    """
    response = client.get("/regions")
    print("Printing response.headers:")
    print(response.headers)
    print('\n Printing response.headers["Content-Type"]:')
    print(response.headers["Content-Type"])
    print("Printing response.status_code:")
    print(response.status_code)
    print("Printing response.data:")
    print(response.data)
    print("Printing response.json:")
    print(response.json)
