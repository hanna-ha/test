import dash
from dash import html, register_page, callback , _dash_renderer
from dash import  dcc, Input, Output,State, dash_table
import dash_bootstrap_components as dbc


import dash_mantine_components as dmc
from dash_iconify import DashIconify
_dash_renderer._set_react_version("18.2.0")

import pandas as pd
import numpy as np

import base64
import tempfile
import io

import plotly.graph_objects as go

# import scanpy as sc
# import matplotlib.pyplot as plt

# import matplotlib
# matplotlib.use("Agg")
# import pickle



dash.register_page(__name__ ,path='/preprocess')


# #################################################################################
# Upload h5 file 
# #################################################################################

# #################################################################################
# LAYOUT
# #################################################################################
file_name='test'

# layout = html.Div([
#     # Main Row with Sidebar and Main Content
#     dbc.Row([
#         # Sidebar
#         dbc.Col([
#             html.Br(),
#             html.H5("Upload H5 File", style={"text-align": "center"}),
#             html.Br(),
#             dcc.Upload(
#                 id="upload-counttable",
#                 children=html.Div([
#                     "Drag and Drop or ", html.A("Select File")
#                 ]),
#                 style={
#                     "borderWidth": "1px",
#                     "borderStyle": "dashed",
#                     "padding": "20px",
#                     "textAlign": "center",
#                     "margin": "10px",
#                 },
#             ),
#             html.Div(id="count-outmessage", style={"text-align": "center"}),
#         ], width=3, style={"background-color": "#f8f9fa", "min-height": "100vh", "overflowY": "auto"}),

#         # Main Content with Tabs
#         dbc.Col([
#             html.Br(),
#             dbc.Tabs([
#                 # Tab 1: Summary
#                 dbc.Tab(label="Summary", children=[
#                     dcc.Loading(html.Div([
#                         html.H4("Summary of Count Table", style={"text-align": "center"}),
#                         dash_table.DataTable(
#                             id="count-summary-table",
#                             columns=[
#                                 {"name": "Metric", "id": "metric"},
#                                 {"name": "Value", "id": "value"}
#                             ],
#                             style_table={"margin": "20px auto", "width": "65%"},
#                             style_cell={"textAlign": "center"},
#                             style_header={"fontWeight": "bold"},
#                         ),
#                         html.H4("Condition Table", style={"text-align": "center"}),
#                         html.Div(id="condition-table", style={"margin": "20px auto", "width": "65%"}),
#                     ]) ,
#                     ),
#                 ]),

#                 # Tab 2: Plots
#                 dbc.Tab(label="Scatter plot", children=[
#                     html.Div([
#                         dcc.Graph(id="scatter-plot", style={"margin": "20px auto", "width": "100%"}),
#                         # dcc.Graph(id="metrics-plot", style={"margin": "20px auto", "width": "100%"}),
#                     ])
#                 ]),
#                 dbc.Tab(label="metrics plot", children=[
#                     dcc.Loading(html.Div([
#                         dcc.Graph(id="metrics-plot", style={"margin": "20px auto", "width": "100%"}),
#                         html.Img(id="metrics-plot2", style={"margin": "20px auto", "width": "100%"}),
#                     ]),
#                     )
#                 ]),

#                 # Tab 3: QC
#                 dbc.Tab(label="QC", children=[
#                     dbc.Card([
#                         dbc.CardHeader("List of Genes for Filtering"),
#                         dbc.CardBody([
#                             dbc.Row([
#                                 dbc.Col([
#                                     dcc.Checklist(
#                                         id="qc-checkbox",
#                                         options=[
#                                             {"label": "  Human mito gene", "value": "hs_mito"},
#                                             {"label": "  Human Ribosomal gene", "value": "hs_ribo"},
#                                             {"label": "  Mouse mito gene", "value": "mm_mito"},
#                                             {"label": "  Mouse Ri8bosomal gene", "value": "mm_ribo"}
#                                         ],
#                                         value=[], persistence= True , 
#                                         style={"margin": "10px"}
#                                     )
#                                 ], width=6),
#                                 dbc.Col([
#                                     dcc.Upload(
#                                         id="qc-upload",
#                                         children=html.Div([
#                                             "Upload Gene List in csv   ", #html.A("Select File")
#                                         ]),
#                                         style={
#                                             "borderWidth": "1px",
#                                             "borderStyle": "dashed",
#                                             "padding": "20px",
#                                             "textAlign": "center",
#                                             "margin": "10px",
#                                         },
#                                     )
#                                 ], width=6),
#                             ]),
#                             html.Div([
#                                 dbc.Button("QC", id="qc-button", color="success", style={"margin-top": "20px"}),
#                             ], style={"text-align": "center"}),
#                         ])
#                     ], style={"margin": "20px"}),

