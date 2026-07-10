package com.zhihire.starmap.module.admin.dto;

import lombok.Data;

@Data
public class TestConnectionRequest {
    private String apiKey;
    private String baseUrl;
    private String model;
}
