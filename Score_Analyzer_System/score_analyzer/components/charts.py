"""
Plotly chart helpers used across all dashboards.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

BLUE_SCALE  = ["#1E3A8A","#1D4ED8","#3B82F6","#60A5FA","#93C5FD","#BFDBFE"]
GREEN_SCALE = ["#065F46","#047857","#10B981","#34D399","#6EE7B7","#A7F3D0"]
MIXED       = ["#1E3A8A","#10B981","#F59E0B","#EF4444","#8B5CF6","#EC4899",
               "#06B6D4","#84CC16","#F97316","#6366F1"]

_layout_defaults = dict(
    font_family="Inter, sans-serif",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=40, b=20),
)

# ─────────────────────────────────────────────
def pie_subject_performance(marks: list) -> go.Figure:
    """Pie chart: subject-wise marks for a student."""
    labels = [m["subject_name"] for m in marks]
    values = [m["marks_obtained"] for m in marks]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=.45,
        marker_colors=MIXED[:len(labels)],
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Marks: %{value}<br>Share: %{percent}<extra></extra>"
    ))
    fig.update_layout(
        title_text="Subject-wise Marks Distribution",
        showlegend=True,
        legend=dict(orientation="v", x=1.02, y=.5),
        **_layout_defaults
    )
    return fig

# ─────────────────────────────────────────────
def bar_subject_marks(marks: list, student_name: str = "") -> go.Figure:
    """Horizontal bar: marks per subject."""
    df = pd.DataFrame(marks).sort_values("marks_obtained", ascending=True)
    colors = ["#10B981" if v >= 75 else "#F59E0B" if v >= 50 else "#EF4444"
              for v in df["marks_obtained"]]

    fig = go.Figure(go.Bar(
        x=df["marks_obtained"],
        y=df["subject_name"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.0f}" for v in df["marks_obtained"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Marks: %{x}<extra></extra>"
    ))
    fig.update_layout(
        title_text=f"Marks by Subject{' – ' + student_name if student_name else ''}",
        xaxis=dict(range=[0, 105], title="Marks Obtained"),
        yaxis=dict(title=""),
        **_layout_defaults
    )
    return fig

# ─────────────────────────────────────────────
def bar_subject_averages(averages: list) -> go.Figure:
    """Bar: subject averages for a section."""
    df = pd.DataFrame(averages)
    fig = go.Figure(go.Bar(
        x=df["subject_name"],
        y=df["avg_marks"],
        marker_color=BLUE_SCALE[2],
        text=[f"{v:.1f}" for v in df["avg_marks"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Avg: %{y:.1f}<extra></extra>"
    ))
    fig.update_layout(
        title_text="Subject-wise Average Marks",
        xaxis_tickangle=-30,
        yaxis=dict(range=[0, 105], title="Average Marks"),
        **_layout_defaults
    )
    return fig

# ─────────────────────────────────────────────
def bar_section_comparison(section_data: dict) -> go.Figure:
    """Grouped bar: section-wise averages per subject."""
    sections = list(section_data.keys())
    all_subjects = set()
    for v in section_data.values():
        for item in v:
            all_subjects.add(item["subject_name"])
    all_subjects = sorted(all_subjects)

    fig = go.Figure()
    for i, sec in enumerate(sections):
        d = {item["subject_name"]: item["avg_marks"] for item in section_data[sec]}
        fig.add_trace(go.Bar(
            name=f"Section {sec}",
            x=all_subjects,
            y=[d.get(s, 0) for s in all_subjects],
            marker_color=MIXED[i]
        ))
    fig.update_layout(
        barmode="group",
        title_text="Section-wise Subject Averages",
        xaxis_tickangle=-30,
        yaxis_title="Average Marks",
        **_layout_defaults
    )
    return fig

# ─────────────────────────────────────────────
def scatter_rank_distribution(rank_data: list) -> go.Figure:
    """Scatter: student percentages with rank."""
    df = pd.DataFrame(rank_data)
    colors = ["gold" if r == 1 else "silver" if r == 2 else
              "#CD7F32" if r == 3 else "#3B82F6"
              for r in df["rank"]]

    fig = go.Figure(go.Scatter(
        x=df["rank"],
        y=df["percentage"],
        mode="markers+text",
        text=df["name"],
        textposition="top center",
        marker=dict(size=10, color=colors),
        hovertemplate="<b>%{text}</b><br>Rank: %{x}<br>%: %{y:.1f}<extra></extra>"
    ))
    fig.update_layout(
        title_text="Student Rank Distribution",
        xaxis_title="Rank",
        yaxis=dict(title="Percentage (%)", range=[0, 105]),
        **_layout_defaults
    )
    return fig

# ─────────────────────────────────────────────
def donut_section_counts(section_counts: dict) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=list(section_counts.keys()),
        values=list(section_counts.values()),
        hole=.55,
        marker_colors=MIXED[:4],
        textinfo="label+value"
    ))
    fig.update_layout(
        title_text="Students per Section",
        **_layout_defaults
    )
    return fig

# ─────────────────────────────────────────────
def bar_performers(data: list, title: str, color: str = "#3B82F6") -> go.Figure:
    df = pd.DataFrame(data)
    fig = go.Figure(go.Bar(
        x=[d["name"] for d in data],
        y=[d["percentage"] for d in data],
        marker_color=color,
        text=[f"{d['percentage']:.1f}%" for d in data],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>%: %{y:.1f}<extra></extra>"
    ))
    fig.update_layout(
        title_text=title,
        yaxis=dict(range=[0, 110], title="Percentage (%)"),
        **_layout_defaults
    )
    return fig
