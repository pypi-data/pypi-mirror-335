import warnings
import io
import os
import subprocess
import pandas as pd
import numpy as np
import seaborn as sns
import ipywidgets as wd
from matplotlib import pyplot as plt
from IPython.display import display, clear_output, HTML
from pandas.io.formats.format import save_to_buffer
# from pyschare.constants import *
# from pyschare.data_functions import *

warnings.filterwarnings("ignore", message="The figure layout has changed to tight")
#constants.py

DPATH: str = 'gs://fc-secure-98d62246-b3af-4e4f-83d9-dac7af979d38/MainTableDatasetsWidgets.csv'
MAIN_TABLE: str = 'MainTableDatasets.csv'
MAIN_TABLE_VAR: str = 'dataset'
MAIN_TITLE: str = 'dataset_title'

visual_helper_text= "<p>Use the dropdown menus to select a dataset and configure your plot parameters.</p><ul><li><strong>Bar, count, box, boxen, strip, swarm, and violin plots</strong> typically require a categorical variable on the X-axis (or hue) and a numeric variable on the Y-axis; see the <a href='https://seaborn.pydata.org/tutorial/categorical.html' target='_blank'>categorical tutorial</a> for details.</li><li><strong>Scatter and line plots</strong> call for numeric variables on both axes (e.g., time vs. measurement); refer to the <a href='https://seaborn.pydata.org/tutorial/relational.html' target='_blank'> relational tutorial</a>.</li><li><strong>Histograms</strong> typically need a single numeric variable on the X-axis and are described in the <a href='https://seaborn.pydata.org/tutorial/distributions.html' target='_blank'> distributions tutorial</a>.</li></ul><p>Use <strong>“hue”</strong> to differentiate categories by color, <strong>“style”</strong> to vary markers or lines, and <strong>“size”</strong> to scale markers based on another variable. The <strong>“col” and “row”</strong> options create subplots (facets) for comparison across categories, while the <strong>“multiple”</strong> parameter (e.g., 'dodge,' 'stack,' 'fill') manages overlapping data displays. Once the plot type and settings are selected, click <strong>“Show Plot”</strong> to visualize the results.</p>"
select_helper_text = "<p>To view the dataset, use the <strong>Select Dataset</strong> dropdown and click the <strong>Show Data</strong> button. To save the displayed data, click the <strong>Save Data</strong> button. The confirmation that where data is saved will be shown below the Save Data button.</p><p> To clear both the confirmation message and the displayed data table, click the <strong>Clear Output</strong> button.</p>"

subset_helper_text = "<p>Use the <strong>Select Dataset</strong> dropdown to choose a dataset. The available variables will be dynamically populated when you select options in the <strong>Select Variables</strong> dropdown. After selecting the desired variables from the <strong>Select Variables</strong> dropdown, you may visualize the data by clicking the <strong>Show Data</strong> button. This will display the first few rows of the specific columns selected in the output area below.</p>     <p>To save the displayed data, click the <strong>Save Data</strong> button. This action will store the selected data in your bucket and confirm the successful operation in the output area. Please make sure you have made selections in both the dataset and variables dropdowns before attempting to save.</p>"


gemini_helper_text= "<p>Use <strong>Gemini Assistant</strong> to launch a simple Q&A chat window to get assistance with writing your data analysis code. The chat interface is powered by the Gemini model and is designed to answer questions related to assisting novice coders with writing analysis code. Type your question in the box and click the <strong>Generate</strong> button to call the model and generate an output.</p><p></p><p></p><p><strong>Note:</strong> while the data you send through this tool and data sent back are protected under Terra's Enterprise Google Cloud permissions, and are not reused by Google for future model training, we advise not sending any sensitive information (e.g. PII or PHI) through the model. Sticking to general questions or inserting dummy variable names to your questions are good practices to ensure the privacy of your data. </p>"

