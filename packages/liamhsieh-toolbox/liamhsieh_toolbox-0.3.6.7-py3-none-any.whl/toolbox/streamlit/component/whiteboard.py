from streamlit_drawable_canvas import st_canvas
import streamlit as st

from PIL import Image
import io

class WhiteBoard:
    def __init__(self):
        self.WB = st.container()
        self.pars={}
        with self.WB:

            self.initial_toolbar()
            self.canvas = self.initial_canvas()
            if self.canvas.image_data is not None:
                jpg_col,png_col, empty = st.columns([1,1,8])
                with jpg_col:
                    self.convert_to_jpg()
                with png_col:
                    self.convert_to_png()
                    

    def convert_to_png(self):
        img = Image.fromarray(self.canvas.image_data.astype("uint8"), mode="RGBA")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_data = buffered.getvalue()

        return st.download_button(
            label="export png",
            data=img_data,
            file_name='WB.png',
            mime='image/png',
        )
    def convert_to_jpg(self):
        img = Image.fromarray(self.canvas.image_data.astype("uint8"), mode="YCbCr")
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_data = buffered.getvalue()

        return st.download_button(
            label="export jpg",
            data=img_data,
            file_name='WB.jpg',
            mime='image/jpg',
        )

    def initial_toolbar(self):
        pars=self.pars

        bg_color_col,bg_image_col, empty = st.columns([1,3,6])
        with bg_color_col:
            pars["bg_color"] = st.color_picker("Background color: ", "#eee")
        with bg_image_col:
            pars["bg_image"] = st.file_uploader("Background image:", type=["png", "jpg"])


        drawing_mode_col,stroke_color_col,stroke_width_col,point_display_radius_col  = st.columns([6,1,2,1])
        with drawing_mode_col:
            pars["drawing_mode"] = st.radio(
                "Mode:",
                ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
                horizontal=True
            )

        with stroke_color_col:
            pars["stroke_color"] = st.color_picker("Stroke color: ")

        with stroke_width_col:
            pars["stroke_width"] = st.slider("Stroke width: ", 1, 10, 1)

        with point_display_radius_col:   
            pars["point_display_radius"]= st.slider("Point radius: ", 1, 25, 3)

    def initial_canvas(self):
        pars=self.pars

        return st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
            stroke_width=pars["stroke_width"],
            stroke_color=pars["stroke_color"],
            background_color=pars["bg_color"],
            background_image=Image.open(pars["bg_image"]) if pars["bg_image"]  else None,
            update_streamlit=True,
            height=900,
            width=1200,
            drawing_mode=pars["drawing_mode"],
            point_display_radius=pars["point_display_radius"] if pars["drawing_mode"] == 'point' else 0,
            key="full_app",
        )
