# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import os
# import tempfile
# from main import ReviewerRecommendationSystem

# # Page configuration
# st.set_page_config(
#     page_title="Reviewer Recommendation System",
#     page_icon="📄",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 2.5rem;
#         font-weight: bold;
#         color: #1f77b4;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
#     .metric-card {
#         background-color: #f0f2f6;
#         padding: 1rem;
#         border-radius: 0.5rem;
#         margin: 0.5rem 0;
#     }
#     .author-card {
#         background-color: #ffffff;
#         border: 2px solid #e0e0e0;
#         border-radius: 0.5rem;
#         padding: 1rem;
#         margin: 0.5rem 0;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#     }
#     .score-badge {
#         display: inline-block;
#         padding: 0.25rem 0.5rem;
#         border-radius: 0.25rem;
#         font-weight: bold;
#         margin: 0.25rem;
#     }
#     .score-high {
#         background-color: #90ee90;
#         color: #006400;
#     }
#     .score-medium {
#         background-color: #ffd700;
#         color: #8b4513;
#     }
#     .score-low {
#         background-color: #ffcccb;
#         color: #8b0000;
#     }
# </style>
# """, unsafe_allow_html=True)


# def initialize_session_state():
#     """Initialize session state variables"""
#     if 'recommender' not in st.session_state:
#         st.session_state.recommender = None
#     if 'authors_loaded' not in st.session_state:
#         st.session_state.authors_loaded = False
#     if 'recommendations' not in st.session_state:
#         st.session_state.recommendations = None
#     if 'processing' not in st.session_state:
#         st.session_state.processing = False


# def load_authors_data(output_dir):
#     """Load authors data with progress tracking"""
#     with st.spinner("Loading authors data..."):
#         recommender = ReviewerRecommendationSystem(output_dir=output_dir)
#         recommender.load_authors_data()
#         st.session_state.recommender = recommender
#         st.session_state.authors_loaded = True
#     return recommender


# def get_score_class(score):
#     """Get CSS class based on score value"""
#     if score >= 0.7:
#         return "score-high"
#     elif score >= 0.4:
#         return "score-medium"
#     else:
#         return "score-low"


# def display_author_card(rank, author, scores):
#     """Display author information in a styled card"""
#     score_class = get_score_class(scores['hybrid_score'])
    
#     st.markdown(f"""
#     <div class="author-card">
#         <h3>#{rank} {author}</h3>
#         <div class="score-badge {score_class}">
#             Hybrid Score: {scores['hybrid_score']:.4f}
#         </div>
#     </div>
#     """, unsafe_allow_html=True)
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.metric("TF-IDF Score", f"{scores['tfidf_score']:.4f}")
    
#     with col2:
#         st.metric("Semantic Score", f"{scores['semantic_score']:.4f}")
    
#     with col3:
#         st.metric("Paper Count", scores['paper_count'])
    
#     if scores.get('keywords'):
#         st.markdown(f"**Top Keywords:** {', '.join(scores['keywords'])}")


# def create_score_comparison_chart(recommendations):
#     """Create interactive comparison chart for scores"""
#     df = pd.DataFrame([
#         {
#             'Author': author,
#             'TF-IDF': scores['tfidf_score'],
#             'Semantic': scores['semantic_score'],
#             'Hybrid': scores['hybrid_score']
#         }
#         for author, scores in recommendations
#     ])
    
#     fig = go.Figure()
    
#     fig.add_trace(go.Bar(
#         name='TF-IDF Score',
#         x=df['Author'],
#         y=df['TF-IDF'],
#         marker_color='lightblue'
#     ))
    
#     fig.add_trace(go.Bar(
#         name='Semantic Score',
#         x=df['Author'],
#         y=df['Semantic'],
#         marker_color='lightgreen'
#     ))
    
#     fig.add_trace(go.Bar(
#         name='Hybrid Score',
#         x=df['Author'],
#         y=df['Hybrid'],
#         marker_color='coral'
#     ))
    
#     fig.update_layout(
#         title='Reviewer Scores Comparison',
#         xaxis_title='Authors',
#         yaxis_title='Score',
#         barmode='group',
#         height=500,
#         hovermode='x unified'
#     )
    
#     return fig


# def create_radar_chart(recommendations, top_n=5):
#     """Create radar chart for top reviewers"""
#     top_recommendations = recommendations[:top_n]
    
#     fig = go.Figure()
    
