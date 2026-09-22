import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Support Analytics", page_icon="📊", layout="wide")

st.title("📊 AI Support Ticket Analytics & Intelligence Platform")
st.markdown("Ask natural language questions about your support tickets and discover anomalies.")

# Health Check
try:
    health = requests.get(f"{API_URL}/health").json()
    st.sidebar.success(f"Backend Status: {health['status'].upper()}")
    st.sidebar.info(f"Tickets Loaded: {health['tickets_loaded']}")
    st.sidebar.info(f"LLM Provider: {health['llm']}")
except Exception as e:
    st.sidebar.error("Backend is unavailable. Please ensure the FastAPI server is running.")

tab1, tab2 = st.tabs(["💬 AI Query", "🚨 Anomalies"])

with tab1:
    st.header("Ask your support data anything")
    
    # Sample Questions
    st.markdown("**Sample Questions:**")
    samples = [
        "How many critical tickets are unresolved?",
        "What is the average resolution time for technical tickets?",
        "Which agent has the lowest customer rating?",
        "Show me all escalated billing tickets.",
        "What percentage of tickets are resolved?"
    ]
    
    selected_sample = st.selectbox("Choose a sample question or type your own:", ["-- Select or Type --"] + samples)
    
    question = st.text_input("Your Question:", value=selected_sample if selected_sample != "-- Select or Type --" else "")
    
    if st.button("Ask AI", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Analyzing data..."):
                try:
                    response = requests.post(f"{API_URL}/query", json={"question": question})
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"**Answer:** {data['answer']}")
                        st.caption(f"Intent interpreted as: `{data['intent']}` | Execution time: {data['execution_time_ms']} ms")
                        
                        result = data['result']
                        if "error" in result:
                            st.error(result['error'])
                        elif "rows" in result:
                            st.dataframe(pd.DataFrame(result['rows']))
                        else:
                            st.json(result)
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {str(e)}")

with tab2:
    st.header("🚨 Anomaly Detection")
    severity_filter = st.selectbox("Filter by Severity:", ["All", "high", "medium", "low"])
    
    if st.button("Refresh Anomalies"):
        with st.spinner("Fetching anomalies..."):
            try:
                url = f"{API_URL}/anomalies"
                if severity_filter != "All":
                    url += f"?severity={severity_filter}"
                
                response = requests.get(url)
                if response.status_code == 200:
                    anomalies = response.json()
                    
                    if not anomalies:
                        st.info("No anomalies found matching the criteria.")
                    else:
                        st.metric("Total Anomalies", len(anomalies))
                        df = pd.DataFrame(anomalies)
                        # Reorder columns
                        df = df[['ticket_id', 'severity', 'anomaly_type', 'reason', 'detected_value', 'threshold']]
                        
                        def highlight_severity(val):
                            color = 'red' if val == 'high' else 'orange' if val == 'medium' else 'yellow'
                            return f'background-color: {color}'
                            
                        st.dataframe(df.style.map(highlight_severity, subset=['severity']))
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Failed to fetch anomalies: {str(e)}")
