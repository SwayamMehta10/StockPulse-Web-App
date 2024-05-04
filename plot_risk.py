import plotly.graph_objects as go


def plot_risk_scores(info):
    try:
        risk_scores = {
            "Audit Risk": info["auditRisk"],
            "Board Risk": info["boardRisk"],
            "Compensation Risk": info["compensationRisk"],
            "Shareholder Rights Risk": info["shareHolderRightsRisk"],
            "Overall Risk": info["overallRisk"],
        }

        color_map = {
            1: "green",
            2: "lightgreen",
            3: "yellowgreen",
            4: "yellow",
            5: "gold",
            6: "orange",
            7: "darkorange",
            8: "orangered",
            9: "red",
            10: "darkred",
        }

        fig = go.Figure()

        for risk, score in risk_scores.items():
            fig.add_trace(
                go.Bar(
                    x=[risk],
                    y=[score],
                    name=risk,
                    marker=dict(color=color_map[score]),
                    hovertemplate="%{x}: %{y}<extra></extra>"
                )
            )

        fig.update_layout(
            xaxis_title="Risk Type",
            yaxis_title="Risk Level",
            xaxis=dict(type="category"),
            yaxis=dict(range=[0, 10]),
            showlegend=False,
        )

        return fig.to_html(full_html=False, default_height=600, default_width=700)
    except:
        return "Data Not Available"
