#!/usr/bin/env python3
#
# Copyright (C) 2024-2025 Jure Cerar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path
import io
import base64

from shiny.express import ui, render, input
from shiny import reactive

import bingo.bingo as bingo

# Parse keyword file
filename = Path(__file__).parent / "bingo" / bingo.INPUT
try:
    with open(filename) as f:
        words = f.read().splitlines()
except:
    @reactive.effect
    def load_error():
        text = ui.p(f"Error: Could not load input file: '{filename}'",
                    style="font-weight: bold;")
        ui.notification_show(text, type="error")

# Define style
ui.tags.style(
    ".shiny-bound-output { display: flex; justify-content: center !important; }",
    ".form-control { height: 47px; }",
    ".footer { font-size: 75%; }",
)

# Main UI elements
ui.h1("⭐ Keyword Bingo")
ui.p(None)
with ui.layout_columns(col_widths=(2, 4, 3, 1,), gap="20px"):
    ui.p(None)
    ui.input_text("input_text", None, None, placeholder="Random seed", width="100%")
    ui.input_action_button("generate", "Generate!", class_="btn-success")
    ui.input_action_button("about", "?")


@render.ui
@reactive.event(input.generate)
def display_image():
    """Bingo card generator and display"""
    # Generate a bingo card
    seed = input.input_text()
    img = bingo.bingo(words, seed=seed)
    
    # Save image into a buffer 
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_data = buffer.read()

    # Encode and image as URI 
    encoded = base64.b64encode(img_data).decode("utf-8")
    data_uri = f"data:image/png;base64,{encoded}"

    return ui.img(src=data_uri, width="60%")


@reactive.effect
@reactive.event(input.about)
def show_about():
    """Display help in a modal"""
    title = "⭐ Keyword Bingo"
    text = ui.markdown(
        f"""
        __Spice up your next meeting with Keyword Bingo!__

        Tired of the same buzzwords and jargon? Turn those dull meetings
        into a game with Keyword Bingo! Just click the __Generate!__ button
        to get a random bingo card filled with classic corporate lingo.
        Want a consistent card to share with friends? Enter a __seed__ value 
        to generate the same card every time.

        Play solo or compete with coworkers. It's way more fun than pretending
        to listen and taking notes. 
        
        Think we're missing a must-have keyword? We'd love to hear your suggestions.
        Let us know at this [address](mailto:{bingo.__contact__}). 
        """
    )
    version = ui.a(bingo.__version__, href=bingo.__url__)
    footer = [
        ui.hr(width="100%", size=1),
        ui.div("Version: ", version, class_="footer"),
    ]
    modal = ui.modal(text, title=title, footer=footer, easy_close=True,)
    ui.modal_show(modal)