#                     # Figures generated below
#                     dcc.Loading(dcc.Graph(id="qc-figures", style={"margin": "20px auto", "width": "100%"}), ), 
#                 ]),
#             ]),
#         ], width=9, style={"padding": "20px"})
#     ]),

#     # Store components for file data
#     # dcc.Store(id="stored-count-df"),
#     dcc.Store(id="uploaded-file-name"),
# ])

layout = html.Div([
    # Main Row with Sidebar and Main Content
    dbc.Row([
        # Sidebar (Narrower and styled with dmc)
        dbc.Col([ dmc.MantineProvider([
            dmc.Paper([
                dmc.Stack([
                    html.Br(),
                    dmc.Title("Upload H5 File", order=4, style={"textAlign": "center"}),  # Center align using style
                    html.Br(),
                    dmc.Group([
                        DashIconify(icon="bi:file-earmark-h5", width=30),
                        dmc.Text(f"{file_name} is ready to use", size="sm"),
                    ], align="center"),
                    html.Br(),
                ]),
            ], style={"background-color": "#f8f9fa", "min-height": "100vh", "padding": "10px"}),  ]),
        ], width=2),  # Narrower sidebar

        # Main Content with Tabs
        dbc.Col([
            html.Br(),
            dbc.Tabs([
                # Tab 1: Summary
                dbc.Tab(label="Summary", children=[
                    dcc.Loading(html.Div([
                        html.H4("Summary of Count Table", style={"text-align": "center"}),
                        dash_table.DataTable(
                            id="count-summary-table",
                            columns=[
                                {"name": "Metric", "id": "metric"},
                                {"name": "Value", "id": "value"}
                            ],
                            style_table={"margin": "20px auto", "width": "65%"},
                            style_cell={"textAlign": "center"},
                            style_header={"fontWeight": "bold"},
                        ),
                        html.H4("Condition Table", style={"text-align": "center"}),
                        html.Div(id="condition-table", style={"margin": "20px auto", "width": "65%"}),
                    ])),
                ]),

                # Tab 2: Plots
                dbc.Tab(label="Scatter plot", children=[
                    html.Div([
                        dcc.Graph(id="scatter-plot", style={"margin": "20px auto", "width": "100%"}),
                    ])
                ]),
                dbc.Tab(label="Metrics Plot", children=[
                    dcc.Loading(html.Div([
                        dcc.Graph(id="metrics-plot", style={"margin": "20px auto", "width": "100%"}),
                        html.Img(id="metrics-plot2", style={"margin": "20px auto", "width": "100%"}),
                    ])),
                ]),

                # Tab 3: QC
                dbc.Tab(label="QC", children=[
                    dbc.Card([
                        dbc.CardHeader("List of Genes for Filtering"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dcc.Checklist(
                                        id="qc-checkbox",
                                        options=[
                                            {"label": "  Human mito gene", "value": "hs_mito"},
                                            {"label": "  Human Ribosomal gene", "value": "hs_ribo"},
                                            {"label": "  Mouse mito gene", "value": "mm_mito"},
                                            {"label": "  Mouse Ribosomal gene", "value": "mm_ribo"}
                                        ],
                                        value=[], persistence=True,
                                        style={"margin": "10px"}
                                    )
                                ], width=6),
                                dbc.Col([
                                    dcc.Upload(
                                        id="qc-upload",
                                        children=html.Div([
                                            "Upload Gene List in csv   ",
                                        ]),
                                        style={
                                            "borderWidth": "1px",
                                            "borderStyle": "dashed",
                                            "padding": "20px",
                                            "textAlign": "center",
                                            "margin": "10px",
                                        },
                                    )
                                ], width=6),
                            ]),
                            html.Div([
                                dbc.Button("QC", id="qc-button", color="success", style={"margin-top": "20px"}),
                            ], style={"text-align": "center"}),
                        ])
                    ], style={"margin": "20px"}),

                    # Figures generated below
                    dcc.Loading(dcc.Graph(id="qc-figures", style={"margin": "20px auto", "width": "100%"})),
                ]),
            ]),
        ], width=10, style={"padding": "20px"})  # Main content takes up more space
    ]),

    # Store components for file data
    dcc.Store(id="uploaded-file-name"),
])

# #################################################################################
# Functions
# #################################################################################

# def serialize_df(df):
#     return base64.b64encode(pickle.dumps(df)).decode()




