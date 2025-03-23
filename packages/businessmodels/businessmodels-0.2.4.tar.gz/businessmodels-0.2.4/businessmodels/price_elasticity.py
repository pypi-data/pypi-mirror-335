import statsmodels.api as sm
import numpy as np
import pandas as pd

class pricing:
    def __init__(self, df):
        self.df = df

    def price_elasticity(self):
        df=self.df
        df = df[df["VOLUME"] > 0]
        df["Unit_price"] = df["SALES"]/df["VOLUME"]
        df_Stock = df.groupby(['VISIT_DT','SKU_ID']).agg({'Unit_price':'mean','VOLUME': 'mean' }).reset_index()
        x_pivot = df_Stock.pivot(index= 'VISIT_DT' ,columns='SKU_ID' ,values='Unit_price')
        x_values = pd.DataFrame(x_pivot.to_records())
        y_pivot = df_Stock.pivot( index = 'VISIT_DT',columns='SKU_ID', values='VOLUME')
        y_values = pd.DataFrame(y_pivot.to_records())
        points = []
        results_values = {
            "name": [],
            "price_elasticity": [],
            "price_mean": [],
            "quantity_mean": [],
            "intercept": [],
            "t_score":[],
            "slope": [],
            "coefficient_pvalue" : [],
        }
        #Append x_values with y_values per same product name
        for column in x_values.columns[1:]:
            column_points = []
            for i in range(len(x_values[column])):
                if not np.isnan(x_values[column][i]) and not np.isnan(y_values[column][i]):
                    column_points.append((x_values[column][i], y_values[column][i]))
            df_sam= pd.DataFrame(list(column_points), columns= ['x_value', 'y_value'])


            #Linear Regression Model
            x_value =df_sam['x_value']
            y_value = df_sam['y_value']
            X = sm.add_constant(x_value)
            model = sm.OLS(y_value, X)
            result = model.fit()
            #(Null Hypothesis test) Coefficient with a p value less than 0.05
            if result.f_pvalue < 0.05:

                rsquared = result.rsquared
                coefficient_pvalue = result.f_pvalue
                intercept,slope = result.params
                mean_price = np.mean(x_value)
                mean_quantity = np.mean(y_value)
                tintercept,t_score = result.tvalues

                #Price elasticity Formula
                price_elasticity = (slope)*(mean_price/mean_quantity)
                #price_elasticity = (slope)*(mean_quantity/mean_price)

                #Append results into dictionary for dataframe
                results_values["name"].append(column)
                results_values["price_elasticity"].append(price_elasticity)
                results_values["price_mean"].append(mean_price)
                results_values["quantity_mean"].append(mean_quantity)
                results_values["intercept"].append(intercept)
                results_values['t_score'].append(t_score)
                results_values["slope"].append(slope)
                results_values["coefficient_pvalue"].append(coefficient_pvalue)

        final_df = pd.DataFrame.from_dict(results_values)
        df_elasticity = final_df[['name','price_elasticity','t_score','coefficient_pvalue','slope','price_mean','quantity_mean','intercept']]
        Elastic_product= df_elasticity[df_elasticity['price_elasticity']<-1]
        Elastic_product_rank =  Elastic_product[['name', 'price_elasticity']]
        Elastic_product_rank = Elastic_product_rank.sort_values(by='price_elasticity')
        Elastic_product_rank['ranking'] = Elastic_product_rank['price_elasticity'].rank()
        Elastic_product_rank.reset_index(drop=True, inplace=True)

        UnitElastic_product= df_elasticity[df_elasticity['price_elasticity']>=-1]
        UnitElastic_product_rank =  UnitElastic_product[['name', 'price_elasticity']]
        UnitElastic_product_rank = UnitElastic_product_rank.sort_values(by='price_elasticity')
        UnitElastic_product_rank['ranking'] = UnitElastic_product_rank['price_elasticity'].rank()
        UnitElastic_product_rank.reset_index(drop=True, inplace=True)

        InElastic_product = df[['SKU_ID']]
        InElastic_product.rename(columns={'SKU_ID': 'name'}, inplace=True)
        # Use the ~ operator and isin method to filter out matching values
        InElastic_product = InElastic_product[~InElastic_product['name'].isin(df_elasticity['name'])]
        # Create a new DataFrame InElastic_product_rank with unique values in the 'name' column
        InElastic_product_rank = pd.DataFrame({'name': InElastic_product['name'].unique()})
        InElastic_product_rank.reset_index(drop=True, inplace=True)
        InElastic_product_rank.rename(columns={'index': 'Rank'}, inplace=True)
        return Elastic_product_rank,UnitElastic_product_rank,InElastic_product_rank