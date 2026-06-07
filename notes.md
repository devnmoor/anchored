You need global declarations inside the timer_loop, because without them when Python sees time_remaining = ... inside the function, it creates a new local variable instead of updating the global one. So you need to add `global time_remaining, paused_time_remaining` before the `while True`.

**Without global variable defined in function**
```
noramoor@noras-mbp-2118 anchored % /usr/local/bin/python3 /Users/noramoor/anchored/timer_test.py
1799.9999558925629
1798.994794845581
1797.989662885666
1796.9841167926788
1795.9786596298218
1794.9734208583832
1793.9732558727264
1792.9731769561768
1791.9713678359985
1790.9676027297974
switched to distracted
switched back to focused
1799.999921798706
1798.9948060512543
1797.9937229156494
1796.9895429611206
1795.984368801117
1794.9791848659515
1793.9786727428436
1792.9753119945526
1791.975056886673
1790.9699461460114
```

**With global variable defined in function**
```
noramoor@noras-mbp-2118 anchored % /usr/local/bin/python3 /Users/noramoor/anchored/timer_test.py
1799.9999430179596
1798.9948019981384
1797.9896938800812
1796.9845960140228
1795.982153892517
1794.9798529148102
1793.9747939109802
1792.9696819782257
1791.964495897293
1790.960144996643
switched to distracted
switched back to focused
1790.9600999355316
1789.9554550647736
1788.9503331184387
1787.9451839923859
1786.9423170089722
1785.937742948532
1784.9326441287994
1783.9277911186218
1782.9234731197357
1781.9183781147003
```


"Why is it `mss.mss()` — the module and class have the same name? Could you do `from mss import mss` and just call `mss()` directly instead?"

```python
# Option 1
import mss
with mss.mss() as sct:
    ...

# Option 2
from mss import mss
with mss() as sct:
    ...
```

The reason the first style is common is to avoid confusion — mss is both the module name and the class name inside it. If you do from mss import mss you now have a variable called mss that shadows the module, which can cause confusion later. Keeping it as mss.mss() makes it explicit that you're calling the mss class from the mss module.


ADR stands for Architecture Decision Record