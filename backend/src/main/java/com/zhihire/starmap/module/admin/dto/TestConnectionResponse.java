package com.zhihire.starmap.module.admin.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class TestConnectionResponse {
    private boolean connected;
    private long latencyMs;
    private String message;
}
