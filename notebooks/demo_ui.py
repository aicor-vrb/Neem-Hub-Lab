import html
import logging
import os
import sys
import warnings
from base64 import b64encode
from pathlib import Path
from pprint import pformat

import ipywidgets as widgets
from IPython.display import HTML, display

logging.disable(logging.CRITICAL)
os.environ.setdefault("PYTHONWARNINGS", "ignore")
warnings.filterwarnings("ignore")


CURRENT_DEMO_SELECTION = {}
BACKGROUND_IMAGE_PATH = (
    Path(__file__).resolve().parent.parent.joinpath("img", "ease-background.png")
)
LOGO_IMAGE_PATH = Path(__file__).resolve().parent.parent.joinpath("img", "acior-logo.png")
DEFAULT_DB_URL = "postgresql+psycopg2://readonly_user:aicor-vrb@134.102.137.85:15432/mydb"
QUERY_TEMPLATES = {
    "actions_by_status": {
        "label": "Actions by status",
        "description": "Find action entries whose recorded task status matches the selected value.",
        "uses_status": True,
    },
    "all_task_executions": {
        "label": "All task executions",
        "description": "Fetch action entries without applying a task-status condition.",
        "uses_status": False,
    },
}


def _ensure_cognitive_architecture_on_path():
    candidates = (
        Path("/root/libs/cognitive_robot_abstract_machine"),
        Path("/home/jovyan/libs/cognitive_robot_abstract_machine"),
        Path("/workspace/libs/cognitive_robot_abstract_machine"),
    )
    for base in candidates:
        if not base.exists():
            continue
        for path in (
            base,
            base / "src",
            base / "pycram",
            base / "pycram" / "src",
            base / "krrood",
            base / "krrood" / "src",
        ):
            if path.exists() and str(path) not in sys.path:
                sys.path.insert(0, str(path))


_ensure_cognitive_architecture_on_path()


