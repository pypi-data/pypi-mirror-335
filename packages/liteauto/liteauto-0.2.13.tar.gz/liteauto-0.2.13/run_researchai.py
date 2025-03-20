import os
import subprocess


def run_deep_research_email():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    ocr_app_path = os.path.join(cur_dir, "liteauto_ext.py")
    cmd = ["python", "-m", ocr_app_path]
    subprocess.run(cmd, env={**os.environ})



def run_app():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    ocr_app_path = os.path.join(cur_dir, "researchai.py")
    cmd = ["streamlit", "run", ocr_app_path]
    subprocess.run(cmd, env={**os.environ, "IN_STREAMLIT": "true"})



if __name__ == "__main__":
    run_app()