import streamlit as st

from db.expenses_repo import rename_category, get_expenses
from db.rules_repo import load_rules, persist, normalize_rules

RESET_ADD_INPUT = "cat_add_reset"
CATEGORIES = "cat_rules"


def render_category_manager_minimal() -> None:
    if CATEGORIES not in st.session_state:
        st.session_state[CATEGORIES] = normalize_rules(load_rules())
    else:
        st.session_state[CATEGORIES] = normalize_rules(st.session_state[CATEGORIES])

    if RESET_ADD_INPUT not in st.session_state:
        st.session_state[RESET_ADD_INPUT] = False

    rules: dict[str, list[str]] = st.session_state[CATEGORIES]
    cats = list(rules.keys())

    left, right = st.columns([10, 1], vertical_alignment="center")

    with left:
        selected = st.pills(
            " ",
            options=["all"] + cats,
            default="all",
            key="cat_pills_min",
            label_visibility="collapsed",
        )
        sel = None if selected == "all" else selected
        st.session_state["selected_category"] = sel

    with right:
        with st.popover("＋", width="stretch"):
            if st.session_state[RESET_ADD_INPUT]:
                st.session_state["cat_add_min"] = ""
                st.session_state[RESET_ADD_INPUT] = False

            new_cat = st.text_input(
                " ",
                placeholder="new category",
                label_visibility="collapsed",
                key="cat_add_min",
            )

            if st.button("Add", key="cat_add_btn_min", width="stretch"):
                new_cat = (new_cat or "").strip()
                if not new_cat:
                    st.caption("Enter a name")
                elif new_cat in rules:
                    st.caption("Already exists")
                else:
                    rules[new_cat] = []
                    rules = normalize_rules(rules)
                    st.session_state[CATEGORIES] = rules
                    persist(rules)
                    st.session_state[RESET_ADD_INPUT] = True
                    st.cache_data.clear()
                    get_expenses.clear()
                    st.rerun()

    if sel:
        a, b, c = st.columns([8, 2, 2], vertical_alignment="center")

        rename_key = f"cat_rename_min_{sel}"

        with a:
            new_name = st.text_input(
                " ",
                value=sel,
                label_visibility="collapsed",
                key=rename_key,
            )

        with b:
            if st.button("Save", width="stretch"):
                old_name = sel
                new_name = (new_name or "").strip()

                if not new_name:
                    st.caption("Enter a name")
                elif new_name != old_name and new_name in rules:
                    st.caption("Name taken")
                else:
                    rename_category(old_name, new_name)
                    rules[new_name] = rules.pop(old_name)
                    rules = normalize_rules(rules)
                    persist(rules)
                    st.session_state[CATEGORIES] = normalize_rules(load_rules())

                    try:
                        st.cache_data.clear()
                        get_expenses.clear()
                        st.rerun()
                    except Exception as e:
                        print(f"Error:{e}")

        with c:
            with st.popover("Delete", width="stretch"):
                st.warning(f"Delete **{sel}**?")
                if st.button("Confirm", type="primary", width="stretch"):
                    rules.pop(sel, None)
                    rules = normalize_rules(rules)
                    st.session_state[CATEGORIES] = rules
                    persist(rules)
                    try:
                        st.cache_data.clear()
                        get_expenses.clear()
                        st.rerun()
                    except Exception as e:
                        print(f"Error:{e}")