def parse_h5(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    # Use a temporary file to read the HDF file
    with tempfile.NamedTemporaryFile(suffix=".h5", delete=True) as temp_file:
        temp_file.write(decoded)
        temp_file.flush()  # Ensure all data is written to disk
        df = pd.read_hdf(temp_file.name, header=0, index_col=0)  # Read the HDF file into a DataFrame
    
    return df


def get_detected_count_and_per_read(df, thr ) :
    read_counts = []
    gene_detected_reads = []
    cellnames=[]
    # detected_gene_per_read_list = []

    for cell in df.columns:
        
        read_count=df[cell].sum()
        gene_detected_read=df[cell][df[cell]>int(thr)].shape[0]
        read_counts.append(read_count)
        gene_detected_reads.append(gene_detected_read)
        cellnames.append(cell)
        # detected_gene_per_read=gene_detected_read/read_count
        # detected_gene_per_read_list.append(detected_gene_per_read)
    
    return read_counts , gene_detected_reads ,cellnames

def calculate_qc_metrics(count_table, mito_genes=None, ribo_genes=None, custom_genes=None):

    # Transpose to cell-by-gene format for easier processing
    cell_metrics = pd.DataFrame(index=count_table.columns)

    # Calculate number of detected genes (non-zero counts per cell)
    cell_metrics["n_genes_by_counts"] = (count_table > 0).sum(axis=0)

    # Calculate total counts (sum of counts per cell)
    cell_metrics["total_counts"] = count_table.sum(axis=0)

    # Calculate mitochondrial gene percentage
    if mito_genes:
        mito_counts = count_table.loc[mito_genes].sum(axis=0)
        cell_metrics["pct_counts_mt"] = (mito_counts / cell_metrics["total_counts"]) * 100

    # Calculate ribosomal gene percentage
    if ribo_genes:
        ribo_counts = count_table.loc[ribo_genes].sum(axis=0)
        cell_metrics["pct_counts_ribo"] = (ribo_counts / cell_metrics["total_counts"]) * 100
    # Calculate ribosomal gene percentage
    if custom_genes:
        selected_gene_count = count_table.loc[custom_genes].sum(axis=0)
        cell_metrics["pct_counts_uploaded_genes"] = (selected_gene_count / cell_metrics["total_counts"]) * 100

    return cell_metrics


def create_violin_plot2(metrics_df):
    fig = go.Figure()
    for column in metrics_df.columns:
        fig.add_trace(go.Violin(
            y=metrics_df[column],
            name=column,
            box_visible=True,
            meanline_visible=True,
            jitter=0.4,
            points='all'
        ))
    fig.update_layout(
        title="QC Metrics Violin Plot",
        yaxis_title="Value",
        xaxis_title="Metric",
        violingap=0.4,
        height=600
    )
    return fig

# def create_violin_plot(adata, metrics=None):
#     fig = go.Figure()
#     if metrics is None : 
#     else :

#     for metric in metrics:
#         fig.add_trace(go.Violin(
#             y=adata.obs[metric],
#             name=metric,
#             box_visible=True,
#             meanline_visible=True,
#             jitter=0.4,
#             points='all'  # Show all points for better visualization
#         ))
#     fig.update_layout(
#         title="QC Metrics Violin Plot",
#         yaxis_title="Value",
#         xaxis_title="Metric",
#         violingap=0.4,  # Gap between violins
#         height=600
#     )
#     return fig

# #################################################################################
# Callbacks
# #################################################################################



@callback(
    Output("uploaded-file-name", "data"),  # Store the file name
    Output("count-outmessage", "children"),  # Display a message
    Output('upload-counttable', 'children'),
    Input("upload-counttable", "contents"),
    State("upload-counttable", "filename")
)
def handle_h5_upload(contents, filename):
    if contents is None:
        return None, "No file uploaded" , 'Drag and Drop or Select File'

    if not filename.endswith('.h5'):
        return None, "Invalid file format. Please upload an H5 file." , 'Invalid format'

    return filename, f"File uploaded successfully." , f'{filename}'

@callback(
    Output("count-summary-table", "data"),
    Output("condition-table", "children"),
    # Output("stored-count-df", "data"),
    Output("scatter-plot", "figure"),
    Output('metrics-plot' ,'figure'),
    # Output('metrics-plot2' ,'figure'),
    Input("upload-counttable", "contents"),
    State("upload-counttable", "filename")
)
def update_summary_table_and_scatter(contents, filename):
    if contents is None:
        return [], html.Div("No data"), {} , go.Figure() 

    try:
        # Parse the uploaded H5 file
        df = parse_h5(contents)
        # print(df)
        # df_json = df.to_json(orient="split")
        

        # Calculate metrics
        num_rows = len(df)
        num_columns = len(df.columns)
        rows_gt_one = (df.sum(axis=1) > 1).sum()
        condition_list = list(set([x.split('_')[0] for x in df.columns]))
        n_condition = len(condition_list)

        # Prepare summary table data
        summary_data = [
            {"metric": "Number of Cells", "value": num_columns},
            {"metric": "Number of Genes", "value": num_rows},
            {"metric": "Number of Detected Genes", "value": rows_gt_one},
            {"metric": "Number of Conditions", "value": n_condition},
        ]

        # Prepare condition table
        condition_table = pd.DataFrame(data={'List of Conditions': condition_list})
        condition_data = dash_table.DataTable(
            data=condition_table.to_dict('records'),
            columns=[{"name": i, "id": i} for i in condition_table.columns],
            page_size=10,
            style_table={'margin': '0 auto', 'width': '90%'},
            style_cell={'textAlign': 'center'},
        )

### Saturation plot 
        x_val , y_val ,cellname = get_detected_count_and_per_read(df, 1)


        # Determine x-axis label based on file name
        if "_read_count" in filename:
            x_axis_label = "Mean Reads"
        elif "_umi_count" in filename:
            x_axis_label = "Mean UMI" 
        else:
            x_axis_label = "Mean Reads"

        # Generate scatter plot
        scatter_fig = {
            "data": [
                {
                    "x": x_val ,
                    "y": y_val ,
                    "mode": "markers",
                    "marker": {"size": 8, "opacity": 0.7},
                    "text": cellname,  # Use the index as labels
                    "textposition": "top center",  # Position of the labels
                    "hoverinfo": "text+x+y",  # Show text, x, and y in hover
                }
            ],
            "layout": {
                "title": "Scatter Plot",
                "xaxis": {"title": x_axis_label},
                "yaxis": {"title": "# Detected genes"},
                "height": 400,
            },
        }
        

        qc_metrics = calculate_qc_metrics(df, mito_genes=None, ribo_genes=None, custom_genes=None)
        # adata=sc.AnnData(df.T)
        # sc.pp.calculate_qc_metrics(adata, percent_top=None, log1p=False, inplace=True)

        # # Create the violin plot
        # sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts'], jitter=0.4, multi_panel=True)

        # # Save the plot to a buffer and encode it as base64
        # buf = BytesIO()
        # plt.savefig(buf, format="png")
        # buf.seek(0)
        # encoded_image = base64.b64encode(buf.read()).decode('utf-8')
        # plt.savefig("debug_violin_plot.png")
        # buf.close()
        # plt.close()  # Close the plot to free memory
        # print(encoded_image[:100])
        # # buf.close()
    
 
        
        df_json = None

        return summary_data, condition_data, scatter_fig , create_violin_plot2(qc_metrics) 
        # return summary_data, condition_data, df_pickle, scatter_fig

    except Exception as e:
        return [], html.Div(f"Error processing file: {str(e)}"), {}  , go.Figure() 
    




@callback(
    Output('qc-figures', 'figure'),
    Input("upload-counttable", "contents"),
    Input('qc-checkbox', 'value'),
    Input('qc-upload', 'contents'),
    Input('qc-button', 'n_clicks'),
    State("upload-counttable", "filename")
)
def update_summary_table_and_scatter(contents, gene_check, gene_upload, n_click, fname):
    if contents is None:
        return go.Figure()  # Return an empty figure if no file is uploaded

    gene_file_path = {
        'hs_mito': 'dash_app/assets/hs_mito2.csv',
        'hs_ribo': 'dash_app/assets/hs_ribo.csv',
        'mm_mito': 'dash_app/assets/mm_mito.csv',
        'mm_ribo': 'dash_app/assets/mm_ribo.csv'
    }

    if n_click:
        print(f"qc_check: {gene_check}")

        try:
            # Parse the uploaded count table
            df = parse_h5(contents)

            mito, ribo, gene_to_filter = None, None, None

            # Case 1: Custom gene list uploaded
            if gene_upload:
                content_type, content_string = gene_upload.split(',')
                decoded = base64.b64decode(content_string)
                gene_to_filter = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                gene_to_filter = gene_to_filter.iloc[:,0].to_list()
                qc_metrics = calculate_qc_metrics(df, mito_genes=None, ribo_genes=None, custom_genes=gene_to_filter)

            # Case 2: Predefined gene sets selected
            elif gene_check:
                for g_to_check in gene_check:
                    print(f'g to check {g_to_check}')
                    if 'mito' in g_to_check:
                        mito=['MTRNR2L9' , 'MTRNR2L8'  , 'MTRNR2L13' , 'MTRNR2L3' ]
                    if 'ribo' in g_to_check:
                        ribo = pd.read_csv(gene_file_path[g_to_check])['Gene_Sym'].to_list()
                
                qc_metrics = calculate_qc_metrics(df, mito_genes=mito, ribo_genes=ribo, custom_genes=None)

            # Create the violin plot using the calculated metrics
            return create_violin_plot2(qc_metrics)

        except Exception as e:
            # Return an empty figure with a title for better UX in case of an error
            return go.Figure().update_layout(title=f"Error processing file: {str(e)}")

    else : 
    # If the button was not clicked, return an empty figure
        return go.Figure()
        