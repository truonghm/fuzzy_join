# fuzzy_join

A small Python package that join 2 Pandas DataFrames using fuzzy matching by calculating the Levenshtein distance.

To install:

```bash
pip install git+https://github.com/truonghm/fuzzy_join.git
```

## Usage

```python
from fuzzy_join import fuzzy_join
import pandas as pd

x = pd.DataFrame({'col1':['abc','def','adsfads','gfhdhgdf']})
y = pd.DataFrame({'col2':['asdgfg','fghjfgj','adsadfsdfads','gferqwradsfhdhgdf']})

z = fuzzy_join(x,y,left_on=['col1'],right_on=['col2'],threshold=10)
print(z)
```

Output:

|   col1   |  col2  | DISTANCE |
| :------: | :----: | :------: |
|   def    | asdgfg |    4     |
|   abc    | asdgfg |    5     |
| adsfads  | asdgfg |    5     |
| gfhdhgdf | asdgfg |    6     |

## Dependencies

```
pandas==1.3.1
numpy==1.21.1
jellyfish==0.8.8
```
