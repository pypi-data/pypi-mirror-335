import os
import streamlit as st
import streamlit.components.v1 as components
from streamlit.runtime.scriptrunner import get_script_run_ctx
from typing import (
    List,
    Any,
    Dict,
    Optional,
    Union,
    Sequence,
    Callable,
    Tuple,
    TYPE_CHECKING,
)
from typing_extensions import Literal
from streamlit.runtime.uploaded_file_manager import UploadedFileRec
from streamlit import session_state

from ._languages import LANGUAGE_PACKS, CustomLanguagePack

if TYPE_CHECKING:
    from streamlit.runtime.memory_uploaded_file_manager import MemoryUploadedFileManager

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = True
COMPONENT_NAME = "st_file_uploader"

if not _RELEASE:
    _component_func = components.declare_component(
        COMPONENT_NAME,
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(COMPONENT_NAME, path=build_dir)

def file_uploader(
    label: str,
    *,
    accept_multiple_files: bool = False,
    type: Optional[Union[str, Sequence[str]]] = None,
    key: Optional[Union[str, int]] = None,
    help: Optional[str] = None,
    on_change: Optional[Callable] = None,
    args: Optional[Tuple] = None,
    kwargs: Optional[Dict[str, Any]] = None,
    disabled: bool = False,
    label_visibility: Literal["visible", "hidden", "collapsed"] = "visible",
    uploader_msg: Optional[str] = None,
    limit_msg: Optional[str] = None,
    button_msg: Optional[str] = None,
    icon: Optional[str] = None,
):
    """
    Display a customized file uploader widget based on Streamlit's file_uploader.
    
    All original parameters from Streamlit's file_uploader are supported, with additional
    customization options for the uploader messages.
    
    Parameters
    ----------
    label : str
        A short label explaining to the user what this file uploader is for.
    accept_multiple_files : bool, default False
        Whether to accept multiple files.
    type : str or list of str or None, default None
        The allowed file extension(s) for uploaded files.
    key : str or int or None, default None
        An optional key that uniquely identifies this component.
    help : str or None, default None
        A tooltip that gets displayed next to the widget label.
    on_change : callable or None, default None
        An optional callback invoked when this file_uploader's value changes.
    args : tuple or None, default None
        An optional tuple of args to pass to the callback.
    kwargs : dict or None, default None
        An optional dict of kwargs to pass to the callback.
    disabled : bool, default False
        An optional boolean, which disables the file uploader if set to True.
    label_visibility : "visible", "hidden", or "collapsed", default "visible"
        The visibility of the label.
    uploader_msg : str or None, default None
        Custom message for "Drag and drop file here".
    limit_msg : str or None, default None
        Custom message for "Limit ... per file".
    button_msg : str or None, default None
        Custom message for "Browse files" button.
    icon : str or None, default None
        Custom icon to use instead of the default cloud upload icon.
        
    Returns
    -------
    None, UploadedFile, or list of UploadedFile
        Same return types as st.file_uploader
    """
    # Prepare component parameters
    max_upload_size = st.get_option("server.maxUploadSize")
    
    # Format limit message if needed
    if limit_msg and "{max_upload_size}" in limit_msg:
        formatted_limit_msg = limit_msg.format(max_upload_size=max_upload_size)
    else:
        formatted_limit_msg = limit_msg or f"Limit {max_upload_size} MB per file"  

    # Create a callback key if we have a callback and a key
    callback_triggered = False
    if key is not None and on_change is not None:
        callback_key = f"{key}_callback_triggered"
        
        # Initialize callback state if not present
        if callback_key not in session_state:
            session_state[callback_key] = False
            
        # Check if we have a previous value to compare with
        value_key = f"{key}_previous_value"
        if value_key not in session_state:
            session_state[value_key] = None

    # Call the component function
    component_value = _component_func(
        label=label,
        type=type,
        acceptMultipleFiles=accept_multiple_files,
        key=key,
        help=help,
        disabled=disabled,
        labelVisibility=label_visibility,
        uploaderMsg=uploader_msg,
        limitMsg=formatted_limit_msg, 
        buttonMsg=button_msg,
        icon=icon,
        default=None,
        maxUploadSize=max_upload_size
    )
    
    # Handle the callback
    if key is not None and on_change is not None:
        # Check if value changed
        previous_value = session_state[value_key]
        if previous_value != component_value:
            # Prepare callback arguments
            callback_args = args or ()
            callback_kwargs = kwargs or {}
            
            # Set the flag that callback should be triggered
            session_state[callback_key] = True
            
            # Store the current value for future comparison
            session_state[value_key] = component_value
        
        # Trigger the callback if the flag is set
        if session_state[callback_key]:
            # Reset the flag
            session_state[callback_key] = False
            
            # Call the callback
            on_change(*callback_args, **callback_kwargs)
    
    # Return uploaded files
    return component_value

# Create language-specific versions of the file uploader
class LanguageFileUploader:
    def __init__(self, language_pack):
        self.language_pack = language_pack
        
    def file_uploader(
        self,
        label: str,
        *,
        accept_multiple_files: bool = False,
        type: Optional[Union[str, Sequence[str]]] = None,
        key: Optional[Union[str, int]] = None,
        help: Optional[str] = None,
        on_change: Optional[Callable] = None,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        disabled: bool = False,
        label_visibility: Literal["visible", "hidden", "collapsed"] = "visible",
        uploader_msg: Optional[str] = None,
        limit_msg: Optional[str] = None,
        button_msg: Optional[str] = None,
        icon: Optional[str] = None,
    ):
        # Custom messages take precedence over language pack defaults
        uploader_msg = uploader_msg or self.language_pack.uploader_msg
        limit_msg = limit_msg or self.language_pack.limit_msg
        button_msg = button_msg or self.language_pack.button_msg
        icon = icon or self.language_pack.icon
        
        return file_uploader(
            label=label,
            accept_multiple_files=accept_multiple_files,
            type=type,
            key=key,
            help=help,
            on_change=on_change,
            args=args,
            kwargs=kwargs,
            disabled=disabled,
            label_visibility=label_visibility,
            uploader_msg=uploader_msg,
            limit_msg=limit_msg,
            button_msg=button_msg,
            icon=icon,
        )


# Create language-specific instances
en = LanguageFileUploader(LANGUAGE_PACKS["en"])
es = LanguageFileUploader(LANGUAGE_PACKS["es"])
fr = LanguageFileUploader(LANGUAGE_PACKS["fr"])
de = LanguageFileUploader(LANGUAGE_PACKS["de"])
it = LanguageFileUploader(LANGUAGE_PACKS["it"])
pt = LanguageFileUploader(LANGUAGE_PACKS["pt"])
zh = LanguageFileUploader(LANGUAGE_PACKS["zh"])
ja = LanguageFileUploader(LANGUAGE_PACKS["ja"])
ko = LanguageFileUploader(LANGUAGE_PACKS["ko"])
ru = LanguageFileUploader(LANGUAGE_PACKS["ru"])
ar = LanguageFileUploader(LANGUAGE_PACKS["ar"])
hi = LanguageFileUploader(LANGUAGE_PACKS["hi"])
nl = LanguageFileUploader(LANGUAGE_PACKS["nl"])
sv = LanguageFileUploader(LANGUAGE_PACKS["sv"])
pl = LanguageFileUploader(LANGUAGE_PACKS["pl"])
tr = LanguageFileUploader(LANGUAGE_PACKS["tr"])
he = LanguageFileUploader(LANGUAGE_PACKS["he"])
th = LanguageFileUploader(LANGUAGE_PACKS["th"])
id = LanguageFileUploader(LANGUAGE_PACKS["id"])
vi = LanguageFileUploader(LANGUAGE_PACKS["vi"])

def create_custom_uploader(
    uploader_msg: Optional[str] = None,
    limit_msg: Optional[str] = None,
    button_msg: Optional[str] = None,
    icon: Optional[str] = None,
) -> LanguageFileUploader:
    """
    Create a custom file uploader with specific messages.
    
    Parameters
    ----------
    uploader_msg : str or None, default None
        Custom message for "Drag and drop file here".
    limit_msg : str or None, default None
        Custom message for "Limit ... per file".
    button_msg : str or None, default None
        Custom message for "Browse files" button.
    icon : str or None, default None
        Custom icon to use instead of the default cloud upload icon.
        
    Returns
    -------
    LanguageFileUploader
        A custom file uploader instance with the specified messages.
    """
    custom_language_pack = CustomLanguagePack(
        uploader_msg=uploader_msg,
        limit_msg=limit_msg,
        button_msg=button_msg,
        icon=icon,
    )
    return LanguageFileUploader(custom_language_pack)