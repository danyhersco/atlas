1. Navigate the [Jupyter](http://jupyter.org/) toolbar to "Insert"->"Insert Cell Below". Note from the toolbar that you can select a cell to be 'Code' (this is the default), 'Markdown' (the cell you are reading right now is written in [Markdown](https://en.wikipedia.org/wiki/Markdown) - double click this cell to investigate further), and 'Raw' (its content is not evaluated by the notebook).
2. Copy&paste the code from the previous code cell into your newly created code cell below. Make sure it runs!
3. To see how important it is to use the correct [syntax](https://en.wikipedia.org/wiki/Syntax), replace `**` with `^` in your code and try running the cell again. You should see something like the following:

```python
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-4-6e110a567f02> in <module>
      3 # cell, or click on the 'Run' widget on the Jupyter toolbar above.
      4 
----> 5 print(5*0.6 - 0.5*9.81*0.6^2)

TypeError: unsupported operand type(s) for ^: 'float' and 'int'
```
4. Undo that change so your code is working again; now change `print` to `write` and see what happens when you run the cell. You should see something like:

```python
---------------------------------------------------------------------------
NameError                                 Traceback (most recent call last)
<ipython-input-5-a3da902ceb19> in <module>
      3 # cell, or click on the 'Run' widget on the Jupyter toolbar above.
      4 
----> 5 write(5*0.6 - 0.5*9.81*0.6**2)

NameError: name 'write' is not defined
```

While a human might still understand these statements, they do not mean anything to the Python interpreter. Rather than throwing your hands up in the air whenever you get an error message like the above (you are going to see many during your course), train yourself to read error messages carefully to get an idea what it is complaining about, and re-read your code from the perspective of the Python interpreter.

Error messages can look bewildering and even frustrating at first, but **it gets much easier with practise**.