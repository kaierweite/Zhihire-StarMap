# 第7天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

实现文档解析功能，使用PDFBox和Apache POI解析PDF/DOC/DOCX文件，提取结构化文本内容。

## 今日能力要求

- Apache PDFBox（熟练）
- Apache POI（熟练）
- Java IO（熟练）

**最终产出：**

```text
backend/.../module/parser/
├──service/
│   ├──DocumentParserService.java     # 文档解析接口
│   ├──impl/
│   │   ├──PdfParser.java            # PDF解析器
│   │   ├──WordParser.java           # DOC/DOCX解析器
│   │   └──DocumentParserFactory.java # 解析器工厂
├──dto/
│   └──ParseResult.java              # 解析结果DTO
└──utils/
    └──TextCleaner.java              # 文本清洗工具
```

---

# 第一阶段：引入解析依赖（15分钟）

```xml
<!-- pom.xml 补充 -->
<dependencies>
    <!-- PDFBox -->
    <dependency>
        <groupId>org.apache.pdfbox</groupId>
        <artifactId>pdfbox</artifactId>
        <version>3.0.1</version>
    </dependency>

    <!-- Apache POI (Word) -->
    <dependency>
        <groupId>org.apache.poi</groupId>
        <artifactId>poi-ooxml</artifactId>
        <version>5.2.5</version>
    </dependency>

    <!-- Apache Tika (文本提取统一接口，可选) -->
    <dependency>
        <groupId>org.apache.tika</groupId>
        <artifactId>tika-core</artifactId>
        <version>2.9.1</version>
    </dependency>
</dependencies>
```

---

# 第二阶段：PDF解析器（1.5小时）

## 任务1：PDF文本提取

```java
@Component
public class PdfParser implements DocumentParser {
    private static final Logger log = LoggerFactory.getLogger(PdfParser.class);

    @Override
    public String parse(InputStream inputStream, String fileName) {
        try (PDDocument document = Loader.loadPDF(inputStream.readAllBytes())) {
            PDFTextStripper stripper = new PDFTextStripper();
            stripper.setSortByPosition(true);
            stripper.setStartPage(1);
            stripper.setEndPage(document.getNumberOfPages());

            String text = stripper.getText(document);
            return TextCleaner.clean(text);
        } catch (IOException e) {
            log.error("PDF解析失败: {}", fileName, e);
            throw new BusinessException(500, "PDF解析失败: " + e.getMessage());
        }
    }

    @Override
    public String supportedType() {
        return "pdf";
    }
}
```

## 任务2：PDF高级特性（可选）

```java
// PDF元数据提取
public Map<String, String> extractMetadata(PDDocument document) {
    PDDocumentInformation info = document.getDocumentInformation();
    Map<String, String> metadata = new HashMap<>();
    metadata.put("title", info.getTitle());
    metadata.put("author", info.getAuthor());
    metadata.put("subject", info.getSubject());
    metadata.put("pages", String.valueOf(document.getNumberOfPages()));
    return metadata;
}

// 按章节分段提取（简单实现：根据空白行分段）
public List<String> extractSections(String text) {
    String[] sections = text.split("\\n\\s*\\n");
    return Arrays.stream(sections)
        .map(String::trim)
        .filter(s -> s.length() > 10)
        .toList();
}
```

---

# 第三阶段：Word解析器（1.5小时）

## 任务1：DOCX解析

```java
@Component
public class WordParser implements DocumentParser {
    private static final Logger log = LoggerFactory.getLogger(WordParser.class);

    @Override
    public String parse(InputStream inputStream, String fileName) {
        try {
            if (fileName.endsWith(".docx")) {
                return parseDocx(inputStream);
            } else if (fileName.endsWith(".doc")) {
                return parseDoc(inputStream);
            }
            throw new BusinessException(400, "不支持的Word格式");
        } catch (IOException e) {
            log.error("Word解析失败: {}", fileName, e);
            throw new BusinessException(500, "Word解析失败");
        }
    }

    private String parseDocx(InputStream inputStream) throws IOException {
        StringBuilder sb = new StringBuilder();
        try (XWPFDocument document = new XWPFDocument(inputStream)) {
            // 解析段落
            for (XWPFParagraph paragraph : document.getParagraphs()) {
                String text = paragraph.getText().trim();
                if (!text.isEmpty()) {
                    sb.append(text).append("\n");
                }
            }

            // 解析表格
            for (XWPFTable table : document.getTables()) {
                for (XWPFTableRow row : table.getRows()) {
                    for (XWPFTableCell cell : row.getTableCells()) {
                        sb.append(cell.getText().trim()).append("\t");
                    }
                    sb.append("\n");
                }
            }
        }
        return TextCleaner.clean(sb.toString());
    }

    private String parseDoc(InputStream inputStream) throws IOException {
        // .doc格式使用HWPF
        StringBuilder sb = new StringBuilder();
        try (HWPFDocument document = new HWPFDocument(inputStream)) {
            WordExtractor extractor = new WordExtractor(document);
            String[] paragraphs = extractor.getParagraphText();
            for (String para : paragraphs) {
                sb.append(para.trim()).append("\n");
            }
        }
        return TextCleaner.clean(sb.toString());
    }

    @Override
    public String supportedType() {
        return "word";
    }
}
```

