const fs = require('fs');
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\enc_test_out.txt";
const t = '中文测试成功';
fs.writeFileSync(p, t, 'utf-8');
console.log('Script ran OK, wrote: ' + t.length + ' chars');
