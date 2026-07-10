const fs = require('fs');
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
const content = fs.readFileSync(p, 'utf-8');
const lines = content.split('\n').length;
const chars = content.length;
console.log('File size: ' + chars + ' chars, ' + lines + ' lines');

// Check nav section
const navStart = content.indexOf('<div class=\"nav-links\">');
const navEnd = content.indexOf('</div>', content.indexOf('nav-actions')) + 6;
const navSection = content.substring(navStart, navEnd - navStart);
console.log('\\n=== Nav section ===');
console.log(navSection);

// Check for common issues
console.log('\\n=== Verification ===');
console.log('Has </router-link> for resume: ' + content.includes('<router-link to=\"/user/resume\"'));

// Check template well-formed
const templateStart = content.indexOf('<template>');
const templateEnd = content.indexOf('</template>');
console.log('Template section: ' + (templateEnd - templateStart) + ' chars');

// Verify no placeholder indicators
console.log('Has BTK markers: ' + content.includes('BTK'));
console.log('Has QQQ markers: ' + content.includes('QQQ'));
console.log('Has  markers: ' + content.includes(''));
