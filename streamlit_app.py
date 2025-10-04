import streamlit as st
import requests
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want for your custom smoothie!")

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit list from Snowflake
df = session.table("smoothies.public.fruit_options").select(col("Fruit_Name"))
fruit_rows = df.collect()
fruit_options = [row["Fruit_Name"] for row in fruit_rows]

# Multiselect UI
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:", fruit_options, max_selections=5
)

if ingredients_list:
    st.subheader("Nutritional Information for Selected Fruits")
    # Prepare to accumulate overall nutrition if needed
    # For each selected fruit, call the API and display results
    for fruit in ingredients_list:
        st.markdown(f"**{fruit}**")
        try:
            resp = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit}")
            if resp.status_code == 200:
                data = resp.json()
                # Show JSON as dataframe (1 row)
                st.dataframe(data, use_container_width=True)
            else:
                st.warning(f"Could not fetch nutrition for **{fruit}** (Status {resp.status_code})")
        except Exception as e:
            st.error(f"Error fetching for {fruit}: {e}")

    # Build the insert statement
    ingredients_string = " ".join(ingredients_list)
    insert_sql = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.write("SQL to run:", insert_sql)

    if st.button("Submit Order"):
        session.sql(insert_sql).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
