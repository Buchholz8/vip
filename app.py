from flask import Flask, request, jsonify, make_response
import dbcreds, dbhelpers

app = Flask(__name__)


## user handlers
@app.post("/api/user")
def post_user():
    error = dbhelpers.check_endpoint_info(request.json, ["username", "email","password","profile_img","banner_img","description"])
    if error != None:
        return make_response(jsonify(error), 500)
    results = dbhelpers.run_procedures(
        "call create_account_post(?,?,?,?,?,?)",
        [
            request.json.get("username"),
            request.json.get("email"),
            request.json.get("password"),
            request.json.get("profile_img"),
            request.json.get("banner_img"),
            request.json.get("description"),
        ],
    )
    if results is None:
        return make_response(jsonify("success"), 200)
    else:
        return make_response(jsonify("Sorry, an error occurred"), 500)


@app.post("/api/user-login")
def post_userlogin():
    token = dbhelpers.generate_token()
    error = dbhelpers.check_endpoint_info(request.json, ["email", "password"])
    if error != None:
        return make_response(jsonify(error), 500)
    results = dbhelpers.run_procedures(
        "call login_post(?,?,?)",
        [token, request.json.get("email"), request.json.get("password")],
    )
    if type(token) == str:
        return make_response(jsonify({"token": token}, results), 200)
    elif type(results) == list:
        return make_response(jsonify(results), 200)
    else:
        return make_response(jsonify("Sorry, an error occurred"), 500)


@app.get("/api/user")
def user_get():
    token = request.args.get("token")
    if not token:
        error = {"error": "missing token"}
        return make_response(jsonify(error), 500)

    error = dbhelpers.check_endpoint_info(request.args, ["token"])
    if error:
        return make_response(jsonify(error), 500)

    results = dbhelpers.run_procedures("CALL user_get(?)", [token])

    if (type(results) == list) and len(results) > 0:
        row = results[0]
        response = {
            "username": row[0],
            "email": row[1],
            "profile_img": row[2],
            "banner_img": row[3],
            "created_at": row[4],
            "description": row[5],
        }

        return make_response(jsonify(response), 200)
    else:
        error = {"error": "No data found"}
        return make_response(jsonify(error), 500)


@app.delete("/api/user-logout")
def delete_user():
    token = request.args.get("token")
    if token is None:
        return make_response(jsonify("Token is required"), 400)

    results = dbhelpers.run_procedures("call login_delete(?)", [token])
    if results is None:
        return make_response(jsonify("success"), 200)
    else:
        return make_response(jsonify("Sorry, an error occurred"), 500)


# group handlers
@app.post("/api/groups")
def post_group():
    group_token = dbhelpers.generate_token()
    error = dbhelpers.check_endpoint_info(
        request.json, ["owner_id", "banner_img", "description", "name", "profile_img"]
    )
    if error is not None:
        return make_response(jsonify(error), 500)
    results = dbhelpers.run_procedures(
        "call group_post(?,?,?,?,?,?)",
        [
            group_token,
            request.json.get("owner_id"),
            request.json.get("banner_img"),
            request.json.get("description"),
            request.json.get("name"),
            request.json.get("profile_img"),
        ],
    )
    if type(results) == list:
        return make_response(jsonify(results), 200)
    else:
        return make_response(jsonify("Sorry, an error occurred"), 500)


@app.post("/api/group-join")
def join_group():
    error = dbhelpers.check_endpoint_info(
        request.json, ["group_token_input", "token_input"]
    )
    if error is not None:
        print("Error:", error)
        return jsonify({"message": str(error)}), 401
    results = dbhelpers.run_procedures(
        "call join_group_post(?, ?)",
        [request.json.get("group_token_input"), request.json.get("token_input")],
    )
    if type(results) == list:
        return make_response(jsonify(results), 200)
    else:
        return make_response(jsonify("Code either isn't correct or doesn't exist"), 500)


@app.get("/api/groups")
def all_groups_get():
    member_id = request.args.get("member_id")
    if not member_id:
        error = {"error": "member_id"}
        return make_response(jsonify(error), 500)
    error = dbhelpers.check_endpoint_info(request.args, ["member_id"])
    if error:
        return make_response(jsonify(error), 500)

    results = dbhelpers.run_procedures("CALL group_get(?)", [member_id])

    if isinstance(results, list) and len(results) > 0:
        response = [{"name": row[0], "profile_picture": row[1], "group_id": row[2]} for row in results]
        return make_response(jsonify(response), 200)
    else:
        error = {"error": "No data found"}
        return make_response(jsonify(error), 500)



