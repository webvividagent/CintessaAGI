import streamlit as st

def main():
    st.title("CintessaAGI v1.1")

    # Add buttons to the top left
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("Tools"):
            st.write("Tools clicked")
            # Add functionality for tools here
            st.write("This is where you can access various tools.")

    with col2:
        if st.button("Tasks"):
            st.write("Tasks clicked")
            # Add functionality for tasks here
            st.write("This is where you can manage your tasks.")

    with col3:
        if st.button("Personal"):
            st.write("Personal clicked")
            # Add functionality for personal here
            st.write("This is where you can access personal settings and data.")

    with col4:
        if st.button("Business"):
            st.write("Business clicked")
            # Add functionality for business here
            st.write("This is where you can access business-related features.")

    with col5:
        if st.button("Code"):
            st.write("Code clicked")
            # Add functionality for code here
            st.write("This is where you can access code snippets and examples.")

    # Add more functionality as needed
    st.write("Welcome to CintessaAGI v1.1!")

if __name__ == "__main__":
    main()