data_explore_helper_text = f"""<p>This widget allows you to explore and manipulate datasets. Follow the steps below to work with the data:</p>

    <ol>
        <li>
            <strong>Selecting a Dataset:</strong>
            <p>
                Use the "Select Dataset" dropdown menu to choose the dataset you want to work with. Click on the dropdown to see a list of available datasets and select your choice.
            </p>
        </li>

        <li>
            <strong>Selecting Variables:</strong>
            <p>
                After selecting a dataset, the "Select Variable" dropdown menu will populate with a list of variables available within that dataset.
                Choose the variables from the "Select Variable" dropdown you want to analyze. You can select multiple variables from this dropdown.
                (<em>Note:</em> If you do not select any variables, actions will be applied to all variables).
            </p>
        </li>

        <li>
            <strong>Viewing Data:</strong>
            <p>
                To view the first few rows of the selected dataset or the selected variables, click the "Show Data" button. The results will be displayed in the output area below the widget.
            </p>
        </li>

        <li>
            <strong>Describing Data:</strong>
            <p>
                To view summary statistics (like mean, median, standard deviation) for the selected variables, click the "Describe Data" button.
                The summary statistics will be shown in the output area below the widget.
                If you haven't selected any variables, statistics for all variables in the dataset will be displayed.
            </p>
        </li>

        <li>
            <strong>Saving Data:</strong>
            <p>
                To save the displayed data (either the entire dataset or the subset of selected variables), click the "Save Data" button.
                A confirmation message, including the location where the data is saved, will be displayed in the output area below the buttons.
                <br>
                <em>Note:</em> Ensure you have selected a dataset and, if applicable, variables before clicking "Save Data."
            </p>
        </li>

        <li>
            <strong>Clearing Output:</strong>
            <p>
                To clear both the confirmation message (from saving) and the displayed data table or statistics in the output area, click the "Clear Output" button.
            </p>
        </li>
    </ol>
"""

calculate_helper_text= f"""<p>This widget allows you to create various types of plots using your selected dataset. Follow the steps below to build your visualization:</p>

    <ol>
        <li>
            <strong>Choose a Dataset:</strong>
            <p>
                Begin by selecting a dataset from the "Select Dataset" dropdown menu. Click the dropdown to see the list of available datasets and choose the one you want to use.
            </p>
        </li>

        <li>
            <strong>Select a Plot Type:</strong>
            <p>
                Next, choose the type of plot you want to create from the "Select Plot" dropdown menu. Common plot types include:
            </p>
            <ul>
                <li><strong>Bar Plots, Count Plots, Box Plots, Boxen Plots, Strip Plots, Swarm Plots, and Violin Plots:</strong> These are typically used to show relationships between categories. They usually require a categorical variable for the X-axis (or "Hue") and a numeric variable for the Y-axis. (See the <a href="link_to_categorical_tutorial">Categorical Tutorial</a> for more details).</li>
                <li><strong>Scatter Plots and Line Plots:</strong> These are used to show relationships between two numeric variables. For example, you might plot time versus measurement. (See the <a href="link_to_relational_tutorial">Relational Tutorial</a> for more details).</li>
                <li><strong>Histograms:</strong> These are used to show the distribution of a single numeric variable. (See the <a href="link_to_distributions_tutorial">Distributions Tutorial</a> for more details).</li>
            </ul>
        </li>

        <li>
            <strong>Configure Plot Parameters:</strong>
            <p>
                <ul>
                    <li><strong>X-Axis and Y-Axis:</strong> Use the "Select X" and "Select Y" dropdown menus to choose the variables you want to plot on the X and Y axes. The available options will depend on the dataset you selected.</li>
                    <li><strong>Hue:</strong> Use the "Select Hue" dropdown to color-code your data points based on categories. This helps to visualize how different categories are distributed.</li>
                    <li><strong>Style:</strong> Use the "Select Style" dropdown to vary the markers or lines in your plot, based on categories.</li>
                    <li><strong>Size:</strong> Use the "Select Size" dropdown to scale the size of the markers based on another variable.</li>
                    <li><strong>Column and Row:</strong> Use the "Select Column" and "Select Row" dropdowns to create subplots (facets). This allows you to compare different categories across multiple plots.</li>
                    <li><strong>Layer (Multiple):</strong> Use the "Select Layer" dropdown to manage how overlapping data points are displayed. Options like "Dodge," "Stack," and "Fill" are available.</li>
                </ul>
            </p>
        </li>

        <li>
            <strong>View Your Plot:</strong>
            <p>
                Once you have selected your plot type and configured the parameters, click the "Show Plot" button. Your plot will be displayed below the widget.
            </p>
        </li>

        <li>
            <strong>Clear Output:</strong>
            <p>
                To clear the displayed plot, click the "Clear Output" button.
            </p>
        </li>
    </ol>
    """