@app.get("/api/group-get")
def group_get():
    group_id = request.args.get("group_id")
    if not group_id:
        error = {"error": "group_id"}
        return make_response(jsonify(error), 500)
    error = dbhelpers.check_endpoint_info(request.args, ["group_id"])
    if error:
        return make_response(jsonify(error), 500)
    group_id = int(group_id)
    results = dbhelpers.run_procedures(
        "CALL single_group_get(?)", [group_id]
    )
    if (type(results) == list) and len(results) > 0:
        row = results[0]
        response = {
            "group_token": row[0],
            "banner_img": row[1],
            "description": row[2],
            "created_at": row[3],
            "name": row[4],
            "profile_img": row[5],
        }
        return make_response(jsonify(response), 200)
    else:
        error = {"error": "No data found"}
        return make_response(jsonify(error), 500)


@app.get("/api/group")
def group_members_get():
    group_id = request.args.get("group_id")
    if not group_id:
        error = {"error": "group_id"}
        return make_response(jsonify(error), 500)
    error = dbhelpers.check_endpoint_info(request.args, ["group_id"])
    if error:
        return make_response(jsonify(error), 500)
    results = dbhelpers.run_procedures("CALL group_member(?)", [group_id])
    if (type(results) == list) and len(results) > 0:
        response = []
        for row in results:
            member = {
                "name": row[0],
                "profile_picture": row[1],
            }
            response.append(member)
        return make_response(jsonify(response), 200)
    else:
        error = {"error": "No data found"}
        return make_response(jsonify(error), 500)



##message handlers


@app.get("/api/messages")
def return_messages():
    group_id = request.args.get("group_id")
    if not group_id:
        error = {"error": "group_id"}
        return make_response(jsonify(error), 500)
    error = dbhelpers.check_endpoint_info(request.args, ["group_id"])
    if error is not None:
        return make_response(jsonify(error), 500)
    results = dbhelpers.run_procedures("CALL messages_get(?)", [group_id])
    if isinstance(results, list) and len(results) > 0:
        response = [{"content": row[0], "created_at": row[1], "username" : row[2]} for row in results]
        return make_response(jsonify(response), 200)
    else:
        return make_response(jsonify("No messages found for the given group_id"), 200)



@app.post("/api/messages")
def message_post():
    group_id = int(request.args.get("group_id"))
    if not group_id:
        error = {"error": "group_id"}
        return make_response(jsonify(error), 500)
    member_id = int(request.args.get("member_id"))
    if not member_id:
        error = {"error": "member_id"}
        return make_response(jsonify(error), 500)
    error = dbhelpers.check_endpoint_info(request.json, ["content"])
    if error is not None:
        return make_response(jsonify(error), 500)
    results = dbhelpers.run_procedures("CALL messages_post(?, ?, ?)",[request.json.get("content"), member_id, group_id])
    if (type(results) == list):
        return make_response(jsonify("success"), 200)
    else:
        return make_response(jsonify("Sorry, an error occurred"), 500)

## friend handlers

@app.post('/api/friends')
def add_frind() :
    error = dbhelpers.check_endpoint_info(request.json ,["username" , "user_id"])
    if error is not None :
        return make_response(jsonify(error) , 500)
    results = dbhelpers.run_procedures("CALL add_friends_post(?,?)" , [request.json.get("username") , request.json.get("user_id")])
    if (type(results) == list) :
        return make_response(jsonify(results) , 200)
    else:
        return make_response(jsonify('an error occured while adding friend'))
    
@app.get("/api/friends")
def return_friends():
    user_id = request.args.get("user_id")
    if not user_id:
        error = {"error": "user_id"}
        return make_response(jsonify(error), 500)
    friend_id = request.args.get("friend_id")
    if not friend_id:
        error = {"error": "friend_id"}
        return make_response(jsonify(error), 500)
    error = dbhelpers.check_endpoint_info(request.args, ["user_id" , "friend_id"])
    if error is not None:
        return make_response(jsonify(error), 500)
    results = dbhelpers.run_procedures("CALL friend_get(? , ?)", [user_id, friend_id])
    if isinstance(results, list) and len(results) > 0:
        response = [{"username": row[0], "profile_img": row[1], "created_at" : row[2]} for row in results]
        return make_response(jsonify(response), 200)
    else:
        return make_response(jsonify("No messages found for the given group_id"), 200)



if dbcreds.production_mode == True:
    print("Running in production mode")
    app.run(debug=True)
else:
    from flask_cors import CORS

    CORS(app)
    print("Running in developer mode")
    app.run(debug=True)