---

# 第四阶段：解析器工厂和文本清洗（1小时）

## 任务1：解析器工厂

```java
@Component
public class DocumentParserFactory {
    @Autowired
    private List<DocumentParser> parsers;

    private final Map<String, DocumentParser> parserMap = new HashMap<>();

    @PostConstruct
    public void init() {
        for (DocumentParser parser : parsers) {
            parserMap.put(parser.supportedType(), parser);
        }
    }

    public DocumentParser getParser(String fileName) {
        String suffix = fileName.substring(fileName.lastIndexOf(".") + 1).toLowerCase();
        String type = switch (suffix) {
            case "pdf" -> "pdf";
            case "doc", "docx" -> "word";
            default -> throw new BusinessException(400, "不支持的文件格式: " + suffix);
        };

        DocumentParser parser = parserMap.get(type);
        if (parser == null) {
            throw new BusinessException(500, "未找到对应的解析器");
        }
        return parser;
    }
}
```

## 任务2：文本清洗工具

```java
public class TextCleaner {
    public static String clean(String text) {
        if (text == null) return "";

        return text
            // 移除多余空白行（连续空行合并为1行）
            .replaceAll("\\n{3,}", "\n\n")
            // 移除页眉页脚常见标记（可选，按需调整）
            .replaceAll("(?m)^\\s*第\\s*\\d+\\s*页\\s*$", "")
            // 移除控制字符（保留换行和制表符）
            .replaceAll("[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F]", "")
            // 统一换行符
            .replaceAll("\\r\\n?", "\n")
            // 移除行首尾空白
            .replaceAll("(?m)^\\s+|\\s+$", "")
            .trim();
    }

    /**
     * 按简历常见章节分割
     */
    public static Map<String, String> splitBySections(String text) {
        Map<String, String> sections = new LinkedHashMap<>();

        // 常见的章节标题
        String[] keywords = {
            "个人信息", "联系方式",
            "教育背景", "教育经历", "学历",
            "工作经历", "工作经验", "工作履历",
            "项目经历", "项目经验", "项目",
            "技能", "专业技能", "技术栈",
            "自我评价", "自我介绍",
            "证书", "荣誉",
            "兴趣爱好"
        };

        // 简单分割：按关键词分割
        String remaining = text;
        for (String keyword : keywords) {
            int index = remaining.indexOf(keyword);
            if (index >= 0) {
                // TODO: 完善章节分割逻辑
            }
        }

        sections.put("fullText", text);
        return sections;
    }
}
```

---

# 第五阶段：解析接口封装（1小时）

## 任务1：文档解析接口

```java
@RestController
@RequestMapping("/api/parser")
public class DocumentParserController {
    @Autowired
    private DocumentParserFactory parserFactory;

    private static final Logger log = LoggerFactory.getLogger(DocumentParserController.class);

    @PostMapping("/extract")
    public Result<String> extractText(@RequestParam("file") MultipartFile file) {
        String fileName = file.getOriginalFilename();
        log.info("开始解析文档: {}", fileName);

        try {
            DocumentParser parser = parserFactory.getParser(fileName);
            String text = parser.parse(file.getInputStream(), fileName);

            // 截取前5000字符展示预览
            String preview = text.length() > 5000
                ? text.substring(0, 5000) + "\n\n...（剩余内容已截断）"
                : text;

            return Result.success(preview);
        } catch (Exception e) {
            log.error("文档解析异常: {}", fileName, e);
            return Result.error(500, "解析失败: " + e.getMessage());
        }
    }
}
```

---

# 第7天验收标准

必须完成：

✅ PDFBox成功提取PDF文本

✅ Apache POI成功提取DOCX文本

✅ Apache POI成功提取DOC文本

✅ 解析器工厂模式正常工作

✅ 文本清洗（去空白页眉页脚）

✅ 解析接口可调用

✅ 大文件解析不卡主线程（异步）

✅ 错误处理和日志记录

✅ Git已提交

---

# 常见问题

**Q：PDFBox解析中文乱码？**

A：确保PDF中的字体嵌入了子集，如果没嵌入需要安装中文字体。

**Q：解析大PDF卡死？**

A：先用文档对象判断页数，超过100页的提示用户。目前控制在10页以内。

**Q：.doc格式兼容性差？**

A：.doc是旧格式，建议用户上传.docx。HWPF对老格式支持有限。

**Q：表格内容丢失？**

A：PDFBox默认不保留表格结构，需要额外处理。Word解析中已包含表格内容。
