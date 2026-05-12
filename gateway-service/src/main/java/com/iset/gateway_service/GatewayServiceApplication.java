package com.iset.gateway_service;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.HashMap;
import java.util.Map;

@SpringBootApplication
public class GatewayServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(GatewayServiceApplication.class, args);
    }

    @Bean
    public RouteLocator gatewayRoutes(RouteLocatorBuilder builder) {
        return builder.routes()

                // ── TICKET SERVICE ──────────────────────────────
                // /api/tickets/** → redirigé vers TICKET-SERVICE
                // lb:// = load balancer (nom vient du Config Service)
                .route("ticket-route", r -> r
                        .path("/api/tickets/**")
                        .filters(f -> f
                                .addRequestHeader("X-Source", "gateway")
                                .addResponseHeader("X-Service", "ticket-service")
                                // Circuit Breaker : si Ticket Service tombe
                                // → renvoie vers /fallback/ticket
                                .circuitBreaker(c -> c
                                        .setName("ticketCircuitBreaker")
                                        .setFallbackUri("forward:/fallback/ticket"))
                        )
                        .uri("lb://TICKET-SERVICE")
                )

                // ── AGENT SERVICE ───────────────────────────────
                // /api/v1/agents/** → redirigé vers AGENT-SERVICE
                .route("agent-route", r -> r
                        .path("/api/v1/agents/**")
                        .filters(f -> f
                                .addRequestHeader("X-Source", "gateway")
                                .addResponseHeader("X-Service", "agent-service")
                                // Circuit Breaker : si Agent Service tombe
                                // → renvoie vers /fallback/agent
                                .circuitBreaker(c -> c
                                        .setName("agentCircuitBreaker")
                                        .setFallbackUri("forward:/fallback/agent"))
                        )
                        .uri("lb://AGENT-SERVICE")
                )

                // ── NOTIFICATION SERVICE ────────────────────────
                // /api/notifications/** → redirigé vers NOTIFICATION-SERVICE
                .route("notification-route", r -> r
                        .path("/api/notifications/**")
                        .filters(f -> f
                                .addRequestHeader("X-Source", "gateway")
                                .addResponseHeader("X-Service", "notification-service")
                                // Circuit Breaker : si Notification Service tombe
                                // → renvoie vers /fallback/notification
                                .circuitBreaker(c -> c
                                        .setName("notificationCircuitBreaker")
                                        .setFallbackUri("forward:/fallback/notification"))
                        )
                        .uri("lb://NOTIFICATION-SERVICE")
                )

                .build();
    }
}

// ════════════════════════════════════════════════════════
//  FALLBACK CONTROLLER
//  Répond quand un service est indisponible (Circuit Breaker)
// ════════════════════════════════════════════════════════
@RestController
class FallbackController {

    // Fallback pour le Ticket Service
    @GetMapping("/fallback/ticket")
    public Map<String, String> ticketFallback() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "SERVICE_UNAVAILABLE");
        response.put("service", "Ticket Service");
        response.put("message", "Le service de tickets est temporairement indisponible.");
        response.put("suggestion", "Veuillez réessayer dans quelques instants.");
        return response;
    }

    // Fallback pour le Agent Service
    @GetMapping("/fallback/agent")
    public Map<String, String> agentFallback() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "SERVICE_UNAVAILABLE");
        response.put("service", "Agent Service");
        response.put("message", "Le service des agents est temporairement indisponible.");
        response.put("suggestion", "Veuillez réessayer dans quelques instants.");
        return response;
    }

    // Fallback pour le Notification Service
    @GetMapping("/fallback/notification")
    public Map<String, String> notificationFallback() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "SERVICE_UNAVAILABLE");
        response.put("service", "Notification Service");
        response.put("message", "Le service de notifications est temporairement indisponible.");
        response.put("suggestion", "Les notifications seront envoyées dès que le service sera rétabli.");
        return response;
    }
}