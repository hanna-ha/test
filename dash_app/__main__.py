import dash
from dash import html, dcc,callback, Input,  Output, State , _dash_renderer
import dash_bootstrap_components as dbc

import dash_uploader as du
# import dash_mantine_components as dmc
from dash_iconify import DashIconify
# _dash_renderer._set_react_version("18.2.0")



# Protect routes
from flask_login.utils import login_required
from flask import session
import pandas as pd
import os 






###################################################################################



###################################################################################


# from dash_uploader.http_request_handler import BaseHttpRequestHandler
# from flask import request

# class CustomHttpRequestHandler(BaseHttpRequestHandler):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def post_before(self):
#         print("\n[UPLOAD DEBUG] Incoming POST request:")
#         print("Headers:", request.headers)
#         print("Form Data:", request.form)
#         print("Files:", request.files)
#         print("Request Path:", request.path)

#     def post(self):
#         self.post_before()
#         returnvalue = super().post()
#         self.post_after()
#         return returnvalue

#     def post_after(self):
#         print("[UPLOAD DEBUG] Post-upload processing done.")

#     def get_before(self):
#         print("\n[UPLOAD DEBUG] Incoming GET request:")
#         print("Request Path:", request.path)
    
#     def get(self):
#         self.get_before()
#         returnvalue = super().get()
#         self.get_after()
#         return returnvalue

#     def get_after(self):
#         print("[UPLOAD DEBUG] GET request processed.")


# Creating the application
def create_dash_application(flask_app, local=False):

    # If local the app is being run for local development!! (no relative imports)
    if local:
        print('Running Locally')
        dash_app = dash.Dash(
            __name__,
            use_pages=True,
            pages_folder='utils', 
            # url_base_pathname='/',
            url_base_pathname='/app/',
            prevent_initial_callbacks=True, # Stops the initial call, ie prevents from running the callback when the layout is loaded into the web browser
            suppress_callback_exceptions=True, # Suppresses app errors from showing up
            external_stylesheets=[dbc.themes.BOOTSTRAP])
        
        

    else:
        print('Not running locally')
        # Initial app declaration, usepages true (THIS IS THE FLASK IMPLEMENTATION)
        dash_app = dash.Dash(
            # Declare server
            
            server=flask_app,
            # Base pathname
            name='DashApp',
            assets_folder='dash_app/assets',
        
            url_base_pathname='/app/', # this sets the requests pathname prefix as well 
            use_pages=True, 
            pages_folder='dash_app/utils', 
            prevent_initial_callbacks=True,
            suppress_callback_exceptions=True,
            external_stylesheets=[dbc.themes.BOOTSTRAP])#suppress_callback_exceptions=True

    try : 
        # du.configure_upload(dash_app, "/home/hanna/dash_upload/", use_upload_id=True,  upload_api="API/resumable")
        UPLOAD_FOLDER_ROOT = "dash_app/assets/user_upload_test"  # Set your upload folder

        if not os.path.exists(UPLOAD_FOLDER_ROOT):
            os.makedirs(UPLOAD_FOLDER_ROOT)
        # du.configure_upload(dash_app, f"/home/hanna/dash_upload/" , use_upload_id=True,  upload_api="API/resumable") 
        du.configure_upload(
            dash_app,
            UPLOAD_FOLDER_ROOT,
            use_upload_id=True,

            upload_api="/API/resumable",  # Ensures the correct upload endpoint
            # http_request_handler=CustomHttpRequestHandler
        )


                
        print('done ')

        print("Upload route:", dash_app.server.url_map)

        print("Available Routes:")
        for rule in dash_app.server.url_map.iter_rules():
            print(rule)   

  
    except Exception as E : 
        return(E)

    # Navigation Bar
    # Define the logo with fixed width
    logo = html.Img( 
        src=dash_app.get_asset_url('images/BioSpyderLogoMidTM.png'),
        style={'height': '85%', 'width': '100%'}  # Set a fixed width for the logo
    )

    # Logo container
    logo_container = html.Div(
        logo,
        style={'flex': '0 0 150px'},  # The logo will neither grow nor shrink accoring to the resizing of the app
        className="d-flex align-items-center"
    )

    # Function for creating the navigation bar item
    def create_navitem(label, href, margin="mx-3"):  # Increase margin with mx-3 (margin on the x-axis) 
        return dbc.NavItem(dbc.NavLink(label, href=href), className=margin)
        
    # Define the dropdown menus with increased left and right margin
    dropdown_menu_style = {'marginLeft': '1rem', 'marginRight': '1rem'}

    # # QC dropdown - Dropdown to include all sections of the QC. This will directly go into the app
    tool_dropdown = dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Convert file format", href="/app/tool1"),
                dbc.DropdownMenuItem("High complex filtering", href="/app/fi"),
                dbc.DropdownMenuItem("tool2", href="/app/tool2"),
                dbc.DropdownMenuItem("tool2", href="/app/tool2"),
                dbc.DropdownMenuItem("tool3", href="/app/tool3"),
                dbc.DropdownMenuItem("tool4", href="/app/tool4"),

            ],
            nav=True, # Used as a navigation elment
            in_navbar=True,
            label="Additional Tools",
            style=dropdown_menu_style,
        )
    
        # # QC dropdown - Dropdown to include all sections of the QC. This will directly go into the app
    umapdropdown = dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Pre-Computed", href="/app/pre_umap"),
                dbc.DropdownMenuItem("Custom", href="/app/custom_umap"),
                dbc.DropdownMenuItem("Request Large-Scale Data", href="/app/urequest"),


            ],
            nav=True, # Used as a navigation elment
            in_navbar=True,
            label="Cell Clustering",
            style=dropdown_menu_style,
        )
    
            # # QC dropdown - Dropdown to include all sections of the QC. This will directly go into the app
    analaysis_dropdown = dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Cell Type Annotation", href="/app/analysis1"),
                dbc.DropdownMenuItem("Differential Expression", href="/app/analysis2"),
                dbc.DropdownMenuItem("Trajectory Analysis", href="/app/analysis3"),
                dbc.DropdownMenuItem("Gene Set Enrichment", href="/app/analysis4"),

            ],
            nav=True, # Used as a navigation elment
            in_navbar=True,
            label="Advanced Analysis",
            style=dropdown_menu_style,
        )
    





