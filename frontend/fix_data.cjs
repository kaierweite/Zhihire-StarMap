const fs = require('fs');

// Fix AbilityMap.vue
let path = 'C:/Users/Administrator/Desktop/Zhihire-StarMap/frontend/src/views/user/AbilityMap.vue';
let content = fs.readFileSync(path, 'utf-8');
content = content.replace('const d = res.data || {}', 'const d = res.data.data || {}');
fs.writeFileSync(path, content);
console.log('Fixed AbilityMap.vue');

// Fix AbilityMapSection.vue
path = 'C:/Users/Administrator/Desktop/Zhihire-StarMap/frontend/src/views/user/AbilityMapSection.vue';
content = fs.readFileSync(path, 'utf-8');
content = content.replace('const d = res.data || {}', 'const d = res.data.data || {}');
content = content.replace('const gd = res.data.data || {}', 'const gd = res.data.data || {}'); // already correct?
fs.writeFileSync(path, content);
console.log('Fixed AbilityMapSection.vue');

// Fix JobAbilityMap.vue
path = 'C:/Users/Administrator/Desktop/Zhihire-StarMap/frontend/src/views/company/JobAbilityMap.vue';
content = fs.readFileSync(path, 'utf-8');
content = content.replace('const gd = graphRes.data || {}', 'const gd = graphRes.data.data || {}');
fs.writeFileSync(path, content);
console.log('Fixed JobAbilityMap.vue');
