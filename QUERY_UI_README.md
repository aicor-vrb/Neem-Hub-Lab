# Query UI README

This document explains how to add new query types to the notebook UI in [notebooks/demo_ui.py](/home/hassouna/neemhub/Neem-Hub-Lab/notebooks/demo_ui.py:1).

## Overview

The query UI is template-based.

Each query shown in the left panel is defined by:

- an entry in `QUERY_TEMPLATES`
- optional UI controls for its parameters
- query-generation logic in `_build_question(...)`
- code-preview logic in `_generated_query_text(...)`

The notebook entrypoint is [notebooks/demo.ipynb](/home/hassouna/neemhub/Neem-Hub-Lab/notebooks/demo.ipynb:1), which creates a database session and calls `run_ui(session=session)`.

## Current Flow

The UI works in this order:

1. The user selects a query template in the `Question` dropdown.
2. The UI shows only the options relevant to that template.
3. The UI renders a read-only `Generated query` preview.
4. Clicking `Fetch NEEM entries` calls `_default_fetch(...)`.
5. `_default_fetch(...)` builds the EQL question, runs it through `eql_to_sql(...)`, and shows the output on the right.

## Main Places To Edit

- Template registry: [notebooks/demo_ui.py](/home/hassouna/neemhub/Neem-Hub-Lab/notebooks/demo_ui.py:19)
- Query preview builder: [notebooks/demo_ui.py](/home/hassouna/neemhub/Neem-Hub-Lab/notebooks/demo_ui.py:373)
- Query object builder: [notebooks/demo_ui.py](/home/hassouna/neemhub/Neem-Hub-Lab/notebooks/demo_ui.py:394)
- Fetch execution: [notebooks/demo_ui.py](/home/hassouna/neemhub/Neem-Hub-Lab/notebooks/demo_ui.py:414)
- UI wiring: [notebooks/demo_ui.py](/home/hassouna/neemhub/Neem-Hub-Lab/notebooks/demo_ui.py:465)

## Add A New Query

Use this process.

### 1. Add a template entry

Add a new item to `QUERY_TEMPLATES`.

Example:

```python
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
    "recent_actions": {
        "label": "Recent actions",
        "description": "Fetch recent action entries.",
        "uses_status": False,
    },
}
```

Required fields:

- `label`: what the user sees in the dropdown
- `description`: short explanation shown in the UI

Optional flags:

- `uses_status`: whether the query should show the `Status` control

If you add a new kind of parameter later, use another explicit flag such as:

- `uses_entity_type`
- `uses_relation`
- `uses_property_name`

That pattern is easier to maintain than hardcoding query names throughout the UI.

### 2. Add UI controls if the query needs parameters

If the query needs an extra parameter, create a widget in `run_ui(...)`.

Example:

```python
entity_type = widgets.Dropdown(
    options=["DesignatorNodeDAO", "ActionNodeDAO"],
    value="DesignatorNodeDAO",
    description="Entity type",
)
```

Then add it to the `controls` layout and show or hide it depending on the selected template.

Example pattern:

```python
entity_type.layout.display = "" if QUERY_TEMPLATES[selection["template"]]["uses_entity_type"] else "none"
```

Also update `_update_selection(...)` so the widget value is stored in `selection`.

### 3. Update the generated query preview

`_generated_query_text(selection)` should return the exact Python/EQL snippet shown in the UI.

This is important because:

- colleagues can see what the UI is generating
- it makes debugging easier
- it keeps the simple UI aligned with the actual code

Example:

```python
def _generated_query_text(selection):
    if selection["template"] == "recent_actions":
        return "\n".join([
            "action = variable(type_=DesignatorNodeDAO, domain=[])",
            "",
            "question = an(entity(action))",
        ])
```

If a query becomes multi-step, keep the preview readable rather than minimizing lines.

### 4. Update the actual query builder

`_build_question(selection)` must construct the real EQL query object.

Example:

```python
def _build_question(selection):
    action = variable(type_=DesignatorNodeDAO, domain=[])

    if selection["template"] == "all_task_executions":
        return an(entity(action))

    if selection["template"] == "actions_by_status":
        return an(entity(action)).where(
            action.status == getattr(TaskStatus, selection["status"])
        )
```

If you add a new template, add a new branch here.

If several templates share the same structure, prefer a small helper function instead of copying branches.

### 5. Make sure selection state has defaults

The `selection` dict in `run_ui(...)` must contain defaults for any new parameter.

Example:

```python
selection = {
    "template": "actions_by_status",
    "status": "SUCCEEDED",
    "entity_type": "DesignatorNodeDAO",
}
```

If you forget this, the UI can render but fail when the query preview or fetch code reads a missing key.

## Example: Add A Simple Query Without Extra Controls

Suppose you want to add `All actions`.

### Template

```python
"all_actions": {
    "label": "All actions",
    "description": "Fetch all action entries.",
    "uses_status": False,
},
```

### Preview

```python
if selection["template"] == "all_actions":
    return "\n".join([
        "action = variable(type_=DesignatorNodeDAO, domain=[])",
        "",
        "question = an(entity(action))",
    ])
```

### Query builder

```python
if selection["template"] == "all_actions":
    return an(entity(action))
```

That is enough if no extra options are needed.

## Example: Add A Query With One Extra Parameter

Suppose you want to add `Actions by status`.

### Template

```python
"actions_by_status": {
    "label": "Actions by status",
    "description": "Find action entries whose recorded task status matches the selected value.",
    "uses_status": True,
},
```

### UI control

The current UI already has:

```python
status = widgets.Dropdown(
    options=_task_status_options(),
    value=selection["status"],
    description="Status",
)
```

### Preview

```python
question = an(entity(action)).where(action.status == TaskStatus.SUCCEEDED)
```

### Query builder

```python
return an(entity(action)).where(
    action.status == getattr(TaskStatus, selection["status"])
)
```

## Recommended Pattern For Future Queries

Use one of these categories when adding new templates:

- `Entity list`
  Example: all actions, all designators
- `Entity + property filter`
  Example: actions by status
- `Entity + relation filter`
  Example: entities related to another entity
- `Advanced/custom`
  Example: raw EQL editor for power users

That keeps the UI coherent as it grows.

## Testing Checklist

After adding a new query:

1. Reload the notebook UI.
2. Select the new template.
3. Check that only the correct controls are visible.
4. Check that the `Generated query` preview matches the intended query.
5. Click `Fetch NEEM entries`.
6. Verify that results appear in the right panel.

For a quick syntax check outside the notebook:

```bash
python3 -m py_compile notebooks/demo_ui.py
```

## Common Mistakes

- Adding a template entry but forgetting to handle it in `_build_question(...)`
- Updating `_build_question(...)` but forgetting `_generated_query_text(...)`
- Adding a new widget but not storing its value in `selection`
- Forgetting to set a default value in `selection`
- Hiding a control visually but still assuming its value exists for every template

## Suggested Next Step

The current code is a good base for adding:

- more entity types
- property-based queries
- relation-based queries
- a future advanced mode with custom EQL input

If the number of templates grows much further, move template definitions and query builders into a separate module such as `notebooks/query_templates.py` so `demo_ui.py` stays readable.