def get_data_path():
    dir_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(dir_path, MAIN_TABLE_VAR, MAIN_TABLE)
    return csv_path


def get_data_info(csv_path=None):
    if csv_path is None:
        csv_path = get_data_path()
    dataset_info = pd.read_csv(csv_path)
    return dataset_info


def get_bucket():
    my_bucket = os.getenv('WORKSPACE_BUCKET')
    return my_bucket


def select_data_options(dataset_info)->list:
    options = dataset_info[MAIN_TITLE].tolist()
    return options


def get_dropdown_value(dropdown):
    return dropdown.value


# def get_selected_data():
#     input_df = get_select_data_value()
#     dataset_info = get_data_info()
#     selected_data = dataset_info[dataset_info[MAIN_TITLE] == input_df]
#     return selected_data


def get_input_path(selected_data):
    # selected_data = get_selected_data()
    if selected_data is not None and not selected_data.empty:
        path = selected_data.iloc[0]['Data']
        dataset_name = selected_data.iloc[0]['file_name']
        return path, dataset_name
    else:
        print("No data found for the selected dataset title.")
        return None

def save_data_to_bucket(path, dataset_name):
    """
    :return: data_path not data
    """
    # path, dataset_name = get_input_path()
    my_bucket = get_bucket()
    args = ["gsutil", "cp", f"{path}", f"{my_bucket}/{dataset_name}"]
    output = subprocess.run(args, capture_output=True, text=True)
    if output.returncode == 0:
        target_path = f"{my_bucket}/{dataset_name}"
        return target_path

def save_to_bucket(dataframe, my_bucket):
    buffer = io.StringIO()
    dataframe.to_csv(buffer, index=False)
    buffer.seek(0)
    args = ['gsutil', 'cp', '-', my_bucket]
    process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate(buffer.getvalue().encode('utf-8'))


def load_data(path):
    """
    :return: data_path not data
    """
    # path, dataset_name = get_input_path()
    args = ["gsutil", "cat", f"{path}"]
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    output, _ = process.communicate()
    return output

def parse_data(dataset_name, output):
    if dataset_name.endswith("csv") or dataset_name.endswith("txt"):
        uploaded_data = pd.read_csv(io.StringIO(output.decode('utf-8')), low_memory=False)
        return uploaded_data

    elif dataset_name.endswith("xlsx"):
        uploaded_data = pd.read_excel(io.BytesIO(output))
        return uploaded_data

    elif dataset_name.endswith("xpt"):
        uploaded_data = pd.read_sas(io.StringIO(output.decode('utf-8')), low_memory=False)
        return uploaded_data

    else:
        print("Unsupported file type.")
        return None

def get_parsed_data(selected_data):
    path, dataset_name = get_input_path(selected_data)
    output = load_data(path)
    parsed_data= parse_data(dataset_name, output)
    return parsed_data


#create_widgets.py


def get_layout(box_name):
    layout_base = wd.Layout(grid_area=f'{box_name}', width='100%',
                            background_color='white', border='1px solid #ababab')
    return layout_base

def create_select_dropdown(options=None, box_name=None, value=None):
    select_dropdown = wd.Select(
        options=options,
        disabled=False,
        rows=10,
        value= value,
        layout=wd.Layout(grid_area=f'{box_name}_select_box', width='100%',
                         background_color='white', border='1px solid #ababab'))
    return select_dropdown

def create_multiple_select_dropdown(options=None, box_name=None):
    select_dropdown = wd.SelectMultiple(
        options=options,
        disabled=False,
        rows=10,
        layout=wd.Layout(grid_area=f'{box_name}_select_box', width='100%',
                         background_color='white', border='1px solid #ababab'))
    return select_dropdown


def create_dropdown(name, options= None, value=None):
    new_dropdown = wd.Dropdown(
        options=options,
        value=value,
        disabled=False,
        layout=wd.Layout(grid_area=f'{name}_dropdown_box')
    )
    return new_dropdown







