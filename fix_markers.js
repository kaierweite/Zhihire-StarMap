const fs = require('fs');
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let content = fs.readFileSync(p, 'utf-8');
content = content.replace(/\$\$\$\$/g, '');
fs.writeFileSync(p, content, 'utf-8');

// Now verify
content = fs.readFileSync(p, 'utf-8');
console.log('File: ' + content.length + ' chars, ' + content.split('\n').length + ' lines');
console.log('Has  markers: ' + content.includes(''));

// Find the nav-links section
const idx = content.indexOf('<div class=\"nav-links\">');
if (idx >= 0) {
  const endIdx = content.indexOf('</div>', idx + 200) + 6;
  console.log('\\n=== Nav section ===');
  console.log(content.substring(idx, endIdx - idx));
}

// Check for the template error (missing end tag)
const resumeLink = content.indexOf('/user/resume');
if (resumeLink >= 0) {
  const lineStart = content.lastIndexOf('\n', resumeLink) + 1;
  const lineEnd = content.indexOf('\n', resumeLink);
  console.log('\\nResume link line: ' + content.substring(lineStart, lineEnd).trim());
}

console.log('\\nHas complete template tags: ' + (content.includes('<template>') && content.includes('</template>')));
console.log('Has complete style tags: ' + (content.includes('<style') && content.includes('</style>')));
console.log('Has complete script tags: ' + (content.includes('<script') && content.includes('</script>')));
