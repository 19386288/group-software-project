#Importing Shiny library
from shiny import App, Inputs, Outputs, Session, render, ui, reactive
from shinywidgets import render_plotly
from shinywidgets import output_widget, render_widget
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import pathlib
import  numpy as np
import statsmodels.api as sm
from statsmodels.stats.anova import AnovaRM
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd


#IMPORT DATA IN CSV FILE
data_dir = pathlib.Path(__file__).parent / "data"

data1 = pd.read_csv(data_dir / "Prescriptions per population (in thousands) per unit of Air Pollutant #1.csv")
data2 = pd.read_csv(data_dir / "Prescriptions per population (in thousands) per unit of Air Pollutant #2.csv")
data3 = pd.read_csv(data_dir / "Prescription Qty Scaled by Population.csv")
data4 = pd.read_csv(data_dir / "Preprocessed Air Pollutant 1 Data.csv")
data5 = pd.read_csv(data_dir / "Preprocessed Air Pollutant 2 Data.csv")

df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)
df3 = pd.DataFrame(data3)
df4 = pd.DataFrame(data4)
df5 = pd.DataFrame(data5)

# Drop unnecessary columns

df1 = df1.drop(['Air Pollutant #1', 'Prescription_Qty', 'Population', 'Population_Thousands', 'Presc_per_thous'], axis=1)
df2 = df2.drop(['Air Pollutant #2', 'Prescription_Qty', 'Population', 'Population_Thousands', 'Presc_per_thous'], axis=1)
df3 = df3.drop(['Prescription_Qty', 'Population', 'Population_Thousands'], axis=1)

# Rename columns
df1.rename(columns={'Presc_per_Poll': 'Data'}, inplace=True)
df2.rename(columns={'Presc_per_Poll': 'Data'}, inplace=True)
df3.rename(columns={'Presc_per_thous': 'Data'}, inplace=True)
df4.rename(columns={'Air Pollutant #1': 'Data'}, inplace=True)
df5.rename(columns={'Air Pollutant #2': 'Data'}, inplace=True)

# Change Years from string to integers
df1['YEAR'] = df1['YEAR'].astype(int)
df2['YEAR'] = df2['YEAR'].astype(int)
df3['YEAR'] = df3['YEAR'].astype(int)
df4['YEAR'] = df4['YEAR'].astype(int)
df5['YEAR'] = df5['YEAR'].astype(int)

pollutant = 'Is there a significant difference between air pollutant levels of two cities?'
prescription = 'Is there a significant difference between medications prescribed in two different cities?'
interaction = 'Is there a significant difference between prescription quantities per air pollutant unit of two cities?'

