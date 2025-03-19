import sys

from annotation_tool import App


def start_app():
    sys.exit(App(sys.argv).exec())


if __name__ == "__main__":
    start_app()