def _inject_styles():
    background_image = ""
    if BACKGROUND_IMAGE_PATH.exists():
        background_image = b64encode(BACKGROUND_IMAGE_PATH.read_bytes()).decode("ascii")

    style_template = """
        <style>
        .demo-shell {
            --demo-ink: #17324d;
            --demo-muted: #64748b;
            --demo-accent: #b64d47;
            --demo-accent-strong: #8d312c;
            --demo-accent-soft: #fdf0ec;
            --demo-card: #ffffff;
            --demo-line: #e7edf3;
            --demo-surface: #f7fafc;
            font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
            color: var(--demo-ink);
            position: relative;
            background:
                linear-gradient(180deg, rgba(251, 253, 255, 0.96) 0%, rgba(244, 248, 251, 0.97) 100%);
            border: 1px solid var(--demo-line);
            border-radius: 24px;
            box-shadow: 0 16px 36px rgba(31, 52, 84, 0.08);
            padding: 30px;
            overflow: hidden;
        }
        .demo-shell::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.78) 0%, rgba(247, 250, 252, 0.84) 100%),
                url("data:image/png;base64,__BACKGROUND_IMAGE__");
            background-position: center top, calc(50% + 240px) -56px;
            background-repeat: no-repeat;
            background-size: auto, 112% auto;
            opacity: 0.72;
            pointer-events: none;
        }
        .demo-shell > * {
            position: relative;
            z-index: 1;
        }
        .demo-logo-wrap {
            display: flex;
            justify-content: center;
            margin-bottom: 22px;
        }
        .demo-logo {
            width: min(100%, 360px);
            height: auto;
            display: block;
            filter: drop-shadow(0 10px 20px rgba(23, 50, 77, 0.12));
        }
        .demo-card {
            background: var(--demo-card);
            border: 1px solid var(--demo-line);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 20px rgba(30, 58, 95, 0.04);
        }
        .demo-hero {
            display: grid;
            gap: 10px;
            margin-bottom: 24px;
            width: min(100%, 760px);
        }
        .demo-kicker {
            display: inline-flex;
            width: fit-content;
            padding: 7px 13px;
            border-radius: 999px;
            background: #edf3f8;
            color: #6a7f93;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .demo-title {
            font-size: 30px;
            font-weight: 700;
            line-height: 1.05;
            letter-spacing: -0.03em;
            margin: 0;
        }
        .demo-copy {
            max-width: 70ch;
            color: var(--demo-muted);
            line-height: 1.55;
            font-size: 15px;
            margin: 0;
        }
        .demo-grid {
            display: grid;
            grid-template-columns: minmax(300px, 420px) minmax(320px, 1fr);
            gap: 18px;
            align-items: start;
        }
        .demo-ui .widget-label {
            color: var(--demo-muted);
            font-size: 13px;
            font-weight: 600;
            min-width: 90px;
        }
        .demo-ui .widget-dropdown select,
        .demo-ui .widget-inttext input,
        .demo-ui .widget-text input {
            border-radius: 12px;
            border: 1px solid var(--demo-line);
            box-shadow: none;
            background: var(--demo-surface);
            font-size: 14px;
            color: var(--demo-ink);
        }
        .demo-action .widget-button {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: auto;
            min-width: 220px;
            border: 0;
            border-radius: 999px;
            padding: 12px 18px;
            background: linear-gradient(135deg, #2f6fa3 0%, #4d8fc4 100%);
            color: white;
            font-weight: 700;
            letter-spacing: 0.01em;
            text-align: center !important;
            line-height: 1.2 !important;
            box-shadow: 0 12px 22px rgba(47, 111, 163, 0.24);
        }
        .demo-stop-button .widget-button {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: auto;
            min-width: 180px;
            border: 0;
            border-radius: 14px;
            padding: 12px 18px;
            background: linear-gradient(135deg, #d39a27 0%, #e8b447 100%);
            color: white;
            font-weight: 700;
            text-align: center !important;
            line-height: 1.2 !important;
            box-shadow: 0 12px 22px rgba(211, 154, 39, 0.24);
        }
        .demo-summary {
            display: grid;
            gap: 10px;
        }
        .demo-badge-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
        }
        .demo-badge {
            display: grid;
            gap: 4px;
            padding: 12px 14px;
            border-radius: 14px;
            background: var(--demo-surface);
            border: 1px solid var(--demo-line);
        }
        .demo-badge-label {
            color: var(--demo-muted);
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .demo-badge-value {
            font-size: 18px;
            font-weight: 700;
        }
        .demo-note {
            padding: 12px 14px;
            border-radius: 14px;
            background: var(--demo-accent-soft);
            color: var(--demo-accent-strong);
            font-size: 13px;
            line-height: 1.5;
        }
        .demo-status {
            margin-top: 14px;
            padding: 16px 18px;
            border-radius: 16px;
            background: linear-gradient(135deg, #fff4df 0%, #ffe8bf 100%);
            border: 1px solid #f1c97a;
            color: #7a4b00;
            font-size: 15px;
            font-weight: 700;
            line-height: 1.4;
        }
        .demo-results {
            display: grid;
            gap: 16px;
        }
        .demo-results-title {
            font-size: 18px;
            font-weight: 700;
            margin: 0;
        }
        .demo-results-copy {
            color: var(--demo-muted);
            font-size: 14px;
            line-height: 1.5;
            margin: 0;
        }
        .demo-code {
            margin: 0;
            padding: 16px;
            border-radius: 16px;
            border: 1px solid var(--demo-line);
            background: #f6f8fb;
            color: #1f2f44;
            font-size: 12px;
            line-height: 1.45;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-word;
        }
        .demo-help {
            display: grid;
            gap: 10px;
            margin-top: 14px;
        }
        .demo-help-row {
            display: grid;
            grid-template-columns: 14px 1fr;
            gap: 10px;
            align-items: start;
            color: var(--demo-muted);
            font-size: 13px;
            line-height: 1.45;
        }
        .demo-help-dot {
            width: 10px;
            height: 10px;
            margin-top: 4px;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--demo-accent) 0%, #dd7463 100%);
        }
        @media (max-width: 900px) {
            .demo-grid {
                grid-template-columns: 1fr;
            }
            .demo-logo {
                width: min(100%, 280px);
            }
        }
        </style>
    """
    display(HTML(style_template.replace("__BACKGROUND_IMAGE__", background_image)))


def _logo_header():
    if not LOGO_IMAGE_PATH.exists():
        return None

    logo_data = b64encode(LOGO_IMAGE_PATH.read_bytes()).decode("ascii")
    return widgets.HTML(
        value=f"""
        <div class="demo-logo-wrap">
          <img class="demo-logo" src="data:image/png;base64,{logo_data}" alt="AICOR" />
        </div>
        """
    )


def _hero():
    return widgets.HTML(
        value="""
        <div class="demo-hero">
          <div class="demo-kicker">NEEM Query Explorer</div>
          <p class="demo-copy">
            This demo now focuses on querying NEEMs directly. Use the controls to build
            a small Entity Query Language lookup, fetch matching entries from the database.
          </p>
        </div>
        """
    )


def _selection_summary(selection):
    template = QUERY_TEMPLATES[selection["template"]]
    if template["uses_status"]:
        query_options = f"Task status: {selection['status'].title()}"
    else:
        query_options = "No extra options"
    return f"""
    <div class="demo-summary">
    </div>
    """