#Creating the User Interface
app_ui = ui.page_fluid(

    # Load Bootstrap Icons for FAQ
    ui.tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
    ),

    #Adding CSS to Improve the design of the page
    ui.tags.style("""
        .faq-icon { margin-right: 0.5rem; }

        .accordion-item {
            margin-bottom: 15px;
        }
        .card {
            border-radius: 12px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
        }
        .card button {
            margin-top: auto;
        }
        body {
            background-color:#f5f5f5;
        }
    """),

    ui.navset_pill(

        # Panel A
        ui.nav_panel(
            "Home",

            #heading section
            ui.div(
                {
                    "style": "background-image:url('/homepage.png'); padding:150px; width:100%; background-position:center top; background-repeat:no-repeat; background-size:100% auto;"
                },
                ui.h1(
                    "England Air Quality & Respiratory Health", align="center"
                ),
                ui.p(
                    "Exploring the correlation between air pollution levels and respiratory medication prescriptions across England",
                    style="text-align: center; font-size:18px;"
                ),
            ),

            #Creating space between elements
            ui.br(),

            #Research question section
            ui.div(
                {"style": "margin-top:20px; margin-bottom:20px;"},
                ui.card(
                    {"style":"font-size:18px;"},
                    "Research Question",
                    ui.p(
                        {"style":"font-size:14px;"},
                        "Is there a statistically significant relationship between air pollution levels (PM10 and PM2.5) and respiratory medication prescriptions in England ?"
                    )
                ),
                ui.card(
                    {"style":"font-size:18px;"},
                    "Why Does Air Pollution Matter?",
                    ui.p(
                        {"style":"font-size:14px;"},
                        "Air pollution is a major environmental health risk linked to asthma, COPD and lung infections. "
                        "Pollutants such as PM10 and PM2.5 consists of very small particles that can penetrate deep into lungs and affect breathing. "
                        "Long-term exposure to these pollutants can worsen existing respiratory conditions and increase the demand for respiratory medications."
                    ),
                    ui.p(
                        {"style":"font-size:14px;"},
                        "As air pollution levels rise, vulnerable populations such as children, the elderly, and people with pre-existing respiratory conditions may experience more severe symptoms. "
                        "This can lead to increased medical consultations and a higher number of prescriptions for respiratory medications, highlighting the importance of understanding the relationship between pollution levels and public health outcomes."
                    ),
                ),
            ),

            #"Dashboard functionality" section
            ui.div(
                ui.h3(
                    {"style":"text-align: center; font-size:20px;"},
                    "What This Dashboard Does"
                ),
                ui.layout_columns(
                    ui.card(
                        ui.h4(
                            {"style":"font-size: 18px;"},
                            "Statiscal Analysis"
                        ),
                        ui.tags.ul(
                            {"style":"font-size:14px;"},
                            ui.tags.li("Analyse the relationship between PM10 / PM2.5 and respiratory medication prescriptions in England."),
                            ui.tags.li("Explore trends in pollution levels and prescription patterns across time."),
                            ui.tags.li("Use regression analysis and visualisations to identify potential correlations between air pollution."),
                        ),
                        ui.input_action_button("stats", "Explore the Data"),
                    ),
                    ui.card(
                        ui.h4(
                            {"style":"font-size: 18px;"},
                            "Learn & Understand"
                        ),
                        ui.p(
                            {"style":"font-size:14px;"},
                            "Discover how PM10 and PM2.5 affect respiratory health. "
                            "Learn about these pollutants, how they enter the lungs, "
                            "and their impact on conditions like asthma, COPD and lungs infections"
                        ),
                        ui.p(
                            {"style":"font-size:14px;"},
                            "The FAQ section provides additional information and answers to common questions about air pollution and respiratory health."
                        ),
                        ui.input_action_button("faq_btn", "Answer your Questions"),
                    ),
                ),
            ),value="home",
        ),

        # Panel B
        ui.nav_panel(
            "Data Analysis",

            #DEFINE THE UI
            ui.page_fluid(
                ui.page_sidebar(
                    ui.sidebar(
                        ui.input_select('question', 'Select Question', [pollutant, prescription, interaction]),
                        ui.panel_conditional(
                            'input.question == "Is there a significant difference between medications prescribed in two different cities?" || input.question == "Is there a significant difference between prescription quantities per air pollutant unit of two cities?"', ui.input_select('medication', 'Select Prescription', ['Salbutamol'])
                            ),
                        ui.panel_conditional(
                            'input.question == "Is there a significant difference between air pollutant levels of two cities?" || input.question == "Is there a significant difference between prescription quantities per air pollutant unit of two cities?"', ui.input_select('pollutant', 'Select Pollutant', ['PM2.5', 'PM10'])
                            ),
                        ui.input_action_button(
                            'submit_q', 'Update Cities'
                            ),
                        ui.input_select(
                            'city1', 'Select City #1', []
                            ),
                        ui.input_select(
                            'city2', 'Select City #2', []
                            ),
                        ui.input_action_button('submit', 'Results')),
                ui.layout_column_wrap(
                    ui.card(ui.output_plot('plot')),
                    ui.card(ui.output_plot('plot2')),
                    width=1/2),
                ui.br(),
                ui.layout_column_wrap(
                    ui.card(ui.output_data_frame('anova_table')),
                    ui.card(ui.output_ui('explanation_text')),
                    width=1/2),
                ui.br(),
                ui.layout_column_wrap(
                ui.card(ui.output_text('notes')),
                width = 1),
                ),
                ), value = "stats"
        ),

        # Panel C
        ui.nav_panel(
            "Learn More",
            ui.h2("Air Quality FAQ"),

            ui.accordion(

                ui.accordion_panel(
                    "What is air quality?",
                    "Air quality describes how clean or polluted the air is, based on levels of pollutants such as PM2.5, NO₂, SO₂, ozone, and carbon monoxide."
                ),

                ui.accordion_panel(
                    "What are the causes of air pollution?",
                    "Common sources include vehicle emissions, construction dust, domestic heating, industrial activities, agriculture, and wildfires."
                ),

                ui.accordion_panel(
                    ui.span(
                        ui.tags.i(class_="bi bi-cloud-fog faq-icon"),
                        "What are the diseases caused by poor air quality?"
                    ),
                    "Poor air quality can contribute to COPD, bronchitis, asthma, lung infections, stroke, allergies, heart disease, and increased long-term risk of lung cancer.",
                    value="diseases"
                ),

                ui.accordion_panel(
                    ui.span(
                        ui.tags.i(class_="bi bi-thermometer-half faq-icon"),
                        "What are the symptoms of poor air quality-related ailments?"
                    ),
                    "Common symptoms include coughing, shortness of breath, sore throat, wheezing, chest tightness, watery eyes, headaches, fatigue, and worsening respiratory conditions.",
                    value="symptoms"
                ),

                ui.accordion_panel(
                    ui.span(
                        ui.tags.i(class_="bi bi-wind faq-icon"),
                        "How do people living with asthma react to poor air quality?"
                    ),
                    "People living with asthma may need increased inhaler use due to flare-ups and reduced lung function.",
                    value="asthma"
                ),

                ui.accordion_panel(
                    ui.span(
                        ui.tags.i(class_="bi bi-shield-check faq-icon"),
                        "How can the public guard themselves during high-pollution periods?"
                    ),
                    "Check air quality forecasts, keep windows closed during peaks, limit outdoor exercise, and avoid busy roads.",
                    value="protect"
                ),

                    id="faq",
                ),
                value="learn_more",
            ),

        id="tab"
    )
)