def create_label(text, writing_style=None):
    if writing_style is None:
        writing_style = get_styles().get('label', '')
    lower_text = text.lower()
    label = wd.HTML(value=f"""<div style="{writing_style}"><p>Select {text}</p></div>""",
                    disabled=False,
                    layout=wd.Layout(grid_area=f'{lower_text}_label_box', width='100%',
                                     background_color='white', border='1px solid #ababab'),
                    style={**style_base, 'border': '1px solid #ababab'})
    return label

def create_helper(text, helper_name, writing_style=None):
    if writing_style is None:
        writing_style = get_styles().get('helper', '')
    helper = wd.HTML(value=f"""<div style="{writing_style}"><p>{text}</p></div>""",
                     disabled=False,
                     layout=wd.Layout(grid_area=f'{helper_name}_helper_box', border='1px solid gray', width='96%', justify='center'),
                     style={**style_base, 'word_break': 'break_all', 'padding': '3px'})
    return helper

def create_button(text, box_name, style):
    button= wd.Button(description=f'{text}', style=style,
              layout=wd.Layout(grid_area=f'{box_name}_button_box', width='100%'))
    return button


#styles
def get_styles():
    styles = {
        "div": "padding-left: 10px; padding-right: 10px; margin: 20px auto;",
        "table": "width: 100%; border-spacing: 0; border-bottom: 1px solid black;",
        "title": "background-color: #FFFFFF; text-align: left; font-size: 20px; font-weight: bold; font-family: Helvetica, Neue; border-bottom: 3px solid black;",
        "first_title": "background-color: #FFFFFF; width: 30%;text-align: left; font-size: 20px; font-weight: bold; font-family: Helvetica, Neue; border-bottom: 3px solid black;",
        "cell": "background-color: #FFFFFF; text-align: right; border-spacing: 0; border-bottom: 1px solid black; font-family: Helvetica, Neue;word-break:break-all;",
        "stats_cell": "background-color: #FFFFFF; text-align: center; border-spacing: 0; border-bottom: 1px solid black; font-family: Helvetica, Neue;",
        "key_cell": "background-color: #FFFFFF; text-align: left; border-spacing: 0;font-weight: bold;  border-bottom: 1px solid black; font-family: Helvetica, Neue;",
        "key_cell_variable": "background-color: #FFFFFF; text-align: left; border-spacing: 0;font-weight: bold;  border-bottom: 1px solid black; font-family: Helvetica, Neue;  word-break:break-all;",
        "sub_cell": "background-color: #FFFFFF;text-align: left; border-spacing: 0;font-weight: bold;  border-bottom: 1px solid black; font-family: Helvetica, Neue;  padding-left: 16px",
        "first_header": "text-align: left; border-spacing: 0; border-bottom: 1px solid black; background-color: white; font-family: Helvetica, Neue; font-weight: bold",
        "header": "text-align: center; border-spacing: 0; border-bottom: 1px solid black; background-color: white; font-family: Helvetica, Neue; font-weight: bold",
        "stats_header": "text-align: center; border-spacing: 0; border-bottom: 1px solid black; background-color: white; font-family: Helvetica, Neue; font-weight: bold; word-break:break-all;",
        "label": "text-align: left; font-weight: bold; font-size: 12px; margin-left: 5px; font-family: font-family: Helvetica, Neue",
        "helper": "text-align: left; font-size: 14px;margin-left: 5px; margin-right: 5px; font-family: font-family: Helvetica, Neue",
    }
    return styles


style_base = {'font_size': '14px', 'text_color': 'black', 'background': 'rgb(247, 247, 247)'}

button_style = {'font_size': '14px', 'text_color': 'white',
                'font_weight': 'bold', 'font_family': ' Tahoma, Verdana,sans-serif',
                'text_align': 'center'}

