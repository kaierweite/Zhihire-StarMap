package com.zhihire.starmap;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@MapperScan("com.zhihire.starmap.module.*.mapper")
@EnableAsync
public class StarMapApplication {

    public static void main(String[] args) {
        SpringApplication.run(StarMapApplication.class, args);
    }
}