#     for author, scores in top_recommendations:
#         fig.add_trace(go.Scatterpolar(
#             r=[scores['tfidf_score'], scores['semantic_score'], scores['hybrid_score']],
#             theta=['TF-IDF', 'Semantic', 'Hybrid'],
#             fill='toself',
#             name=author
#         ))
    
#     fig.update_layout(
#         polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
#         showlegend=True,
#         title=f'Top {top_n} Reviewers - Score Breakdown',
#         height=500
#     )
    
#     return fig


# def create_score_distribution(recommendations):
#     """Create distribution chart for hybrid scores"""
#     scores = [scores['hybrid_score'] for _, scores in recommendations]
    
#     fig = go.Figure()
    
#     fig.add_trace(go.Histogram(
#         x=scores,
#         nbinsx=20,
#         marker_color='steelblue',
#         opacity=0.7
#     ))
    
#     fig.update_layout(
#         title='Hybrid Score Distribution',
#         xaxis_title='Hybrid Score',
#         yaxis_title='Number of Authors',
#         height=400
#     )
    
#     return fig


# def main():
#     initialize_session_state()
    
#     # Header
#     st.markdown('<div class="main-header">Reviewer Recommendation System</div>', unsafe_allow_html=True)
    
#     # Sidebar
#     with st.sidebar:
#         st.header("Configuration")
        
#         output_dir = st.text_input(
#             "Authors Data Directory",
#             value="output",
#             help="Directory containing author metadata files"
#         )
        
#         st.divider()
        
#         st.subheader("Scoring Weights")
#         tfidf_weight = st.slider(
#             "TF-IDF Weight (Lexical)",
#             min_value=0.0,
#             max_value=1.0,
#             value=0.4,
#             step=0.1,
#             help="Weight for lexical similarity"
#         )
        
#         semantic_weight = st.slider(
#             "Semantic Weight",
#             min_value=0.0,
#             max_value=1.0,
#             value=0.6,
#             step=0.1,
#             help="Weight for semantic similarity"
#         )
        
#         if abs((tfidf_weight + semantic_weight) - 1.0) > 0.01:
#             st.warning("Weights should sum to 1.0")
        
#         st.divider()
        
#         k_reviewers = st.number_input(
#             "Number of Top Reviewers",
#             min_value=1,
#             max_value=50,
#             value=10,
#             step=1
#         )
        
#         st.divider()
        
#         if st.button("Load Authors Data", type="primary", use_container_width=True):
#             if os.path.exists(output_dir):
#                 load_authors_data(output_dir)
#                 st.success(f"Loaded {len(st.session_state.recommender.authors_data)} authors")
#             else:
#                 st.error(f"Directory not found: {output_dir}")
    
#     # Main content
#     if not st.session_state.authors_loaded:
#         st.info("Please load authors data from the sidebar to begin.")
#         st.markdown("""
#         ### Getting Started
#         1. Ensure you have processed the dataset using the data extraction pipeline
#         2. Configure the authors data directory in the sidebar
#         3. Click 'Load Authors Data'
#         4. Upload a candidate paper to get reviewer recommendations
#         """)
#         return
    
#     # Show loaded authors summary
#     st.success(f"Authors loaded: {len(st.session_state.recommender.authors_data)}")
    
#     # File upload
#     st.header("Upload Candidate Paper")
#     uploaded_file = st.file_uploader(
#         "Choose a PDF file",
#         type=['pdf'],
#         help="Upload the research paper that needs reviewers"
#     )
    
#     if uploaded_file is not None:
#         # Save uploaded file temporarily
#         with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
#             tmp_file.write(uploaded_file.getvalue())
#             tmp_path = tmp_file.name
        
#         col1, col2 = st.columns([3, 1])
        
#         with col1:
#             st.info(f"File uploaded: {uploaded_file.name}")
        
#         with col2:
#             if st.button("Find Reviewers", type="primary", use_container_width=True):
#                 st.session_state.processing = True
        
#         if st.session_state.processing:
#             with st.spinner("Analyzing paper and computing similarity scores..."):
#                 try:
#                     # Get recommendations
#                     recommendations = st.session_state.recommender.get_top_reviewers(
#                         candidate_pdf=tmp_path,
#                         k=k_reviewers,
#                         tfidf_weight=tfidf_weight,
#                         semantic_weight=semantic_weight
#                     )
                    
#                     st.session_state.recommendations = recommendations
#                     st.session_state.processing = False
                    
#                     # Clean up temp file
#                     os.unlink(tmp_path)
                    