#DEFINE SERVER
def server(input, output, session):

    @reactive.effect
    @reactive.event(input.stats)
    def _go_stats():
        ui.update_navset("tab", selected="stats", session=session)

    @reactive.effect
    @reactive.event(input.faq_btn)
    def _go_faq():
        ui.update_navset("tab", selected="learn_more", session=session)
        

   # Update city according to previous answers
    @reactive.effect
    @reactive.event(input.submit_q)
    def _():
        #https://posit-dev.github.io/py-shiny/docs/api/core/ui.update_select.html#shiny.ui.update_select
        

        if input.question() == prescription:
            cities = df3['City'].unique().tolist()
        elif input.question() == pollutant:
            if input.pollutant() == "PM2.5":
                cities = df4['City'].unique().tolist()
            elif input.pollutant() == "PM10":
                cities = df5['City'].unique().tolist()
        elif input.question() == interaction:
            if input.pollutant() == "PM2.5":
                cities = df1['City'].unique().tolist()
            elif input.pollutant() == "PM10":
                cities = df2['City'].unique().tolist()
        
        ui.update_select(
            "city1",
            label = 'Select City #1',
            choices = cities,
            selected = cities[0] if cities else None,
        )

        ui.update_select(
            "city2",
            label = 'Select City #2',
            choices = cities,
            selected = cities[0] if cities else None,
        )

    @reactive.Calc
    @reactive.event(input.submit)
    def dataframe():
        # Select dataframe from user selection
        if input.question() == pollutant:
            if input.pollutant() == 'PM2.5':
                df = df4[((df4['City'] == input.city1()) | (df4['City'] == input.city2()))]
                title = 'PM2.5 (µg/m3)'
                x_title = 'Year'
                y_title = 'Quantity of PM2.5 (µg/m3)'
            else:
                df = df5[((df5['City'] == input.city1()) | (df5['City'] == input.city2()))]
                title = 'PM10 (µg/m3)'
                x_title = 'Year'
                y_title = 'Quantity of PM10 (µg/m3)'
        elif input.question() == interaction:
            if input.pollutant() == 'PM2.5':
                df = df1[((df1['City'] == input.city1()) | (df1['City'] == input.city2()))]
                title = 'Prescription per PM2.5 (µg/m3)'
                x_title = 'Year'
                y_title = 'Prescription quantity per unit of PM2.5 (µg/m3)'
            else:
                df = df2[((df2['City'] == input.city1()) | (df2['City'] == input.city2()))]
                title = 'Prescription per PM10 (µg/m3)'
                x_title = 'Year'
                y_title = 'Prescription quantity per unit of PM10 (µg/m3)'
        elif input.question() == prescription:
            df = df3[((df3['City'] == input.city1()) | (df3['City'] == input.city2()))]
            title = 'Prescription per Population (Thousands)'
            x_title = 'Year'
            y_title = 'Prescription Quantity per Population (Thousands)'
        return {'df': df, 'title': title, 'ylabel': y_title}

    
    # ADD BUTTON TO MAKE THE GRAPH, GRAPH / TABLES SHOULD ONLY UPDATE AFTER CLICKING BUTTON

    @render.plot()
    @reactive.event(input.submit)
    def plot():
        df = dataframe()
        ax = sns.barplot(data= df['df'], x = df['df']['YEAR'], y = df['df']['Data'], hue = df['df']['City'], palette='colorblind')
        ax.set_title(df['title'])
        ax.set_xlabel('Year')
        ax.set_ylabel(df['ylabel'])
        return ax

    @render.plot() 
    @reactive.event(input.submit)                   
    def plot2():
        df = dataframe()
        ax = sns.barplot(data=df['df'], x =df['df']['MONTH'], y = df['df']['Data'], hue = df['df']['City'], palette='colorblind' )
        ax.set_title(df['title'])
        ax.set_xlabel('Month')
        ax.set_ylabel(df['ylabel'])
        return ax
    
    
    @reactive.calc
    @reactive.event(input.submit)
    def anova_results():
        df = dataframe()['df']
        df['YEAR'] = df['YEAR'].astype(int)
        model = ols("Data ~ C(City) * YEAR", data=df).fit()
        anova_results = sm.stats.anova_lm(model, typ=2)
        return anova_results
    

    @render.data_frame
    @reactive.event(input.submit)
    def anova_table():
        city1 = input.city1()
        city2 = input.city2()
        error_list = ['Please select two different cities']
        if city1 == city2:
            return render.DataTable(pd.DataFrame({'Error': error_list}))
        else:
            return render.DataTable(anova_results().round(2).reset_index())

    @render.text
    @reactive.event(input.submit)
    def notes():
        return f"Contains public sector information licensed under the Open Government Licence v3.0."

    @render.ui
    @reactive.event(input.submit)
    def explanation_text(): 
        question = input.question()
        city1 = input.city1()
        city2 = input.city2()
        pollutant2 = input.pollutant()
        if city1 == city2:
            return f"Error: Please select two different cities."
        else:
            results = anova_results()
            pvalue_city = results['PR(>F)'].iloc[0]
            pvalue_year = results['PR(>F)'].iloc[1]
            pvalue_both = results['PR(>F)'].iloc[2]


            if question == pollutant:
                if pvalue_city < 0.05:
                    if pvalue_year < 0.05:
                        if pvalue_both < 0.05: # S / S / S
                            return ui.markdown(f"""
                            City: For {pollutant2}, the difference between {city1} and {city2} is statistically significant. Therefore the difference is likely not caused by random chance.
                            
                            Year: For {pollutant2}, the difference between 2024 and 2025 is statistically significant. Therefore the difference is likely not caused by random chance.
                            
                            City|Year: For {pollutant2}, the difference between the interaction of cities ({city1} & {city2}) and years (2024 & 2025) is statistically significant. Therefore the difference is likely not caused by random chance.
                            """) 
                        else: # S / S / NS
                            return ui.markdown(f"""
                            City: For {pollutant2}, the difference between {city1} and {city2} is statistically significant. Therefore the difference is likely not caused by random chance.
                            
                            Year: For {pollutant2}, the difference between 2024 and 2025 is statistically significant. Therefore the difference is likely not caused by random chance.
                            
                            City|Year: For {pollutant2}, the difference between the interaction of cities ({city1} & {city2}) and years (2024 & 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                            """)
                    else: 
                        if pvalue_both < 0.05: # S / NS / S
                            return ui.markdown(f"""
                            City: For {pollutant2}, the difference between {city1} and {city2} is statistically significant. Therefore the difference is likely not caused by random chance.
                            
                            Year: For {pollutant2}, the difference between 2024 and 2025 is not statistically significant. Therefore the difference is likely caused by random chance.
                            
                            City|Year: For {pollutant2}, the difference between the interaction of cities ({city1} & {city2}) and years (2024 & 2025) is statistically significant. Therefore the difference is likely not caused by random chance.
                            """)
                        else: # S / NS / NS
                            return ui.markdown(f"""
                            City: For {pollutant2}, the difference between {city1} and {city2} is statistically significant. Therefore the difference is likely not caused by random chance.
                            
                            Year: For {pollutant2}, the difference between 2024 and 2025 is not statistically significant. Therefore the difference is likely caused by random chance.
                            
                            City|Year: For {pollutant2}, the difference between the interaction of cities ({city1} & {city2}) and years (2024 & 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                            """)
                else:
                    if pvalue_year < 0.05: 
                        if pvalue_both < 0.05: # NS / S / S
                            return ui.markdown(f"""
                            City: For {pollutant2}, the difference between {city1} and {city2} is not statistically significant. Therefore the difference is likely caused by random chance.
                            
                            Year: For {pollutant2}, the difference between 2024 and 2025 is  statistically significant. Therefore the difference is not likely caused by random chance.
                            
                            City|Year: For {pollutant2}, the difference between the interaction of cities ({city1} & {city2}) and years (2024 & 2025) is statistically significant. Therefore the difference is likely not caused by random chance.
                            """)
                        else: # NS / S / NS
                            return ui.markdown(f"""
                            City: For {pollutant2}, the difference between {city1} and {city2} is not statistically significant. Therefore the difference is likely caused by random chance.
                            
                            Year: For {pollutant2}, the difference between 2024 and 2025 is statistically significant. Therefore the difference is not likely caused by random chance.
                            
                            City|Year: For {pollutant2}, the difference between the interaction of cities ({city1} & {city2}) and years (2024 & 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                            """)
                    else:
                        if pvalue_both < 0.05: # NS / NS / S
                            return ui.markdown(f"""
                            City: For {pollutant2}, the difference between {city1} and {city2} is not statistically significant. Therefore the difference is likely caused by random chance.
                            
                            Year: For {pollutant2}, the difference between 2024 and 2025 is not statistically significant. Therefore the difference is likely caused by random chance.
                            
                            City|Year: For {pollutant2}, the difference between the interaction of cities ({city1} & {city2}) and years (2024 & 2025) is statistically significant. Therefore the difference is not likely caused by random chance.
                            """)
                        else: # NS / NS / NS
                            return ui.markdown(f"""
                            City: For {pollutant2}, the difference between {city1} and {city2} is not statistically significant. Therefore the difference is likely caused by random chance.
                            
                            Year: For {pollutant2}, the difference between 2024 and 2025 is not statistically significant. Therefore the difference is likely caused by random chance.
                            
                            City|Year: For {pollutant2}, the difference between the interaction of cities ({city1} & {city2}) and years (2024 & 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                            """)
            if question == interaction:
                if pvalue_city < 0.05:
                    if pvalue_year < 0.05:
                        if pvalue_both < 0.05:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions per {pollutant2}, the difference between {city1} and {city2} is statistically significant. Therefore the difference is not likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions per {pollutant2}, the difference between 2024 and 2025 is statistically significant. Therefore the difference is not likely caused by random chance.

                    City|Year: For Salbutamol prescriptions per {pollutant2}, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is statistically significant. Therefore the difference is not likely caused by random chance.
                    """)
                        else:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions per {pollutant2}, the difference between {city1} and {city2} is statistically significant. Therefore the difference is not likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions per {pollutant2}, the difference between 2024 and 2025 is statistically significant. Therefore the difference is not likely caused by random chance.

                    City|Year: For Salbutamol prescriptions per {pollutant2}, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                    """)
                    else:
                        if pvalue_both < 0.05:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions per {pollutant2}, the difference between {city1} and {city2} is statistically significant. Therefore the difference is not likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions per {pollutant2}, the difference between 2024 and 2025 is not statistically significant. Therefore the difference is likely caused by random chance.

                    City|Year: For Salbutamol prescriptions per {pollutant2}, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is statistically significant. Therefore the difference is not likely caused by random chance.
                    """)
                        else:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions per {pollutant2}, the difference between {city1} and {city2} is statistically significant. Therefore the difference is not likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions per {pollutant2}, the difference between 2024 and 2025 is not statistically significant. Therefore the difference is likely caused by random chance.

                    City|Year: For Salbutamol prescriptions per {pollutant2}, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                    """)
                else:
                    if pvalue_year < 0.05:
                        if pvalue_both < 0.05:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions per {pollutant2}, the difference between {city1} and {city2} is not statistically significant. Therefore the difference is likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions per {pollutant2}, the difference between 2024 and 2025 is statistically significant. Therefore the difference is not likely caused by random chance.

                    City|Year: For Salbutamol prescriptions per {pollutant2}, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is statistically significant. Therefore the difference is not likely caused by random chance.
                    """)
                        else:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions per {pollutant2}, the difference between {city1} and {city2} is not statistically significant. Therefore the difference is likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions per {pollutant2}, the difference between 2024 and 2025 is statistically significant. Therefore the difference is not likely caused by random chance.

                    City|Year: For Salbutamol prescriptions per {pollutant2}, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                    """)
                    else:
                        if pvalue_both < 0.05:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions per {pollutant2}, the difference between {city1} and {city2} is not statistically significant. Therefore the difference is likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions per {pollutant2}, the difference between 2024 and 2025 is statistically significant. Therefore the difference is not likely caused by random chance.

                    City|Year: For Salbutamol prescriptions per {pollutant2}, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                    """)
                        else:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions per {pollutant2}, the difference between {city1} and {city2} is not statistically significant. Therefore the difference is likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions per {pollutant2}, the difference between 2024 and 2025 is not statistically significant. Therefore the difference is likely caused by random chance.

                    City|Year: For Salbutamol prescriptions per {pollutant2}, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                    """)
            if question == prescription:
                if pvalue_city < 0.05:
                    if pvalue_year < 0.05:
                        if pvalue_both < 0.05:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions, the difference between {city1} and {city2} is statistically significant. Therefore the difference is not likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions, the difference between 2024 and 2025 is statistically significant. Therefore the difference is not likely caused by random chance.

                    City|Year: For Salbutamol prescriptions, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is statistically significant. Therefore the difference is not likely caused by random chance.
                    """)
                        else:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions, the difference between {city1} and {city2} is statistically significant. Therefore the difference is not likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions, the difference between 2024 and 2025 is statistically significant. Therefore the difference is not likely caused by random chance.

                    City|Year: For Salbutamol prescriptions, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                    """)
                    else:
                        if pvalue_both < 0.05:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions, the difference between {city1} and {city2} is statistically significant. Therefore the difference is not likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions, the difference between 2024 and 2025 is not statistically significant. Therefore the difference is likely caused by random chance.

                    City|Year: For Salbutamol prescriptions, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is statistically significant. Therefore the difference is not likely caused by random chance.
                    """)
                        else:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions, the difference between {city1} and {city2} is statistically significant. Therefore the difference is not likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions, the difference between 2024 and 2025 is not statistically significant. Therefore the difference is likely caused by random chance.

                    City|Year: For Salbutamol prescriptions, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                    """)
                else:
                    if pvalue_year < 0.05:
                        if pvalue_both < 0.05:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions, the difference between {city1} and {city2} is not statistically significant. Therefore the difference is likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions, the difference between 2024 and 2025 is statistically significant. Therefore the difference is not likely caused by random chance.

                    City|Year: For Salbutamol prescriptions, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is statistically significant. Therefore the difference is not likely caused by random chance.
                    """)
                        else:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions, the difference between {city1} and {city2} is not statistically significant. Therefore the difference is likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions, the difference between 2024 and 2025 is statistically significant. Therefore the difference is not likely caused by random chance.

                    City|Year: For Salbutamol prescriptions, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                    """)
                    else:
                        if pvalue_both < 0.05:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions, the difference between {city1} and {city2} is not statistically significant. Therefore the difference is likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions, the difference between 2024 and 2025 is statistically significant. Therefore the difference is not likely caused by random chance.

                    City|Year: For Salbutamol prescriptions, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                    """)
                        else:
                            return ui.markdown(f"""
                    Salbutamol prescriptions were scaled by city population so that prescription quantities could be compared across multiple cities.
                                       
                    City: For Salbutamol prescriptions, the difference between {city1} and {city2} is not statistically significant. Therefore the difference is likely caused by random chance.
                    
                    Year: For Salbutamol prescriptions, the difference between 2024 and 2025 is not statistically significant. Therefore the difference is likely caused by random chance.

                    City|Year: For Salbutamol prescriptions, the difference between the intereaction of cities ({city1} and {city2}) and years (2024 and 2025) is not statistically significant. Therefore the difference is likely caused by random chance.
                    """)

""" @render.plot
    def plot():
        fig, ax = plt.subplots()
        sns.barplot(data=df1, x="YEAR", y="Presc_per_Poll", hue="City", ax=ax)
        ax.set_title("Pollution Levels by city and year")
        ax.set_xlabel("Year")
        ax.set_ylabel("Pollution Level")
        ax.grid(True)
        plt.tight_layout()
        return fig"""

#Importing pathlib for static files
#Path to the "www" file containing images
static_dir = pathlib.Path(__file__).parent / "www"

#Creating the Shiny Application
app = App(app_ui, server, static_assets=static_dir)
