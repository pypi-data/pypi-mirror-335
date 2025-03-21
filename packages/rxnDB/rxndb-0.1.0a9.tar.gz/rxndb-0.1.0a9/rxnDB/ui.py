from shiny import ui
from faicons import icon_svg
from rxnDB.utils import app_dir
from shinywidgets import output_widget

def configure_ui(phases: list[str], init_phases: list[str]) -> ui.page_sidebar:
    """
    Creates and configures the user interface for the rxnDB Shiny app
    """
    return ui.page_sidebar(
        ui.sidebar(
            # Dark mode toggle for the app
            ui.input_dark_mode(id="mode"),

            # Checkbox group for selecting reactants
            ui.input_checkbox_group(
                "reactants",
                "Reactants",
                phases,
                selected=init_phases,
            ),

            # Checkbox group for selecting products
            ui.input_checkbox_group(
                "products",
                "Products",
                phases,
                selected=init_phases,
            )
        ),

        # Main content layout with columns for sliders and action buttons
        ui.layout_column_wrap(
            # Action button to download current figure
            ui.input_action_button("download_plotly", "Download Figure"),

            # Action button to select all reactants
            ui.input_action_button("show_plot_labels", "Show Rxn ID Labels"),

            # Action button to select all reactants
            ui.input_action_button("toggle_reactants", "Select All Reactants"),

            # Action button to select all products
            ui.input_action_button("toggle_products", "Select All Products"),

            # Prevents the layout from filling the entire page width
            fill=False
        ),

        # Layout with two cards: one for the phase diagram and one for the datatable
        ui.layout_columns(
            ui.card(
                ui.card_header("Phase Diagram"),
                output_widget("plotly"),
                full_screen=True,
            ),
            ui.card(
                ui.card_header("Database"),
                ui.output_data_frame("datatable"),
                ui.layout_column_wrap(
                    ui.input_action_button("toggle_find_similar_rxns", "Show Similar Rxns"),
                    ui.input_action_button("clear_selection", "Clear Selection"),
                    fill=False,
                ),
                full_screen=True,
            )
        ),

        # Include custom styles from the styles.css file
        ui.include_css(app_dir / "styles.css"),

        # Set the title of the page
        title="rxnsDB",

        # Allow the app to be resized (fillable)
        fillable=True
    )
