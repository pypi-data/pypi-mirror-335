import requests
from thonny import get_workbench

EXAM_MODE = False

def download_gplugin():
    global EXAM_MODE
    
    PLUGIN = "/somchai/thonny_grader_plugin.py"
    url_exam = f"http://10.0.5.52{PLUGIN}"
    url_normal = f"https://comprog.nattee.net{PLUGIN}"
    try:
        response = requests.get(url_exam, timeout=3)
        response.raise_for_status()
        EXAM_MODE = True
    except requests.exceptions.RequestException as e:
        response = requests.get(url_normal, timeout=3)
        EXAM_MODE = False
    if response.ok:
        return response.text
    return """
import tkinter as tk
class GraderView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
"""
exec(download_gplugin())

def load_plugin():
    get_workbench().add_view(
        GraderView,
        "2110101: Grader" + (" (Exam.)" if EXAM_MODE else ""),
        "nw",
        visible_by_default = True,
        #default_position_key = "grader_view_position"
    )