###################################################################################


###################################################################################

    # Setting layout based on the access level of the user
    def serve_layout():
        # Selecting the pages to be shown based on the stored data from the session - Checks if the value alloted to the user is true/false. Keeping default false
        # show_qc = session.get('qc_pages', False)
        # show_ssg = session.get('ssg', False)

        # Creating a list to hold the default nav_items - available for all users
        nav_items_list = [
            # create_navitem("Home", "/app/home"),

            dbc.NavItem(dbc.NavLink([DashIconify(icon="mdi:home", width=20, height=20), " Home"], href="/app/")),
            create_navitem("UMAP Visualization", "/app/umap"),
            umapdropdown,
            analaysis_dropdown,
            create_navitem("Upload Files", "/app/preprocess"),
            # create_navitem("Quality Control", "/app/qc"),
            tool_dropdown
        ]


        # For running local
        if local:
            # Getting the username and userpath for reads directory since there is no user details to find from flask
            username = 'user' 

            # # Tool dropdown for local app - Different from flask server as the page paths are different
            tool_dropdown_local = dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Convert file format", href="/app/tool1"),
                    dbc.DropdownMenuItem("tool2", href="/app/tool2"),

                ],
                nav=True, # Used as a navigation elment
                in_navbar=True,
                label="Tools",
                style=dropdown_menu_style,
            )
            
            # The nav_list will contain everything for local run
            nav_items_list = [
                # create_navitem("Home", "/app/home"),
                dbc.NavItem(dbc.NavLink([DashIconify(icon="mdi:home", width=20, height=20), " Home"], href="/app/")),
                create_navitem("Preprocessing", "/app/preprocess"),
                # create_navitem("UMAP analysis", "/app/umap"),
                umapdropdown,
                create_navitem("Cluster Annotation", "/app/annotation"),
                analaysis_dropdown,

                # create_navitem("Quality Control", "/app/qc"),
                tool_dropdown,
            ]

        # Define the navbar based on the user based generated list
        nav_items = dbc.Navbar(
            dbc.Container(
                [
                    # Navbar toggler for smaller screens - refer callback
                    dbc.NavbarToggler(id="navbar-toggler"), 
                    
                    # Collapsible part of the navbar which contains navigation items
                    dbc.Collapse(
                        # Navigation items wrapped in a Nav component
                        dbc.Nav(
                            nav_items_list,
                            # Class to center the navigation items and allow them to grow within the navbar
                            className="justify-content-center flex-grow-1",
                            navbar=True,
                        ),
                        id="navbar-collapse",
                        navbar=True,
                        is_open=False,  # Initially, the collapsible part is not open (for smaller screens)
                    ),
                    
                ],
                fluid=True,  # The container takes the full width of the parent
            ),
            # color="dark",  # Set the color of the navbar
            # dark=True,     # Dark theme 
            style={"backgroundColor": "#f8f9fa"}, 
        )

        # Getting the username and userpath - flask run
        username = session.get('username', 'user') 

        if local:
            # Getting the username and userpath for reads directory since there is no user details to find from flask
            # username = 'user' 
            username='hanna_umap_path_test'
            


        # Define the dropdown menus with increased right margin for the user dropdown
        dropdown_menu_style_user = { 'marginRight': '70px'} # 'marginLeft': '1rem' ,

        # Just a fun way of seeing the user name before logging out
        user_dropdown = dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem(f'Hello {username}' , id="user-display"),
                dbc.DropdownMenuItem('Logout', id='logout-button'),
            ],
            nav=True, # Used as a navigation elment
            in_navbar=True,
            label= username,
            style=dropdown_menu_style_user,
        )


        user_items = dbc.Navbar(
            dbc.Container(
                [
                    # Navbar toggler for smaller screens
                    dbc.NavbarToggler(id="user-navbar-toggler"),
                    # Collapsible part of the navbar which contains navigation items
                    dbc.Collapse(
                        # Navigation items wrapped in a Nav component
                        dbc.Nav(
                            [DashIconify(icon="mdi:user-circle-outline", width=20, height=44),  # Icon before the user dropdown
                            user_dropdown],
                            # Class to center the navigation items and allow them to grow within the navbar
                            className="ms-auto",
                            navbar=True,
                        ),
                        id="user-navbar-collapse",
                        navbar=True,
                        is_open=False,  # Initially, the collapsible part is not open (for smaller screens)
                    ),  
                ],
                fluid=True,  # The container takes the full width of the parent
            ),
            # color="dark",  # Set the color of the navbar
            style={"backgroundColor": "#f8f9fa"}, 
            # dark=True,     # Dark theme 
        )

    
        # Define the navbar with three sections - Admin
        navbar = dbc.Navbar(
            dbc.Container(
                [
                    logo_container,  # Left section
                    nav_items,       # Center section
                    user_items,      # Right section (user)
                ],
                fluid=True,
                style={'display': 'flex'}
            ),
            # color="dark",
            # dark=True,
            style={"backgroundColor": "#f8f9fa"}, 
        )

        return html.Div([
            navbar,
            dash.page_container,
            # The updated data will be stored on these dcc.Store components on the upload data page and is called on all pages, regardless if they are used or not, to ensure that the/
            # data is persistent across the pages of the app
            # dcc.Store(id='stored-count-df', storage_type='memory'), # Stores gene count data

            #UMAP page
            dcc.Store(id="uploaded-file-name" , storage_type='session'),
            dcc.Store(id="userpath-store" , storage_type='session'),
            dcc.Store(id='user-file-store' , storage_type='session'),
            dcc.Store(id='custom-path-store'  , storage_type='session'),
            dcc.Store(id='persistent-inputs', storage_type='session'),  # For persistent inputs
            dcc.Store(id='persistent-tab2-content', storage_type='session'),  # For tab2-content persistence
            dcc.Store(id='persistent-custom-results-content', storage_type='session'),  # For tab2-content persistence
            dcc.Store(id='custom-request-data', storage_type='session'), 




            dcc.Location(id='url', refresh=False),
            dcc.Location(id='logout_location')
        ])

    dash_app.layout = serve_layout

