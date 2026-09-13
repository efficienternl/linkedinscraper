"""Streamlit web interface for LinkedIn scraper."""
import streamlit as st

st.set_page_config(page_title="LinkedIn Scraper", layout="wide", initial_sidebar_state="collapsed")

# Custom styling
st.markdown("""
<style>
    .main { padding: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
</style>
""", unsafe_allow_html=True)

st.title("LinkedIn Scraper")
st.markdown("Bulk-scrape LinkedIn profielen, bedrijven en vacatures")

# Sidebar config
with st.sidebar:
    st.markdown("### Instellingen")
    session_file = st.text_input("Session bestand", value="session.json")
    headless = st.checkbox("Headless modus", value=True, help="Browser verborgen")
    delay_min = st.slider("Min. vertraging (s)", 1.0, 30.0, 5.0)
    delay_max = st.slider("Max. vertraging (s)", 1.0, 60.0, 15.0)
    max_errors = st.slider("Max. fouten op rij", 1, 10, 3)

tabs = st.tabs(["Login", "Profiel", "Bedrijf", "Bulk Profielen", "Vacatures", "Zoeken (Apify)"])

# TAB 1: Login
with tabs[0]:
    st.header("LinkedIn Inloggen")
    st.info("Jij logt handmatig in bij LinkedIn. De tool slaat je sessie op.")

    if st.button("Start inloggen", use_container_width=True, key="login_btn"):
        st.info("Start je terminal en voer uit:")
        st.code("python cli.py login", language="bash")
        st.info("Na inloggen in je browser, kom je hier terug.")

# TAB 2: Single Profile
with tabs[1]:
    st.header("LinkedIn Profiel Scrapen")
    profile_url = st.text_input("LinkedIn profiel URL", placeholder="https://www.linkedin.com/in/naam/")

    if st.button("Scrape", use_container_width=True, key="person_btn"):
        if not profile_url:
            st.error("Voer een URL in")
        else:
            st.info("Start je terminal en voer uit:")
            st.code(f'python cli.py person "{profile_url}"', language="bash")

# TAB 3: Single Company
with tabs[2]:
    st.header("LinkedIn Bedrijfspagina Scrapen")
    company_url = st.text_input("LinkedIn bedrijf URL", placeholder="https://www.linkedin.com/company/naam/")

    if st.button("Scrape", use_container_width=True, key="company_btn"):
        if not company_url:
            st.error("Voer een URL in")
        else:
            st.info("Start je terminal en voer uit:")
            st.code(f'python cli.py company "{company_url}"', language="bash")

# TAB 4: Bulk Profiles
with tabs[3]:
    st.header("Bulk: Meerdere Profielen")

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload tekstbestand met URLs", type=["txt"])
    with col2:
        output_file = st.text_input("Output JSONL bestand", value="output/results.jsonl")

    if uploaded_file and st.button("Bulk Scrape", use_container_width=True, key="bulk_btn"):
        file_content = uploaded_file.read().decode()
        urls = [line.strip() for line in file_content.split('\n') if line.strip()]
        st.info(f"{len(urls)} URLs gevonden")

        # Save to temp file
        temp_file = "temp_urls.txt"
        with open(temp_file, "w") as f:
            f.write("\n".join(urls))

        st.info("Start je terminal en voer uit:")
        cmd = f'python cli.py people --file {temp_file} --out {output_file} --delay-min {delay_min} --delay-max {delay_max}'
        st.code(cmd, language="bash")

# TAB 5: Job Search
with tabs[4]:
    st.header("Vacatures Zoeken & Scrapen")

    col1, col2 = st.columns(2)
    with col1:
        job_keywords = st.text_input("Zoekterm", placeholder="e.g. 'python developer'")
        job_location = st.text_input("Locatie", placeholder="e.g. 'Amsterdam'")
    with col2:
        job_limit = st.number_input("Max. vacatures", 5, 500, 25)
        job_output = st.text_input("Output bestand", value="output/jobs.jsonl")

    if st.button("Zoeken & Scrapen", use_container_width=True, key="jobs_btn"):
        if not job_keywords:
            st.error("Voer een zoekterm in")
        else:
            cmd = f'python cli.py jobs --keywords "{job_keywords}" --limit {job_limit} --out {job_output}'
            if job_location:
                cmd += f' --location "{job_location}"'

            st.info("Start je terminal en voer uit:")
            st.code(cmd, language="bash")

# TAB 6: Apify Search (MULTI-KEYWORD)
with tabs[5]:
    st.header("Zoeken via Apify (meerdere keywords)")
    st.info("Zoek op LinkedIn via Apify (jouw account loopt geen risico). Voer meerdere zoektermen in.")

    col1, col2 = st.columns(2)
    with col1:
        search_keywords_input = st.text_area(
            "Zoektermen (één per regel)",
            placeholder="transport\nlogistics\nshipping",
            height=100
        )
        search_seniority = st.selectbox("Seniority", ["", "manager", "director", "executive"], help="Functieniveau")
        search_manager_type = st.text_input("Manager type", placeholder="e.g. 'operations', 'logistics'")
    with col2:
        search_location = st.text_input("Locatie", placeholder="e.g. 'Netherlands'")
        search_limit = st.number_input("Max. profielen per keyword", 10, 500, 100)
        search_output = st.text_input("Output bestand", value="output/search_results.jsonl")

    if st.button("Zoeken & Scrapen", use_container_width=True, key="search_btn"):
        if not search_keywords_input:
            st.error("Voer minstens een zoekterm in")
        else:
            keywords_list = [kw.strip() for kw in search_keywords_input.split('\n') if kw.strip()]

            # Build command with multiple keywords
            cmd = f'python cli.py search'
            for kw in keywords_list:
                cmd += f' --keywords "{kw}"'

            cmd += f' --limit {search_limit} --out {search_output}'

            if search_seniority:
                cmd += f' --seniority {search_seniority}'
            if search_manager_type:
                cmd += f' --manager-type "{search_manager_type}"'
            if search_location:
                cmd += f' --location "{search_location}"'

            st.success(f"{len(keywords_list)} zoekterm(en) gevonden:")
            for kw in keywords_list:
                st.text(f"  • {kw}")

            st.info("Start je terminal en voer uit:")
            st.code(cmd, language="bash")

# Footer
st.divider()
st.markdown("""
### Instructies
1. Start je terminal in deze folder
2. Activeer venv: `source .venv/bin/activate`
3. Kopieer het commando hierboven
4. Wacht tot het klaar is

### Output
Alle resultaten worden als JSONL opgeslagen (een profiel per regel in JSON format).
""")
