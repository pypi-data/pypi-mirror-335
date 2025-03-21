import pandas as pd
import altair as alt


def plot_titers(
    data: pd.DataFrame,
    titer_col: str,
    condition_cols: list[str],
    facet_col: str = None,
    color_col: str = None,
    shape_col: str = None,
    interactive: bool = True,
    log_scale: bool = True,
    title: str = None,
    show_facet_title: bool = True,
    y_axis_label: str = "Titer (IU/ml)",
    width: int = 300,
    point_size: int = 100,
    filled: bool = True,
    text_size: int = 15,
    title_size: int = 20,
    axis_title_size: int = 16,
    axis_label_size: int = 14,
    legend_title_size: int = 16,
    legend_label_size: int = 14,
    facet_title_size: int = 16,
) -> alt.VConcatChart:
    """
    Create an Altair visualization of viral titer data from factorial/combinatorial experiments.
    This function generates a strip plot of titer values with a matrix of condition indicators below.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing titer values and experimental conditions.
        See example data for expected structure.
    titer_col : str
        Name of the column containing titer values (numeric).
    conditions_col : list[str]
        List of column names to use for condition indicators in the
        matrix display (e.g., ['Condition_A', 'Condition_B']).
    facet_col : str, optional
        Name of the column to use for creating separate faceted panels.
    color_col : str, optional
        Name of the column to use for color encoding in the strip plot
    shape_col : str, optional
        Name of the column to use for shape encoding in the strip plot.
    interactive : bool, default=True
        Whether to create an interactive plot with tooltips.
    log_scale : bool, default=True
        Whether to use logarithmic scale for the y-axis.
    title : str, default=""
        Title for the entire chart.
    show_facet_title : bool, default=True
        Whether to show the facet title in the strip plot.
    y_axis_label : str, default="Titer"
        Label for the y-axis.
    width : int, default=300
        Width of each facet panel in pixels.
    point_size : int, default=100
        Size of the points in the strip plot.
    filled : bool, default=True
        Whether to fill the points in the strip plot.
    text_size : int, default=15
        Size of the text in the condition matrix.
    title_size : int, default=20
        Size of the chart title text.
    axis_title_size : int, default=16
        Size of the axis title text.
    axis_label_size : int, default=14
        Size of the axis label text.
    legend_title_size : int, default=16
        Size of the legend title text.
    legend_label_size : int, default=14
        Size of the legend label text.
    facet_title_size : int, default=16
        Size of the facet title text.


    Returns
    -------
    alt.VConcatChart
        A vertically concatenated Altair chart object combining the
        strip plot and condition matrix.


    Examples
    --------
    >>> import pandas as pd
    >>> import altair as alt
    >>> from titerplot import plot_titers
    >>>
    >>> # Sample data
    >>> data = pd.DataFrame({
    ...     "Titer": [100000, 500000, 150000, 1000000, 300000, 100000],
    ...     "Virus": ["Virus A", "Virus A", "Virus B", "Virus B", "Virus C", "Virus C"],
    ...     "Facet": ["Facet A", "Facet A", "Facet A", "Facet A", "Facet A", "Facet A"],
    ...     "Condition_A": ["+", "+", "+", "+", "+", "+"],
    ...     "Condition_B": ["+", "+", "+", "+", "+", "+"],
    ...     "Condition_C": ["-", "+", "-", "+", "-", "+"],
    ...     "Condition_D": ["+", "-", "+", "-", "+", "-"]
    ... })
    >>>
    >>> # Create the plot
    >>> chart = plot_titers(
    ...     data=data,
    ...     titer_col="Titer",
    ...     conditions_col=["Condition_A", "Condition_B", "Condition_C", "Condition_D"],
    ...     facet_col="Facet",
    ...     color_col="Virus"
    ... )
    >>>
    >>> # Display the chart
    >>> chart
    """
    # Validate input data and parameters
    if data.empty:
        raise ValueError("Data is empty")
    if titer_col not in data.columns:
        raise ValueError(f"Column '{titer_col}' not found in DataFrame")
    if not pd.api.types.is_numeric_dtype(data[titer_col]):
        raise TypeError(f"Column '{titer_col}' must contain numeric data")
    missing_cols = [col for col in condition_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Condition columns not found: {missing_cols}")
    if facet_col is not None and facet_col not in data.columns:
        raise ValueError(f"Facet column '{facet_col}' not found in DataFrame")
    if color_col is not None and color_col not in data.columns:
        raise ValueError(f"Color column '{color_col}' not found in DataFrame")
    if shape_col is not None and shape_col not in data.columns:
        raise ValueError(f"Shape column '{shape_col}' not found in DataFrame")
    for col in condition_cols:
        valid_values = data[col].isin(["+", "-"])
        if not valid_values.all():
            invalid_values = data.loc[~valid_values, col].unique()
            raise ValueError(
                f"Column '{col}' contains invalid values: {invalid_values}. Expected '+' or '-'"
            )

    # Create a unique ID based on condition
    data["ID"] = ""
    for index, row in data.iterrows():
        conditions = []
        for col in condition_cols:
            if row[col] == "+":
                conditions.append(col.replace("Condition_", ""))
        data.at[index, "ID"] = "_".join(conditions)

    # Make the base strip plot
    strip_plot = (
        alt.Chart(data)
        .mark_point(size=point_size, filled=filled)
        .encode(
            x=alt.X(
                "ID:N",
                axis=alt.Axis(
                    title=None,
                    domain=False,
                    ticks=True,
                    labels=False,
                    grid=False,
                    labelFontSize=axis_label_size,
                ),
            )
        )
        .properties(
            width=width,
        )
    )

    # Make the base condition matrix by folding condition columns
    condition_matrix = (
        # strokeWidth=.00001 is necessary to avoid matrix shifting relative to the strip plot
        alt.Chart(data, view=alt.ViewConfig(strokeWidth=0.00001))
        .transform_fold(condition_cols, as_=["Condition", "Text"])
        .mark_text(size=text_size)
        .encode(
            x=alt.X("ID:N", axis=None),
            y=alt.Y(
                "Condition:N",
                axis=alt.Axis(
                    title=None,
                    domain=False,
                    grid=False,
                    ticks=False,
                    labelFontSize=axis_label_size,
                ),
            ),
            text="Text:N",
        )
        .properties(
            width=width,
        )
    )

    # Configure the titer axis with a log or linear scale
    y_axis = alt.Y(
        titer_col,
        title=y_axis_label,
        scale=alt.Scale(type="log" if log_scale else "linear"),
        axis=alt.Axis(
            titleFontSize=axis_title_size,
            labelFontSize=axis_label_size,
        ),
    )
    strip_plot = strip_plot.encode(
        y=y_axis,
    )

    # Add the facet column if provided
    if facet_col is not None:
        strip_plot = strip_plot.encode(
            column=alt.Column(
                facet_col,
                header=alt.Header(
                    title=None,
                    labels=show_facet_title,
                    labelFontSize=facet_title_size,
                ),
            )
        )
        condition_matrix = condition_matrix.encode(
            column=alt.Column(facet_col, header=alt.Header(title=None, labels=False))
        )
    # Add the color column if provided
    if color_col is not None:
        strip_plot = strip_plot.encode(
            color=alt.Color(
                color_col,
                legend=alt.Legend(
                    title=color_col,
                    titleFontSize=legend_title_size,
                    labelFontSize=legend_label_size,
                ),
            ),
        )
    # Add the shape column if provided
    if shape_col is not None:
        strip_plot = strip_plot.encode(
            shape=alt.Shape(
                shape_col,
                legend=alt.Legend(
                    title=shape_col,
                    titleFontSize=legend_title_size,
                    labelFontSize=legend_label_size,
                ),
            ),
        )

    # Add tooltips if interactive
    if interactive:
        strip_plot = strip_plot.encode(
            tooltip=[col for col in data.columns if col != "ID"]
        )

    # Combine the strip plot and condition matrix without vertical spacing
    title_config = alt.TitleParams(
        text=title if title is not None else "",
        fontSize=title_size,
        anchor="middle",
        align="center",
        offset=20,
    )
    chart = alt.vconcat(strip_plot, condition_matrix, spacing=0).properties(
        title=title_config
    )

    return chart
