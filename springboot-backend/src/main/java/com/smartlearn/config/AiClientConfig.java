package com.smartlearn.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

@Configuration
public class AiClientConfig {

    @Value("${smartlearn.ai.base-url}")
    private String aiBaseUrl;

    @Bean
    public RestTemplate aiRestTemplate() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(30000);
        factory.setReadTimeout(600000); // 10 minutes for large PDF parsing
        return new RestTemplate(factory);
    }

    public String getAiBaseUrl() { return aiBaseUrl; }
}
