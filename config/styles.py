"""CSS styles for the Streamlit application."""

CSS_STYLES = """
<style>
. header {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap: 1rem;
}
.title {
    font-size:28px;
    font-weight:700;
}
.subtitle {
    font-size:13px;
    color: #6c6c6c;
}
.byline {
    font-size:12px;
    color: #8a8a8a;
}
.error-cell {
    background-color: #ffebee;
    padding: 2px 5px;
    border-radius: 3px;
}
.warning-cell {
    background-color: #fff3e0;
    padding: 2px 5px;
    border-radius: 3px;
}
.preview-box {
    background-color: #f5f5f5;
    border-left: 4px solid #2196F3;
    padding: 10px;
    margin: 10px 0;
}
.match-highlight {
    background-color: #e8f5e9;
    padding: 2px 5px;
    border-radius: 3px;
}
</style>
"""