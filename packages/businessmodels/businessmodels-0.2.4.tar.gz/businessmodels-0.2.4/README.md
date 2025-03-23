businessmodels package made by Business Brio team members. 

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This python package has several modules to work for data analysis. 

## Installation

Following code is to install package.

```bash
pip install businessmodels
```

## DOCUMENTATION
businessmodels is a helpful package in data science. It contains several modules to get desired analysis output. Most of the modules are dedicated to business analysis purposes.
You can find the documentation [here](https://github.com/Business-Brio/businessmodels/tree/main/businessmodels/Documentation)

- ## Customer Segmentation
Data Overview: 
![image](https://github.com/Business-Brio/businessmodels/assets/134270407/35c5e11e-2c94-4fcd-a3f9-f2fbf677e712)

Function Call - 
Perform customer segmentation using the 'businessmodels' library and 'customersegmentation.cust_seg' is a function in the library, so it takes the 'df' DataFrame and a date (Ex.- '2023-04-02') as arguments.

```bash
from businessmodels import customersegmentation
Segments = customersegmentation.cust_seg(df, '2023-04-02')
Customer_rfm,active_customer_segments,inactive_customers,segments_summary = Segments.Daily()
```

![image](https://github.com/Business-Brio/businessmodels/assets/134270407/70701ef1-e1d3-401d-87d4-551453af0484)
By changing the Segments.daily to Weekly, Monthly, Quarterly get others segments customers.

- ## Price Elasticity of Products 
Data Overview: 
![image](https://github.com/Business-Brio/businessmodels/assets/134270407/20fdc5df-17f2-459e-96f8-eace327398a9)

Function Call - 
Calculate price elasticity using the 'pricing' function from the 'price_elasticity' module. Get the results of price elasticity, separating products into different categories
- 'Elastic_Products' are products with elastic demand
- 'Unit_Elastic_Products' are products with unitary elastic demand
- 'Inelastic_Products' are products with inelastic demand

```bash
from businessmodels import price_elasticity
Separated = price_elasticity.pricing(df)
Elastic_Products,Unit_Elastic_Products,Inelastic_Products = Separated.price_elasticity()
```

![image](https://github.com/Business-Brio/businessmodels/assets/134270407/b7d78384-ded1-4488-a587-1125b9687192)

- ## Recommendation Engine
Data Overview: 
![image](https://github.com/Business-Brio/businessmodels/assets/134270407/8e34a3e4-a3d5-4e8a-8f87-c94a52e411b0)

Function Call - 
Call the 'recommendation' method from the recommendation_engine module and pass the 'df' DataFrame as an argument than Call the 'final_recomendations' method on the 'run' object to generate the list of recommended products.
Print or use the 'product_list' variable, which contains the recommended products.

```bash
from businessmodels import recommendation_engine
run = recommendation_engine.recommendation(df)
product_list = run.final_recomendations()
```

![image](https://github.com/Business-Brio/businessmodels/assets/134270407/cb1176df-d1f6-49f2-9e99-c41ef342af7b)

- ## GET SLA Module
Data Overview: The data used to demonstrate this module is basically a sales data having time taken to contact lead for the very first time units in minutes(Lead2FirstIntr_datedifference_Minute), Sale non-sale column(saleflag) with 0 referring to non-sale and 1 referring sale, date of order(order_date), lead generation date(lead_date), number of interactions done by sales team after the generation of lead(interactions) and difference of date between order date and lead generation date(Lead_to_Sale_diff).

The module needs to be imported from the businessmodels package using the following line of code
Function Call - 
```bash
from businessmodels import get_sla
sla_determination = get_sla.SLADetermination(df)
sla_determination.filter_and_convert_dates(st,et)
sla_determination.calculate_lead_to_sale_diff()
x,y = sla_determination.categorize_lead_to_sale_calculate()
```
- ## GET SLA DETERMINATION Module
Data Overview: The data used to demonstrate this module is basically a sales data having time taken to contact lead for the very first time units in minutes(Lead2FirstIntr_datedifference_Minute), Sale non-sale column(saleflag) with 0 referring to non-sale and 1 referring sale, date of order(order_date), lead generation date(lead_date).

The module needs to be imported from the businessmodels package using the following line of code
Function Call -
```bash
from businessmodels import sla_determine
column = "Required Column Name"
sla_check = sla_determine.SLA_Determination(df, column)
a,b,c,d = sla_check.calculate_sla(st, et)
```

- ## Performance Rank
Function Call -

```bash
from businessmodels import performance_rank
```

Data where columns are as follow: column1: Individual associate id(s) or name. column2: Saleflag or success of individual where 0 is unfulfiled (unsold) and 1 is fulfiled (sold). column3: Market type containing two labels for each affiliate. For example- urban_market and rural_market It contains following methods:

* feed_data(data, percentage, column1, column2, column3): Feed the dataframe, set percentage to get interpretetion, name of first column (e.g. "salesman_id"), name of second column (e.g. "saleflag"), name of third column (e.g. "market_type") N.B: percentage will help to classify top n% and bottom n% associates for each market type according to their performance. Create an instance with the feed_data method.
* interpret(): Call this method on the created feed_data instance. This will return a dictionary containing interpreted performance result of each associate.
* output_table(): Call this method on the early created instance of feed_data and get a dictionary containing mathematical results (salesman_id, actual_fulfiled, actual_unfulfiled, expected fulfiled, chi fulfiled value, sale percentage)

The result is generated by using chi square method for each salesman and the "sale percentage" is nothing but the percentage of fulfiled cases from the total amount of opportunities (fulfiled and unfulfiled) one associate got.

Good or bad performer in the interpreted dictionary is distinguished by observing each associate's actual fulfiled and expected fulfiled amount. If expected fulfiled is more than actual fulfiled then the associate is labeled as bad. If expected fulfiled is less than actual fulfiled then the associate is labeled as good.

- ## SAM From Voronoi Tessellation

Function Call -

```bash
from businessmodels import SAMfromVTess
```
Extraction of Serviceable Addressable Market(SAM) for a business unit/entity (DMU for DEA Models) by taking inputs for GIS coordinates for the specifics business unit's catchment area as received after running Voronoi Tessellation.

## MAIN FEATURES
- performance rank model (model name: performance_rank)
    - Get affiliates' ranked table on basis of their performance and their interpreted result. This module's documentation is here: 
- customer segmentation model (model name: customersegmentation)
- to compute Price Elasticity of Products (model name: price_elasticity)
- recommendate a product to a customer (model name: recommendation_engine)
- get sla model (model name: get_sla)

## CONTRIBUTORS
[Gautam Banerjee](https://in.linkedin.com/in/gautambanerjee/),
[Bhargab Ganguli](https://www.linkedin.com/in/bhargab-ganguli-570750195/),
[Shuvadeep Maity](https://www.linkedin.com/in/shuvadeep-maity/),
[Manas Roy](https://www.linkedin.com/in/manas-roy-ba809515b/),
[Arnab Basak](https://in.linkedin.com/in/arnab-basak-09954a94/),
[Ayan Chakraborty](https://www.linkedin.com/in/ayan-chakraborty/),
[Riddhiman Syed](https://www.linkedin.com/in/riddhiman-syed-045947220/),
[Tanuka Chattaraj](https://www.linkedin.com/in/tanuka-chattaraj-b80a0a198/),
[Anasua Ghosh]() .

- For furthers enquiries, pelase reach out to [info@businessbrio.com](info@businessbrio.com)

## LICENSE
It is licensed under OSI approved MIT open license.