def _style_label(value):
    return value.replace("_", " ").title()


def _format_preview(value, max_chars=5000):
    text = pformat(value, width=100, compact=False)
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + "\n... [truncated]"
    return html.escape(text)


def _render_results(result):
    query_repr = html.escape(result["query_repr"])
    first_result = result["first"]
    first_repr = "No rows returned." if first_result is None else _format_preview(first_result)

    return f"""
    <div class="demo-results">
      <div>
        <p class="demo-results-title">Query Results</p>
        <p class="demo-results-copy">
          Retrieved <strong>{result['count']}</strong> matching entries from the NEEM database.
        </p>
      </div>
      <div>
        <p class="demo-results-copy">EQL query</p>
        <pre class="demo-code">{query_repr}</pre>
      </div>
      <div>
        <p class="demo-results-copy">First result preview</p>
        <pre class="demo-code">{first_repr}</pre>
      </div>
    </div>
    """


def _generated_query_text(selection):
    template = QUERY_TEMPLATES[selection["template"]]
    lines = ["action = variable(type_=DesignatorNodeDAO, domain=[])", ""]
    if not template["uses_status"]:
        lines.append("question = an(entity(action))")
    else:
        lines.append(
            "question = an(entity(action)).where("
            "action.status == TaskStatus."
            f"{selection['status']})"
        )
    return "\n".join(lines)


def _task_status_options():
    try:
        from pycram.datastructures.enums import TaskStatus

        return [(_style_label(status.name), status.name) for status in TaskStatus]
    except Exception:
        return [
            ("Succeeded", "SUCCEEDED"),
            ("Failed", "FAILED"),
            ("Running", "RUNNING"),
        ]


def _build_question(selection):
    try:
        from krrood.entity_query_language.factories import an, entity, variable
        from pycram.datastructures.enums import TaskStatus
        from pycram.orm.ormatic_interface import DesignatorNodeDAO
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Could not import CRAM query modules. The Binder image is missing "
            "`krrood` or `pycram`, or their source paths are not visible to the notebook kernel."
        ) from exc

    template = QUERY_TEMPLATES[selection["template"]]
    action = variable(type_=DesignatorNodeDAO, domain=[])
    question = an(entity(action))
    if template["uses_status"]:
        question = question.where(
            action.status == getattr(TaskStatus, selection["status"])
        )
    return question


def _default_fetch(selection, session):
    if session is None:
        raise ValueError("A SQLAlchemy session is required to fetch NEEMs.")

    from krrood.ormatic.eql_interface import eql_to_sql

    question = _build_question(selection)
    results = eql_to_sql(question, session).evaluate()
    return {
        "query_repr": _generated_query_text(selection),
        "count": len(results),
        "first": results[0] if results else None,
        "results": results,
    }


def run_info_ui():
    _inject_styles()
    children = []
    logo_header = _logo_header()
    if logo_header is not None:
        children.append(logo_header)
    children.append(
        widgets.HTML(
            value="""
            <div class="demo-card">
              <p class="demo-results-title">How To Use This Demo</p>
              <div class="demo-help">
                  <div class="demo-help-row">
                    <div class="demo-help-dot"></div>
                  <div>Choose the question you want to ask about the NEEM data.</div>
                </div>
                <div class="demo-help-row">
                  <div class="demo-help-dot"></div>
                  <div>Inspect the generated query preview to see the exact EQL expression behind that question.</div>
                </div>
                <div class="demo-help-row">
                  <div class="demo-help-dot"></div>
                  <div>Click <code>Fetch NEEM entries</code> to evaluate the query and inspect the returned objects.</div>
                </div>
              </div>
            </div>
            """
        )
    )
    container = widgets.VBox(children, layout=widgets.Layout(width="100%"))
    container.add_class("demo-shell")
    display(container)


