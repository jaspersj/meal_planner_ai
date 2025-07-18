import streamlit as st
from backend.pantry.db import init_db, list_items, add_item, remove_item

# Import the proper rerun exception and data
from streamlit.runtime.scriptrunner import RerunException, RerunData

def main():
    st.title("🍱 JR & Yvie's Pantry Manager")

    # ─── Initialize Database ────────────────────────────────────────────────
    if st.button("Initialize Database"):
        init_db()
        st.success("Database initialized.")
        # force Streamlit to reload the whole script
        raise RerunException(RerunData())

    # ─── Show Current Items ────────────────────────────────────────────────
    st.subheader("Current Items")
    rows = list_items()
    if rows:
        for r in rows:
            expires = r["expires_at"] or "—"
            unit    = r["unit"] or ""
            st.text(f"{r['name']} — {r['quantity']} {unit} (expires: {expires})")
    else:
        st.text("Your pantry is empty. Add something below!")

    st.markdown("---")

    # ───  Add / Update Item Form ───────────────────────────────────────────
    st.subheader("Add / Update Item")
    with st.form("add_form", clear_on_submit=True):
        name    = st.text_input("Name")
        qty     = st.number_input("Quantity", value=1.0, step=0.5)
        unit    = st.text_input("Unit (optional)")
        exp_str = st.text_input(
            "Expires on (optional, YYYY-MM-DD)",
            placeholder="YYYY-MM-DD"
        )
        submitted = st.form_submit_button("Save Item")

        if submitted:
            add_item(
                name=name.strip(),
                qty=qty,
                unit=(unit.strip() or None),
                expires_at=(exp_str.strip() or None),
            )
            st.success(
                f"Saved **{name}** ({qty} {unit or ''})"
                + (f", expires {exp_str}" if exp_str.strip() else "")
            )
            # force a full rerun
            raise RerunException(RerunData())

    st.markdown("---")

    # ───  Remove Item Form ─────────────────────────────────────────────────
    st.subheader("Remove Item")
    with st.form("remove_form", clear_on_submit=True):
        to_remove = st.selectbox(
            "Select item to remove",
            options=[r["name"] for r in rows] or [""]
        )
        removed = st.form_submit_button("Remove")

        if removed and to_remove:
            remove_item(to_remove)
            st.success(f"Removed **{to_remove}**")
            # force a full rerun
            raise RerunException(RerunData())

if __name__ == "__main__":
    main()