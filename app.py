import streamlit as st
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# Load custom CSS for styling
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# Define states to manage user interaction
class State:
    INITIAL = "initial"
    GENERATE_CLICKED = "generate_clicked"
    SUBMIT_DECISION = "submit_decision"

def generate_dilemma(model):
    prompt_template = (
        "system: You are an AI specialized in generating compelling and thought-provoking "
        "ethical dilemmas that are short, easy to understand, and engaging.\n"
        "user: Generate a unique ethical dilemma for an Ethical Dilemma Simulator. "
        "It should ask all sorts of dilemma questions. "
        "Dont ask repetitive questions, make sure each dilemma is not same themed/ similar to the previous dilemma you generate"
        "The dilemma should be very brief, clear, and engaging. It should present a challenging decision "
        "that involves making the user ponder about what they should do, make them creative, abstract, and interesting. "
        "Ensure the scenario is understandable to a wide audience.\n"
        "assistant: "
    )

    message = HumanMessage(content=prompt_template)
    response = model.stream([message])
    
    # Collect all chunks of the response
    response_texts = [chunk.content for chunk in response]
    dilemma = ''.join(response_texts).strip()
    
    # Remove asterisks and format the text properly
    dilemma = dilemma.replace('*', '')
    
    return dilemma

def provide_perspectives(model, decision, dilemma):
    perspectives_template = (
        "system: Welcome! I'm here to analyze your decision from multiple ethical perspectives.\n"
        "user: Decision: {decision}\n"
        "Dilemma: {dilemma}\n"
        "assistant: Let's delve into the decision you made, exploring its implications and potential outcomes.\n"
        "Tell me the possible future consequences of my choice. "
        "Your analysis should be fun and very brief to read."
    )

    prompt = perspectives_template.format(decision=decision, dilemma=dilemma)
    message = HumanMessage(content=prompt)
    response = model.stream([message])
    
    # Collect all chunks of the response
    response_texts = [chunk.content for chunk in response]
    
    perspectives = ' '.join(response_texts).strip()  # Concatenate into a single string
    
    # Remove asterisks and format the text properly (if needed)
    perspectives = perspectives.replace('*', '')
    
    return perspectives

def main():
    st.title('SparkDilemmaX')
    st.header('The Ethical Predicament Simulator')

    # User input for API key
    api_key = st.text_input("Enter your Google API Key", type="password")
    
    if api_key:
        # Set the Google API key as an environment variable
        os.environ['GOOGLE_API_KEY'] = api_key

        # Initialize the model
        model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

        # Manage app state
        state = st.session_state.get("state", State.INITIAL)

        if state == State.INITIAL:
            # Generate Dilemma Button
            if st.button('Generate Dilemma'):
                st.session_state.state = State.GENERATE_CLICKED
                st.info('Generating new dilemma...click on the generate button again to view')
        
        elif state == State.GENERATE_CLICKED:
            # Show generated dilemma
            dilemma = generate_dilemma(model)
            st.success('Dilemma Generated Successfully!')
            st.markdown(f'### Dilemma\n{dilemma}')

            # Decision Form
            decision = st.text_area('Your Decision, please be elaborate to get better analysis:', '')
            if st.button('Submit Decision'):
                st.session_state.state = State.SUBMIT_DECISION
                st.info('Analyzing perspectives...')
                perspectives = provide_perspectives(model, decision, dilemma)
                st.success('Perspectives Analyzed Successfully!')
                st.markdown(f'### Perspectives\n{perspectives}')
                st.info('Scroll up to view the newly generated dilemma.')
    else:
        st.warning("Please enter your Google API Key to proceed.")

if __name__ == '__main__':
    main()
