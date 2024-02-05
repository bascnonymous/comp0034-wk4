from flask import current_app as app, request, make_response, abort, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from paralympics import db
from paralympics.models import Region, Event
from paralympics.schemas import RegionSchema, EventSchema

# Flask-Marshmallow Schemas
regions_schema = RegionSchema(many=True)
region_schema = RegionSchema()
events_schema = EventSchema(many=True)
event_schema = EventSchema()


@app.errorhandler(ValidationError)
def register_validation_error(error):
    """Error handler for marshmallow schema validation errors.

    Args:
        error (ValidationError): Marshmallow error.
    Returns:
        HTTP response with the validation error message and the 400 status code
    """
    response = error.messages
    return response, 400


@app.errorhandler(NoResultFound)
def resource_not_found(e):
    """Error handler for 404.

    Args:
        HTTP 404 error
    Returns:
        JSON response with the validation error message and the 404 status code
    """
    return jsonify(error=str(e)), 404


@app.get("/regions", endpoint="get_regions")
def get_regions():
    """Returns a list of NOC region codes and their details in JSON.

    :returns: JSON
    """
    try:
        # Select all the regions using Flask-SQLAlchemy
        all_regions = db.session.execute(db.select(Region)).scalars()
        # Dump the data using the Marshmallow regions schema; '.dump()' returns JSON.
        result = regions_schema.dump(all_regions)
        # Return the data in the HTTP response
    except SQLAlchemyError as e:
        # See https://flask.palletsprojects.com/en/2.3.x/errorhandling/#returning-api-errors-as-json
        abort(404, description="Region not found.")
    return result


@app.get("/regions/<code>", endpoint="get_region")
def get_region(code):
    """Returns one region in JSON.

    :param code: The NOC code of the region to return
    :param type code: str
    :returns: JSON
    """
    # Query structure shown at https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/queries/#select
    region = db.session.execute(db.select(Region).filter_by(NOC=code)).scalar_one()
    # Dump the data using the Marshmallow region schema; '.dump()' returns JSON.
    result = region_schema.dump(region)
    # Return the data in the HTTP response
    return result


@app.get("/events", endpoint="get_events")
def get_events():
    """Returns a list of events and their details in JSON.

    :returns: JSON
    """
    all_events = db.session.execute(db.select(Event)).scalars()
    result = events_schema.dump(all_events)
    return result


@app.get("/events/<event_id>", endpoint="get_event")
def get_event(event_id):
    """Returns the event with the given id JSON.

    :param event_id: The id of the event to return
    :param type event_id: int
    :returns: JSON"""
    event = db.session.execute(db.select(Event).filter_by(id=event_id)).scalar_one()
    result = event_schema.dump(event)
    return result


@app.post("/events", endpoint="add_event")
def add_event():
    """Adds a new event.

    Gets the JSON data from the request body and uses this to deserialise JSON to an object using Marshmallow
    event_schema.loads()

    :returns: JSON
    """
    ev_json = request.get_json()
    event = event_schema.load(ev_json)
    db.session.add(event)
    db.session.commit()
    return {"message": f"Event added with id= {event.id}"}, 201


@app.post("/regions", endpoint="add_region")
def add_region():
    """Adds a new region.

     Gets the JSON data from the request body and uses this to deserialise JSON to an object using Marshmallow
    region_schema.loads()

     :returns: JSON"""
    json_data = request.get_json()
    region = region_schema.load(json_data)
    db.session.add(region)
    db.session.commit()
    return {"message": f"Region added with NOC= {region.NOC}"}, 201


@app.delete("/events/<int:event_id>", endpoint="delete_event")
def delete_event(event_id):
    """Deletes the event with the given id.

    :param event_id: The id of the event to delete
    :returns: JSON"""
    event = db.session.execute(db.select(Event).filter_by(id=event_id)).scalar_one()
    db.session.delete(event)
    db.session.commit()
    return {"message": f"Event {event_id} deleted"}


@app.delete("/regions/<noc_code>", endpoint="delete_region")
def delete_region(noc_code):
    """Deletes the region with the given code.

    <noc_code> is the NOC code of the region to delete.

    :returns: JSON"""
    region = db.session.execute(db.select(Region).filter_by(NOC=noc_code)).scalar_one()
    db.session.delete(region)
    db.session.commit()
    return {"message": f"Region {noc_code} deleted"}


@app.patch("/events/<event_id>", endpoint="event_update")
def event_update(event_id):
    """
    Updates changed fields for the event.

    """
    # Find the event in the database
    existing_event = db.session.execute(
        db.select(Event).filter_by(event_id=event_id)
    ).scalar_one_or_none()
    # Get the updated details from the json sent in the HTTP patch request
    event_json = request.get_json()
    # Use Marshmallow to update the existing records with the changes from the json
    event_updated = event_schema.load(event_json, instance=existing_event, partial=True)
    # Commit the changes to the database
    db.session.add(event_updated)
    db.session.commit()
    # Return json showing the updated record
    updated_event = db.session.execute(
        db.select(Event).filter_by(event_id=event_id)
    ).scalar_one_or_none()
    result = event_schema.jsonify(updated_event)
    response = make_response(result, 200)
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/regions/<noc_code>", methods=["PUT", "PATCH"], endpoint="region_update")
def region_update(noc_code):
    """

    Updates changed fields for the region in accordance with the method received.

    PUT:
        - Used to update a resource or create a new resource if it does not exist.
        - The entire resource is replaced with the new data.
        - If the resource does not exist, it will be created.
    PATCH:
        - Used to partially update a resource.
        - Useful when you want to update only a few fields of a resource without replacing the entire resource.
        - Specify the fields that need to be updated in the request body.

    """

    # Find the region in the database
    existing_region = db.session.execute(
        db.select(Region).filter_by(NOC=noc_code)
    ).scalar_one_or_none()

    print(existing_region)

    # Get the updated details from the json sent in the HTTP patch request
    region_json = request.get_json()

    # Use Marshmallow to update the existing records with the changes from the json
    if request.method == "PATCH":
        r = region_schema.load(region_json, instance=existing_region, partial=True)
    if request.method == "PUT":
        # If the region exists, update it
        if existing_region:
            try:
                r = region_schema.load(region_json, instance=existing_region)
            except ValidationError as err:
                return err.messages, 400
        else:
            # If it doesn't exist add a new region if all the necessary field values are provided
            try:
                r = region_schema.load(region_json)
                return {"message": f"Region added with NOC= {noc_code}"}
            except ValidationError as err:
                return err.messages, 400

    # Commit the changes to the database
    db.session.add(r)
    db.session.commit()

    return {"message": f"Region {noc_code} updated"}
