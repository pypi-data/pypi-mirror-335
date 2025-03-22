from itables.streamlit import interactive_table


def create_interactive_table(df):
    interactive_table(
        df,
        caption="Countries",
        select=True,
    )
