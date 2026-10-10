"""Text cleaning tab UI."""

import streamlit as st
from services.text_cleaning import clean_text, is_code_snippet, SPELLCHECKER_AVAILABLE


def render_text_cleaning_tab():
    """Render the text cleaning tab content."""
    
    st.subheader("✍️ Text Editor & Cleaner")
    st.write("""
    Clean and correct text automatically.  Code snippets are detected and preserved.
    """)
    
    # Show spellchecker status
    if SPELLCHECKER_AVAILABLE:
        st. success("✅ Advanced spell checker is active")
    else:
        st. warning("⚠️ Install `pyspellchecker` for better spelling correction:  `pip install pyspellchecker`")
    
    # Initialize session state
    if "cleaned_text" not in st.session_state:
        st.session_state["cleaned_text"] = ""
    if "input_method" not in st.session_state:
        st.session_state["input_method"] = "text"
    
    # Cleaning options in an expander
    with st.expander("⚙️ Cleaning Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            fix_whitespace = st.checkbox("Fix whitespace issues", value=True, 
                help="Remove extra spaces and normalize line breaks")
            fix_punctuation = st.checkbox("Fix punctuation", value=True,
                help="Correct spacing around punctuation marks")
            remove_special = st.checkbox("Remove special characters in words", value=True,
                help="Remove symbols like % !  @ from middle of words and fix the word")
        
        with col2:
            capitalize = st.checkbox("Capitalize sentences", value=True,
                help="Capitalize the first letter of each sentence")
            fix_typos = st.checkbox("Fix common typos", value=True,
                help="Correct common typing mistakes like 'dont' -> 'don't'")
            remove_duplicates = st.checkbox("Remove duplicate words", value=True,
                help="Remove accidentally repeated words")
        
        st.markdown("---")
        col3, col4 = st.columns(2)
        
        with col3:
            fix_spelling = st.checkbox("🔤 Fix spelling mistakes", value=True,
                help="Correct spelling errors and complete incomplete words")
        
        with col4:
            preserve_code = st.checkbox("🔒 Preserve code snippets", value=True,
                help="Automatically detect and preserve code like $x = 5; or HTML tags")
    
    # ==================== INPUT SECTION ====================
    st.markdown("---")
    st.markdown("### 📥 Input")
    
    # Input method selector with tabs
    input_tab1, input_tab2 = st.tabs(["📝 Type or Paste Text", "📁 Upload File"])
    
    text_to_clean = None
    source = None
    
    # ==================== TAB 1: Text Area ====================
    with input_tab1:
        st.markdown("""
        <div style="padding: 10px 0;">
            <p style="color: #888; margin-bottom: 10px;">
                ✏️ Type or paste your text in the box below
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        text_input = st.text_area(
            "Your text:",
            height=250,
            placeholder="Enter your text here...",
            key="text_area_input",
            label_visibility="collapsed"
        )
        
        # Info row
        if text_input:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"📊 {len(text_input)} characters")
            with col2:
                st.caption(f"📝 {len(text_input. split())} words")
            with col3:
                if is_code_snippet(text_input):
                    st.caption("🔍 Code detected")
        
        # Clean button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧹 Clean Text", type="primary", use_container_width=True, key="clean_text_btn"):
            if text_input:
                text_to_clean = text_input
                source = "typed"
            else: 
                st.warning("⚠️ Please enter some text to clean.")
    
    # ==================== TAB 2: File Upload ====================
    with input_tab2:
        st.markdown("""
        <div style="padding: 10px 0;">
            <p style="color: #888; margin-bottom: 10px;">
                📂 Upload a text file to clean its contents
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["txt", "md", "text", "log"],
            help="Supported formats: .txt, .md, . text, .log",
            key="text_file_uploader",
            label_visibility="collapsed"
        )
        
        file_content = None
        
        if uploaded_file is not None: 
            try:
                # Try to read the file with UTF-8 encoding
                file_content = uploaded_file.read().decode("utf-8")
                
                # File info card
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    border:  1px solid #30475e;
                    border-radius:  10px;
                    padding: 15px;
                    margin: 10px 0;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 1.2em;">📄</span>
                            <strong style="color: #fff; margin-left: 8px;">{uploaded_file.name}</strong>
                        </div>
                        <div style="color: #888;">
                            {len(file_content):,} characters • {len(file_content.split()):,} words
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Preview expander
                with st.expander("👁️ Preview file content"):
                    preview_text = file_content[: 1000] + ("..." if len(file_content) > 1000 else "")
                    st.text(preview_text)
                
                # Code detection
                if is_code_snippet(file_content):
                    st.info("🔍 Code detected in file - will be preserved")
                    
            except UnicodeDecodeError:
                try:
                    uploaded_file.seek(0)
                    file_content = uploaded_file.read().decode("latin-1")
                    st. info(f"📄 **{uploaded_file.name}** ({len(file_content):,} characters)")
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
            except Exception as e:
                st. error(f"❌ Error reading file: {str(e)}")
        else:
            # Empty state
            st.markdown("""
            <div style="
                border: 2px dashed #30475e;
                border-radius: 10px;
                padding: 40px;
                text-align:  center;
                margin: 10px 0;
            ">
                <p style="color: #888; margin:  0;">
                    📁 No file uploaded yet<br>
                    <small>Drag and drop or click to browse</small>
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Clean button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧹 Clean File", type="primary", use_container_width=True, key="clean_file_btn"):
            if file_content:
                text_to_clean = file_content
                source = "file"
            else:
                st.warning("⚠️ Please upload a file first.")
    
    # ==================== PROCESS AND SHOW RESULTS ====================
    if text_to_clean and source: 
        process_and_display_result(
            text_to_clean,
            fix_whitespace,
            fix_punctuation,
            remove_special,
            capitalize,
            fix_typos,
            remove_duplicates,
            fix_spelling,
            preserve_code,
            source
        )
    
    # ==================== EXAMPLES & TIPS ====================
    st.markdown("---")
    with st.expander("💡 Examples & Tips", expanded=False):
        col1, col2 = st. columns(2)
        
        with col1:
            st. markdown("""
            **✨ What this tool fixes:**
            
            | Before | After |
            |--------|-------|
            | `hello   world` | `hello world` |
            | `dont, cant` | `don't, can't` |
            | `the the quick` | `the quick` |
            | `welco%e` | `welcome` |
            | `exoplain` | `explain` |
            """)
        
        with col2:
            st.markdown("""
            **🔒 What's preserved:**
            
            - ✅ Email:  `user@example.com`
            - ✅ URLs: `https://example.com`
            - ✅ Code:  `$x = 5;`
            - ✅ HTML: `<div>`
            - ✅ Arabic: `مرحبا`
            
            **📁 Supported files:** `.txt`, `.md`, `.text`, `.log`
            """)


def process_and_display_result(
    text:  str,
    fix_whitespace: bool,
    fix_punctuation: bool,
    remove_special: bool,
    capitalize: bool,
    fix_typos: bool,
    remove_duplicates: bool,
    fix_spelling: bool,
    preserve_code: bool,
    source: str
):
    """Process text and display results."""
    
    with st.spinner("🔄 Cleaning text..."):
        result = clean_text(
            text,
            fix_whitespace=fix_whitespace,
            fix_punctuation_errors=fix_punctuation,
            remove_special_chars=remove_special,
            capitalize=capitalize,
            fix_typos=fix_typos,
            remove_duplicates=remove_duplicates,
            fix_spelling_errors=fix_spelling,
            preserve_code=preserve_code
        )
        
        st.session_state["cleaned_text"] = result. cleaned_text
    
    # ==================== RESULTS SECTION ====================
    st.markdown("---")
    st.markdown("### ✨ Results")
    
    # Statistics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Original",
            value=f"{result.stats['original_length']:,}",
            help="Original character count"
        )
    
    with col2:
        st.metric(
            label="Cleaned",
            value=f"{result.stats['cleaned_length']: ,}",
            help="Cleaned character count"
        )
    
    with col3:
        diff = result.stats['characters_removed']
        st.metric(
            label="Removed",
            value=f"{abs(diff):,}",
            delta=f"{diff:+,}" if diff != 0 else "0",
            delta_color="normal" if diff >= 0 else "inverse",
            help="Characters removed"
        )
    
    with col4:
        st.metric(
            label="Changes",
            value=result.stats['total_changes'],
            help="Total cleaning operations applied"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Cleaned text output
    st.markdown("#### 📄 Cleaned Text")
    st.text_area(
        "Result:",
        value=result.cleaned_text,
        height=200,
        key=f"cleaned_output_{source}",
        label_visibility="collapsed"
    )
    
    # Changes made
    if result.changes_made:
        with st.expander("📋 Changes Made", expanded=True):
            for change in result.changes_made:
                st.markdown(f"✓ {change}")
            
            # Show spelling corrections if any
            if result.stats. get("spelling_corrections"):
                st. markdown("---")
                st.markdown("**📝 Spelling Corrections:**")
                corrections_text = " • ".join(result.stats["spelling_corrections"])
                st.markdown(f"<small>{corrections_text}</small>", unsafe_allow_html=True)
    else:
        st.success("✨ Text is already clean!  No changes needed.")
    
    # Comparison view
    with st.expander("🔍 Side-by-Side Comparison", expanded=False):
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            st.markdown("**Original:**")
            display_text = text[: 2000] + ("..." if len(text) > 2000 else "")
            st.code(display_text, language=None)
        
        with comp_col2:
            st. markdown("**Cleaned:**")
            display_cleaned = result.cleaned_text[:2000] + ("..." if len(result.cleaned_text) > 2000 else "")
            st.code(display_cleaned, language=None)
    
    # Export section
    st.markdown("#### 💾 Export")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.download_button(
            "📥 Download",
            data=result.cleaned_text. encode('utf-8'),
            file_name="cleaned_text.txt",
            mime="text/plain",
            use_container_width=True,
            key=f"download_{source}"
        )
    
    with col2:
        st.caption("Download the cleaned text as a . txt file")