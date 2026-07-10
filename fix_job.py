import os
vue = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\company\JobManage.vue"

with open(vue, "r", encoding="utf-8") as f:
    c = f.read()

# Add computed import
c = c.replace(
    'import { ref, onMounted } from "vue"',
    'import { ref, computed, onMounted } from "vue"'
)

# Add searchKw and filteredJobs
old = "const stats = ref({ total: 0, open: 0, closed: 0, draft: 0 })"
new = old + "\nconst searchKw = ref('')\nconst filteredJobs = computed(() => {\n  if (!searchKw.value.trim()) return jobs.value\n  const kw = searchKw.value.trim().toLowerCase()\n  return jobs.value.filter(j => j.title.toLowerCase().includes(kw))\n})"
c = c.replace(old, new)

# Remove detail link and duplicate edit
old_actions = """<el-button text type="primary" size="small" @click="openEdit(row)">
                <Edit :size="14" /> ??
              </el-button>
              <el-button text type="primary" size="small" @click="router.push('/company/jobs/detail/' + row.id)">
                <Eye :size="14" /> ??
              </el-button>
              <el-button text type="primary" size="small" @click="openEdit(row)">
                <Edit :size="14" /> ??
              </el-button>
              <el-button text type="danger" size="small" @click="handleDelete(row)">
                <Delete :size="14" /> ??
              </el-button>"""
new_actions = """<el-button text type="primary" size="small" @click="openEdit(row)">
                <Edit :size="14" /> ??
              </el-button>
              <el-button text type="danger" size="small" @click="handleDelete(row)">
                <Delete :size="14" /> ??
              </el-button>"""
c = c.replace(old_actions, new_actions)

# Remove unused Eye import
c = c.replace(
    "import { Plus, Edit, Delete, Eye, Search, Clock, MapPin }",
    "import { Plus, Edit, Delete, Search, Clock, MapPin }"
)

with open(vue, "w", encoding="utf-8") as f:
    f.write(c)

print("Done")
