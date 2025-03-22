import base64

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder,JsCode,GridUpdateMode, DataReturnMode
#from st_aggrid.shared import GridUpdateMode
from ...dao.connector import BlobConnector,parse_db_access
import pandas as pd
import azure



#db_access = parse_db_access("./examples/db_connector_testing/db.ini","optisuitestorage")

def ReadPictureFile(wch_fl):
    try:
        return base64.b64encode(open(wch_fl, 'rb').read()).decode()

    except:
        return ""

def create_BCE_explorer(df: pd.DataFrame,selected_rows:list):
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """


    image_nation = JsCode("""function (params) {
        console.log(params);
        var element = document.createElement("span");
        var imageElement = document.createElement("img");
    
        imageElement.src = params.data.imgPath;
        imageElement.width="20";
        imageElement.height="20";

        element.appendChild(imageElement);
        element.appendChild(document.createTextNode(params.value));
        return element;
        }""")

    if df.shape[0] > 0:
        for _, row in df.iterrows():
            imgExt = row.imgPath[-4:]
            row.imgPath = f'data:image/{imgExt};base64,' + ReadPictureFile(row.imgPath)

    #theme: # options-> "streamlit","alpine", "light", "dark", "blue", "fresh", "material"
    #https://streamlit-aggrid.readthedocs.io/en/docs/GridOptionsBuilder.html
    gb = GridOptionsBuilder.from_dataframe(df)
    # gb = GridOptionsBuilder.from_dataframe(
    #     df, enableRowGroup=True, enableValue=True, enablePivot=True
    # )
    gb.configure_column('icon', cellRenderer=image_nation,width=80)
    gb.configure_column("imgPath", hide = "True")
    gb.configure_column("type", hide = "True")
    gb.configure_column("path", hide = "True")
    gb.configure_column("blob name",width=640)
    gb.configure_default_column(
        resizable=True,
        sortable=True,
        filterable =True,
        autoSizeColumns=True
    )
    #gb.configure_side_bar()

    grid_height = 300 #st.sidebar.number_input("Grid height", min_value=200, max_value=800, value=300)
    return_mode = "FILTERED" # st.sidebar.selectbox("Return Mode", list(DataReturnMode.__members__), index=1)
    return_mode_value = DataReturnMode.__members__[return_mode]

    selection_mode='single' #st.sidebar.radio("Selection Mode", ['single','multiple'], index=1)
    gb.configure_selection(selection_mode,
                            use_checkbox=True,
                            suppressRowClickSelection =True,
                            pre_selected_rows=selected_rows)
    #gb.configure_selection(selection_mode,use_checkbox=True,groupSelectsChildren=True, groupSelectsFiltered=True)
    #gb.configure_selection(selection_mode, use_checkbox=True, groupSelectsChildren=groupSelectsChildren, groupSelectsFiltered=groupSelectsFiltered)
    
    #gb.configure_pagination(paginationAutoPageSize=True)
    paginationPageSize=10
    gb.configure_pagination(paginationAutoPageSize=False,
                            paginationPageSize=paginationPageSize
                            )


    grid_response  = AgGrid(
        df,
        enable_enterprise_modules=False,
        gridOptions=gb.build(),
        width='60%',
        height=grid_height, 
        theme="streamlit",
        data_return_mode=return_mode_value, 
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=False,
        reload_data=True,
        key="selection",
        #columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        #GridUpdateMode.MODEL_CHANGED,
    )

    return grid_response 

class BlobVirtualFolder:
    def __init__(self,db_access,path:str):
        BC = BlobConnector(db_access)
        self.path=path
        self.elements = pd.DataFrame(
            map(
                lambda x:['','folder',"folder.png",x.name,path] if isinstance(x,azure.storage.blob._list_blobs_helper.BlobPrefix) else ['','file',"file.png",x.name,path],BC.blob_container_client.walk_blobs(path)    
            ), columns = ['icon',"type","imgPath","blob name","path"]
        )

        self._folders = [
            x.name for x in BC.blob_container_client.walk_blobs(path)
            if isinstance(x,azure.storage.blob._list_blobs_helper.BlobPrefix)
        ]
        
        if path is not None:
            self.parent_path = self._get_parent_folder()
            self.elements = pd.concat([pd.DataFrame({
                "icon":'',
                "type":'folder',
                'imgPath':'undo.png',
                "blob name":self.parent_path,
                "path":path 
            },index =[0]),self.elements]).reset_index(drop = True)
        else:
            self.parent_path = "root"

    def _get_parent_folder(self):
        if len(self.path.split("/"))<=2:
            return None
        else:
            temp = self.path.split("/")
            return "/".join(temp[:-2])+"/"
    
    @property
    def folders(self):
        return self._folders

    @folders.setter
    def folders(self,f_list:list):
        self._folders = f_list

class BlobContainerExplorer:
    def __init__(self,db_access):
        self.BC = BlobConnector(db_access)
        self.db_access = db_access

        # initialize BVF and walk all folder by DFS
        self.BVF = self.start_dfs()
         
    @property
    def path(self):
        return self._path

    @path.setter
    def path(self,folder_path:str):
        self._path = folder_path
        self._parent_path=self.BVF[self._path].parent_path
        self._elements = self.BVF[self._path].elements
        

    @property
    def parent_path(self):
        return self._parent_path

    @parent_path.setter
    def parent_path(self):
        self._parent_path = self.BVF[self._path].parent_path

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self):
        self._elements = self.BVF[self._path].elements


    def start_dfs(self):
        self.BVF = {}
        self.walk_folder(None)
        return self.BVF


    def walk_folder(self,path):
        if path not in self.BVF.keys():
            self.BVF[path] = BlobVirtualFolder(self.db_access,path)

        if len(self.BVF[path].folders)>0:
            self.walk_folder(self.BVF[path].folders.pop())
        elif self.BVF[path].parent_path != "root":
                return self.walk_folder(self.BVF[path].parent_path)
        else:
                return None


