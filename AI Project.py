import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

#Configure Gemini
GOOGLE_API_KEY= "AIzaSyDfmhjiNyHwShFbBW4MQL7VxBYM9MPftak"
genai.configure(api_key=GOOGLE_API_KEY)

#iNITIALIZE SESSION STATE
if 'health profile' not in st.session_state:
  st.session_state.health_profile ={
      'goals': 'Lose 10 pounds in 3 months\nImprove cardiovascular health',
      'conditions': 'None',
      'routine': '30-minute walk 4x/week',
      'preferences': 'Vegetarian\nLow Carb',
      'restrictions': 'No Dairy \nNo Nuts'
  }

  #Function to Get Gemini Response
  def get_gemini_response(input_prompt, image_data=None):
    model = genai.GenerativeModel('gemini-2.5-flash')

    content = [input_prompt]

    if image_data:
      content.extend(image_data)

    try:
      response = model.generate_content(content)
      return response.text
    except Exception as e:
      st.error(f"Error getting Gemini response: {str(e)}")

  def input_image_setup(uploaded_file):
    if uploaded_file is not None:
      bytes_data = uploaded_file.getvalue()
      image_parts = [{
          "mime_type": uploaded_file.type,
          "data": bytes_data
      }]
      return image_parts
    return None
  # App layout
  st.set_page_config(page_title="AI Health Comapanion", layout="wide")
  st.header(" AI Health Companion - Your Personal AI Doctor")

  # Sidebar for health profile
  with st.sidebar:
    st.subheader("Your Health Profile")

    health_goals = st.text_area("Health Outcomes you expect",
                                value=st.session_state.health_profile['goals'])
    medical_conditions = st.text_area("Your Medical Conditon",
                                      value=st.session_state.health_profile['conditions'])
    fitness_routines = st.text_area("Your Fitness Routine",
                                    value=st.session_state.health_profile['routine'])
    food_preferences = st.text_area("Food Preferences",
                                    value=st.session_state.health_profile['preferences'])
    restrictions = st.text_area("Inevitable Dietary Restrictions",
                                value=st.session_state.health_profile['restrictions'])

    if st.button("Update Health Profile"):
      st.session_state.health_profile = {
        'goals': health_goals,
        'conditions': medical_conditions,
        'routine': fitness_routines,
        'preferences': food_preferences,
        'restrictions': restrictions
      }
      st.success("Health profile updated successfully!")

  #Main content Area
  tab1, tab2, tab3 = st.tabs(["Meal Planning And Check", "Food Analysis", "Health Insightful Check Ups"])

  with tab1:
    st.subheader("Personalized Meal Planning and Diet Check-up")

    col1, col2 = st.columns(2)

    with col1:
      st.write("Your Current Needs (Important ones)")
      user_input = st.text_area("Describe your current needs and preferences",
                                placeholder="e.g., 'I need quick meal for work'"
                                )

    with col2:
      st.write("Your Health Profile")
      st.json(st.session_state.health_profile)

    if st.button("Generate My Personalized Meal Plan"):
      if not any(st.session_state.health_profile.values()):
        st.warning("Please update your health profile first in the sidebar")
      else:
        with st.spinner("Wait A Minute For Personalized Meal Plan..."):
          #Construct the prompt

          prompt = f"""

          Create a personalized meal plan based on the following health preferences
          Health Goals: {st.session_state.health_profile['goals']}
          Medical Condition: {st.session_state.health_profile['conditions']}
          Fitness Routine: {st.session_state.health_profile['routine']}
          Food Preferences: {st.session_state.health_profile['preferences']}
          Dietary Restrictions: {st.session_state.health_profile['restrictions']}

          Additional requirements: {user_input if user_input else 'None'}

          Provide:
          1. A 7-day meal plan with breakfast, lunch, dinner, and snacks
          2. Nutritional breakdown for each day (Calories, macros)
          3. Contextual explanantion for why each meal was chosen
          4. Shopping list organized by category
          5. Preperation tips and time-saving suggestions

          Format the output clearly with heading and bullet points.
          """

          #Get the response from Gemini
          response = get_gemini_response(prompt)

          st.subheader("Your Personalized Meal Plan is Ready!!")
          st.markdown(response)

          # add download button
          st.download_button(
              label="Download Meal Plan",
              data=response,
              file_name="meal_plan.txt",
              mime="text/plain"
          )

  with tab2:
    st.subheader("Food Analysis")

    uploaded_file = st.file_uploader("Upload a food image",
                                     type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
      image = Image.open(uploaded_file)
      st.image(image, caption="Uploaded Image", use_column_width=True)

      if st.button("Analyze Food"):
        with st.spinner("Analyzing Food..."):
          image_data = input_image_setup(uploaded_file)

          prompt = f"""
          You are an expert nutritionist. Analyse this food image.

          Provide detailed nutritional information about:
          - Estimates calories
          - Macronutrient breakdown
          - Potential health benefits
          - Any concerns based on coomn dietary restrictiones
          - Suggested portion sizes

          If the food contains multiple items, analyze each seperately.
          """

          response = get_gemini_response(prompt, image_data)
          st.subheader("Analysis Results")
          st.markdown(response)
  with tab3:
    st.subheader("Health Insightful Check-ups")

    health_Query = st.text_input("Ask any Health Related Question",
                                 placeholder="e.g., 'How can I improve my Breathing?")
    if st.button("Get Expert Insight"):
      with st.spinner("Getting Health Insight..."):
        prompt = f"""
        You are a certified nutritionist and health expert.
        Provide detailed, science-backed insights about:
        {health_Query}

        Consider the user's health profile:
        {st.session_state.health_profile}

        Include:
        1. Clear explanation of science
        2. Practical recommendations
        3. Any relevant Precautions
        4. Reference to studies(if applicable)
        5. Suggested foods/supplements if appropriate

        Use simple language but maintain accuracy.
        """

        response = get_gemini_response(prompt)
        st.subheader("Expert Health Insight")
        st.markdown(response)