#                     st.success("Analysis complete!")
                    
#                 except Exception as e:
#                     st.error(f"Error during analysis: {e}")
#                     st.session_state.processing = False
#                     if os.path.exists(tmp_path):
#                         os.unlink(tmp_path)
    
#     # Display recommendations
#     if st.session_state.recommendations:
#         st.header("Recommendation Results")
        
#         # Tabs for different views
#         tab1, tab2, tab3, tab4 = st.tabs(["Top Reviewers", "Score Analysis", "Detailed Comparison", "Export"])
        
#         with tab1:
#             st.subheader(f"Top {k_reviewers} Recommended Reviewers")
            
#             for i, (author, scores) in enumerate(st.session_state.recommendations, 1):
#                 with st.expander(f"#{i} {author} - Score: {scores['hybrid_score']:.4f}", expanded=(i <= 3)):
#                     display_author_card(i, author, scores)
        
#         with tab2:
#             st.subheader("Score Visualizations")
            
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 fig_comparison = create_score_comparison_chart(st.session_state.recommendations)
#                 st.plotly_chart(fig_comparison, use_container_width=True)
            
#             with col2:
#                 fig_distribution = create_score_distribution(st.session_state.recommendations)
#                 st.plotly_chart(fig_distribution, use_container_width=True)
            
#             fig_radar = create_radar_chart(st.session_state.recommendations, top_n=5)
#             st.plotly_chart(fig_radar, use_container_width=True)
        
#         with tab3:
#             st.subheader("Detailed Score Comparison")
            
#             df = pd.DataFrame([
#                 {
#                     'Rank': i + 1,
#                     'Author': author,
#                     'Hybrid Score': scores['hybrid_score'],
#                     'TF-IDF Score': scores['tfidf_score'],
#                     'Semantic Score': scores['semantic_score'],
#                     'Papers': scores['paper_count'],
#                     'Keywords': ', '.join(scores.get('keywords', []))
#                 }
#                 for i, (author, scores) in enumerate(st.session_state.recommendations)
#             ])
            
#             st.dataframe(
#                 df,
#                 use_container_width=True,
#                 hide_index=True,
#                 column_config={
#                     "Hybrid Score": st.column_config.ProgressColumn(
#                         "Hybrid Score",
#                         format="%.4f",
#                         min_value=0,
#                         max_value=1,
#                     ),
#                 }
#             )
        
#         with tab4:
#             st.subheader("Export Recommendations")
            
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 csv = df.to_csv(index=False)
#                 st.download_button(
#                     label="Download as CSV",
#                     data=csv,
#                     file_name="reviewer_recommendations.csv",
#                     mime="text/csv",
#                     use_container_width=True
#                 )
            
#             with col2:
#                 json_data = {
#                     'recommendations': [
#                         {
#                             'rank': i + 1,
#                             'author': author,
#                             'scores': scores
#                         }
#                         for i, (author, scores) in enumerate(st.session_state.recommendations)
#                     ],
#                     'weights': {
#                         'tfidf_weight': tfidf_weight,
#                         'semantic_weight': semantic_weight
#                     }
#                 }
                
#                 import json
#                 json_str = json.dumps(json_data, indent=2)
#                 st.download_button(
#                     label="Download as JSON",
#                     data=json_str,
#                     file_name="reviewer_recommendations.json",
#                     mime="application/json",
#                     use_container_width=True
#                 )
            
#             st.info("Recommendations can be exported in CSV or JSON format for further analysis.")


# if __name__ == "__main__":
#     main()

## check what lines are missing from thsi and below in commentation
# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go
# import os
# import tempfile
# import json
# import pickle
# from main import ReviewerRecommendationSystem

