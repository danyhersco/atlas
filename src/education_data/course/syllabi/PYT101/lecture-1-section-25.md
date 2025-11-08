So far, one variable has referred to one number (or string). Sometimes, however, we naturally have a collection of numbers, e.g. degrees −20, −15, −10, −5, 0, ..., 40. One way to store these values in a computer program would be to have one variable per value:


```python
C1 = -20
C2 = -15
C3 = -10
...
C13 = 40
```

This is clearly a terrible solution, particularly if we have lots of values. A better way of doing this is to collect values together in a list:


```python
C = [-20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40]
```

Now, there is just one variable, `C`, holding all the values. We access elements in a list via an index. List indices are always *zero-indexed*, i.e. they are numbered as 0, 1, 2, and so forth up to the number of elements minus one:


```python
mylist = [4, 6, -3.5]
print("First element:", mylist[0])
print("Second element:", mylist[1])
print("Third element:", mylist[2])
```

Here are a few examples of operations that you can perform on lists:


```python
C = [-10, -5, 0, 5, 10, 15, 20, 25, 30]
C.append(35)  # add new element 35 at the end
print(C)
```


```python
C = C + [40, 45]  # And another list to the end of C
print(C)
```


```python
C.insert(0, -15)  # Insert -15 as index 0
print(C)
```


```python
del C[2]  # delete 3rd element
print(C)
```


```python
del C[2]  # delete what is now 3rd element
print(C)
```


```python
print(len(C))  # length of list
```


```python
print(C.index(10))  # Find the index of the element with the value 10
```


```python
print(10 in C)  # True only if the value 10 is stored in the list
```


```python
print(C[-1])  # The last value in the list
```


```python
print(C[-2])  # The second last value in the list
```

We can also extract sublists using `:`:


```python
print(C[5:])  # From index 5 to the end of the list
```


```python
print(C[5:7])  # From index 5 up to, but NOT including index 7
```


```python
print(C[7:-1])  # From index 7 up to the second last element
```


```python
print(C[:])  # [:] specifies the whole list.
```

We can also *unpack* the elements of a list into separate variables:


```python
somelist = ["Curly", "Larry", "Moe"]
stooge1, stooge2, stooge3 = somelist
print(f"stooge1: {stooge1}, stooge2: {stooge2}, stooge3: {stooge3}")
```