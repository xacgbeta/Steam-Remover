
# **Steam Game Remover Tool**  
This tool removes `.st, .lua, .manifest, and .bin` files from:  
📂 `C:/Program Files (x86)/Steam/`

## **How to Use:**  

1. **Download** `Steam Remover` from the [release](https://github.com/xacgbeta/Steam-Remover/releases/tag/main).  
2. **Run** `Remover.exe`.
3. Input AppID.
4. Click `Remove Game`.
5. Click `Restart Steam` to apply changes.
6. Done!

## Additional Notes
- Steam path folder set by default (`C:/Program Files (x86)/Steam/`), unless the steam installation is different then you need to set to where it stores steam.
- Use `Steam Folder` to change the folder path.

### Compiling
`python -m nuitka --follow-imports --enable-plugin=anti-bloat --enable-plugin=tk-inter --remove-output --windows-icon-from-ico=icon.ico --windows-console-mode=disable --standalone --onefile ".\Steam_Remover.py`

Updated: 17/7/25 and still working.