# # ----------------------------------------------------------
# # Page configuration
# # ----------------------------------------------------------
# st.set_page_config(
#     page_title="Reviewer Recommendation System",
#     page_icon="📄",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ----------------------------------------------------------
# # Custom CSS
# # ----------------------------------------------------------
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 2.5rem;
#         font-weight: bold;
#         color: #1f77b4;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
#     .metric-card {
#         background-color: #f0f2f6;
#         padding: 1rem;
#         border-radius: 0.5rem;
#         margin: 0.5rem 0;
#     }
#     .author-card {
#         background-color: #ffffff;
#         border: 2px solid #e0e0e0;
#         border-radius: 0.5rem;
#         padding: 1rem;
#         margin: 0.5rem 0;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#     }
#     .score-badge {
#         display: inline-block;
#         padding: 0.25rem 0.5rem;
#         border-radius: 0.25rem;
#         font-weight: bold;
#         margin: 0.25rem;
#     }
#     .score-high {
#         background-color: #90ee90;
#         color: #006400;
#     }
#     .score-medium {
#         background-color: #ffd700;
#         color: #8b4513;
#     }
#     .score-low {
#         background-color: #ffcccb;
#         color: #8b0000;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ----------------------------------------------------------
# # Initialize session state
# # ----------------------------------------------------------
# def initialize_session_state():
#     if 'recommender' not in st.session_state:
#         st.session_state.recommender = None
#     if 'authors_loaded' not in st.session_state:
#         st.session_state.authors_loaded = False
#     if 'recommendations' not in st.session_state:
#         st.session_state.recommendations = None
#     if 'processing' not in st.session_state:
#         st.session_state.processing = False


# # ----------------------------------------------------------
# # Step 1: Cached loading (shared across users)
# # ----------------------------------------------------------
# @st.cache_resource(show_spinner="Loading authors data into memory...")
# def load_authors_data_cached(output_dir):
#     """Cached version of loading authors data."""
#     recommender = ReviewerRecommendationSystem(output_dir=output_dir)
#     recommender.load_authors_data()
#     return recommender


# # ----------------------------------------------------------
# # Step 5: Optional persistent cache using pickle
# # ----------------------------------------------------------
# @st.cache_resource
# def load_persistent_recommender(output_dir="output", cache_file="recommender.pkl"):
#     """Load recommender persistently across restarts (optional)."""
#     if os.path.exists(cache_file):
#         with open(cache_file, "rb") as f:
#             return pickle.load(f)
#     else:
#         recommender = ReviewerRecommendationSystem(output_dir=output_dir)
#         recommender.load_authors_data()
#         with open(cache_file, "wb") as f:
#             pickle.dump(recommender, f)
#         return recommender


# # ----------------------------------------------------------
# # Helper functions
# # ----------------------------------------------------------
# def get_score_class(score):
#     if score >= 0.7:
#         return "score-high"
#     elif score >= 0.4:
#         return "score-medium"
#     else:
#         return "score-low"


# def display_author_card(rank, author, scores):
#     score_class = get_score_class(scores['hybrid_score'])
#     st.markdown(f"""
#     <div class="author-card">
#         <h3>#{rank} {author}</h3>
#         <div class="score-badge {score_class}">
#             Hybrid Score: {scores['hybrid_score']:.4f}
#         </div>
#     </div>
#     """, unsafe_allow_html=True)
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.metric("TF-IDF Score", f"{scores['tfidf_score']:.4f}")
#     with col2:
#         st.metric("Semantic Score", f"{scores['semantic_score']:.4f}")
#     with col3:
#         st.metric("Paper Count", scores['paper_count'])
#     if scores.get('keywords'):
#         st.markdown(f"**Top Keywords:** {', '.join(scores['keywords'])}")


# def create_score_comparison_chart(recommendations):
#     df = pd.DataFrame([
#         {
#             'Author': author,
#             'TF-IDF': scores['tfidf_score'],
#             'Semantic': scores['semantic_score'],
#             'Hybrid': scores['hybrid_score']
#         }
#         for author, scores in recommendations
#     ])
#     fig = go.Figure()
#     fig.add_bar(name='TF-IDF', x=df['Author'], y=df['TF-IDF'], marker_color='lightblue')
#     fig.add_bar(name='Semantic', x=df['Author'], y=df['Semantic'], marker_color='lightgreen')
#     fig.add_bar(name='Hybrid', x=df['Author'], y=df['Hybrid'], marker_color='coral')
#     fig.update_layout(
#         title='Reviewer Scores Comparison',
#         xaxis_title='Authors',
#         yaxis_title='Score',
#         barmode='group',
#         height=500,
#         hovermode='x unified'
#     )
#     return fig


# def create_radar_chart(recommendations, top_n=5):
#     top_recommendations = recommendations[:top_n]
#     fig = go.Figure()
#     for author, scores in top_recommendations:
#         fig.add_scatterpolar(
#             r=[scores['tfidf_score'], scores['semantic_score'], scores['hybrid_score']],
#             theta=['TF-IDF', 'Semantic', 'Hybrid'],
#             fill='toself',
#             name=author
#         )
#     fig.update_layout(
#         polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
#         title=f'Top {top_n} Reviewers - Score Breakdown',
#         height=500
#     )
#     return fig


