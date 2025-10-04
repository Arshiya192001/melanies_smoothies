# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# App Title
st.title("Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake and get fruit list
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_options = [row['FRUIT_NAME'] for row in my_dataframe.collect()]

# Fruit selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:", fruit_options, max_selections=5
)

# 🍎 Show nutrition info for each selected fruit
if ingredients_list:
    st.subheader("Nutritional Information for your choices")
    for fruit_chosen in ingredients_list:
        try:
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
            if fruityvice_response.status_code == 200:
                fruity_data = fruityvice_response.json()
                # Display simple nutrition info
                st.write(f"**{fruit_chosen}**")
                st.write(f"- Calories: {fruity_data['nutritions']['calories']}")
                st.write(f"- Sugar: {fruity_data['nutritions']['sugar']} g")
                st.write(f"- Carbohydrates: {fruity_data['nutritions']['carbohydrates']} g")
                st.write(f"- Protein: {fruity_data['nutritions']['protein']} g")
                st.write(f"- Fat: {fruity_data['nutritions']['fat']} g")
            else:
                st.warning(f"Nutritional data not found for {fruit_chosen}")
        except Exception as e:
            st.error(f"Error fetching nutrition for {fruit_chosen}: {e}")

    # Save smoothie order to Snowflake
    ingredients_string = ' '.join(ingredients_list)
    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
