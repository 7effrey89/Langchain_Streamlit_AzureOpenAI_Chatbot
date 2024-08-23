import streamlit as st
#Icons
#https://mui.com/material-ui/material-icons/

#this page is to define the navigation and the pages to be displayed. Will by default redirect user to the first page in the list
Langchain_SimpleHistory = st.Page("Langchain_SimpleHistory.py", title="Simple History Implementation", icon=":material/language:")
Langchain_ComplexHistory = st.Page("Langchain_ComplexHistory.py", title="Complex History Implementation", icon=":material/language:")

pg = st.navigation({
    "Langchain" : [Langchain_SimpleHistory, Langchain_ComplexHistory]
    })
st.set_page_config(page_title="Streamlit", page_icon=":material/edit:")
pg.run()


# 2. Create environment
# python -m venv .venv

# 3. Activate the environment
#.venv\Scripts\activate

# To run our demo
#pip install -r requirements.txt
# python -m streamlit run main.py

#debugging in vscode:
#add the launch.json to .vscode folder

#on the leftside click on the Run and Debug icon, then on the dropdown select the configuration from the launch.json file
#choose the file you want to debug from the fileexplorer, and click on the green play button to start debugging