# def create_score_distribution(recommendations):
#     scores = [s['hybrid_score'] for _, s in recommendations]
#     fig = go.Figure()
#     fig.add_histogram(x=scores, nbinsx=20, marker_color='steelblue', opacity=0.7)
#     fig.update_layout(
#         title='Hybrid Score Distribution',
#         xaxis_title='Hybrid Score',
#         yaxis_title='Number of Authors',
#         height=400
#     )
#     return fig


# # ----------------------------------------------------------
# # Main App
# # ----------------------------------------------------------
# def main():
#     initialize_session_state()
#     st.markdown('<div class="main-header">Reviewer Recommendation System</div>', unsafe_allow_html=True)

#     with st.sidebar:
#         st.header("Configuration")

#         output_dir = st.text_input(
#             "Authors Data Directory",
#             value="output",
#             help="Directory containing author metadata files"
#         )

#         st.divider()

#         st.subheader("Scoring Weights")
#         tfidf_weight = st.slider("TF-IDF Weight", 0.0, 1.0, 0.4, 0.1)
#         semantic_weight = st.slider("Semantic Weight", 0.0, 1.0, 0.6, 0.1)
#         if abs((tfidf_weight + semantic_weight) - 1.0) > 0.01:
#             st.warning("Weights should sum to 1.0")

#         st.divider()
#         k_reviewers = st.number_input("Number of Top Reviewers", 1, 50, 10)

#         st.divider()
#         if st.button("Load Authors Data", type="primary", use_container_width=True):
#             if os.path.exists(output_dir):
#                 recommender = load_authors_data_cached(output_dir)
#                 st.session_state.recommender = recommender
#                 st.session_state.authors_loaded = True
#                 st.success(f"Loaded {len(st.session_state.recommender.authors_data)} authors (cached)")
#             else:
#                 st.error(f"Directory not found: {output_dir}")

#         # Optional cache reset button
#         if st.button("Clear Cached Data", use_container_width=True):
#             load_authors_data_cached.clear()
#             st.session_state.recommender = None
#             st.session_state.authors_loaded = False
#             st.success("Cache cleared successfully. You can reload updated data.")

#     # ----------------------------------------------------------
#     # Main content area
#     # ----------------------------------------------------------
#     if not st.session_state.authors_loaded:
#         st.info("Please load authors data from the sidebar to begin.")
#         st.markdown("""
#         ### Getting Started
#         1. Process dataset and ensure output directory exists
#         2. Configure the authors data directory in the sidebar
#         3. Click **'Load Authors Data'**
#         4. Upload a candidate paper to get reviewer recommendations
#         """)
#         return

#     st.success(f"Authors loaded: {len(st.session_state.recommender.authors_data)}")

#     st.header("Upload Candidate Paper")
#     uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

#     if uploaded_file is not None:
#         with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
#             tmp.write(uploaded_file.getvalue())
#             tmp_path = tmp.name

#         col1, col2 = st.columns([3, 1])
#         with col1:
#             st.info(f"File uploaded: {uploaded_file.name}")
#         with col2:
#             if st.button("Find Reviewers", type="primary", use_container_width=True):
#                 st.session_state.processing = True

#         if st.session_state.processing:
#             with st.spinner("Analyzing paper and computing similarity scores..."):
#                 try:
#                     recs = st.session_state.recommender.get_top_reviewers(
#                         candidate_pdf=tmp_path,
#                         k=k_reviewers,
#                         tfidf_weight=tfidf_weight,
#                         semantic_weight=semantic_weight
#                     )
#                     st.session_state.recommendations = recs
#                     st.session_state.processing = False
#                     os.unlink(tmp_path)
#                     st.success("Analysis complete!")
#                 except Exception as e:
#                     st.error(f"Error: {e}")
#                     st.session_state.processing = False
#                     if os.path.exists(tmp_path):
#                         os.unlink(tmp_path)

#     if st.session_state.recommendations:
#         st.header("Recommendation Results")
#         tab1, tab2, tab3, tab4 = st.tabs(["Top Reviewers", "Score Analysis", "Detailed Comparison", "Export"])

#         with tab1:
#             for i, (author, scores) in enumerate(st.session_state.recommendations, 1):
#                 with st.expander(f"#{i} {author} - Score: {scores['hybrid_score']:.4f}", expanded=(i <= 3)):
#                     display_author_card(i, author, scores)

