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
from constants import *


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