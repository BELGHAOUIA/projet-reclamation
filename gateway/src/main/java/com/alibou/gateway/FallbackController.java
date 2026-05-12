package com.alibou.gateway;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
public class FallbackController {

    @GetMapping("/fallback/weather")
    public Map<String, String> weatherFallback() {
        Map<String, String> r = new HashMap<>();
        r.put("status", "SERVICE_UNAVAILABLE");
        r.put("service", "Weather API");
        r.put("message", "Service météo temporairement indisponible.");
        return r;
    }
}