#         with tab2:
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.plotly_chart(create_score_comparison_chart(st.session_state.recommendations), use_container_width=True)
#             with col2:
#                 st.plotly_chart(create_score_distribution(st.session_state.recommendations), use_container_width=True)
#             st.plotly_chart(create_radar_chart(st.session_state.recommendations, top_n=5), use_container_width=True)

#         with tab3:
#             df = pd.DataFrame([
#                 {
#                     'Rank': i + 1,
#                     'Author': author,
#                     'Hybrid Score': s['hybrid_score'],
#                     'TF-IDF': s['tfidf_score'],
#                     'Semantic': s['semantic_score'],
#                     'Papers': s['paper_count'],
#                     'Keywords': ', '.join(s.get('keywords', []))
#                 }
#                 for i, (author, s) in enumerate(st.session_state.recommendations)
#             ])
#             st.dataframe(df, use_container_width=True, hide_index=True)

#         with tab4:
#             csv = df.to_csv(index=False)
#             st.download_button("Download CSV", csv, "reviewer_recommendations.csv", "text/csv", use_container_width=True)
#             json_data = {
#                 'recommendations': [
#                     {'rank': i + 1, 'author': a, 'scores': s}
#                     for i, (a, s) in enumerate(st.session_state.recommendations)
#                 ],
#                 'weights': {'tfidf_weight': tfidf_weight, 'semantic_weight': semantic_weight}
#             }
#             st.download_button("Download JSON", json.dumps(json_data, indent=2),
#                                "reviewer_recommendations.json", "application/json", use_container_width=True)


# if __name__ == "__main__":
#     main()

# ✅ Integrated Hybrid PDF Extractor (GROBID + PyMuPDF fallback)
# ------------------------------------------------------------
# Added based on your requirement — rest of your app unchanged

import os
import re
import fitz  # PyMuPDF
import requests
from typing import Dict, Optional


def extract_pdf_text_pymupdf(pdf_path: str) -> str:
    """Fallback method: Extract all text from PDF using PyMuPDF."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"[PyMuPDF Error] {e}")
    return text.strip()


def extract_basic_metadata(
    pdf_path: str,
    use_grobid: bool = False,  # Default False (safe for Streamlit Cloud)
    grobid_url: Optional[str] = "http://localhost:8070/api/processHeaderDocument"
) -> Dict[str, str]:
    """
    Extracts metadata (title, authors, abstract) from a PDF.
    Falls back to PyMuPDF if GROBID is unavailable or fails.
    """
    metadata = {"title": "", "authors": "", "abstract": "", "source": ""}

    if use_grobid:
        try:
            with open(pdf_path, "rb") as pdf_file:
                response = requests.post(
                    grobid_url,
                    files={"input": pdf_file},
                    timeout=10
                )
            if response.status_code == 200 and "<titleStmt>" in response.text:
                metadata["source"] = "GROBID"
                title_match = re.search(r"<title>(.*?)</title>", response.text)
                metadata["title"] = title_match.group(1) if title_match else ""
                names = re.findall(r"<forename>(.*?)</forename>\s*<surname>(.*?)</surname>", response.text)
                metadata["authors"] = ", ".join([f"{f} {l}" for f, l in names])
                abstract_match = re.search(r"<abstract>(.*?)</abstract>", response.text, re.S)
                if abstract_match:
                    metadata["abstract"] = re.sub(r"<.*?>", "", abstract_match.group(1)).strip()
                return metadata
            else:
                print("[Warning] GROBID invalid, falling back to PyMuPDF.")
        except Exception as e:
            print(f"[Warning] GROBID error: {e}. Using PyMuPDF.")

    metadata["source"] = "PyMuPDF"
    pdf_text = extract_pdf_text_pymupdf(pdf_path)
    metadata["abstract"] = pdf_text[:2000]
    metadata["title"] = os.path.basename(pdf_path)
    metadata["authors"] = "Unknown"
    return metadata

# ✅ Use cached wrapper in Streamlit
import streamlit as st

@st.cache_data
def get_metadata_cached(pdf_path: str, use_grobid: bool = False):
    return extract_basic_metadata(pdf_path, use_grobid)

# ------------------------------------------------------------------------------------------------
# BELOW THIS LINE: your original Streamlit code EXACTLY as-is
# ------------------------------------------------------------------------------------------------
import streamlit as st 
import pandas as pd
import plotly.graph_objects as go
import os
import tempfile
import json
import pickle
from main import ReviewerRecommendationSystem

# ----------------------------------------------------------
# Page configuration
# ----------------------------------------------------------
st.set_page_config(
    page_title="Reviewer Recommendation System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------
# Custom CSS
# ----------------------------------------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .author-card {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .score-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    .score-high {
        background-color: #90ee90;
        color: #006400;
    }
    .score-medium {
        background-color: #ffd700;
        color: #8b4513;
    }
    .score-low {
        background-color: #ffcccb;
        color: #8b0000;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# Initialize session state
# ----------------------------------------------------------
def initialize_session_state():
    if 'recommender' not in st.session_state:
        st.session_state.recommender = None
    if 'authors_loaded' not in st.session_state:
        st.session_state.authors_loaded = False
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False


# ----------------------------------------------------------
# Step 1: Cached loading (shared across users)
# ----------------------------------------------------------
@st.cache_resource(show_spinner="Loading authors data into memory...")
def load_authors_data_cached(output_dir):
    """Cached version of loading authors data."""
    recommender = ReviewerRecommendationSystem(output_dir=output_dir)
    recommender.load_authors_data()
    return recommender


# ----------------------------------------------------------
# Step 5: Optional persistent cache using pickle
# ----------------------------------------------------------
@st.cache_resource
def load_persistent_recommender(output_dir="output", cache_file="recommender.pkl"):
    """Load recommender persistently across restarts (optional)."""
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    else:
        recommender = ReviewerRecommendationSystem(output_dir=output_dir)
        recommender.load_authors_data()
        with open(cache_file, "wb") as f:
            pickle.dump(recommender, f)
        return recommender


# ----------------------------------------------------------
# Helper functions
# ----------------------------------------------------------
def get_score_class(score):
    if score >= 0.7:
        return "score-high"
    elif score >= 0.4:
        return "score-medium"
    else:
        return "score-low"


def display_author_card(rank, author, scores):
    score_class = get_score_class(scores['hybrid_score'])
    st.markdown(f"""
    <div class="author-card">
        <h3>#{rank} {author}</h3>
        <div class="score-badge {score_class}">
            Hybrid Score: {scores['hybrid_score']:.4f}
        </div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("TF-IDF Score", f"{scores['tfidf_score']:.4f}")
    with col2:
        st.metric("Semantic Score", f"{scores['semantic_score']:.4f}")
    with col3:
        st.metric("Paper Count", scores['paper_count'])
    if scores.get('keywords'):
        st.markdown(f"**Top Keywords:** {', '.join(scores['keywords'])}")


