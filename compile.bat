:: Compile all .py files to .mpy files using mpy-cross
@echo off
for %%f in (*.py) do (
    echo "Will delete %%~nf.mpy"
    del %%~nf.mpy
    echo "Will compile %%f file"
    start C:\Tools\micropython-master\mpy-cross\mpy-cross.exe %%f
)