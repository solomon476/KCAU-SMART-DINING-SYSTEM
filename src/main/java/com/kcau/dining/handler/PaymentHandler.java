package com.kcau.dining.handler;

import com.kcau.dining.model.Payment;
import com.kcau.dining.service.PaymentService;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Handles HTTP requests for payment simulation and payment ledger queries.
 */
public class PaymentHandler implements HttpHandler {

    private final PaymentService paymentService = new PaymentService();

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        if (HttpHelper.handleCorsPreflight(exchange)) return;

        String path = exchange.getRequestURI().getPath();
        String method = exchange.getRequestMethod();

        try {
            if ("/api/payments".equals(path) && "POST".equalsIgnoreCase(method)) {
                handleRecordPayment(exchange);
            } else if ("/api/payments".equals(path) && "GET".equalsIgnoreCase(method)) {
                handleGetAllPayments(exchange);
            } else {
                HttpHelper.sendError(exchange, 404, "Endpoint not found");
            }
        } catch (IllegalArgumentException e) {
            HttpHelper.sendError(exchange, 400, e.getMessage());
        } catch (Exception e) {
            HttpHelper.sendError(exchange, 500, "Server error: " + e.getMessage());
        }
    }

    private void handleRecordPayment(HttpExchange exchange) throws Exception {
        Map<String, String> body = HttpHelper.parseJsonBody(exchange);
        String orderId = body.get("orderId");
        String method = body.getOrDefault("method", "MPESA");
        String amountStr = body.get("amount");
        String status = body.getOrDefault("status", "SIMULATED_SUCCESS");
        String reference = body.get("reference");

        if (orderId == null || orderId.isBlank()) {
            HttpHelper.sendError(exchange, 400, "orderId is required");
            return;
        }

        double amount = 0.0;
        if (amountStr != null) {
            try { amount = Double.parseDouble(amountStr); } catch (Exception ignored) {}
        }

        Payment payment = paymentService.recordPayment(orderId, method, amount, status, reference);

        Map<String, Object> resp = new HashMap<>();
        resp.put("message", "Payment recorded successfully (Simulated)");
        resp.put("paymentId", payment.getId());
        resp.put("orderId", payment.getOrderId());
        resp.put("reference", payment.getReference());
        resp.put("amount", payment.getAmount());
        resp.put("status", payment.getStatus());
        resp.put("createdAt", payment.getCreatedAt().toString());
        HttpHelper.sendJson(exchange, 201, resp);
    }

    private void handleGetAllPayments(HttpExchange exchange) throws Exception {
        List<Payment> list = paymentService.getAllPayments();
        List<Map<String, Object>> responseList = new ArrayList<>();
        for (Payment p : list) {
            Map<String, Object> m = new HashMap<>();
            m.put("paymentId", p.getId());
            m.put("orderId", p.getOrderId());
            m.put("method", p.getMethod());
            m.put("amount", p.getAmount());
            m.put("status", p.getStatus());
            m.put("reference", p.getReference());
            m.put("createdAt", p.getCreatedAt().toString());
            responseList.add(m);
        }
        HttpHelper.sendJson(exchange, 200, responseList);
    }
}
