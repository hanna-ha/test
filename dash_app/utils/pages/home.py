import dash
from dash import register_page, dcc, html, callback, Input, Output ,State , dash_table, _dash_renderer , ctx


import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
_dash_renderer._set_react_version("18.2.0")

from dash.dependencies import ALL
import dash_uploader as du

import time
import random

from datetime import datetime
import os , base64
import glob





# ###################################################################################


# ###################################################################################

register_page(
    __name__,
    name='Home',
    top_nav=True,
    path='/'
)


# # ###################################################################################
# Layout
# # ###################################################################################


layout = dbc.Container([
    html.Br(),
    html.H1("Welcome to the TempoLinc Portal", style={'textAlign': 'center'}),
    html.Br(),

    # List avilable project in a table 
    dbc.Card([
        dbc.CardHeader("User Project List", style={"fontSize": "20px", "fontWeight": "bold"}),
        dbc.CardBody([
            html.Div(id="user-info-section", style={"fontSize": "18px"}), 
            html.Div(id="subfolders-table-section"),
        ])
    ]),

    # Data Upload/Selection Section
    dbc.Card([
        dbc.CardHeader("Load Your Data", style={"fontSize": "20px", "fontWeight": "bold"}),

        dbc.CardBody([
            html.P('Upload or select project'),
            html.Div(id="selection-status", style={"marginTop": "10px"}) , # Selection status message
      
        du.Upload(
        id="uploader",
        text="Drag & Drop Files Here or Click to Browse",
        filetypes=['csv', 'h5', 'gz', 'zip'],
        # max_file_size=1000,
        default_style={
            "width": "100%",
            "height": "80px",
            "border": "2px dashed #1971c2",
            "borderRadius": "10px",
            "textAlign": "center",
            # "paddingTop": "5px",
            "fontSize": "15px",
            "color": "#1971c2",
            "backgroundColor": "#f8f9fa"
        },
        upload_id=None,
   
    # upload_url="/custom-upload",  # Use the custom route
), 
    html.Div(id="upload-output"),  # Placeholder for upload status/output
    html.Br(),


            html.Br(),
            
            # Right box: Dropdown for selecting the project from uploaded data
            html.Div([
                html.H4('Select Project'),
                dcc.Dropdown(
                    id="project-dropdown",
                    options=[],  # Placeholder, will be updated dynamically
                    placeholder="Select a project",
                    style={"marginTop": "10px"}
                )
            ], style={"marginTop": "20px"})
        ])
    ], style={"marginTop": "20px", "padding": "10px"}),
    html.Br(),



    # User Info Section
    dbc.Card([
        dbc.CardHeader("User Info", style={"fontSize": "20px", "fontWeight": "bold"}),
        # dbc.CardBody([
        #     html.Div(id="user-info-section", style={"fontSize": "18px"})
        # ])
    ], style={"marginTop": "20px", "padding": "10px"}),


    dcc.Store(id="home-selected-project-store", storage_type="session"),  # Stores selected project
    dcc.Store(id="home-n-click-store", storage_type="session") ,
    dcc.Store(id='most-recent-action-store', data=None),
])


# #################################################################################
# Callback
# #################################################################################



