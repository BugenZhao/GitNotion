# GitNotion
A simple way to manage your Notion pages with Git. For example, back up your notes or deploy them on GitHub Pages.

## Usage
1. Run `pip3 install -r requirements.txt` in Terminal.
2. Duplicate `config.example.py` to `config.py` and set your configurations.
    ```python
    TOKEN = '123456'  # Notion token
    PAGE = "Notes"  # name of the main page
    TYPE = 'markdown'  # 'markdown' or 'html'
    
    PROXY = 'socks5://localhost:8888'  # set to NONE if you don't need it
    
    LOCAL = '/Users/bugenzhao/Documents/Notes'  # repo's local path
    REMOTE = 'https://github.com/BugenZhao/Notes.git'  # remote repo
    
    PRESERVED = ["README.md"]
    ```
   Find your browser's cookies to get the Notion `token_v2`. For further instructions, visit *Step 1* [here](https://hackernoon.com/4-notionzapier-integrations-you-can-implement-today-l860l30hh).
 
3. Run `python3 ./main.py`