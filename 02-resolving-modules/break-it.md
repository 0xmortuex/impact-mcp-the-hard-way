# Break it: Module 02

1. Add `src/shop/util/__init__.py` and write `from .util import helper` somewhere. Does the edge go to the package's `__init__.py`?
2. Write `from shop import Cart` in a new file. The edge goes to `__init__.py`. Is that right? What does `Cart` actually come from, and how would you find out? (This is why the real server follows re-exports.)
3. Write `from ..outside import x` in `src/shop/cart.py` where no `outside` exists. Which bucket does it land in?
4. Create `src/shop/json.py`. Now `import json` inside `src/shop/pricing.py`: stdlib or ours? What does real Python 3 do for absolute imports, and what does your index say?
5. Make two files with the same module name under different roots. Which one should win, and why might "closest to the importer" be a good rule?
