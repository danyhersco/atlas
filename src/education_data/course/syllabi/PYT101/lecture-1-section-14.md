Variables defined within a function are said to have *local scope*. That is to say that we can only reference them within that function. Consider the example function defined above where we used the *local* variable *height*. You can see that if you try to print the variable height outside the function, you will get an error.

```python
print(height)

---------------------------------------------------------------------------
NameError                                 Traceback (most recent call last)
<ipython-input-50-aa6406a13920> in <module>
----> 1 print(height)

NameError: name 'height' is not defined
```