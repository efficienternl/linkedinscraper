"""Streamlit web interface for LinkedIn scraper."""
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="LinkedIn Scraper", layout="wide", initial_sidebar_state="collapsed")


# ============================================================================
# AUTHENTICATION SYSTEM
# ============================================================================

def parse_users_from_env():
    """Parse STREAMLIT_USERS env var into a dict of username:password."""
    users_str = os.getenv("STREAMLIT_USERS", "")
    users = {}
    if users_str:
        for pair in users_str.split(","):
            if ":" in pair:
                username, password = pair.split(":", 1)
                users[username.strip()] = password.strip()
    return users


def check_login():
    """Check if user is logged in. If not, show login screen and return False."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None

    if not st.session_state.logged_in:
        show_login_screen()
        return False

    return True


def show_login_screen():
    """Display the login screen."""
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("LinkedIn Scraper")
        st.markdown("---")
        st.subheader("Login Required")

        # Get valid users from env
        valid_users = parse_users_from_env()

        if not valid_users:
            st.error("No users configured. Set STREAMLIT_USERS in .env")
            st.stop()

        # Login form
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", use_container_width=True, key="login_submit"):
            if username in valid_users and valid_users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    st.stop()


def show_logout_button():
    """Show logout button in sidebar."""
    with st.sidebar:
        st.markdown("---")
        if st.button("Logout", use_container_width=True, key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
        st.markdown(f"*Logged in as: {st.session_state.username}*", help="Click Logout to sign out")

# Custom styling
st.markdown("""
<style>
    .main { padding: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .command-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1.5rem 0;
    }
    .output-section {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# REUSABLE COMPONENTS
# ============================================================================

def output_file_selector(key_prefix="output"):
    """
    Creates a standardized output file configuration UI.
    Returns: (base_filename, output_format, full_path)
    """
    st.markdown("### Uitvoer-instellingen")

    col1, col2 = st.columns(2)

    with col1:
        base_filename = st.text_input(
            "Bestandsnaam (zonder extensie)",
            value="results",
            placeholder="bijv. 'mijn_resultaten'",
            key=f"{key_prefix}_base",
            help="De naam van het uitvoerbestand"
        )

    with col2:
        output_format = st.selectbox(
            "Formaat",
            ["JSONL", "CSV"],
            key=f"{key_prefix}_format",
            help="JSONL: één profiel per regel | CSV: spreadsheet-formaat"
        )

    # Auto-generate full path
    extension = "jsonl" if output_format == "JSONL" else "csv"
    full_path = f"output/{base_filename}.{extension}"

    # Show the generated path
    st.info(f"📁 **Uitvoerbestand:** `{full_path}`")

    return base_filename, output_format, full_path


def show_command_preview(cmd):
    """Display a nicely formatted command preview before execution."""
    with st.container():
        st.markdown("### Commando dat wordt uitgevoerd")
        st.code(cmd, language="bash")
        st.caption("📋 Copy & paste dit commando in je terminal")

# ============================================================================
# AUTHENTICATION CHECK - GATE THE ENTIRE APP
# ============================================================================
if not check_login():
    st.stop()

# Show logout button in sidebar (only visible when logged in)
show_logout_button()

# ============================================================================
# MAIN APPLICATION (only shown when logged in)
# ============================================================================

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

# Tabs (no longer need "Login" tab)
tabs = st.tabs(["Profiel", "Bedrijf", "Bulk Profielen", "Vacatures", "Zoeken (Apify)"])

# TAB 1: Single Profile
with tabs[0]:
    st.header("LinkedIn Profiel Scrapen")

    profile_url = st.text_input(
        "LinkedIn profiel URL",
        placeholder="https://www.linkedin.com/in/naam/",
        help="Volledige URL van het LinkedIn profiel"
    )

    st.divider()

    if profile_url:
        base_filename, output_format, output_path = output_file_selector(key_prefix="person")

        st.divider()

        # Generate and show command preview
        cmd = f'python cli.py person "{profile_url}" --out {output_path}'
        show_command_preview(cmd)

        if st.button("Scrape Profiel", use_container_width=True, key="person_btn", type="primary"):
            st.success("Commando klaar! Kopieer het bovenstaande en voer uit in je terminal.")
    else:
        st.info("Voer een LinkedIn profiel URL in om te starten")

# TAB 2: Single Company
with tabs[1]:
    st.header("LinkedIn Bedrijfspagina Scrapen")

    company_url = st.text_input(
        "LinkedIn bedrijf URL",
        placeholder="https://www.linkedin.com/company/naam/",
        help="Volledige URL van de bedrijfspagina"
    )

    st.divider()

    if company_url:
        base_filename, output_format, output_path = output_file_selector(key_prefix="company")

        st.divider()

        # Generate and show command preview
        cmd = f'python cli.py company "{company_url}" --out {output_path}'
        show_command_preview(cmd)

        if st.button("Scrape Bedrijf", use_container_width=True, key="company_btn", type="primary"):
            st.success("Commando klaar! Kopieer het bovenstaande en voer uit in je terminal.")
    else:
        st.info("Voer een LinkedIn bedrijf URL in om te starten")

# TAB 3: Bulk Profiles
with tabs[2]:
    st.header("Bulk: Meerdere Profielen")

    uploaded_file = st.file_uploader(
        "Upload tekstbestand met URLs",
        type=["txt"],
        help="Elk profiel op een nieuwe regel"
    )

    st.divider()

    if uploaded_file:
        file_content = uploaded_file.read().decode()
        urls = [line.strip() for line in file_content.split('\n') if line.strip()]

        st.success(f"✓ {len(urls)} URL(s) geladen")

        st.divider()

        # Output file selector
        base_filename, output_format, output_path = output_file_selector(key_prefix="bulk")

        st.divider()

        # Generate and show command preview
        temp_file = "temp_urls.txt"
        cmd = f'python cli.py people --file {temp_file} --out {output_path} --delay-min {delay_min} --delay-max {delay_max}'

        show_command_preview(cmd)

        if st.button("Start Bulk Scrape", use_container_width=True, key="bulk_btn", type="primary"):
            # Save to temp file
            with open(temp_file, "w") as f:
                f.write("\n".join(urls))

            st.success("✓ Bestand opgeslagen! Kopieer het commando en voer uit in je terminal.")

# TAB 4: Job Search
with tabs[3]:
    st.header("Vacatures Zoeken & Scrapen")

    col1, col2 = st.columns(2)
    with col1:
        job_keywords = st.text_input(
            "Zoekterm",
            placeholder="e.g. 'python developer'",
            help="Functie of specialiteit om naar te zoeken"
        )
        job_location = st.text_input(
            "Locatie (optioneel)",
            placeholder="e.g. 'Amsterdam'",
            help="Laat leeg voor alle locaties"
        )
    with col2:
        job_limit = st.number_input("Max. vacatures", min_value=5, max_value=500, value=25)

    st.divider()

    if job_keywords:
        base_filename, output_format, output_path = output_file_selector(key_prefix="jobs")

        st.divider()

        # Generate and show command preview
        cmd = f'python cli.py jobs --keywords "{job_keywords}" --limit {job_limit} --out {output_path}'
        if job_location:
            cmd += f' --location "{job_location}"'

        show_command_preview(cmd)

        if st.button("Zoeken & Scrapen", use_container_width=True, key="jobs_btn", type="primary"):
            st.success("Commando klaar! Kopieer het bovenstaande en voer uit in je terminal.")
    else:
        st.info("Voer een zoekterm in om het commando te genereren")

# TAB 5: Apify Search (MULTI-KEYWORD)
with tabs[4]:
    st.header("Zoeken via Apify (meerdere keywords)")
    st.info("💡 Zoek op LinkedIn via Apify (jouw account loopt geen risico). Voer meerdere zoektermen in.")

    col1, col2 = st.columns(2)
    with col1:
        search_keywords_input = st.text_area(
            "Zoektermen (één per regel)",
            placeholder="transport\nlogistics\nshipping",
            height=100,
            help="Voer minstens één zoekterm in"
        )
        search_seniority = st.selectbox(
            "Seniority (optioneel)",
            ["", "manager", "director", "executive"],
            help="Functieniveau van kandidaten"
        )
        search_manager_type = st.text_input(
            "Manager type (optioneel)",
            placeholder="e.g. 'operations', 'logistics'",
            help="Type manager/specialiteit"
        )
    with col2:
        search_location = st.text_input(
            "Locatie (optioneel)",
            placeholder="e.g. 'Netherlands'",
            help="Geografische regio"
        )
        search_limit = st.number_input("Max. profielen per keyword", min_value=10, max_value=500, value=100)

    st.divider()

    if search_keywords_input:
        keywords_list = [kw.strip() for kw in search_keywords_input.split('\n') if kw.strip()]

        st.success(f"✓ {len(keywords_list)} zoekterm(en) geladen:")
        for kw in keywords_list:
            st.caption(f"  • {kw}")

        st.divider()

        # Output file selector
        base_filename, output_format, output_path = output_file_selector(key_prefix="search")

        st.divider()

        # Build command with multiple keywords
        cmd = f'python cli.py search'
        for kw in keywords_list:
            cmd += f' --keywords "{kw}"'

        cmd += f' --limit {search_limit} --out {output_path}'

        if search_seniority:
            cmd += f' --seniority {search_seniority}'
        if search_manager_type:
            cmd += f' --manager-type "{search_manager_type}"'
        if search_location:
            cmd += f' --location "{search_location}"'

        show_command_preview(cmd)

        if st.button("Zoeken & Scrapen", use_container_width=True, key="search_btn", type="primary"):
            st.success("Commando klaar! Kopieer het bovenstaande en voer uit in je terminal.")
    else:
        st.info("Voer minstens één zoekterm in om het commando te genereren")

# Footer
st.divider()
st.markdown("""
### Hoe het werkt

1. **Configureer je zoekopdracht** - Voer URL's, zoektermen, of locaties in
2. **Kies je uitvoerformaat** - JSONL (standaard) of CSV (spreadsheet)
3. **Bekijk het commando** - Je ziet precies wat zal worden uitgevoerd
4. **Kopieer en voer uit** - Copy & paste in je terminal
5. **Wacht op de resultaten** - Controleer regelmatig de output map

### Output Mappen
- JSONL: Standaardformaat (één profiel per regel)
- CSV: Spreadsheet-formaat voor analyse in Excel
- Alle bestanden gaan naar de `output/` folder

### Tips
- Gebruik passende **vertragingen** in Instellingen om geblokkeerd te worden voorkomen
- Test eerst met een **klein aantal** profielen
- Sluit alles af als je klaar bent (`Ctrl+C` in terminal)
""")
