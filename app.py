import streamlit as st
import pandas as pd
from datetime import datetime
import copy


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Gtrans - Auth Test",
    page_icon="🚚",
    layout="wide",
)


# =========================================================
# OPTIONS
# =========================================================

ROUTE_OPTIONS = [
    "ΧΑΛΚΙΔΙΚΗ (ΓΑΛΑΤΙΣΤΑ)",
    "ΧΑΛΚΙΔΙΚΗ",
    "ΚΙΛΚΙΣ",
    "ΠΙΕΡΙΑ",
    "ΗΜΑΘΙΑ",
    "ΕΛΑΣΣΟΝΑ",
    "ΘΕΣΣΑΛΟΝΙΚΗ",
    "ΑΜΥΝΤΑΙΟ",
    "ΑΝΕΦΟΔΙΑΣΜΟΣ",
    "ΣΥΝΕΡΓΕΙΟ",
]


CLIENT_OPTIONS = [
    "ΜΕΒΓΑΛ",
    "ΛΥΚΑΣ",
    "PROLACTA",
]


VEHICLE_OPTIONS = [
    "ΕΚΒ 4058",
    "ΙΑΕ 6034",
    "ΝΧΥ 3413",
    "ΙΕΜ 1556",
    "ΖΝΒ 7991",
    "ΖΝΒ 7971",
    "XZH1006",
    "ΝΧΥ 3547",
    "ΙΤΜ 3656",
    "ΝΧΥ 3546",
    "ΙΕΜ 1356",
    "IAE 4351",
    "ΕΚΒ 3941",
    "ΒΚΤ 9409",
]


DRIVER_OPTIONS = [
    "ΒΑΚΑΛΦΩΤΗΣ ΒΑΓΓΕΛΗΣ",
    "ΒΑΚΑΛΦΩΤΗΣ ΓΡΗΓΟΡΗΣ",
    "ΚΟΛΤΣΙΝΑΚΟΣ ΒΑΓΓΕΛΗΣ",
    "ΙΜΠΑΣ ΙΟΡΔΑΝΗΣ",
    "ΠΑΤΣΑΒΟΥΔΗΣ ΤΡΑΪΑΝΟΣ",
    "ΣΠΑΡΤΑΛΙΔΗΣ ΧΡΗΣΤΟΣ",
]


# =========================================================
# MOCK DATA
# Δεν υπάρχει καμία σύνδεση με Supabase
# =========================================================

INITIAL_MOCK_ROUTES = [
    {
        "id": 1,
        "route": "ΧΑΛΚΙΔΙΚΗ",
        "client": "ΜΕΒΓΑΛ",
        "plate": "ΕΚΒ 4058",
        "driver": "ΒΑΚΑΛΦΩΤΗΣ ΒΑΓΓΕΛΗΣ",
        "start_km": 120000,
        "started_at": "15/10/2026 06:30",
        "is_closed": False,
    },
    {
        "id": 2,
        "route": "ΠΙΕΡΙΑ",
        "client": "ΛΥΚΑΣ",
        "plate": "ΙΑΕ 6034",
        "driver": "ΣΠΑΡΤΑΛΙΔΗΣ ΧΡΗΣΤΟΣ",
        "start_km": 85000,
        "started_at": "15/10/2026 07:00",
        "is_closed": False,
    },
    {
        "id": 3,
        "route": "ΘΕΣΣΑΛΟΝΙΚΗ",
        "client": "PROLACTA",
        "plate": "ΙΤΜ 3656",
        "driver": "ΙΜΠΑΣ ΙΟΡΔΑΝΗΣ",
        "start_km": 97500,
        "started_at": "15/10/2026 07:15",
        "is_closed": False,
    },
    {
        "id": 4,
        "route": "ΚΙΛΚΙΣ",
        "client": "ΜΕΒΓΑΛ",
        "plate": "ΝΧΥ 3546",
        "driver": "ΠΑΤΣΑΒΟΥΔΗΣ ΤΡΑΪΑΝΟΣ",
        "start_km": 110000,
        "started_at": "14/10/2026 05:45",
        "is_closed": True,
    },
]


if "routes" not in st.session_state:
    st.session_state.routes = copy.deepcopy(INITIAL_MOCK_ROUTES)


# =========================================================
# LOGIN
# =========================================================

def login():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return

    st.title("🚚 Gtrans")
    st.subheader("🔐 Σύνδεση χρήστη")

    with st.form("login_form"):

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password",
        )

        login_button = st.form_submit_button(
            "Σύνδεση",
            use_container_width=True,
        )

        if login_button:

            username = username.strip().lower()

            try:
                users = st.secrets["users"]

                if username not in users:
                    st.error("Λάθος username ή password.")
                    return

                user = users[username]

                if password != user["password"]:
                    st.error("Λάθος username ή password.")
                    return

                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.role = user["role"]
                st.session_state.driver = user.get("driver", "")

                st.rerun()

            except Exception:
                st.error(
                    "Δεν έχουν ρυθμιστεί ακόμη τα Streamlit Secrets."
                )

    st.stop()


login()


# =========================================================
# CURRENT USER
# =========================================================

CURRENT_USERNAME = st.session_state.username
CURRENT_ROLE = st.session_state.role
CURRENT_DRIVER = st.session_state.driver

IS_ADMIN = CURRENT_ROLE == "admin"


# =========================================================
# HELPERS
# =========================================================

def get_routes_dataframe():

    return pd.DataFrame(
        st.session_state.routes
    )


