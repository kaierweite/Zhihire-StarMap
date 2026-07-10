package com.zhihire.starmap.module.system.service;

import com.zhihire.starmap.module.common.exception.BusinessException;
import com.zhihire.starmap.module.system.entity.UploadFile;
import com.zhihire.starmap.module.system.mapper.UploadFileMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.Set;
import java.util.UUID;

@Slf4j
@Service
public class SystemFileServiceImpl implements SystemFileService {

    private final UploadFileMapper uploadFileMapper;
    @Value("") private String basePath;
    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024;
    private static final Set<String> ALLOWED_EXTENSIONS = Set.of(".pdf", ".doc", ".docx");
    private static final byte[] PDF_MAGIC = {0x25, 0x50, 0x44, 0x46};
    private static final byte[] ZIP_MAGIC = {0x50, 0x4B, 0x03, 0x04};

    public SystemFileServiceImpl(UploadFileMapper uploadFileMapper) { this.uploadFileMapper = uploadFileMapper; }

    @Override
    public UploadFile store(MultipartFile file, Long uploaderId) {
        if (file.isEmpty()) throw new BusinessException(400, "文件不能为空");
        if (file.getSize() > MAX_FILE_SIZE) throw new BusinessException(400, "文件大小超过 10MB 限制");
        String originalName = file.getOriginalFilename();
        String ext = getExtension(originalName);
        if (!ALLOWED_EXTENSIONS.contains(ext.toLowerCase())) throw new BusinessException(400, "仅支持 PDF/DOC/DOCX 格式");
        validateMagicNumber(file, ext);
        String monthDir = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM"));
        String storedName = UUID.randomUUID().toString().replace("-", "") + ext;
        Path storageDir = Paths.get(basePath, monthDir).toAbsolutePath();
        Path storagePath = storageDir.resolve(storedName);
        try {
            Files.createDirectories(storageDir);
            try (InputStream is = file.getInputStream()) { Files.copy(is, storagePath, StandardCopyOption.REPLACE_EXISTING); }
            log.info("文件存储成功：{} → {}", originalName, storagePath);
        } catch (IOException e) { log.error("文件写入失败：{}", e.getMessage(), e); throw new BusinessException(500, "文件存储失败"); }
        UploadFile uploadFile = new UploadFile();
        uploadFile.setOriginalName(originalName); uploadFile.setStoredName(storedName); uploadFile.setPath(storagePath.toString());
        uploadFile.setSize(file.getSize()); uploadFile.setMimeType(file.getContentType()); uploadFile.setUploaderId(uploaderId);
        uploadFileMapper.insert(uploadFile); return uploadFile;
    }

    private String getExtension(String filename) { if (filename == null || !filename.contains(".")) throw new BusinessException(400, "文件缺少扩展名"); return filename.substring(filename.lastIndexOf(".")); }
    private void validateMagicNumber(MultipartFile file, String ext) { try { byte[] allBytes = file.getBytes(); if (allBytes.length < 4) throw new BusinessException(400, "文件过小"); byte[] header = Arrays.copyOfRange(allBytes, 0, 4); String lowerExt = ext.toLowerCase(); if (".pdf".equals(lowerExt) && !startsWith(header, PDF_MAGIC)) throw new BusinessException(400, "PDF 文件魔数校验失败"); if (".docx".equals(lowerExt) && !startsWith(header, ZIP_MAGIC)) throw new BusinessException(400, "DOCX 文件魔数校验失败"); } catch (BusinessException e) { throw e; } catch (IOException e) { throw new BusinessException(500, "文件读取失败"); } }
    private boolean startsWith(byte[] data, byte[] prefix) { if (data.length < prefix.length) return false; for (int i = 0; i < prefix.length; i++) { if (data[i] != prefix[i]) return false; } return true; }
}