# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests 
import pandas as pd

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input('Name on Smoothie: ')
st.write('The name on your Smoothie will be: ', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# Add new coumn to dataframe which feeds multiselect
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
# Uncomment for visual
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()    # Focus on this section

# Convert snowpark dataframe to pandas dataframe for LOC function usage
pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
)

# if list is null, then don't display
if ingredients_list:
    # create var for storing list as a string
    ingredients_string = ''

    # loop to add ingredients into list
    for each_fruit in ingredients_list:
      ingredients_string += each_fruit + ' '

      # Gets search-on value
      search_on = pd_df.loc[pd_df['FRUIT_NAME'] == each_fruit, 'SEARCH_ON'].iloc[0]
      st.write('The search value for ', each_fruit,' is ', search_on, '.')
      
      # Section to display smoothiefruit nutrition information 
      st.subheader(each_fruit + ' Nutrition Information')
      smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/{search_on}")  
      sf_df = st.dataframe(data = smoothiefroot_response.json(), use_container_width = True)

    # output string
    #st.write(ingredients_string)

    # SQL insert statement with test
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                        values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    #st.write(my_insert_stmt)
    #st.stop()

    time_to_insert = st.button('Submit Order')

    # Instead of the string having a value, use submit button to send sql statement
    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")

  