def create_score_comparison_chart(recommendations):
    df = pd.DataFrame([
        {
            'Author': author,
            'TF-IDF': scores['tfidf_score'],
            'Semantic': scores['semantic_score'],
            'Hybrid': scores['hybrid_score']
        }
        for author, scores in recommendations
    ])
    fig = go.Figure()
    fig.add_bar(name='TF-IDF', x=df['Author'], y=df['TF-IDF'], marker_color='lightblue')
    fig.add_bar(name='Semantic', x=df['Author'], y=df['Semantic'], marker_color='lightgreen')
    fig.add_bar(name='Hybrid', x=df['Author'], y=df['Hybrid'], marker_color='coral')
    fig.update_layout(
        title='Reviewer Scores Comparison',
        xaxis_title='Authors',
        yaxis_title='Score',
        barmode='group',
        height=500,
        hovermode='x unified'
    )
    return fig


def create_radar_chart(recommendations, top_n=5):
    top_recommendations = recommendations[:top_n]
    fig = go.Figure()
    for author, scores in top_recommendations:
        fig.add_scatterpolar(
            r=[scores['tfidf_score'], scores['semantic_score'], scores['hybrid_score']],
            theta=['TF-IDF', 'Semantic', 'Hybrid'],
            fill='toself',
            name=author
        )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title=f'Top {top_n} Reviewers - Score Breakdown',
        height=500
    )
    return fig


def create_score_distribution(recommendations):
    scores = [s['hybrid_score'] for _, s in recommendations]
    fig = go.Figure()
    fig.add_histogram(x=scores, nbinsx=20, marker_color='steelblue', opacity=0.7)
    fig.update_layout(
        title='Hybrid Score Distribution',
        xaxis_title='Hybrid Score',
        yaxis_title='Number of Authors',
        height=400
    )
    return fig


