import streamlit as st
from .whiteboard import WhiteBoard

class StSupplement:
    _tabs = {
        "whiteboard":True,
        "document": True,
        "file_manager":True
    }


    def __init__(self,label = "supplement",expanded=False, **kwargs):
        self._expander = st.expander(label, expanded=expanded)

        # load **kwargs to adjust which tabs should be put into supplement
        for k,v in self._tabs.items():
            if k in kwargs.keys(): self._tabs[k]=kwargs[k]



    def initialize_expander(self):
        activator = {
            "whiteboard":self.set_whiteboard,
            "document":self.set_document,
            "file_manager":self.set_file_manager
        }

        tab_list = [k for k,v in self._tabs.items() if v is True]
        self._tabs =  self._expander.tabs(tab_list)
        for i,tab in enumerate(tab_list):
            activator[tab](self._tabs[i]) 

        return self._expander

    def set_whiteboard(self,tab):
        with tab:
            WB=WhiteBoard()
    def set_document(self, tab, header:str="Document"):
        with tab:
            st.header(header)
            doc_file = open("./doc/document.md", "r")
            doc_str = doc_file.read()
            st.markdown(doc_str,unsafe_allow_html=True)

    def set_file_manager(self,tab):
        pass


