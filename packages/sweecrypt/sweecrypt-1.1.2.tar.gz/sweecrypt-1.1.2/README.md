# SweeCrypt
A basic and fun cipher module for everyone. it converts regular text into symbols on a keyboard, kind of like a cipher. This is only for fun, using this module for cybersecurity is NOT ADVISED

Install:  
```
pip3 install sweecrypt
```

Import:  
```python
>>> import sweecrypt
```

Encrypt:  
```python
>>> sweecrypt.encrypt("hello, world!")
!?~~(:,}(>~/a
```

Decrypt:  
```python
>>> sweecrypt.decrypt("!?~~(:,}(>~/a")
hello, world!
```

With newer versions of sweecrypt (>= 1.1.0), you can shift the encryption database:

```python
>>> sweecrypt.encrypt("hello, world", 3)
'\\!((>ba_>](#'
>>> sweecrypt.decrypt("\\!((>ba_>](#", 3)
'hello, world'
```

So it will output a nonsense string if shifted incorrectly.

```python
>>> sweecrypt.decrypt("\\!((>ba_>](#")
'khoor?!zruog'
```