# ----------------------------------------------------------
# Main App
# ----------------------------------------------------------
def main():
    initialize_session_state()
    st.markdown('<div class="main-header">Reviewer Recommendation System</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("Configuration")

        output_dir = st.text_input(
            "Authors Data Directory",
            value="output",
            help="Directory containing author metadata files"
        )

        st.divider()

        st.subheader("Scoring Weights")
        tfidf_weight = st.slider("TF-IDF Weight", 0.0, 1.0, 0.4, 0.1)
        semantic_weight = st.slider("Semantic Weight", 0.0, 1.0, 0.6, 0.1)
        if abs((tfidf_weight + semantic_weight) - 1.0) > 0.01:
            st.warning("Weights should sum to 1.0")

        st.divider()
        k_reviewers = st.number_input("Number of Top Reviewers", 1, 50, 10)

        st.divider()
        if st.button("Load Authors Data", type="primary", use_container_width=True):
            if os.path.exists(output_dir):
                recommender = load_authors_data_cached(output_dir)
                st.session_state.recommender = recommender
                st.session_state.authors_loaded = True
                st.success(f"Loaded {len(st.session_state.recommender.authors_data)} authors (cached)")
            else:
                st.error(f"Directory not found: {output_dir}")

        # Optional cache reset button
        if st.button("Clear Cached Data", use_container_width=True):
            load_authors_data_cached.clear()
            st.session_state.recommender = None
            st.session_state.authors_loaded = False
            st.success("Cache cleared successfully. You can reload updated data.")

    # ----------------------------------------------------------
    # Main content area
    # ----------------------------------------------------------
    if not st.session_state.authors_loaded:
        st.info("Please load authors data from the sidebar to begin.")
        st.markdown("""
        ### Getting Started
        1. Process dataset and ensure output directory exists
        2. Configure the authors data directory in the sidebar
        3. Click **'Load Authors Data'**
        4. Upload a candidate paper to get reviewer recommendations
        """)
        return

    st.success(f"Authors loaded: {len(st.session_state.recommender.authors_data)}")

    st.header("Upload Candidate Paper")
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"File uploaded: {uploaded_file.name}")
        with col2:
            if st.button("Find Reviewers", type="primary", use_container_width=True):
                st.session_state.processing = True

        if st.session_state.processing:
            with st.spinner("Analyzing paper and computing similarity scores..."):
                try:
                    # ✅ Use hybrid extractor
                    meta = get_metadata_cached(tmp_path, use_grobid=False)
                    paper_text = meta["abstract"]

                    recs = st.session_state.recommender.get_top_reviewers(
                        candidate_text=paper_text,
                        k=k_reviewers,
                        tfidf_weight=tfidf_weight,
                        semantic_weight=semantic_weight
                    )
                    st.session_state.recommendations = recs
                    st.session_state.processing = False
                    os.unlink(tmp_path)
                    st.success("Analysis complete!")
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state.processing = False
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

    if st.session_state.recommendations:
        st.header("Recommendation Results")
        tab1, tab2, tab3, tab4 = st.tabs(["Top Reviewers", "Score Analysis", "Detailed Comparison", "Export"])

        with tab1:
            for i, (author, scores) in enumerate(st.session_state.recommendations, 1):
                with st.expander(f"#{i} {author} - Score: {scores['hybrid_score']:.4f}", expanded=(i <= 3)):
                    display_author_card(i, author, scores)

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(create_score_comparison_chart(st.session_state.recommendations), use_container_width=True)
            with col2:
                st.plotly_chart(create_score_distribution(st.session_state.recommendations), use_container_width=True)
            st.plotly_chart(create_radar_chart(st.session_state.recommendations, top_n=5), use_container_width=True)

        with tab3:
            df = pd.DataFrame([
                {
                    'Rank': i + 1,
                    'Author': author,
                    'Hybrid Score': s['hybrid_score'],
                    'TF-IDF': s['tfidf_score'],
                    'Semantic': s['semantic_score'],
                    'Papers': s['paper_count'],
                    'Keywords': ', '.join(s.get('keywords', []))
                }
                for i, (author, s) in enumerate(st.session_state.recommendations)
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)

        with tab4:
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "reviewer_recommendations.csv", "text/csv", use_container_width=True)
            json_data = {
                'recommendations': [
                    {'rank': i + 1, 'author': a, 'scores': s}
                    for i, (a, s) in enumerate(st.session_state.recommendations)
                ],
                'weights': {'tfidf_weight': tfidf_weight, 'semantic_weight': semantic_weight}
            }
            st.download_button("Download JSON", json.dumps(json_data, indent=2),
                               "reviewer_recommendations.json", "application/json", use_container_width=True)


if __name__ == "__main__":
    main()