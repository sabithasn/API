from flask import Blueprint, render_template, redirect, url_for, request, session
import pandas as pd

def load_campuses_and_departments():
    return pd.read_csv("data/campus_departments.csv")

routes = Blueprint("routes", __name__)

def load_users():
    users = pd.read_csv("data/alumniData.csv")  # Load the CSV file
    users.columns = users.columns.str.strip()  # Remove leading/trailing spaces
    print("Cleaned Columns:", users.columns)  # Debug cleaned column names
    return users
    #return pd.read_csv("data/alumniData.csv")  # Update CSV name

def load_roles():
    return pd.read_csv("data/roles.csv")

@routes.route("/test")
def test_form():
    # Provide an example entry dictionary
    entry = {"profile_id": 2099126}
    return render_template("test.html", entry=entry)


@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Load users and validate
        users = load_users()
        user = users[(users["profile_id"] == int(username)) & (users["profile_id"] == int(password))]
        
        if not user.empty:  # Valid credentials
            session["profile_id"] = user.iloc[0]["profile_id"]
            session["role"] = user.iloc[0]["Role"]
            session["campus"] = user.iloc[0]["campus"]
            session["department"] = user.iloc[0]["department"]
            print("Role set in session:", session["role"])  # Debugging
            if session["role"] == "Faculty":
                session["campus"] = user.iloc[0]["campus"]
                session["department"] = user.iloc[0]["department"]

                # Load all alumni records and filter by the faculty's campus and department
                data = load_users()
                filtered_data = data[(data["campus"] == session["campus"]) & (data["department"] == session["department"])]

                # Choose the first alumni record's profile_id as the default entry
                default_profile_id = filtered_data["profile_id"].iloc[0]

                # Redirect faculty users to the individual alumni entry view
                return redirect(url_for("routes.department_entry", campus=session["campus"], department=session["department"], profile_id=default_profile_id))
            elif session["role"] == "Admin":
                return redirect(url_for("routes.admin_dashboard"))
            elif session["role"] == "Alumni":
                return redirect(url_for("routes.alumni_dashboard"))
            else:
                print("Debug: Invalid role found, redirecting to login")
                return redirect(url_for("routes.login"))
            #return redirect(url_for("routes.faculty_dashboard"))  # Redirect for valid login
        else:  # Invalid credentials
            print("Invalid credentials")  # Debugging
            return "Invalid Profile ID", 401  # Unauthorized

    return render_template("login.html")  # Default for GET request

@routes.route('/department/<campus>/<department>/<int:profile_id>')
def department_entry(campus, department, profile_id):
    data = load_users()  # Load all alumni data
    filtered_data = data[(data["campus"] == campus) & (data["department"] == department)]

    # Get the current alumni entry
    entry = filtered_data[filtered_data["profile_id"] == profile_id].iloc[0].to_dict()

    # Find the next profile ID dynamically
    profile_ids = filtered_data["profile_id"].tolist()
    current_index = profile_ids.index(profile_id) if profile_id in profile_ids else -1
    next_id = profile_ids[current_index + 1] if current_index + 1 < len(profile_ids) else profile_ids[0]

    return render_template("department_entry.html", campus=campus, department=department, entry=entry, next_id=next_id)

@routes.route('/update_alumni/<int:profile_id>', methods=["POST"])
def update_alumni(profile_id):
    print("updated reached")
    data = load_users()  # Load the CSV file

    # Ensure profile_id is used correctly
    data.loc[data["profile_id"] == profile_id, "name"] = request.form["name"]
    data.loc[data["profile_id"] == profile_id, "email"] = request.form["email"]

    # Save updated data back to CSV
    data.to_csv("data/alumniData.csv", index=False)
    print("updated file")
    # Redirect back to the department entry view using profile_id
    return redirect(url_for('routes.department_entry',
                            campus=session["campus"],
                            department=session["department"],
                            profile_id=profile_id))

@routes.route("/faculty_dashboard")
def faculty_dashboard():
    if "role" in session:
        print("Role found in session:", session["role"])
    else:
        print("Role not found in session")  # Debugging missing session key
    #print("Session Data:", session)  # Debug session contents
    #print("Current Role:", session.get("role"))  # Debug role from session
    #print("Current Campus:", session.get("campus"))  # Debug campus from session
    #print("Current Department:", session.get("department"))  # Debug department from session

    users = load_users()
    
    filtered_data = users[(users["department"] == session["department"]) & (users["campus"] == session["campus"])]
    #print("Filtered Data (First 5 Rows):")
    #print(filtered_data.head())  # Debug filtered results

    return render_template("dashboard.html", users=filtered_data.to_dict(orient="records"), role="Faculty")

@routes.route("/campus/<campus>")
def campus(campus):
    if not user.empty:  # Valid login
        session["role"] = user.iloc[0]["Role"]
        session["campus"] = user.iloc[0]["campus"]  # Assign campus
        session["department"] = user.iloc[0]["department"]  # Assign department

        print("Session role:", session.get("role"))  # Debug role storage
        print("Session campus:", session.get("campus"))  # Debug campus storage
        print("Session department:", session.get("department"))  # Debug department storage

    if "role" in session:
        print("Role found in session:", session["role"])
    else:
        print("Role not found in session")  # Debugging missing session key
    print("Selected Campus:", campus)  # Debug campus name

    campus_data = load_campuses_and_departments()
    print("Loaded Campus and Department Data (First 5 Rows):")
    print(campus_data.head())  # Debug campus data

    departments = campus_data[campus_data["campus_name"] == campus]["department_name"].unique()
    print("Filtered Departments for Campus:", departments)  # Debug filtered departments

    return render_template("departments.html", campus=campus, departments=departments)

@routes.route('/department/<campus>/<department>')
def department_data(campus, department):
    # Use session variables to filter data
    if "role" in session and session["role"] == "Faculty":
        print("Session Campus:", session["campus"])
        print("Session Department:", session["department"])
        users = load_users()
        filtered_data = users[
            (users["campus"] == campus) & (users["department"] == department)
        ]
        return render_template("dashboard.html", users=filtered_data.to_dict(orient="records"), role="Faculty")
    else:
        return redirect(url_for("routes.login"))

@routes.route("/dashboard")
def dashboard():
    if "role" in session:
        print("Role found in session:", session["role"])
    else:
        print("Role not found in session")  # Debugging missing session key
    if "role" not in session:
        return redirect(url_for("routes.login"))  # Redirect if user isn't logged in
    
    users = load_users()
    roles = load_roles()  # Load the roles.csv file
    role_id = session["role"]  # Retrieve role_id from the session

    # Map role_id to the corresponding role name
    role_name = roles.loc[roles["role_id"] == int(role_id), "role_name"].values[0]

    print("Mapped Role Name:", role_name)  # Debugging - Check the role name

    # Filter data based on the mapped role name
    filtered_data = users if role_name == "Admin" else users[users["Role"] == role_name]

    print("Filtered Data (First 5 Rows):")
    print(filtered_data.head())  # Debugging - Check filtered results

    return render_template("dashboard.html", users=filtered_data.to_dict(orient="records"), role=role_name)

@routes.route("/logout")
def logout():
    session.pop("role", None)  # Remove session data
    return redirect(url_for("routes.login"))