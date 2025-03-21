from datetime import datetime as dt    
import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules
from scipy.sparse import csr_matrix
from collections import defaultdict
import re

class recommandation:
    def __init__(self, df):
        self.df = df
        self.df1=self.recomendation_by_customer()
        self.df2=self.recomendation_by_product()
        self.df3=self.find_common_products()
        self.df4=self.mba()
        self.df5=self.convert_to_frozensets()
         
    def recomendation_by_customer (self):
        df=self.df
        df_crosstab = pd.crosstab(df['CUST_ID'], df['CAT_ID'])
        # if the value is more than 1 then replace it with 1
        df_crosstab[df_crosstab > 1] = 1
        # Do a total column wise
        df_crosstab['total_column'] = df_crosstab.sum(axis=1)
        # find the 90 percentile value
        ninety_percentile = np.percentile(df_crosstab['total_column'], 90)
        # keep only the top 90 percentile customers
        df_cat_crosstab_90 = df_crosstab[df_crosstab['total_column'] >= ninety_percentile]
        CT1 =df_crosstab.copy()
        CT2 =df_cat_crosstab_90.copy()
        jaccard_scores = {} # Creating an empty dictionary to store the Jaccard scores
        for cust_id1, row1 in CT1.iterrows(): # Creating a for loop to iterate through the rows of CT1
            jaccard_scores[cust_id1] = [] # Creating an empty list to store the Jaccard scores
            for cust_id2, row2 in CT2.iterrows(): # Creating a for loop to iterate through the rows of CT2
                intersection = row1 & row2 # Calculating the intersection of the rows
                union = row1 | row2 # Calculating the union of the rows
                jaccard_score = intersection.sum() / union.sum() # Calculating the Jaccard score
                jaccard_scores[cust_id1].append((cust_id2, jaccard_score)) # Appending the Jaccard score to the list
            jaccard_scores[cust_id1].sort(key=lambda x: x[1], reverse=True) # Sorting the list in descending order
            jaccard_scores[cust_id1] = [score[0] for score in jaccard_scores[cust_id1][:5]] # Selecting the top 5 customers

        n_dic=jaccard_scores.copy()
        cm_mat=df_crosstab.copy()

        prod = {} # Creating an empty dictionary to store the recommended products

        for i in n_dic.keys(): # Creating a for loop to iterate through the keys of n_dic
            prod[i] = () # Creating an empty tuple to store the recommended products

        for i in n_dic.keys(): # Creating a for loop to iterate through the keys of n_dic
            ncust = n_dic.get(i) # Storing the value of the key in ncust
            ncust.append(i) # Appending the key to ncust
            custprod_mat = cm_mat[cm_mat.index.isin(ncust)] # Creating a matrix with the customers in ncust
            custprod_mat.loc['coltotal'] = custprod_mat.sum() # Calculating the column total
            custprod_df = custprod_mat[custprod_mat.columns[custprod_mat.loc['coltotal'] != 0]] # Removing the columns with 0 values

            for b in custprod_df.index[~custprod_df.index.isin(['coltotal'])]: # Creating a for loop to iterate through the index of custprod_df
                c_b = custprod_df.loc[[b, 'coltotal']].T # Transposing the matrix
                c_b1 = c_b[c_b.iloc[:, 0] == 0] # Selecting the rows with 0 values
                c_b2 = np.round(c_b1[['coltotal']] / len(custprod_df), 3) # Calculating the percentage of 0 values
                c_l = list(c_b2.itertuples(name=None)) # Converting the dataframe to a list
                c_l = tuple(c_l) # Converting the list to a tuple
                prod[b] = prod[b] + c_l # Appending the tuple to the dictionary
                l1 = prod.get(b) # Storing the value of the key in l1
                l1_df = pd.DataFrame(l1, columns=['P_Name', 'rank']) # Creating a dataframe from the list
                l1_df1 = pd.DataFrame(l1_df.groupby('P_Name')['rank'].max()) # Calculating the maximum rank
                l1_df2 = l1_df1.sort_values(by=['rank'], ascending=False) # Sorting the dataframe in descending order
                list_of_tuples = l1_df2.to_records().tolist() # Converting the dataframe to a list of tuples
                tuple_of_tuples = tuple(list_of_tuples) # Converting the list to a tuple of tuples
                prod[b] = tuple_of_tuples # Storing the tuple of tuples in the dictionary

        recommended_products_dict=prod.copy()
        recomendation_customer = pd.DataFrame.from_dict(recommended_products_dict, orient='index')
        return recomendation_customer
   
    def recomendation_by_product (self):
        df=self.df
        p1=pd.crosstab(index=df['CAT_ID'],columns=df['CUST_ID'])   ## making a cross tab where rows are unique customers and columns are unique models
        p1[p1!=0]=1  ## substituting non zero values with 1 in the cross tab
        row_total=pd.DataFrame(p1.sum(axis=1),columns=['total'])  ## calculating sum for each row
        col_total=pd.DataFrame(p1.sum(axis=0),columns=['total'])  ## calculating sum for each column
        X = np.asmatrix(p1.values,dtype=np.float64) ## converting cross tab into a matrix
        sX = csr_matrix(X) ## converting X matrix into a sparse matrix
        numerator = sX.dot(sX.T)  ## calculating the numerator of the jaccared index i.e. the intersection part of the customers
        ones = np.ones(sX.shape[::-1],dtype=np.float64)  ## creating a unit matrix
        B = sX.dot(ones) ## multiplying the sparse matrix with unit matrix
        C=B+B.T ## Adding the matrix B & B transpose
        denominator=C-numerator ## calculating denominator of the jaccared index i.e. the union part of the customers
        j_matrix=numerator/denominator ## calculating jaccared index for each customer pair by dividing numerator and denominator
        j_matrix1=j_matrix.toarray() ## converting sparse matrix into a dense matrix : Scipy library change
        uppert_matrix=np.triu(j_matrix1,k=1)  ## considering only upper traingular matrix with diagonal elements 0.
        j_nonzero=pd.DataFrame(uppert_matrix[uppert_matrix > 0],columns=['j_index'])  ## considering only the non-zero elements of the upper traingular matrix
        j_matrix2=1-j_matrix1  ## calculating the distance for each pair of products
        j_matrix2[np.diag_indices_from(j_matrix1)] = np.nan  ## replacing the value of diagonal elements with 'nan' value of the distance matrix
        j_matrix1_df=pd.DataFrame(j_matrix2,index=p1.index,columns=p1.index)  ## converting distance matrix into a df and adding product ids
        x={}
        for i in j_matrix1_df.columns:

            u_df=j_matrix1_df[[i]]   ## getting the ith product column from the distance matrix
            u_df1=u_df[~ (u_df[i].isna())]   ## excluding the 'nan' value
            u_df1=u_df1[~ (u_df1[i]==1)]  ## excluding those products whose distance is 1 i.e. 100% from the ith product
            u_df2=u_df1.sort_values(by=[i])   ## sorting the distance values in ascending order
            u_df2=u_df2.reset_index()       ## resetting the df index
            x[i]=[tuple(r) for r in u_df2.to_numpy()]
        prodpair_list=x.copy()
        cust_list = p1.columns#[:1000]
        suggested_prod_list={}
        for i in cust_list:
       
            suggested_prod_list[i]=[]  ## creating keys in the empty dictionary for each custmer present in customer list
            m1=p1[[i]]    ## getting the i th customer column from the binary matrix  
            m_1=m1[m1[i]==1]   ## getting the product ids bought by ith customer
            purchased_prod=list(m_1.index)  ## making a list of product ids bought by ith customer
            filtered_d = dict((k, prodpair_list[k]) for k in purchased_prod if k in prodpair_list)  ## filtering the product neighbour dict according to purchased_prod list
            m_2=m1[m1[i]==0]  ## getting the product ids which are not bought by ith customer
            nonpurchased_prod=list(m_2.index)  ## making a list of product ids which are not bought by ith customer
       
            for j in purchased_prod:  ## generating a for loop on the purchased_prod list
                nprod=filtered_d.get(j)  ## filtering the filtered_d dict based on j th product and getting the neighbour list for j th prod
                df=pd.DataFrame.from_records(nprod, columns =['prod','distance'])  ## creating a df from the list of tuples
                df1=df[df['prod'].isin(nonpurchased_prod)].head(1)  ## filtering the above df based on nonpurchased product list of ith customer and capturing only the first non purchased product with its rank (i.e. distance) if there is any nonpurchased product from the neighbour list of j th purchased product of ith customer
                   
                if len(df1.index)!=0:   ## if the above df  is not empty then
                    tup1=[(k, v) for k, v in zip(df1['prod'],df1['distance'])][0]  ## make a tuple from the above df i.e. ('nonpurchased_prod_id','rank')
                    suggested_prod_list[i].append(tup1)  ## appending the tuple in the list of ith customer's recommended product list
        for k in suggested_prod_list.keys():
           
            l1=suggested_prod_list.get(k)  ## getting the recommended products for b th customer                 
            l1_df = pd.DataFrame(l1, columns =['P_Name', 'rank'])  ## converting the tuple of recommended products to a df      
            l1_df1=pd.DataFrame(l1_df.groupby('P_Name')['rank'].max())  ## groupby the df wrt unique products with highest rank   
            l1_df2=l1_df1.sort_values(by=['rank'],ascending=True)  ## sorting the unique recommended products according to ranks
            list_of_tuples = l1_df2.to_records().tolist()  ## converting the dataframe to a list of tuples
            suggested_prod_list[k]=list_of_tuples  ## final list of recommended products for b th customer
        df_rec_prod = pd.DataFrame.from_dict(suggested_prod_list, orient='index')
        # add a index label s as "CUST_ID"
        df_rec_prod.index.name = 'CUST_ID'
        return df_rec_prod
   
    def find_common_products(self):
        df1=self.df1
        df2=self.df2
        common_products = {} # Creating an empty dictionary to store the common products
        # Iterate over the row indexes (customer ids) of the first dataframe
        for customer_id in df1.index:
            # Check if the customer ID exists in both dataframes
            if customer_id in df2.index:
                # Get the products for the current customer from both dataframes
                products1 = set([item[0] for item in df1.loc[customer_id] if pd.notnull(item)]) # Creating a set of the products
                products2 = set([item[0] for item in df2.loc[customer_id] if pd.notnull(item)]) # Creating a set of the products
           
                # Find the common products for the current customer
                common_products[customer_id] = list(products1.intersection(products2)) # Creating a list of the common products
   
        # Create a new dataframe with the common products
        df_common = pd.DataFrame.from_dict(common_products, orient='index') # Creating a dataframe from the dictionary
        df_common.index.name = 'Customer' # Renaming the index column
        #df_common.set_index('Customer', inplace=True)
        # appenindg Recomendation to each column name
        
        df_common.columns = ['Recommendation_' + str(col) for col in df_common.columns] # Renaming the columns
        # change itesm to intgers
        df_common = df_common.astype('Int64') # Changing the datatype of the dataframe to integer
        df_common.reset_index(inplace=True)
        return df_common
    
    def mba(self):
        threshold = 0.01  # Adjust the minimum support threshold as needed
        df_original = self.df
        basket = df_original.groupby(['VISIT_ID', 'CAT_ID']).size().unstack().fillna(0)
        basket[basket != 0] = 1
        basket.max(axis=1).sum()
        minTransaction = len(basket.index) * threshold
        totalTransactions = len(basket.index)
        min_support_calc = minTransaction / totalTransactions

        # Perform frequent itemset mining
        frequent_itemsets = fpgrowth(basket, min_support=min_support_calc, use_colnames=True)
        frequent_itemsets.describe()

        # Adjust the minimum threshold for association rules to capture more rules
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=0.2)  # Adjust the threshold as needed
        rules.sort_values('confidence', ascending=False, inplace=True)
        
        return rules

    def convert_to_frozensets(self):
        dataframe=self.df4
        # Iterate over each column in the DataFrame
        for column in dataframe.columns:
            # Convert the column to a frozenset and update the DataFrame
            dataframe[column] = dataframe[column].apply(lambda x: frozenset(map(int, re.findall(r'\d+', str(x)))))
        return dataframe
    
    def final_recomendations(self):
        df=self.df
        df_common=self.df3
        basket_P = df.groupby(['CUST_ID','CAT_ID']).size().unstack().fillna(0)    
        basket_P[basket_P!=0]=1
        basket_P['purchases'] = basket_P.apply(lambda x: tuple(x.index[x==1]), axis=1)
        basket_P['purchases'] = basket_P['purchases'].apply(lambda x: frozenset(x))
        # drop all columns except purchases
        basket_P.drop(columns=basket_P.columns.difference(['purchases']), inplace=True)
        basket_P['recomendations'] = None
        for index, row in basket_P.iterrows():
            cust_id = index
            recomendations = df_common[df_common ['Customer'] == cust_id].iloc[:, 0:].values.tolist()
            recomendations = [item for sublist in recomendations for item in sublist]
            # remove the nan values
            recomendations = [x for x in recomendations if str(x) != 'nan']
            # make it int 
            recomendations = [int(x) if pd.notna(x) else 0 for x in recomendations]
            recomendations = frozenset(recomendations)
            basket_P.at[cust_id, 'recomendations'] = recomendations
        df_mba=self.df4
        recommendations = defaultdict(set)
        for _, row in basket_P.iterrows():
            purchases = row['purchases']
            for _, mba_row in df_mba.iterrows():
                antecedent = frozenset(mba_row['antecedents'])  # Convert antecedent to a frozenset
                consequent = mba_row['consequents']
                confidence = mba_row['confidence']
                if antecedent.issubset(purchases) and isinstance(confidence, (int, float)) and confidence >= 0:
                    recommendations[row.name].update(consequent)

        rec_mba_column = [recommendations.get(cust_id, set()) for cust_id in basket_P.index]
        basket_P['recommendation_mba'] = rec_mba_column
        # change the datatype to frozenset
        basket_P['recommendation_mba'] = basket_P['recommendation_mba'].apply(lambda x: frozenset(x))
        basket_P['recommendation_mba'] = basket_P.apply(lambda x: x['recommendation_mba'] - x['purchases'], axis=1)
        basket_P['common'] = None
        for index, row in basket_P.iterrows():
            common = row['recomendations'].intersection(row['recommendation_mba'])
            # if common is empty then set it to None
            if len(common) == 0:
                common = None
            basket_P.at[index, 'common'] = common
        return basket_P
    