def run_ui(session=None, on_fetch=None):
    global CURRENT_DEMO_SELECTION

    _inject_styles()

    selection = {
        "template": "actions_by_status",
        "status": "SUCCEEDED",
    }
    CURRENT_DEMO_SELECTION = selection.copy()

    query_template = widgets.Dropdown(
        options=[
            (template["label"], key) for key, template in QUERY_TEMPLATES.items()
        ],
        value=selection["template"],
        description="Question",
    )
    status = widgets.Dropdown(
        options=_task_status_options(),
        value=selection["status"],
        description="Status",
    )

    summary = widgets.HTML(value=_selection_summary(selection))
    option_summary = widgets.HTML(
        value=f"""
        <div class="demo-note">
          {html.escape(QUERY_TEMPLATES[selection["template"]]["description"])}
        </div>
        """
    )
    query_preview = widgets.HTML(
        value=f"""
        <div>
          <p class="demo-results-copy">Generated query</p>
          <pre class="demo-code">{html.escape(_generated_query_text(selection))}</pre>
        </div>
        """
    )
    fetch_button = widgets.Button(description="Fetch NEEM entries", icon="database")
    clear_button = widgets.Button(description="Clear results", icon="eraser")
    running_notice = widgets.HTML(value="")
    result_panel = widgets.HTML(
        value="""
        <div class="demo-card">
          <p class="demo-results-title">Ready</p>
          <p class="demo-results-copy">
            Run the query to see how many NEEM entries match and inspect the first result inline.
          </p>
        </div>
        """
    )
    output = widgets.Output()

    fetch_button_box = widgets.Box([fetch_button])
    fetch_button_box.add_class("demo-action")
    clear_button_box = widgets.Box([clear_button])
    clear_button_box.add_class("demo-stop-button")
    action_row = widgets.VBox(
        [
            fetch_button_box,
            clear_button_box,
        ],
        layout=widgets.Layout(gap="10px", align_items="flex-start"),
    )
    action_row.add_class("demo-action-row")

    controls = widgets.VBox(
        [
            widgets.HTML(
                value="""
                <div class="demo-card">
                  <p class="demo-results-title">What Do You Want To Ask?</p>
                  <p class="demo-results-copy">
                    Choose a query template first. The notebook will build the corresponding
                    EQL question and show it before running anything.
                  </p>
                </div>
                """
            ),
            query_template,
            status,
            option_summary,
            summary,
            query_preview,
            action_row,
            running_notice,
        ]
    )
    controls.add_class("demo-card")
    controls.add_class("demo-ui")

    results = widgets.VBox([result_panel, output])
    results.add_class("demo-card")

    def _update_selection(change):
        global CURRENT_DEMO_SELECTION
        if change["owner"] is query_template:
            selection["template"] = change["new"]
        elif change["owner"] is status:
            selection["status"] = change["new"]
        CURRENT_DEMO_SELECTION = selection.copy()
        status.layout.display = "" if QUERY_TEMPLATES[selection["template"]]["uses_status"] else "none"
        summary.value = _selection_summary(selection)
        option_summary.value = f"""
        <div class="demo-note">
          {html.escape(QUERY_TEMPLATES[selection["template"]]["description"])}
        </div>
        """
        query_preview.value = f"""
        <div>
          <p class="demo-results-copy">Generated query</p>
          <pre class="demo-code">{html.escape(_generated_query_text(selection))}</pre>
        </div>
        """

    query_template.observe(_update_selection, names="value")
    status.observe(_update_selection, names="value")
    status.layout.display = ""

    def _set_running_state(is_running, message=""):
        fetch_button.disabled = is_running
        query_template.disabled = is_running
        status.disabled = is_running
        running_notice.value = message

    def _handle_fetch(_):
        callback = on_fetch or _default_fetch
        output.clear_output()
        _set_running_state(
            True,
            '<div class="demo-status">Querying the NEEM database. This can take a moment.</div>',
        )
        try:
            result = callback(selection.copy(), session)
        except Exception as exc:
            result_panel.value = f"""
            <div class="demo-card">
              <p class="demo-results-title">Query Failed</p>
              <p class="demo-results-copy">
                {html.escape(str(exc))}
              </p>
            </div>
            """
            _set_running_state(False, "")
            return

        result_panel.value = _render_results(result)
        with output:
            if result["results"]:
                print(f"Fetched {result['count']} matching entries.")
                print("First result:")
                print(result["results"][0])
            else:
                print("Fetched 0 matching entries.")
        _set_running_state(False, "")

    def _handle_clear(_):
        output.clear_output()
        running_notice.value = ""
        result_panel.value = """
        <div class="demo-card">
          <p class="demo-results-title">Ready</p>
          <p class="demo-results-copy">
            Run the query to see how many NEEM entries match and inspect the first result inline.
          </p>
        </div>
        """

    fetch_button.on_click(_handle_fetch)
    clear_button.on_click(_handle_clear)

    children = []
    logo_header = _logo_header()
    if logo_header is not None:
        children.append(logo_header)
    children.append(_hero())
    children.append(
        widgets.VBox(
            [controls, results],
            layout=widgets.Layout(width="100%"),
        )
    )

    container = widgets.VBox(children, layout=widgets.Layout(width="100%"))
    container.add_class("demo-shell")
    display(container)


show_demo_ui = run_ui
show_demo_info_ui = run_info_ui
