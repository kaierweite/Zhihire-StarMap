import sys
path = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\user\\ResumeCenter.vue"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
i = content.find("<!-- Upload Strip -->")
j = content.find("        <AbilityMapSection />", i)
old = content[i:j]
my41 = chr(39)
new = '''<!-- Upload Strip / File Strip -->
        <div v-if="!resumeList.length" class="upload-strip" @dragover.prevent @drop="handleDrop">
          <div class="strip-body">
            <div class="strip-left">
              <Upload :size="22" class="strip-icon" />
              <div class="strip-text">
                <span class="strip-title">拖拽简历文件到此处</span>
                <span class="strip-hint">支持 PDF / DOC / DOCX . 最大 10MB</span>
              </div>
            </div>
            <div class="strip-right">
              <button class="strip-btn" type="button" @click="triggerFileInput">
                <Upload :size="15" /> 选择文件
              </button>
            </div>
          </div>
          <input ref="fileInputRef" type="file" accept=".pdf,.doc,.docx" @change="handleFileChange" hidden />
        </div>

        <div v-else class="file-strip" @dragover.prevent @drop="handleDrop">
          <div class="file-strip-inner">
            <div class="file-strip-items">
              <div
                v-for="item in resumeList"
                :key="item.id"
                class="file-strip-item"
                @click="openDetail(item.id)"
                :title="item.title ''' + my41 + my41 + ''' item.file_name ''' + my41 + my41 + my41 + my41 + '''
              >
                <FileText :size="16" class="file-strip-icon" />
                <span class="file-strip-name">{{ item.title ''' + my41 + my41 + ''' item.file_name ''' + my41 + my41 + ''' \u672a\u547d\u540d''' + my41 + my41 + ''' }}</span>
              </div>
            </div>
            <button class="file-strip-add" type="button" @click="triggerFileInput" title="继续上传">
              <Plus :size="18" />
            </button>
          </div>
          <div class="file-strip-footer">
            <span class="file-strip-count">共 {{ totalCount }} 份简历</span>
            <span class="file-strip-hint">点击简历查看详情</span>
          </div>
          <input ref="fileInputRef" type="file" accept=".pdf,.doc,.docx" @change="handleFileChange" hidden />
        </div>

'''
content = content.replace(old, new, 1)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("OK")
