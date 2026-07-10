import pathlib
path = pathlib.Path(r"C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\UserProfile.vue")
old = path.read_text(encoding="utf-8-sig")
script_end = old.find("</script>") + len("</script>")
rest = old[script_end:]
print(f"Script ends at {script_end}, rest length {len(rest)}")