def get_visible_routes(open_only=False):

    df = get_routes_dataframe()

    if df.empty:
        return df

    # DRIVER:
    # βλέπει μόνο εγγραφές με το δικό του όνομα
    if not IS_ADMIN:
        df = df[
            df["driver"] == CURRENT_DRIVER
        ]

    if open_only:
        df = df[
            df["is_closed"] == False
        ]

    return df.copy()


def get_available_drivers():

    # ADMIN βλέπει όλους
    if IS_ADMIN:
        return DRIVER_OPTIONS

    # DRIVER βλέπει μόνο τον εαυτό του
    return [CURRENT_DRIVER]


def logout():

    for key in [
        "authenticated",
        "username",
        "role",
        "driver",
    ]:

        if key in st.session_state:
            del st.session_state[key]

    st.rerun()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("👤 Χρήστης")

    if IS_ADMIN:

        st.success("ADMIN")
        st.write(
            f"Username: **{CURRENT_USERNAME}**"
        )

    else:

        st.info("DRIVER")

        st.write(
            f"**{CURRENT_DRIVER}**"
        )

    st.divider()

    if st.button(
        "🚪 Αποσύνδεση",
        use_container_width=True,
    ):
        logout()

    if IS_ADMIN:

        st.divider()

        if st.button(
            "🔄 Reset Test Data",
            use_container_width=True,
        ):

            st.session_state.routes = copy.deepcopy(
                INITIAL_MOCK_ROUTES
            )

            st.rerun()


# =========================================================
# HEADER
# =========================================================

st.title("🚚 Gtrans - Test Login")

st.warning(
    "🧪 TEST ΠΕΡΙΒΑΛΛΟΝ — "
    "Δεν υπάρχει σύνδεση με Supabase."
)


# =========================================================
# TABS
# =========================================================

tab_new, tab_open, tab_all = st.tabs(
    [
        "🆕 Νέο Δρομολόγιο",
        "✏️ Ανοιχτά Δρομολόγια",
        "📄 Όλα & Αναφορές",
    ]
)


# =========================================================
# TAB 1
# =========================================================

with tab_new:

    st.subheader(
        "🆕 Νέο Δρομολόγιο"
    )

    available_drivers = get_available_drivers()

    with st.form(
        "new_route_form",
        clear_on_submit=True,
    ):

        route = st.selectbox(
            "Δρομολόγιο",
            ROUTE_OPTIONS,
        )

        client = st.selectbox(
            "Πελάτης",
            CLIENT_OPTIONS,
        )

        vehicle = st.selectbox(
            "Όχημα",
            VEHICLE_OPTIONS,
        )

        start_km = st.number_input(
            "Χιλιομετρική ένδειξη έναρξης",
            min_value=0.0,
            step=1.0,
            format="%.0f",
        )

        driver = st.selectbox(
            "Ονοματεπώνυμο οδηγού",
            available_drivers,
        )

        submitted = st.form_submit_button(
            "✅ Δημιουργία TEST δρομολογίου",
            use_container_width=True,
        )

        if submitted:

            next_id = max(
                [
                    r["id"]
                    for r
                    in st.session_state.routes
                ],
                default=0,
            ) + 1

            new_record = {

                "id": next_id,

                "route": route,

                "client": client,

                "plate": vehicle,

                "driver": driver,

                "start_km": start_km,

                "started_at":
                    datetime.now().strftime(
                        "%d/%m/%Y %H:%M"
                    ),

                "is_closed": False,
            }

            st.session_state.routes.append(
                new_record
            )

            st.success(
                f"TEST δρομολόγιο "
                f"#{next_id} δημιουργήθηκε."
            )


# =========================================================
# TAB 2
# =========================================================

with tab_open:

    st.subheader(
        "✏️ Ανοιχτά Δρομολόγια"
    )

    open_df = get_visible_routes(
        open_only=True
    )

    if open_df.empty:

        st.info(
            "Δεν υπάρχουν ανοιχτά "
            "δρομολόγια για τον χρήστη."
        )

    else:

        st.dataframe(
            open_df,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        route_labels = []

        for _, row in open_df.iterrows():

            route_labels.append(
                f"ID {row['id']} | "
                f"{row['route']} | "
                f"{row['plate']} | "
                f"{row['driver']}"
            )

        selected_route = st.selectbox(
            "Επιλογή δρομολογίου",
            route_labels,
        )

        selected_id = int(
            selected_route
            .split("|")[0]
            .replace("ID", "")
            .strip()
        )

        if st.button(
            "✅ Κλείσιμο TEST δρομολογίου"
        ):

            for record in st.session_state.routes:

                if record["id"] == selected_id:

                    record["is_closed"] = True

                    break

            st.success(
                f"Το δρομολόγιο "
                f"#{selected_id} έκλεισε."
            )

            st.rerun()


# =========================================================
# TAB 3
# =========================================================

with tab_all:

    st.subheader(
        "📄 Όλα & Αναφορές"
    )

    visible_df = get_visible_routes()

    if visible_df.empty:

        st.info(
            "Δεν υπάρχουν εγγραφές."
        )

    else:

        st.dataframe(
            visible_df,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            f"Εγγραφές που βλέπει ο χρήστης: "
            f"{len(visible_df)}"
        )

        if IS_ADMIN:

            st.success(
                "Ως ADMIN βλέπεις "
                "όλες τις εγγραφές."
            )

        else:

            st.info(
                f"Βλέπεις μόνο τις εγγραφές του: "
                f"{CURRENT_DRIVER}"
            )