class Visuals:
    def __init__(self):
        self.data_info = get_data_info(DPATH)
        self.data_options = select_data_options(self.data_info)
        self.dataset_label = create_label(text='Dataset')
        self.x_axis_label = create_label(text='X')
        self.y_axis_label = create_label(text='Y')

        self.hue_dropdown_label = create_label(text='Hue')
        self.style_dropdown_label = create_label(text='Style')
        self.size_dropdown_label = create_label(text='Size')
        self.col_dropdown_label = create_label(text='Column')
        self.row_dropdown_label = create_label(text='Row')
        self.multiple_dropdown_label = create_label(text='Layer')
        self.plot_dropdown_label = create_label(text='Plot')
        self.dataset_dropdown = create_select_dropdown(options=['None'] + self.data_options, box_name='dataset')

        self.x_axis_dropdown = create_dropdown(name='x', options=[])
        self.y_axis_dropdown = create_dropdown(name='y', options=[])
        self.hue_dropdown = create_dropdown(name='hue', options=[])
        self.style_dropdown = create_dropdown(name='style', options=[])
        self.size_dropdown = create_dropdown(name='size', options=[])

        self.col_dropdown = create_dropdown(name='col', options=[])
        self.row_dropdown = create_dropdown(name='row', options=[])

        self.multiple_dropdown = create_dropdown(name='layer',
                                                 options=[('None', 'None'), ('Layer', 'layer'), ('Dodge', 'dodge'),
                                                          ('Stack', 'stack'), ('Fill', 'fill')], value='layer')
        self.plot_dropdown = create_select_dropdown(
            options=[('None', 'None'), ('Bar Plot', 'bar'), ('Box Plot', 'box'), ('Boxen Plot', 'boxen'),
                     ('Count Plot', 'count'),
                     ('Histogram', 'histogram'), ('Line Plot', 'line'), ('Point Plot', 'point'),
                     ('Scatter Plot', 'scatter'),
                     ('Strip Plot', 'strip'), ('Swarm Plot', 'swarm'), ('Violin Plot', 'violin')], box_name='plot',
            value='None')

        self.dataset_dropdown.observe(self.update_variable_options, names='value')

        self.show_plot_button = create_button(text='Show Plot', box_name='show_plot',
                                              style={**button_style, 'button_color': 'blue'})

        self.clear_plot_button = create_button(text='Clear Output', box_name='clear_plot',
                                               style={**button_style, 'button_color': 'red'})

        self.visual_helper = create_helper(text=calculate_helper_text, helper_name='visual')
        self.show_plot_output = wd.Output(layout=wd.Layout(grid_area='output_box', width='98%', height='80vh'))

        self.show_plot_button.on_click(self.show_plot)
        self.clear_plot_button.on_click(self.clear_output)

        self.visual_grid_layout = wd.GridBox(
            children=[self.visual_helper, self.dataset_label, self.dataset_dropdown,
                      self.x_axis_label, self.x_axis_dropdown,
                      self.y_axis_label, self.y_axis_dropdown,
                      self.hue_dropdown_label, self.hue_dropdown,
                      self.style_dropdown_label, self.style_dropdown,
                      self.size_dropdown_label, self.size_dropdown,
                      self.plot_dropdown_label, self.plot_dropdown,
                      self.col_dropdown_label, self.col_dropdown,
                      self.row_dropdown_label, self.row_dropdown,
                      self.multiple_dropdown_label, self.multiple_dropdown,
                      self.show_plot_button, self.clear_plot_button
                      ],
            layout=wd.Layout(display='grid',
                             grid_template_columns='15% 35% 15% 35%',
                             grid_template_rows='repeat(12, auto)',
                             grid_template_areas='''    
                             "visual_helper_box visual_helper_box visual_helper_box visual_helper_box "
                             "visual_helper_box visual_helper_box visual_helper_box visual_helper_box "
                             "dataset_label_box  dataset_select_box x_label_box x_dropdown_box "
                             " . dataset_select_box  y_label_box y_dropdown_box"
                             " . dataset_select_box hue_label_box hue_dropdown_box"
                             " . dataset_select_box  style_label_box style_dropdown_box" 
                             "plot_label_box plot_select_box  size_label_box size_dropdown_box"
                             " . plot_select_box  column_label_box col_dropdown_box "
                             " . plot_select_box  row_label_box row_dropdown_box"
                              " . plot_select_box layer_label_box layer_dropdown_box"
                              ". . . ."
                              " . show_plot_button_box . clear_plot_button_box"


                              ''',
                             grid_gap='10px',
                             width='98%',
                             height='auto',
                             margin='5px 5px 5px 5px'

                             ))

        display(wd.VBox([self.visual_grid_layout, self.show_plot_output]))

        self.input_data = self.data_info[self.data_info[MAIN_TITLE] == self.dataset_dropdown.value]

    def show_plot(self, b):
        with self.show_plot_output:
            clear_output(wait=True)
            self.create_plot()

    def update_variable_options(self, change):
        selected_title = self.dataset_dropdown.value
        selected_data = self.data_info[self.data_info[MAIN_TITLE] == selected_title]
        dataset = get_parsed_data(selected_data)
        if dataset is not None:
            self.x_axis_dropdown.options = ['None'] + dataset.columns.tolist()
            self.y_axis_dropdown.options = ['None'] + dataset.columns.tolist()
            self.hue_dropdown.options = ['None'] + dataset.columns.tolist()
            self.style_dropdown.options = ['None'] + dataset.columns.tolist()
            self.size_dropdown.options = ['None'] + dataset.columns.tolist()
            self.col_dropdown.options = ['None'] + dataset.columns.tolist()
            self.row_dropdown.options = ['None'] + dataset.columns.tolist()

    def get_x_axis(self):
        return self.x_axis_dropdown.value

    def get_y_axis(self):
        return self.y_axis_dropdown.value

    def get_hue(self):
        return self.hue_dropdown.value

    def get_style(self):
        return self.style_dropdown.value

    def get_size(self):
        return self.style_dropdown.value

    def get_multiple(self):
        return self.multiple_dropdown.value

    def get_column(self):
        return self.col_dropdown.value

    def get_row(self):
        return self.row_dropdown.value

    def get_plot(self):
        return self.plot_dropdown.value

    def create_plot(self):
        selected_title = self.dataset_dropdown.value
        selected_data = self.data_info[self.data_info[MAIN_TITLE] == selected_title]

        dataset = get_parsed_data(selected_data)
        if dataset is None:
            print("No dataset selected.")
            return

        plot_parameters = {
            'x': self.get_x_axis(),
            'data': dataset
        }
        temp_multiple = ""

        if self.get_y_axis() is not None:
            plot_parameters['y'] = self.get_y_axis()

        if self.get_hue() is not None:
            plot_parameters['hue'] = self.get_hue()

        if self.get_style() is not None:
            plot_parameters['style'] = self.get_style()
        if self.get_size() is not None:
            plot_parameters['size'] = self.get_size()
        if self.get_multiple() is not None:
            temp_multiple = self.get_multiple()

        if self.get_column() is not None:
            plot_parameters['col'] = self.get_column()
        if self.get_row() is not None:
            plot_parameters['row'] = self.get_row()

        plot_type = self.get_plot()

        with self.show_plot_output:
            clear_output(wait=True)
            if plot_type in ['bar', 'box', 'boxen', 'count', 'point', 'strip', 'swarm', 'violin']:
                g = sns.catplot(kind=plot_type, **plot_parameters)
                g.set_xticklabels(rotation=45, ha='right')
                #                 plt.tight_layout()
                plt.show()
                plt.close()

            elif plot_type == 'scatter':
                g = sns.relplot(kind='scatter', **plot_parameters)
                g.set_xticklabels(rotation=45, ha='right')
                #                 plt.tight_layout()
                plt.show()
                plt.close()

            elif plot_type == 'line':
                g = sns.relplot(kind='line', **plot_parameters)
                g.set_xticklabels(rotation=45, ha='right')
                #                 plt.tight_layout()
                plt.show()
                plt.close()

            elif plot_type == 'histogram':
                g = sns.displot(kind='hist', multiple=temp_multiple, **plot_parameters)
                g.set_xticklabels(rotation=45, ha='right')
                #                 plt.tight_layout()
                plt.show()
                plt.close()

    def clear_output(self, b):
        with self.show_plot_output:
            self.show_plot_output.clear_output()
        self.dataset_dropdown.value = 'None'
        self.x_axis_dropdown.value = []
        self.y_axis_dropdown.value = []
        self.hue_dropdown.value = []
        self.style_dropdown.value = []
        self.size_dropdown.value = []

        self.col_dropdown.value = []
        self.row_dropdown.value = []

        self.multiple_dropdown.value = 'layer'
        self.plot_dropdown.value = 'None'