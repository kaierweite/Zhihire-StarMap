import sys
c = open(sys.argv[1], "r", encoding="utf-8").read()
checks = [
    ("root color", "itemStyle: { color:" in c),
    ("level1 white+shadow", "textShadowColor: 'rgba(0,0,0,0.5)'" in c),
    ("all labels white", c.count("color: '#fff'") >= 2),
]
for name, ok in checks:
    print(f"{name}: {'OK' if ok else 'FAIL'}")
