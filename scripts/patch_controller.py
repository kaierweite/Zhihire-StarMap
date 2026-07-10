# -*- coding: utf-8 -*-
import os

path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'backend',
    'src', 'main', 'java', 'com', 'zhihire', 'starmap',
    'module', 'admin', 'controller', 'AdminAIConfigController.java')

with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Add imports
text = text.replace(
    'import com.zhihire.starmap.module.common.result.Result;',
    'import com.zhihire.starmap.module.common.result.Result;\n'
    'import org.springframework.beans.factory.annotation.Value;\n'
    'import org.springframework.web.client.RestTemplate;'
)

# Add fields
text = text.replace(
    '    private final ObjectMapper objectMapper;',
    '    private final ObjectMapper objectMapper;\n'
    '    private final RestTemplate restTemplate;\n'
    '    @Value("${ai.service.url:http://localhost:8000}")\n'
    '    private String aiServiceUrl;'
)

# Constructor
text = text.replace(
    'public AdminAIConfigController(AiModelConfigMapper configMapper, ObjectMapper objectMapper) {',
    'public AdminAIConfigController(AiModelConfigMapper configMapper, ObjectMapper objectMapper, RestTemplate restTemplate) {'
)
text = text.replace(
    '        this.objectMapper = objectMapper;\n    }',
    '        this.objectMapper = objectMapper;\n        this.restTemplate = restTemplate;\n    }'
)

# Add notifyAiService after each CRUD
text = text.replace(
    'log.info("AI config created: providerId={}", entity.getProviderId());',
    'log.info("AI config created: providerId={}", entity.getProviderId());\n        notifyAiService();'
)
text = text.replace(
    'log.info("AI config updated: id={}", id);',
    'log.info("AI config updated: id={}", id);\n        notifyAiService();'
)
text = text.replace(
    'log.info("AI config deleted: id={}", id);',
    'log.info("AI config deleted: id={}", id);\n        notifyAiService();'
)

# Add notifyAiService method
text = text.replace(
    '    // \u2013 helpers \u2013',
    '    private void notifyAiService() {\n'
    '        try {\n'
    '            restTemplate.postForEntity(\n'
    '                    aiServiceUrl + "/ai/internal/refresh-config", null, String.class);\n'
    '            log.info("Notified ai-service to refresh configs");\n'
    '        } catch (Exception e) {\n'
    '            log.warn("Failed to notify ai-service (non-fatal): {}", e.getMessage());\n'
    '        }\n'
    '    }\n\n'
    '    // \u2013 helpers \u2013'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print(f"Controller patched, {os.path.getsize(path)} bytes")
