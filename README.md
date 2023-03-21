# guid_rest_api

Rest API that adheres to these instructions:<br />

Design and implement a RESTful web API that can be used to maintain a database of GUIDs (Globally Unique Identifier) and associated
metadata. The API must expose commands to perform CRUD operations (Create, Read, Update, Delete). The application should use a cache
layer to quickly serve the most recently used GUIDs. GUIDs should be 32 hexadecimal characters, all uppercase. The GUIDs should be valid only
for a limited period of time, with a default of 30 days from the time of creation, if an expiration time is not provided. The expiration time should be
formatted in Unix Time. Input and output data should be valid JSON format. Validations should be put in place to make sure input data
conforms the specified formats. Code must be documented.<br />

Commands specification<br />

Create<br />
Creates a new GUID and stores it in the database along with the metadata<br />
provided. If a GUID is not specified, the system should generate a random one.<br />

Example 1<br />
URL: POST /guid/9094E4C980C74043A4B586B420E69DDF<br />
Input:<br />
{<br />
"expire": "1427736345",<br />
"user": "Cylance, Inc."<br />
}<br />
Output:<br />
{<br />
"guid": "9094E4C980C74043A4B586B420E69DDF",<br />
"expire": "1427736345",<br />
"user": "Cylance, Inc."<br />
}<br />

Example 2<br />
URL: POST /guid<br />
Input:<br />
{<br />
"user": "Cylance, Inc."<br />
}<br />
Output:<br />
{<br />
"guid": "9094E4C980C74043A4B586B420E69DDF",<br />
"expire": "1427736345",<br />
"user": "Cylance, Inc."<br />
}<br />

Read<br />
Returns the metadata associated to the given GUID.<br />

Example<br />
URL: GET /guid/9094E4C980C74043A4B586B420E69DDF<br />

Output:<br />
{<br />
"guid": "9094E4C980C74043A4B586B420E69DDF",<br />
"expire": "1427736345",<br />
"user": "Cylance, Inc."<br />
}<br />

Update<br />
Updates the metadata associated to the given GUID. The GUID itself cannot be
updated using this command.<br />

Example<br />
URL: POST /guid/9094E4C980C74043A4B586B420E69DDF<br />
Input:<br />
{<br />
"expire": "1427822745",<br />
}<br />
Output:<br />
{<br />
"guid": "9094E4C980C74043A4B586B420E69DDF",<br />
"expire": "1427822745",<br />
"user": "Cylance, Inc."<br />
}<br />

Delete<br />
Deletes the GUID and its associated data.<br />

Example<br />
URL: DELETE /guid/9094E4C980C74043A4B586B420E69DDF<br />
No output.<br />

Error code returns<br />
The following response codes should be returned by the service:<br />
200's on accepted/successful requests<br />
400's on client errors<br />
500's on server errors<br />


Built using python, MongoDB, redis, and tornado webframe.<br />

How to run:<br />
make sure tornado, redis, and mongoDB are installed.<br />
pipenv install (module)<br />

start redis:<br />
run redis-server in terminal<br />

run this command to start server (http://localhost:8080/):<br />
pipenv run python guid.py<br />

can use postman to send requests to server <br />

Assumptions: <br />
could not call post request with guid that already exists in database <br />
could not call put request with guid inside body of input <br />
used put handler for updates rather than post <br />
