import typer
import webbrowser
from typing import Annotated
import pywinctl as pwc
from .config import load_config, init_config

app = typer.Typer()

def open_in_browser(browser: str, url: str):
    """Open URL in specified browser"""
    if browser.lower() == "chrome":
        webbrowser.get('google-chrome').open_new(url)
    else:
        webbrowser.open(url)

def switch_to_window(
    window_name: Annotated[str, typer.Argument(help="Name of the window to switch to")]
):
    """Switch to a window that matches the given name or open it if configured"""
    try:
        config = load_config()
        shortcuts = config.get("shortcuts", {})
        
        # Check if we have a shortcut configured
        if window_name in shortcuts:
            shortcut = shortcuts[window_name]
            browser = shortcut.get("browser", "default")
            url = shortcut.get("url")
            
            # Try to find existing window first
            matching_windows = pwc.getWindowsWithTitle(
                window_name,
                condition=pwc.Re.CONTAINS,
                flags=pwc.Re.IGNORECASE
            )
            
            if matching_windows:
                # Activate existing window
                window = list(reversed(matching_windows))[0]
                window.activate()
                print(f"Switched to window: {window.title}")
            else:
                # Open new browser window
                open_in_browser(browser, url)
                print(f"Opening {url} in {browser}")
            return
        
        # Default behavior - try to switch to matching window
        matching_windows = pwc.getWindowsWithTitle(
            window_name, 
            condition=pwc.Re.CONTAINS, 
            flags=pwc.Re.IGNORECASE
        )
        
        if not matching_windows:
            print(f"No windows found matching '{window_name}'")
            return
        
        window = list(reversed(matching_windows))[0]
        window.activate()
        print(f"Switched to window: {window.title}")
        
    except Exception as e:
        print(f"Error switching windows: {e}")

@app.command()
def init():
    """Initialize the config file with default values"""
    init_config()

@app.command()
def switch(
    window_name: Annotated[str, typer.Argument(help="Name of the window to switch to")]
):
    """Switch to a window or open it based on config"""
    switch_to_window(window_name)

@app.command()
def show(
    app_name: Annotated[str, typer.Argument(help="Name of the application to show recent windows for")],
    limit: Annotated[int, typer.Option(help="Number of recent windows to show")] = None
):
    """Show recent windows for a given application"""
    try:
        matching_windows = pwc.getWindowsWithTitle(
            app_name,
            condition=pwc.Re.CONTAINS,
            flags=pwc.Re.IGNORECASE
        )
        
        if not matching_windows:
            print(f"No windows found for '{app_name}'")
            return
        
        recent_windows = list(reversed(matching_windows))
        if limit:
            recent_windows = recent_windows[:limit]
        
        print(f"\nRecent windows for '{app_name}':")
        for i, window in enumerate(recent_windows, 1):
            print(f"{i}. {window.title}")
            
    except Exception as e:
        print(f"Error listing windows: {e}")

def main():
    app()
