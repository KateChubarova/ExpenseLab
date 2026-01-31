import streamlit as st
import json
from pathlib import Path


def render_category_manager_minimal(
        *,
        categories_file: str = "category_rules.json",
        default_rules: dict[str, list[str]] | None = None,
        keep_other: bool = True,
) -> None:
    if default_rules is None:
        default_rules = {"other": []}

    path = Path(categories_file)

    def load_rules() -> dict[str, list[str]]:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    out: dict[str, list[str]] = {}
                    for k, v in data.items():
                        k = str(k).strip()
                        if not k:
                            continue
                        if isinstance(v, list):
                            out[k] = [str(x) for x in v if str(x).strip()]
                        else:
                            out[k] = []
                    return out
            except Exception:
                pass
        return default_rules.copy()

    def persist(rules: dict[str, list[str]]) -> None:
        try:
            path.write_text(json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def normalize_rules(rules: dict[str, list[str]]) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for k, v in rules.items():
            k = str(k).strip()
            if not k:
                continue
            lst = v if isinstance(v, list) else []
            cleaned = []
            seen = set()
            for x in lst:
                s = str(x).strip()
                if not s:
                    continue
                if s in seen:
                    continue
                seen.add(s)
                cleaned.append(s)
            out[k] = cleaned

        if keep_other and "other" not in out:
            out["other"] = []

        return out

    if "cat_rules" not in st.session_state:
        st.session_state["cat_rules"] = normalize_rules(load_rules())
    else:
        st.session_state["cat_rules"] = normalize_rules(st.session_state["cat_rules"])

    if "cat_add_reset" not in st.session_state:
        st.session_state["cat_add_reset"] = False

    rules: dict[str, list[str]] = st.session_state["cat_rules"]
    cats = sorted(rules.keys())

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
        with st.popover("＋", use_container_width=True):
            if st.session_state["cat_add_reset"]:
                st.session_state["cat_add_min"] = ""
                st.session_state["cat_add_reset"] = False

            new_cat = st.text_input(
                " ",
                placeholder="new category",
                label_visibility="collapsed",
                key="cat_add_min",
            )

            if st.button("Add", key="cat_add_btn_min", use_container_width=True):
                new_cat = (new_cat or "").strip()
                if not new_cat:
                    st.caption("Enter a name")
                elif new_cat in rules:
                    st.caption("Already exists")
                else:
                    rules[new_cat] = []
                    rules = normalize_rules(rules)
                    st.session_state["cat_rules"] = rules
                    persist(rules)
                    st.session_state["cat_add_reset"] = True
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
            if st.button("Save", use_container_width=True):
                new_name = (new_name or "").strip()
                if not new_name:
                    st.caption("Enter a name")
                elif new_name != sel and new_name in rules:
                    st.caption("Name taken")
                else:
                    rules[new_name] = rules.pop(sel)
                    rules = normalize_rules(rules)
                    st.session_state["cat_rules"] = rules
                    persist(rules)
                    st.rerun()

        with c:
            with st.popover("Delete", use_container_width=True):
                st.warning(f"Delete **{sel}**?")
                if st.button("Confirm", type="primary", use_container_width=True):
                    rules.pop(sel, None)
                    rules = normalize_rules(rules)
                    st.session_state["cat_rules"] = rules
                    persist(rules)
                    st.rerun()
