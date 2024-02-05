def test_get_regions_status_code(client):
    """
    GIVEN a Flask test client
    WHEN a request is made to /regions
    THEN the status code should be 200
    """
    response = client.get("/regions")
    assert response.status_code == 200


def test_get_regions_json(client):
    """
    GIVEN a Flask test client
    AND the database contains data of the regions
    WHEN a request is made to /regions
    THEN the response should contain json
    AND a JSON object for Tonga should be in the json
    """
    response = client.get("/regions")
    assert response.headers["Content-Type"] == "application/json"
    tonga = {"NOC": "AFG", "notes": "", "region": "Afghanistan"}
    assert tonga in response.json


def test_get_specified_region(client):
    """
    GIVEN a Flask test client
    AND the 5th entry is AND,Andorra,
    WHEN a request is made to /regions/AND
    THEN the response json should match that for Andorra
    AND the response status_code should be 200
    """
    and_json = {"NOC": "AND", "notes": "", "region": "Andorra"}
    response = client.get("/regions/AND")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    assert response.json == and_json


def test_get_region_not_exists(client):
    """
    GIVEN a Flask test client
    WHEN a request is made for a region code that does not exist
    THEN the response status_code should be 404 Not Found
    """
    response = client.get("/regions/LLL")
    assert response.status_code == 404


def test_post_region(client):
    """
    GIVEN a Flask test client
    AND valid JSON for a new region
    WHEN a POST request is made to /regions
    THEN the response status_code should be 201
    """
    # JSON to create a new region
    region_json = {"NOC": "ZZR", "region": "ZedZedArr"}
    # pass the JSON in the HTTP POST request
    response = client.post(
        "/regions",
        json=region_json,
        content_type="application/json",
    )
    # 201 is the HTTP status code for a successful POST or PUT request
    assert response.status_code == 201


def test_region_post_error(client):
    """
    GIVEN a Flask test client
    AND JSON for a new region that is missing a required field ("region")
    WHEN a POST request is made to /regions
    THEN the response status_code should be 400
    """
    missing_region_json = {"NOC": "ZZY"}
    response = client.post("/regions", json=missing_region_json)
    assert response.status_code == 400


def test_patch_region(client, new_region):
    """
    GIVEN an existing region
    AND a Flask test client
    WHEN an UPDATE request is made to /regions/<noc-code> with notes json
    THEN the response status code should be 200
    AND the response content should include the message 'Region <NOC_code> updated'
    """
    new_region_notes = {"notes": "An updated note"}
    code = new_region.NOC
    response = client.patch(f"/regions/{code}", json=new_region_notes)
    assert response.json["message"] == "Region NEW updated"
    assert response.status_code == 200


def test_delete_region(client, new_region):
    """
    GIVEN an existing region in JSON format
    AND a Flask test client
    WHEN a DELETE request is made to /regions/<noc-code>
    THEN the response status code should be 200
    AND the response content should include the message 'Region {noc_code} deleted.'
    """
    # Get the NOC code from the JSON which is returned in the new_region fixture
    code = new_region.NOC
    response = client.delete(f"/regions/{code}")
    assert response.status_code == 200
    assert response.json["message"] == "Region NEW deleted"
