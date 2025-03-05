import streamlit as st
import plotly.graph_objects as go

# Constants
CLASSES = ["Y13a", "Y13b", "Y13c", "Y12a", "Y12b", "Y12c", "Y12d", "Y12e"]
TEACHERS = ["None", "CFE", "AHA", "TOB"]
TEACHER_COLORS = {"None": "#CCCCCC", "CFE": "#1E90FF", "AHA": "#FF4500", "TOB": "#32CD32"}

# Initialize session state for assignments if not done already
if "assignments" not in st.session_state:
    st.session_state.assignments = {f"{cls}_{unit}": "None" for cls in CLASSES for unit in ["Micro", "Macro"]}

# Streamlit Title
st.title("Class Scheduling Dashboard")

# Helper Functions

def render_teacher_buttons(unit_suffix, row):
    """Renders buttons for a given unit type (Micro or Macro)."""
    for i, cls in enumerate(CLASSES):
        unit = f"{cls}_{unit_suffix}"
        current_teacher = st.session_state.assignments[unit]
        button_label = f"{cls} {unit_suffix} ({current_teacher})"
        
        with row[i]:
            if st.button(button_label, key=unit, use_container_width=True):
                new_teacher = TEACHERS[(TEACHERS.index(current_teacher) + 1) % len(TEACHERS)]
                st.session_state.assignments[unit] = new_teacher
                st.rerun()  # Trigger a rerun to immediately reflect the change

def check_rules():
    """Check the validation rules and return the results."""
    rules = {
        "All units in all classes have an assigned teacher": rule_all_units_assigned(),
        "Every class has a different teacher across Micro and Macro": rule_different_teachers_in_class(),
        "Every teacher has 5 or 6 classes": rule_teacher_class_count(),
        "No teacher has a class in all four combinations (Y12 + Y13, Macro and Micro)": rule_no_teacher_in_all_combinations()
    }
    return rules

def rule_all_units_assigned():
    """Check if all units in all classes have an assigned teacher."""
    return all(st.session_state.assignments[f"{cls}_Micro"] != "None" and st.session_state.assignments[f"{cls}_Macro"] != "None" for cls in CLASSES)

def rule_different_teachers_in_class():
    """Check if every class has a different teacher across Micro and Macro."""
    return all(st.session_state.assignments[f"{cls}_Micro"] != st.session_state.assignments[f"{cls}_Macro"] for cls in CLASSES)

def rule_teacher_class_count():
    """Check if every teacher has 5 or 6 classes."""
    teacher_class_counts = {teacher: 0 for teacher in TEACHERS}
    for cls in CLASSES:
        teacher_class_counts[st.session_state.assignments[f"{cls}_Micro"]] += 1
        teacher_class_counts[st.session_state.assignments[f"{cls}_Macro"]] += 1
    invalid_teachers = {teacher: count for teacher, count in teacher_class_counts.items() if count < 5 or count > 6}
    return invalid_teachers

def rule_no_teacher_in_all_combinations():
    """Check if no teacher has a class in all four combinations (Y12 + Y13, Micro and Macro)."""
    teacher_class_combinations = {teacher: set() for teacher in TEACHERS}
    for cls in CLASSES:
        micro_teacher = st.session_state.assignments[f"{cls}_Micro"]
        macro_teacher = st.session_state.assignments[f"{cls}_Macro"]
        teacher_class_combinations[micro_teacher].add((cls[0], "Micro"))
        teacher_class_combinations[macro_teacher].add((cls[0], "Macro"))
    
    return all(len(combinations) < 4 for combinations in teacher_class_combinations.values())
def create_class_layout():
    """Create the class layout diagram using Plotly."""
    x_vals, y_vals, marker_colors, size_vals = [], [], [], []
    
    for i, cls in enumerate(CLASSES):
        micro_teacher = st.session_state.assignments[f"{cls}_Micro"]
        macro_teacher = st.session_state.assignments[f"{cls}_Macro"]
        x_vals.extend([i] * 2)  # Repeat x position for each row (Micro and Macro)
        y_vals.extend([1, 1.25])  # Micro on 1, Macro on 1.25 (closer together)
        marker_colors.extend([TEACHER_COLORS[micro_teacher], TEACHER_COLORS[macro_teacher]])
        size_vals.extend([30, 30])  # Increased size of the circles

    # Create the scatter plot
    fig = go.Figure()

    # Add circles (markers) for Micro and Macro units
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='markers',
        marker=dict(
            color=marker_colors,
            size=size_vals,
            line=dict(width=2, color='DarkSlateGrey')
        ),
        text=[f"{CLASSES[i % len(CLASSES)]} Micro" if i % 2 == 0 else f"{CLASSES[i // 2]} Macro" for i in range(len(x_vals))],
        hovertemplate="%{text}<br>Teacher: %{marker.color}<extra></extra>",
    ))

    # Layout adjustments for Plotly
    fig.update_layout(
        title="",
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(CLASSES))),
            ticktext=CLASSES,
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=[1, 1.25],  # Micro on 1, Macro on 1.25 (closer together)
            ticktext=["Micro", "Macro"],
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=14)
        ),
        xaxis_title="Classes",
        yaxis_title="Units",
        margin=dict(t=20, b=50, l=50, r=20),  # Reduce margins to make the diagram compact
        height=200,
        width=800,
        dragmode=False,
        hovermode="closest",
        showlegend=False,
        title_font=dict(size=20),
        shapes=[
            dict(
                type="rect",
                x0=-0.5,
                x1=2.5,
                y0=0.85,
                y1=1.4,
                fillcolor="rgba(255, 200, 200, 0.6)",  # Y13 color
                opacity=0.6,
                layer="below",
                line_width=0
            ),
            dict(
                type="rect",
                x0=2.5,
                x1=7.5,
                y0=0.85,
                y1=1.4,
                fillcolor="rgba(200, 200, 255, 0.6)",  # Y12 color
                opacity=0.6,
                layer="below",
                line_width=0
            ),
        ],
    )

    # Display the Plotly figure
    st.plotly_chart(fig)


# UI: Render the buttons and the class layout
st.subheader("Click a Class Unit to Cycle Through Teachers")
macro_row = st.columns(len(CLASSES))
render_teacher_buttons("Macro", macro_row)

micro_row = st.columns(len(CLASSES))
render_teacher_buttons("Micro", micro_row)

# UI: Display the class layout diagram
st.subheader("Class Layout Diagram")
create_class_layout()

# Validation Rules Section
st.subheader("Validation Rules")
rules = check_rules()

for rule, is_valid in rules.items():
    icon = "✅" if is_valid else "❌"
    st.markdown(f"{icon} {rule}")

invalid_teachers = rule_teacher_class_count()
if invalid_teachers:
    st.subheader("Teachers with invalid class counts")
    for teacher, count in invalid_teachers.items():
        st.markdown(f"❌ {teacher} has {count} classes (must have 5 or 6).")

# Legend for Teacher Colors
st.subheader("Legend")
st.write("""
- **CFE**: Blue
- **AHA**: Red
- **TOB**: Green
- **None**: Gray
""")
