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