# Callback for refreshing project list after upload
@callback(
    [Output("subfolders-table-section", "children"),
     Output("project-dropdown", "options")],
    [Input("userpath-store", "data")],  # Triggered when data upload is done
    prevent_initial_call=True
)
def refresh_projects_after_upload(folder_path):
    # sleep(2)

    if not os.path.exists(folder_path):
        return dbc.Alert("No uploaded projects found.", color="warning"), []

    subfolders = [
        (f, datetime.fromtimestamp(os.path.getctime(os.path.join(folder_path, f))).strftime('%Y-%m-%d'))
        for f in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, f))
    ]

    if not subfolders:
        return dbc.Alert("No uploaded projects found.", color="warning"), []

    # Generate table rows
    table = dbc.Table(
        [
            html.Thead(html.Tr([ html.Th("Project"), html.Th("Date")])),
            html.Tbody([
                html.Tr([

                    html.Td(name),
                    html.Td(date)
                ]) for name, date in subfolders
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        style={"width": "60%", "margin": "0 auto"}
    )

    # Generate dropdown options
    dropdown_options = [{"label": name, "value": name} for name, _ in subfolders]

    return table, dropdown_options



@callback(
    [Output("selection-status", "children"),
     Output("user-info-section", "children"),
     Output('user-file-store', 'data'),
     Output('home-n-click-store', 'data'),  # Update n_click store
     Output('home-selected-project-store', 'data'),  # Update selected_project store
     Output('most-recent-action-store', 'data')],  # Update most recent action store
    [Input("userpath-store", "data"),
     Input("project-dropdown", "value"),
     Input("upload-data-button", "n_clicks")],
    [State('home-n-click-store', 'data'),  # Current n_click value
     State('home-selected-project-store', 'data'),  # Current selected_project value
     State('most-recent-action-store', 'data')],  # Current most recent action
    # prevent_initial_call=True
)
def handle_project_selection(userpath, selected_project, n_click, stored_n_click, stored_selected_project, stored_most_recent_action):
    print(f"userpath, selected_project, n_click: {userpath, selected_project, n_click}")
    print(f"stored_n_click, stored_selected_project, stored_most_recent_action: {stored_n_click, stored_selected_project, stored_most_recent_action}")
    
    username = userpath.replace('/data/reads/', '')


    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    print(f"Triggered by: {triggered_id}")
   

    # Determine the most recent action
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    if triggered_id == "project-dropdown":
        most_recent_action = {"action": "dropdown", "data": selected_project}
    elif triggered_id == "upload-data-button":
        most_recent_action = {"action": "upload", "data": n_click}
    else:
        most_recent_action = stored_most_recent_action


    print(f"nost recent {most_recent_action}")
    if most_recent_action : 
        # Use the most recent action to determine what to display
        if most_recent_action["action"] == "dropdown":
            selected_project = most_recent_action["data"]
            if not selected_project:
                return "", f"Hi {username}", "", stored_n_click, stored_selected_project, most_recent_action

            status_message = dbc.Alert(f"✅ Data '{selected_project}' is loaded. You can use this data in the app.", color="success")

            user_message = html.Div([
                html.P(f"Hi {username}, now you can explore the functionality on TempoLinc Portal."),
                html.P(f"Selected data: {selected_project}", style={"fontWeight": "bold"})
            ])
            return status_message, user_message, selected_project, stored_n_click, selected_project, most_recent_action

        elif most_recent_action["action"] == "upload":
            upload_folder = f"dash_app/assets/user_upload_test"  # Create folder if not available

            try:
                # Get list of directories in the upload folder
                folders = [f for f in os.listdir(upload_folder) if os.path.isdir(os.path.join(upload_folder, f))]
                if not folders:
                    return dbc.Alert("No upload data found.", color="warning"), "", stored_n_click, stored_selected_project, most_recent_action

                # Get the most recent folder (based on modification time)
                most_recent_folder = max(folders, key=lambda folder: os.path.getmtime(os.path.join(upload_folder, folder)))

                # Get the most recent file in the most recent folder
                folder_path = os.path.join(upload_folder, most_recent_folder)
                files = glob.glob(os.path.join(folder_path, '*'))  # List all files in the folder

                if not files:
                    return dbc.Alert(f"No files found in folder {most_recent_folder}.", color="warning"), "", stored_n_click, stored_selected_project, most_recent_action

                most_recent_file = max(files, key=os.path.getmtime)  # Get the most recent file based on modification time

                # Prepare status and user info messages
                status_message = dbc.Alert(f"✅ Data from File: {os.path.basename(most_recent_file)} is loaded. You can use this data in the app.", color="success")

                user_message = html.Div([
                    html.P(f"Hi {username}, now you can explore the functionality on TempoLinc Portal."),
                    html.P(f"Selected data: {os.path.basename(most_recent_file)}", style={"fontWeight": "bold"})
                ])

            except Exception as e:
                return dbc.Alert(f"An error occurred while loading the data: {str(e)}", color="danger"), "", stored_n_click, stored_selected_project, most_recent_action

            return status_message, user_message, os.path.basename(most_recent_file), n_click, stored_selected_project, most_recent_action

        else:
            # No action triggered, use stored values
            return "", f"Hi {username}", "", stored_n_click, stored_selected_project, most_recent_action
    
    
@callback(
    Output("upload-output", "children"),
    Input("uploader", "isCompleted"),
    State("uploader", "fileNames"),
    State("uploader", "upload_id"),
    prevent_initial_call=True
)
def handle_upload(is_completed, file_names, upload_id):
    print(f"is completeed {is_completed }")
    print(f"fil name { file_names}")
    print(f"upload id {upload_id}")


    if is_completed:
        if file_names:
            return html.Div([
                html.P(f"Uploaded files: {', '.join(file_names)}"),
                html.P(f"Upload ID: {upload_id}"),
                html.P("Files have been successfully uploaded!"),
            ])
        else:
            return html.Div("No files were uploaded.")
    return html.Div("Upload in progress...")

