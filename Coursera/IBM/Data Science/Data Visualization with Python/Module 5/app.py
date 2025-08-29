import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import requests
import io


URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"
response = requests.get(URL)
response.raise_for_status() # Raise an exception for HTTP errors
csv_content = io.StringIO(response.text)
df = pd.read_csv(csv_content)


df = df.rename(columns={
    'Unemployment_Rate': 'Unemployment Rate',
    'Automobile_Sales': 'Automobile Sales',
    'Advertising_Expenditure': 'Advertising Expenditure'
})

df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month_name() # Get month names for better labels


# Generate a list of years for the dropdown
year_list = [i for i in range(1980, 2014)]

# Create the Dash application instance
app = dash.Dash(__name__)

# TASK 2.1: Create a Dash application and give it a meaningful title. (2 points)
# The layout defines the structure of the dashboard, including titles, dropdowns, and output areas.
app.layout = html.Div([
    html.H1("Automobile Sales Statistics Dashboard",
            style={'textAlign': 'center', 'color': '#503036', 'font-size': 24}),

    # Division for the Report Type dropdown
    html.Div([
        html.H2("Select Report Type:", style={'margin-right': '2em'}),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
            ],
            placeholder='Select a report type',
            value='Select Statistics', # Default value
            style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'}
        )
    ]),

    # Division for the Year Selection dropdown
    html.Div([
        html.H2("Select Year:", style={'margin-right': '2em'}),
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            placeholder='Select year',
            value='Select Year' # Default value
        )
    ]),

    # TASK 2.3: Add a division for output display with appropriate 'id' and 'classname' property. (1 point)
    # This division will hold the generated plots.
    html.Div(id='output-container', className='chart-grid', style={'display': 'flex', 'flex-wrap': 'wrap'}),
])


# TASK 2.4: Creating Callbacks; Define the callback function to update the input container. (5 points)

# Callback to enable/disable the year dropdown based on report type selection
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    # If 'Yearly Statistics' is selected, the year dropdown is enabled (False for disabled property)
    if selected_statistics == 'Yearly Statistics':
        return False
    # Otherwise (for 'Recession Period Statistics'), the year dropdown is disabled (True for disabled property)
    else:
        return True

# Callback to update the output container with plots based on selections
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'),
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_statistics, input_year):
    # Check if 'Recession Period Statistics' is selected
    if selected_statistics == 'Recession Period Statistics':
        # TASK 2.5: Create and display graphs for Recession Report Statistics. (3 points)
        recession_data = df[df['Recession'] == 1].copy() # Ensure it's a copy to avoid SettingWithCopyWarning

        # Plot 1: Line chart for Average Automobile Sales Fluctuation Over Recession Period (Year-wise)
        yearly_rec = recession_data.groupby('Year')['Automobile Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, x='Year', y='Automobile Sales',
                           title="Average Automobile Sales Fluctuation Over Recession Period (Year-wise)"))

        # Plot 2: Bar chart for Average Number of Vehicles Sold by Vehicle Type during recessions
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales, x='Vehicle_Type', y='Automobile Sales',
                          title="Average Number of Vehicles Sold by Vehicle Type"))

        # Plot 3: Pie chart for Total Expenditure Share by Vehicle Type During Recessions
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec, values='Advertising Expenditure', names='Vehicle_Type',
                          title="Total Expenditure Share by Vehicle Type During Recessions"))

        # Plot 4: Bar chart for Effect of Unemployment Rate on Vehicle Type and Sales
        unemp_data = recession_data.groupby(['Unemployment Rate', 'Vehicle_Type'])['Automobile Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(
            figure=px.bar(unemp_data, x='Unemployment Rate', y='Automobile Sales',
                          color='Vehicle_Type',
                          labels={'Unemployment Rate': 'Unemployment Rate', 'Automobile Sales': 'Average Automobile Sales'},
                          title='Effect of Unemployment Rate on Vehicle Type and Sales'))

        # Return the recession plots arranged in two rows, two columns
        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)], style={'display': 'flex', 'flex': '1 1 50%'}),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)], style={'display': 'flex', 'flex': '1 1 50%'})
        ]

    # Check if 'Yearly Statistics' is selected and a year is provided
    elif (input_year and selected_statistics == 'Yearly Statistics'):
        # TASK 2.6: Create and display graphs for Yearly Report Statistics. (2 points)
        yearly_data = df[df['Year'] == input_year]

        # Plot 1: Line chart for Yearly Automobile Sales for the Whole Period
        # This plot uses the full dataframe to show overall yearly trend, not just the selected year's data
        yas = df.groupby('Year')['Automobile Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas, x='Year', y='Automobile Sales',
                           title='Yearly Automobile Sales for the Whole Period'))

        # Plot 2: Line chart for Total Monthly Automobile Sales for the Selected Year
        mas = yearly_data.groupby('Month')['Automobile Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(mas, x='Month', y='Automobile Sales',
                           title=f'Total Monthly Automobile Sales in {input_year}'))

        # Plot 3: Bar chart for Average Vehicles Sold by Vehicle Type in the Selected Year
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(avr_vdata, x='Vehicle_Type', y='Automobile Sales',
                          title=f'Average Vehicles Sold by Vehicle Type in {input_year}'))

        # Plot 4: Pie chart for Total Advertisement Expenditure for Each Vehicle in the Selected Year
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data, values='Advertising Expenditure', names='Vehicle_Type',
                          title=f'Total Advertisement Expenditure for Each Vehicle in {input_year}'))

        # Return the yearly plots arranged in two rows, two columns
        return [
            html.Div(className='chart-item', children=[html.Div(children=Y_chart1), html.Div(children=Y_chart2)], style={'display': 'flex', 'flex': '1 1 50%'}),
            html.Div(className='chart-item', children=[html.Div(children=Y_chart3), html.Div(children=Y_chart4)], style={'display': 'flex', 'flex': '1 1 50%'})
        ]
    else:
        # Return an empty div if no valid selection is made
        return html.Div([])

# Run the app
if __name__ == '__main__':
    app.run(debug=False)