###################################################################################


###################################################################################

    # Callback for logging out!
    @callback(
        Output('logout_location', 'href'),
        Input('logout-button', 'n_clicks')
    )
    def logout(click):
        if click:
            return '/logout'

    # Callback to enable or disable navbar collapse
    # On smaller screens, clicking navbar toggler opens and closes navbar  
    @callback(
        Output("navbar-collapse", "is_open"),
        [Input("navbar-toggler", "n_clicks")],
        [State("navbar-collapse", "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open
    
    # Callback to enable or disable navbar collapse on the users navbar (user name and logout)
    @callback(
        Output("user-navbar-collapse", "is_open"),
        [Input("user-navbar-toggler", "n_clicks")],
        [State("user-navbar-collapse", "is_open")],
    )
    def toggle_user_navbar_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    # Callback to store username 
    @callback(
        Output("userpath-store", "data"),
        Input("user-display", "children")  # Trigger when the user info is displayed
    )
    def store_username(display_text):
        # Extract the username (assuming "Hello username" format)
        username = display_text.replace("Hello ", "").strip()
        userpath=f'/data/reads/{username}'
        return userpath
    

    # Code to protect all routes inside dash app!!! (only needed if running inside flask) - Only runs if logged in
    if not local:
        for view_function in dash_app.server.view_functions:
            # If it has 'app' in front of it
            if view_function.startswith(dash_app.config.url_base_pathname):
                dash_app.server.view_functions[view_function] = login_required(dash_app.server.view_functions[view_function])


    

    return dash_app


        

###################################################################################


###################################################################################
 
# Run dash_app
if __name__ == '__main__':
    app = create_dash_application(__name__, local=True)

 
    app.run_server(port=4414, host='192.168.168.60' , debug=True) # , debug=True
