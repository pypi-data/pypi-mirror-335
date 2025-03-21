# Dataframe with button

Streamlit component that allows you to display Dataframe with a button

## Installation instructions

```sh
pip install dataframe_with_buttons
```

## Usage instructions

```python
import streamlit as st
import pandas as pd
from dataframe_with_button import static_dataframe
from dataframe_with_button import editable_dataframe
import json
df = pd.DataFrame({
    "BATCH_ID": ["item1", "item2", "item3"],
    "Name": ["Apple", "Banana", "Cherry"],
    "Price": [1.2, 0.8, 2.5],
    "IN_STOCK": [True, False, True],
    "EMAIL": ["abc@gmail.com", "cde@k.com", "abc@gmail.com"]
})

df["EMAIL"] = pd.Categorical(df["EMAIL"], categories=["abc@gmail.com", "cde@k.com"])
result = static_dataframe(df, clickable_column="BATCH_ID")
result2 = editable_dataframe(df, clickable_column="BATCH_ID")
```
<img width="790" alt="Screenshot 2025-01-03 at 10 35 48 PM" src="https://github.com/user-attachments/assets/6581bf69-04f7-4f39-aaed-412d11417cf5" />

